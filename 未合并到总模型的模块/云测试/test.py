import requests
import json

# 1. 配置请求参数
url = "http://61.49.87.61:31000/v1/chat/completions"

payload = {
    "model": "qwenvl",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    # ⚠️ 注意：这里直接给图片的 URL 即可，不需要 HTML 标签
                    "image_url": {
                        "url": "https://modelscope.oss-cn-beijing.aliyuncs.com/resource/qwen.png"
                    }
                },
                {
                    "type": "text",
                    "text": "Explain the details in the image."
                }
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

headers = {
    "Content-Type": "application/json"
}

# 2. 发送 POST
try:
    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=60)
    response.raise_for_status()          # 若返回非 2xx 会抛异常
    result = response.json()
    print("状态码:", response.status_code)
    print("模型回复:", result["choices"][0]["message"]["content"])
except requests.exceptions.RequestException as e:
    print("请求失败:", e)
except (KeyError, IndexError) as e:
    print("解析结果异常:", e, "原始返回:", response.text)