import json
import os
import re

import requests
from 配置 import *
from io import BytesIO
import base64
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def detect_frame(question, image_base64):
    # 这是把 Base64 内容包装成 Data URI（数据 URL）
    image_data_url = f"data:image/png;base64,{image_base64}"  # 注意前缀

    data = {
        "model": "qwen2_5_vl",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}},
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

    try:
        response = requests.post(
            "http://192.168.0.161:1025/v1/chat/completions",
            json=data,
            timeout=60
        )
        response.raise_for_status()
        response_data = response.json()

        reply = response_data["choices"][0]["message"]["content"]
        print("大模型响应数据:", reply)
        return reply

    except Exception as e:
        print(f"[detect_frame] 调用异常: {type(e).__name__} - {e}")
        return '{"result": "no"}'

def pil_image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")  # 或 JPEG，看你需求
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def pattern_recognition(question, image):
    # 假设 image 是 PIL Image 对象
    img_b64 = pil_image_to_base64(image)
    response = detect_frame(question, img_b64)  # 返回的是 list，比如 [str]

    result_data = {"result": "no"}  # 默认值

    if response and isinstance(response[0], str):
        try:
            # 提取第一个 {} 包含的 JSON 片段
            match = re.search(r'\{.*\}', response[0], re.S)
            if match:
                result_data = json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析错误: {e}, 原始数据: {response[0]}")

    return result_data