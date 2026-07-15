from detectors.占用挖掘公路连续帧识别 import process_images as process_images1
from detectors.四项违法行为识别 import process_images as process_images2
from detectors.堆放物品_摆设摊位 import process_images as process_images3
from config.配置 import IMAGE_QIEPIAN_PATH, IMAGE_API
from datetime import datetime, time
from PIL import Image
def load_image(path):
    try:
        image = Image.open(path)
        return image
    except Exception as e:
        print(f"加载图片时出错: {e}")
        return None


import requests

# 1. 定义类型映射，将违法行为归类到对应的处理函数
# 这样即便以后增加类型，也只需修改这个字典
# 直接在字典里存储函数对象
PROCESSOR_MAP = {
    '擅自占用、挖掘公路': process_images1,
    '在公路用地范围内设置公路标志以外的其他标志': process_images2,
    '遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全': process_images2,
    '在公路范围内擅自移动井盖': process_images2,
    '在公路上及公路用地范围内摆摊设点': process_images3,
    '在公路上及公路用地范围内堆放物品': process_images3,
}

# 获取图片列表方法
def fetch_images_by_violation(violation_type, base_url):
    """
    根据违法行为类型获取未处理的图片列表

    :param violation_type: 违法行为类型，如 "擅自占用、挖掘公路"
    :param base_url: 服务基础 URL
    :return: 图片列表（list）或 None（出错时）
    """
    url = f"{base_url}/images"
    payload = {"violation_type": violation_type}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            images = response.json()
            print(f"✅ 成功获取 {len(images)} 条图片信息")
            return images

        elif response.status_code == 404:
            error_detail = response.json().get("detail", "未知原因")
            print(f"⚠️ 未找到数据: {error_detail}")
            return []

        elif response.status_code == 500:
            error_detail = response.json().get("detail", "未知服务器错误")
            print(f"❌ 服务器错误: {error_detail}")
            return None

        else:
            print(f"❓ 未知响应状态码: {response.status_code}, 内容: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return None
# 修改数据库处理状态方法
def submit_feedback(violation_type, name_list, base_url):
    url = f"{base_url}/feedback"
    payload = {
        "violation_type": violation_type,
        "name_list": name_list
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print("✅ 反馈提交成功:", result)
            return result
        elif response.status_code == 500:
            error = response.json()
            print("❌ 服务器错误:", error.get("detail", "未知错误"))
        else:
            print(f"⚠️ 未知响应状态码: {response.status_code}, 内容: {response.text}")

    except requests.exceptions.RequestException as e:
        print("❌ 请求失败:", e)
        return None

def chuli(question, output_folder):
    violation_type = list(question.keys())[0]
    print(f"正在处理违法行为：{violation_type}")

    # 2. 检查类型是否在定义的映射中
    processor = PROCESSOR_MAP.get(violation_type)
    if not processor:
        print(f"未知的违法类型: {violation_type}")
        return

    url = IMAGE_API
    try:
        # 3. 修复参数传递，通常需要键值对
        print(f"\n📤 正在获取{violation_type}行为数据库列表")
        response = fetch_images_by_violation(violation_type,url)
        if response == None:
            print(f"{violation_type}列表里没有数据，程序退出")
            return None
        print(f'获取了{len(response)}条数据')
        # 4. 统一的循环处理逻辑

        index = 0
        # print(response)
        # 1. 安全检查：确保 response 是列表且不为空
        if response and isinstance(response, list):


            if len(response) > 200:
                print(f"检测到数据量为 {len(response)}，触发去重策略：每个地点仅保留最新的一条。")

                latest_data_map = {}  # 用于存储 {location: data_item}

                for item in response:
                    loc = item.get("location")
                    current_time = item.get("capture_time", "")

                    # 如果该地点还没出现过，或者当前记录的时间比已存的记录更晚
                    if loc not in latest_data_map or current_time > latest_data_map[loc].get("capture_time"):
                        latest_data_map[loc] = item

                # 将去重后的字典值转回列表
                response = list(latest_data_map.values())
                print(f"去重完成，剩余处理数据量：{len(response)} 条,数据：{response}")
            else:
                print('数据量低于200条，直接处理')
            # --- 数据过滤逻辑结束 ---

        total_count = len(response)
        for data in response:
            index += 1
            image_name = data.get("name")
            print(f'📤{violation_type}正在处理第{index}条数据，图片名称{image_name},共{total_count}条')
            try:
                path = f"{IMAGE_QIEPIAN_PATH}{image_name}"

                frame = load_image(path)

                # 获取当前时间（建议直接使用系统时间或已有的时间获取方式）
                now = datetime.now().time()

                # 定义静默时段：21:45 ~ 次日 06:15
                start_time = time(21, 45)
                end_time = time(6, 15)

                # 判断是否在静默时段内（跨午夜）
                in_quiet_period = now >= start_time or now <= end_time

                if not in_quiet_period:
                    print(f"当前时间 {now.strftime('%H:%M')} 不在静默时段内，继续执行处理。")
                    # 不在静默时段，正常执行
                    processor(
                        frame,
                        question,
                        output_folder=output_folder,
                        monitor_point=data.get('location'),
                        camera_id=data.get('camera_id'),
                        action_time=data.get('capture_time'),
                        other_data=data
                    )
                else:
                    # 在静默时段内，跳过执行
                    print(f"当前时间 {now.strftime('%H:%M')} 处于静默时段(21:45-06:15)，跳过执行。")

                feedback_data = [image_name]
                # 2. 提交反馈
                print(f"\n📤 图片{image_name}正在提交修改数据库处理状态的反馈")
                submit_feedback(
                    violation_type=violation_type,
                    name_list=feedback_data,
                    base_url=url
                )
            except Exception as e:
                print(f"处理单条数据 {image_name} 时出错: {e}")

        print(f"{violation_type} 处理完成")

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
    except Exception as e:
        print(f"程序运行出错: {e}")
