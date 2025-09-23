import requests
import json

# 要测试的服务地址
servers = [
    "http://192.168.0.161:1025/v1/chat/completions",
    "http://192.168.0.161:2025/v1/chat/completions",
    "http://192.168.0.92:1025/v1/chat/completions",
]

# 请求体
payload = {
    "model": "qwen2_5_vl",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": "https://modelscope.oss-cn-beijing.aliyuncs.com/resource/qwen.png"},
            {"type": "text", "text": "Explain the details in the image."}
        ]
    }],
    "max_tokens": 512,
    "do_sample": True,
    "repetition_penalty": 1.0,
    "temperature": 0.01,
    "top_p": 0.001,
    "top_k": 1
}

# 循环测试
for url in servers:
    print(f"\n===== 请求 {url} =====")
    try:
        resp = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            print("✅ 成功响应")
            # 打印模型回复内容
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 错误：HTTP {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"⚠️ 请求失败: {e}")
