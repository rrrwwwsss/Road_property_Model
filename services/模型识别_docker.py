import json
import re

import requests
from config.配置 import *
from io import BytesIO
import base64
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def detect_frame(question, image_base64):
    # 这是把 Base64 内容包装成 Data URI（数据 URL）
    image_data_url = f"data:image/png;base64,{image_base64}"  # 注意前缀
    data = {
        # "model": "qwen2_5_vl",  # 使用的模型名称，这里是 Qwen2.5-VL (多模态，支持图文输入)
        "model": "Qwen3.5-VL-27B",
        "messages": [  # 对话历史，采用 Chat 格式
            {
                # 【新增】系统提示词，严厉限制它的输出格式
                "role": "system",
                "content": "You are a strict image analysis program. No matter what you see, you must and can only output valid JSON format. Under no circumstances are you allowed to output any introductory remarks, concluding remarks, English text, analysis processes, or thought processes."
            },
            {
                "role": "user",  # 角色，这里是用户
                "content": [  # 输入的内容，可以是图片+文字的多模态输入
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    # 图片输入，image_data_url 是 base64 或 http 链接
                    {"type": "text", "text": question}  # 文字输入，即用户的问题
                ]
            }
        ],
        "max_tokens": 1024,  # 限制长度
        # "do_sample": True,  # 是否启用采样（随机性），True 表示不是完全贪心搜索
        "repetition_penalty": 1.1,  # 重复惩罚系数，>1 会惩罚模型重复的内容，这里 1.0 表示不做惩罚
        "temperature": 0.1, # 【修改】调低温度，让它变得极其确定理智，不再发散思维
        "top_p": 0.9,  # nucleus sampling 截断概率。取累计概率 ≤0.001 的 token 候选，非常严格
        "top_k": 50  # 只从概率最高的前 1 个 token 中选取 → 和 greedy search 很像
    }

    try:
        response = requests.post(
            LIANTONG_MODEL,
            json=data,
            timeout=120  # 【关键修改】把 60 改成 120 秒，给它足够的从容
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
    if image is None:
        print('没截取到图片，不交给大模型')
        return None
    img_b64 = pil_image_to_base64(image)
    response = detect_frame(question, img_b64)  # 返回的是 list，比如 [str]

    result_data = {"result": "错误"}  # 默认值

    if isinstance(response, dict):
        print("response 类型: dict")
        result_data = response
    elif isinstance(response, str):
        print("response 类型: str")
        # 提取第一个 {...} JSON
        match = re.search(r'\{.*?\}', response, re.S)
        if match:
            try:
                json_str = match.group(0)
                json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.S)  # 去掉块注释
                json_str = re.sub(r"//.*?$", "", json_str, flags=re.M)  # 去掉行注释
                result_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析错误: {e}, 原始数据: {match.group(0)}")
    elif isinstance(response, list) and response and isinstance(response[0], str):
        print("response 类型: list[str]")
        match = re.search(r'\{.*?\}', response[0], re.S)
        if match:
            try:
                json_str = match.group(0)
                json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.S)  # 去掉块注释
                json_str = re.sub(r"//.*?$", "", json_str, flags=re.M)  # 去掉行注释
                result_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析错误: {e}, 原始数据: {match.group(0)}")
    else:
        print("response 类型未知:", type(response))

    return result_data