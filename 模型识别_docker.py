import json
import os

import requests
from 配置 import *
from io import BytesIO
import base64
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def detect_frame(question, image_base64):
    data = {"prompt": question, "image_base64": image_base64}
    try:
        response = requests.post(MODEL_SERVE_URL, json=data, verify=False)
        response_data = response.json()
        file_path = "output.txt"

        # 判断文件是否存在
        if os.path.exists(file_path):
            print(f"{file_path} 已经存在")
        # 使用 'a' 模式打开文件（追加模式）
        with open(file_path, "a", encoding="utf-8") as file:
            json.dump(response_data, file, ensure_ascii=False, indent=4)  # 将响应数据写为格式化的 JSON 字符串
            file.write("\n")  # 添加换行符，以便每次追加数据后占一行

        print(f"{file_path} 文件已创建并写入数据")
        print('大模型响应数据', response_data)
        return response_data
    except Exception as e:
        print(f"[detect_frame] 调用异常: {type(e).__name__} - {e}")
        return ['{"result": "no"}']


def pil_image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")  # 或 JPEG，看你需求
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def pattern_recognition(question, image):
    # 假设 image 是 PIL Image 对象
    img_b64 = pil_image_to_base64(image)
    response = detect_frame(question, img_b64)
    # 解析响应
    try:
        result_data = json.loads(response[0])
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        result_data = {"result": "no"}
    return result_data