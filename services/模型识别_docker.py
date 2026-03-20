import base64
from io import BytesIO

import requests
import urllib3

from config.配置 import LIANTONG_MODEL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def detect_frame(question, image_base64):
    # 把 Base64 图片包装成 Data URI，作为多模态输入。
    image_data_url = f"data:image/png;base64,{image_base64}"
    data = {
        "model": "qwen2_5_vl",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    {"type": "text", "text": question},
                ],
            }
        ],
        "max_tokens": 1024,
        "do_sample": True,
        "repetition_penalty": 1.1,
        "temperature": 0.4,
        "top_p": 0.9,
        "top_k": 50,
    }

    try:
        response = requests.post(
            LIANTONG_MODEL,
            json=data,
            timeout=60,
        )
        response.raise_for_status()
        response_data = response.json()
        reply = response_data["choices"][0]["message"]["content"]
        print("大模型响应数据:", reply)
        return reply
    except Exception as exc:
        print(f"[detect_frame] 调用异常: {type(exc).__name__} - {exc}")
        return '{"result": "no"}'


def pil_image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def pattern_recognition(question, image):
    # 这里返回 detect_frame 的原始文本 reply；
    # JSON 解析由上层 safe_json_parse 处理。
    if image is None:
        print("没截取到图片，不交给大模型")
        return None
    img_b64 = pil_image_to_base64(image)
    reply = detect_frame(question, img_b64)
    return reply
