import os
import csv
import requests
import json

base_folder = "./pic_pack"
output_csv = "./results.csv"

# 大模型 API 地址
url = "http://61.49.87.61:31000/v1/chat/completions"

# 支持的图片格式
img_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp")

results = []


def call_model(img_path, prompt):
    """调用大模型接口，返回结果文本"""
    payload = {
        "model": "qwenvl",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": img_path},  # 如果是本地，需要改成服务可访问的 URL
                    {"type": "text", "text": prompt}
                ]
            }
        ],
        "max_tokens": 512,
        "temperature": 0.01
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"请求失败: {e}"


selected_folder = os.path.join(base_folder, "selected")

for root, dirs, files in os.walk(base_folder):
    if root == base_folder:
        continue  # 跳过根目录 pic_pack

    # 跳过 selected 自身
    if os.path.basename(root) == "selected":
        continue
    print(root)
    # 当前文件夹名
    xingwei = os.path.basename(root)

    # 读取当前文件夹提示词
    prompt_path = os.path.join(root, "新建文本文档.txt")
    prompt_text = ""
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_text = f.read().strip()

    print(prompt_text)
    # 当前文件夹图片列表
    folder_images = [os.path.join(root, f) for f in files if f.lower().endswith(img_extensions)]

    # selected 文件夹图片列表
    selected_images = []
    if os.path.exists(selected_folder):
        selected_images = [os.path.join(selected_folder, f) for f in os.listdir(selected_folder)
                           if f.lower().endswith(img_extensions)]

    # 遍历普通文件夹图片
    for img_path in folder_images:
        img_name = os.path.basename(img_path)
        img_url = f"http://60.205.12.90:5002/preview/{xingwei}/{img_name}"  # 普通文件夹名
        rel_path = os.path.relpath(img_path, base_folder)
        model_result = call_model(img_url, prompt_text)
        results.append([rel_path, model_result])
        print(f"处理完成: {rel_path}")

    # 遍历 selected 文件夹图片
    for img_path in selected_images:
        img_name = os.path.basename(img_path)
        img_url = f"http://60.205.12.90:5002/preview/selected/{img_name}"  # URL 中使用 selected
        rel_path = os.path.relpath(img_path, base_folder)
        model_result = call_model(img_url, prompt_text)
        results.append([rel_path, model_result])
        print(f"处理完成: {rel_path}")

# 保存到 CSV
with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["image_path", "model_result"])
    writer.writerows(results)

print(f"所有结果已保存到 {output_csv}")
