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
        "model": "qwen2_5_vl",  # 使用的模型名称，这里是 Qwen2.5-VL (多模态，支持图文输入)
        "messages": [  # 对话历史，采用 Chat 格式
            {
                "role": "user",  # 角色，这里是用户
                "content": [  # 输入的内容，可以是图片+文字的多模态输入
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    # 图片输入，image_data_url 是 base64 或 http 链接
                    {"type": "text", "text": question}  # 文字输入，即用户的问题
                ]
            }
        ],
        "max_tokens": 512,  # 最大输出 token 数，限制生成回复的长度
        "do_sample": True,  # 是否启用采样（随机性），True 表示不是完全贪心搜索
        "repetition_penalty": 1.0,  # 重复惩罚系数，>1 会惩罚模型重复的内容，这里 1.0 表示不做惩罚
        "temperature": 0.01,  # 温度系数，控制生成的随机性。越接近 0 越确定，越大越随机，这里 0.01 表示几乎确定性输出
        "top_p": 0.001,  # nucleus sampling 截断概率。取累计概率 ≤0.001 的 token 候选，非常严格
        "top_k": 1  # 只从概率最高的前 1 个 token 中选取 → 和 greedy search 很像
    }

    try:
        response = requests.post(
            LIANTONG_MODEL,
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