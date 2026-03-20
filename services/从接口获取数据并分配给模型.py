import requests
from PIL import Image

from detectors.占用挖掘公路连续帧识别 import process_images as process_images1
from detectors.四项违法行为识别 import process_images as process_images2
from detectors.堆放物品_摆设摊位 import process_images as process_images3
from config.配置 import IMAGE_API, IMAGE_QIEPIAN_PATH

# 违法行为到处理函数映射：后续新增行为时只需要补充这里。
PROCESSOR_MAP = {
    '擅自占用、挖掘公路': process_images1,
    '在公路用地范围内设置公路标志以外的其他标志': process_images2,
    '遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全': process_images2,
    '在公路范围内擅自移动井盖': process_images2,
    '在公路上及公路用地范围内摆摊设点': process_images3,
    '在公路上及公路用地范围内堆放物品': process_images3,
}


def load_image(path):
    """按文件路径加载图片，失败时返回 None。"""
    try:
        return Image.open(path)
    except Exception as exc:
        print(f"加载图片失败: {path}, 错误: {exc}")
        return None


def fetch_images_by_violation(violation_type, base_url):
    """从图片接口拉取指定违法行为的待处理图片列表。"""
    url = f"{base_url}/images"
    payload = {"violation_type": violation_type}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            images = response.json()
            print(f"成功获取 {len(images)} 条图片记录")
            return images
        if response.status_code == 404:
            detail = response.json().get("detail", "未知原因")
            print(f"未找到数据: {detail}")
            return []
        if response.status_code == 500:
            detail = response.json().get("detail", "未知服务端错误")
            print(f"服务端错误: {detail}")
            return None

        print(f"未知响应状态码: {response.status_code}, 内容: {response.text}")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"请求异常: {exc}")
        return None


def submit_feedback(violation_type, name_list, base_url):
    """回写图片处理状态，避免同一图片重复处理。"""
    url = f"{base_url}/feedback"
    payload = {
        "violation_type": violation_type,
        "name_list": name_list,
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("反馈提交成功:", result)
            return result
        if response.status_code == 500:
            error = response.json()
            print("服务端错误:", error.get("detail", "未知错误"))
            return None

        print(f"未知响应状态码: {response.status_code}, 内容: {response.text}")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"提交反馈失败: {exc}")
        return None


def keep_latest_per_location(data_list):
    """当待处理数据过大时，每个地点仅保留最新一条。"""
    latest_data_map = {}
    for item in data_list:
        location = item.get("location")
        current_time = item.get("capture_time", "")
        if location not in latest_data_map:
            latest_data_map[location] = item
            continue

        if current_time > latest_data_map[location].get("capture_time", ""):
            latest_data_map[location] = item

    return list(latest_data_map.values())


def chuli(question, output_folder):
    """处理某一种违法行为的全量待检测图片。"""
    violation_type = list(question.keys())[0]
    print(f"正在处理违法行为: {violation_type}")

    processor = PROCESSOR_MAP.get(violation_type)
    if not processor:
        print(f"未知违法类型: {violation_type}")
        return

    response = fetch_images_by_violation(violation_type, IMAGE_API)
    if response is None:
        print(f"未获取到可处理数据: {violation_type}")
        return

    if response and isinstance(response, list) and len(response) > 200:
        print(f"数据量为 {len(response)}，启用按地点去重（仅保留最新记录）")
        response = keep_latest_per_location(response)
        print(f"去重后剩余 {len(response)} 条")

    total_count = len(response)
    for index, data in enumerate(response, 1):
        image_name = data.get("name")
        print(f"[{violation_type}] 处理第 {index}/{total_count} 条: {image_name}")

        try:
            image_path = f"{IMAGE_QIEPIAN_PATH}{image_name}"
            frame = load_image(image_path)
            processor(
                frame,
                question,
                output_folder=output_folder,
                monitor_point=data.get("location"),
                camera_id=data.get("camera_id"),
                action_time=data.get("capture_time"),
                other_data=data,
            )

            submit_feedback(
                violation_type=violation_type,
                name_list=[image_name],
                base_url=IMAGE_API,
            )
        except Exception as exc:
            print(f"处理图片失败: {image_name}, 错误: {exc}")

    print(f"{violation_type} 处理完成")

