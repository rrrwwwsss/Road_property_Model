import base64
import json
from pathlib import Path

import requests

# 直接在这里修改提示词和图片路径
PROMPT = "请识别图片中的内容，并按 JSON 返回结果。"
IMAGE_PATH = r"./test/demo.jpg"

# 按模型识别_docker.py的调用方式，直接请求chat/completions接口
MODEL_URL = "http://192.168.0.161:1025/v1/chat/completions"
MODEL_NAME = "qwen2_5_vl"


def image_file_to_base64(image_path: str) -> str:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"图片不存在: {path.resolve()}")
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def call_model(question: str, image_base64: str) -> str:
    image_data_url = f"data:image/png;base64,{image_base64}"

    payload = {
        "model": MODEL_NAME,
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

    response = requests.post(MODEL_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def main() -> None:
    image_b64 = image_file_to_base64(IMAGE_PATH)
    result = call_model(PROMPT, image_b64)

    print("=== 模型原始输出 ===")
    print(result)

    if isinstance(result, str):
        try:
            print("=== 尝试解析为JSON ===")
            print(json.dumps(json.loads(result), ensure_ascii=False, indent=2))
        except Exception:
            pass


if __name__ == "__main__":
    main()
