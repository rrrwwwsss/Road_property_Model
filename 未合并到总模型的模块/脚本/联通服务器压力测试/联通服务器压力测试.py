import aiohttp
import asyncio
import base64
import time
from PIL import Image
import io

# ------------------ 配置部分 ------------------
API_URL = "http://192.168.0.161:1025/v1/chat/completions"  # 目标接口
IMAGE_PATH = "camera_11000000001313208456_20251015_120919.jpg"  # 测试图片
CONCURRENCY = 10  # 并发客户端数
REQUESTS_PER_CLIENT = 1  # 每个客户端请求次数
MAX_IMAGE_SIZE_KB = 300  # 压缩后的图片最大大小，避免超长

# ------------------ 图片处理 ------------------
def encode_image(image_path):
    img = Image.open(image_path)
    # 压缩图片
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

IMAGE_DATA_URL = encode_image(IMAGE_PATH)

# ------------------ 构造 payload ------------------
wajue_question = """
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

def build_payload(question: str):
    return {
        "model": "qwen2_5_vl",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": IMAGE_DATA_URL}},
                    {"type": "text", "text": question}
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

# ------------------ 异步请求逻辑 ------------------
async def send_request(session, question):
    payload = build_payload(question)
    headers = {"Content-Type": "application/json"}
    try:
        async with session.post(API_URL, json=payload, headers=headers, timeout=60) as resp:
            result = await resp.text()
            if resp.status == 200:
                return True, result
            else:
                return False, f"{resp.status}: {result}"
    except Exception as e:
        return False, str(e)

async def worker(name, session):
    for i in range(REQUESTS_PER_CLIENT):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {name} 开始第 {i+1} 次请求")
        success, result_or_err = await send_request(session, wajue_question)
        if success:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {name} 第 {i+1} 次请求成功, 返回长度: {len(result_or_err)}")
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {name} 第 {i+1} 次请求失败: {result_or_err}")

async def main():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [worker(f"客户端-{i}", session) for i in range(CONCURRENCY)]
        await asyncio.gather(*tasks)
    print(f"总耗时: {time.time() - start:.2f} 秒")

if __name__ == "__main__":
    asyncio.run(main())
