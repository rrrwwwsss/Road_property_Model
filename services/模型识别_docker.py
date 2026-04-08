import ast
import json
import re

import requests
from config.配置 import *
from io import BytesIO
import base64
import urllib3
from utils.logger_handler import get_logger
# 快捷获取日志器
logger = get_logger()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def detect_frame(question, image_base64):
    # 这是把 Base64 内容包装成 Data URI（数据 URL）
    image_data_url = f"data:image/png;base64,{image_base64}"  # 注意前缀
    data = {
        "model": "qwen2_5_vl",  # 使用的模型名称，这里是 Qwen2.5-VL (多模态，支持图文输入)
        # "model": "Qwen3.5-VL-27B",
        "messages": [  # 对话历史，采用 Chat 格式
            # {
            #     # 【新增】系统提示词，严厉限制它的输出格式
            #     "role": "system",
            #     "content": "You are a strict image analysis program. No matter what you see, you must and can only output valid JSON format. Under no circumstances are you allowed to output any introductory remarks, concluding remarks, English text, analysis processes, or thought processes."
            # },
            {
                "role": "user",  # 角色，这里是用户
                "content": [  # 输入的内容，可以是图片+文字的多模态输入
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    # 图片输入，image_data_url 是 base64 或 http 链接
                    {"type": "text", "text": question}  # 文字输入，即用户的问题
                ]
            }
        ],
        "max_tokens": 3072,  # 限制长度
        # "do_sample": True,  # 是否启用采样（随机性），True 表示不是完全贪心搜索
        "repetition_penalty": 1.1,  # 重复惩罚系数，>1 会惩罚模型重复的内容，这里 1.0 表示不做惩罚
        "temperature": 0.1, # 【修改】调低温度，让它变得极其确定理智，不再发散思维
        "top_p": 0.9,  # nucleus sampling 截断概率。取累计概率 ≤0.001 的 token 候选，非常严格
        "top_k": 50,  # 只从概率最高的前 1 个 token 中选取 → 和 greedy search 很像
        # # 【调用端写法】只对这一次请求关闭思考模式
        # "extra_body": {
        #     "chat_template_kwargs": {"enable_thinking": False}
        # }
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
    import ast  # 确保 ast 被导入

    # 假设 image 是 PIL Image 对象
    if image is None:
        print('没截取到图片，不交给大模型')
        return None
    img_b64 = pil_image_to_base64(image)
    response = detect_frame(question, img_b64)  # 返回的是 list，比如 [str]
    logger.info(f"大模型输出：{response}")
    result_data = {"result": "错误"}  # 默认值

    # --- 内部定义一个专门用来提取和解析 JSON 的小方法 ---
    def parse_text(text):
        # 1. 截断：如果有 </think>，直接把包含 </think> 及以前的所有废话全部切掉
        if '</think>' in text:
            text = text.split('</think>')[-1]

        # 2. 寻找 ```json ... ``` 或 ``` ... ``` 里的内容
        block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.S)
        if block_match:
            json_str = block_match.group(1)
        else:
            # 如果没有代码块，再去找大括号 {...}（使用贪婪匹配 .* 获取完整的最外层括号）
            match = re.search(r'\{.*\}', text, re.S)
            if match:
                json_str = match.group(0)
            else:
                return None

        # 3. 清理注释
        json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.S)  # 去掉块注释
        json_str = re.sub(r"//.*?$", "", json_str, flags=re.M)  # 去掉行注释

        # 4. 尝试解析
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("标准 JSON 解析失败，尝试使用 ast 解析...")
            try:
                # 把可能误伤的 ... 替换为 []，防止 ast 将其解析为 Ellipsis 对象
                json_str_safe = json_str.replace("...", "[]")
                return ast.literal_eval(json_str_safe)
            except Exception as e:
                print(f"⚠️ ast 解析也失败: {e}, 原始数据: {json_str}")
        return None

    # --------------------------------------------------

    if isinstance(response, dict):
        print("response 类型: dict")
        result_data = response

    elif isinstance(response, str):
        print("response 类型: str")
        parsed = parse_text(response)
        if parsed is not None:
            result_data = parsed

    elif isinstance(response, list) and response and isinstance(response[0], str):
        print("response 类型: list[str]")
        parsed = parse_text(response[0])
        if parsed is not None:
            result_data = parsed

    else:
        print("response 类型未知:", type(response))

    return result_data,response