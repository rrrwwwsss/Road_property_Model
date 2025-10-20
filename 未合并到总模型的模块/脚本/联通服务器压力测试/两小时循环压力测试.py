import aiohttp
import asyncio
import base64
import time
from PIL import Image
import io
import os
from datetime import datetime

# ------------------ 配置部分 ------------------
API_URL = "http://192.168.0.161:1025/v1/chat/completions"  # 模型接口地址
IMAGE_DIR = "/data1/qwen2v/road_property_rightsmodel/shibie_yuantu/wajue/"  # 图片目录
CONCURRENCY = 10            # 并发客户端数量
REQUESTS_PER_CLIENT = 1     # 每轮每客户端请求次数
MAX_IMAGE_SIZE_KB = 300     # 最大压缩后体积
RUN_DURATION = 1 * 60 * 60  # 持续时间(秒) —— 2小时
LOG_FILE = "pressure_test_log.txt"         # 请求运行日志
MODEL_OUTPUT_FILE = "model_output_log.txt" # 模型返回内容单独保存

# ------------------ 工具函数 ------------------
def log_write(text):
    """写入运行日志"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def log_model_output(image_name, output_text):
    """写入模型输出日志"""
    with open(MODEL_OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"【图片】{image_name}\n")
        f.write(output_text.strip() + "\n")
        f.write("-" * 80 + "\n")

def encode_image(image_path):
    """压缩并Base64编码图片"""
    img = Image.open(image_path)
    buffer = io.BytesIO()
    quality = 90
    while True:
        buffer.seek(0)
        img.save(buffer, format="JPEG", quality=quality)
        size_kb = buffer.tell() / 1024
        if size_kb <= MAX_IMAGE_SIZE_KB or quality <= 10:
            break
        quality -= 5
    base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_str}"

def get_all_images(dir_path):
    """获取目录下所有jpg文件"""
    images = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            if f.lower().endswith(".jpg"):
                images.append(os.path.join(root, f))
    return sorted(images)

# ------------------ 请求内容 ------------------
QUESTION = """
Role: You are an intelligent assistant capable of accurately identifying road occupation or excavation activities in images.
Task: Analyze the given image and determine if any vehicles are engaged in road occupation or excavation operations. 
Special attention should be paid to:
1. Are there any obvious construction-related signs or obstacles around the vehicle, such as fences, traffic cones, or earth mounds?
2. Are there people interacting with the vehicle, operating the vehicle, or directing the operation?
Exclude interfering factors:
1. Ignore large vehicles that are normally driving or parked in a safe area and not engaged in construction.
2. Ignore buildings, pedestrians, toll stations, and road isolation facilities.
3. Image quality limitation: If the image is blurry or poorly lit, answer "no".
"""
model_result = 'Output : If the above behavior can be identified, then the following result will be returned: {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]}, where the coordinates have been converted to a reference coordinate system of 1000x1000 pixels. Otherwise, return {"result": "no"}.'

def build_payload(image_b64, question):
    """构造 payload"""
    return {
        "model": "qwen2_5_vl",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_b64}},
                    {"type": "text", "text": question+model_result}
                ]
            }
        ],
        "max_tokens": 512,
        "do_sample": True,
        "repetition_penalty": 1.0,
        "temperature": 0.01,
        "top_p": 0.001,
        "top_k": 1
    }

# ------------------ 异步逻辑 ------------------
async def send_request(session, image_path):
    """发送单个请求"""
    image_b64 = encode_image(image_path)
    payload = build_payload(image_b64, QUESTION)
    headers = {"Content-Type": "application/json"}

    try:
        async with session.post(API_URL, json=payload, headers=headers, timeout=60) as resp:
            text = await resp.text()
            if resp.status == 200:
                return True, text
            else:
                return False, f"{resp.status}: {text}"
    except Exception as e:
        return False, str(e)

async def worker(name, session, images, stop_time, counter):
    """客户端任务：循环遍历图片并持续发送请求"""
    while time.time() < stop_time:
        for img_path in images:
            if time.time() >= stop_time:
                break
            img_name = os.path.basename(img_path)
            start_t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{start_t}] {name} 发送: {img_name}")

            success, result = await send_request(session, img_path)
            end_t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if success:
                counter["success"] += 1
                msg = f"[{end_t}] ✅ {name} 成功 ({img_name}) | 响应长度: {len(result)}"
                print(msg)
                log_write(msg)
                log_model_output(img_name, result)
            else:
                counter["fail"] += 1
                msg = f"[{end_t}] ❌ {name} 失败 ({img_name}): {result}"
                print(msg)
                log_write(msg)

        await asyncio.sleep(0.5)  # 控制速率

async def main():
    start = time.time()
    stop_time = start + RUN_DURATION
    os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)

    all_images = get_all_images(IMAGE_DIR)
    if not all_images:
        print(f"❌ 未找到任何 JPG 文件，请检查路径: {IMAGE_DIR}")
        return

    log_write(f"====== 压力测试开始 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ======")
    log_write(f"图片总数: {len(all_images)} 张")

    counter = {"success": 0, "fail": 0}
    async with aiohttp.ClientSession() as session:
        tasks = [worker(f"客户端-{i}", session, all_images, stop_time, counter) for i in range(CONCURRENCY)]
        await asyncio.gather(*tasks)

    total_time = time.time() - start
    total_processed = counter["success"] + counter["fail"]
    print(f"\n====== ✅ 测试结束 ======")
    print(f"总处理图片数: {total_processed}")
    print(f"成功: {counter['success']} | 失败: {counter['fail']}")
    print(f"总耗时: {total_time/60:.2f} 分钟")

    log_write(f"====== 压力测试结束 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ======")
    log_write(f"总处理图片: {total_processed}, 成功: {counter['success']}, 失败: {counter['fail']}")
    log_write(f"总耗时: {total_time:.2f} 秒")

if __name__ == "__main__":
    asyncio.run(main())
