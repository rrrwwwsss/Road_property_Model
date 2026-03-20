import requests
import json
from 公共方法 import safe_json_parse, rescale_bounding_boxes, draw_bounding_boxes
from datetime import datetime, timedelta
import os
from PIL import Image

import os

model_result = 'Output : If the above behavior can be identified, then the following result will be returned: {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]}, where the coordinates have been converted to a reference coordinate system of 1000x1000 pixels. Otherwise, return {"result": "no"}.'

qusetion = """
    Role: You are an intelligent assistant with the ability to accurately identify road occupation/digging activities in images.
    Task: Please analyze this image and determine if any vehicles are currently engaged in road occupation/digging activities.
    Firstly, you need to determine if there are any **large stationary vehicles** (such as construction trucks, engineering vehicles, excavators, etc.) in the image. Ignore vehicles that are moving normally or waiting to pass.
    Then, determine if these **stationary large vehicles** are in a construction operation state, including but not limited to:
    - The vehicle body is tilted, is unloading or loading;
    - The digging arm or bucket is in operation;
    - The vehicle's mechanical arm or fixed device has physical contact with the road surface;
    - There are obvious construction signs or construction obstacles (such as fences, cones, earth mounds, etc.) that are in line with the construction behavior;
    - Personnel are interacting with the vehicle, operating it, or directing the operation. Ignore the following interfering content: normal vehicle movement, vehicle parked in a safe area but without construction activities, buildings, pedestrians, toll stations, dividers, etc.
    If the image is blurry, the view is obstructed, or there is severe lack of light, making it impossible to accurately determine, please reply "no".
    """+model_result
qusetion = """
    Role: You are an intelligent assistant with the ability to recognize road signs or banners. You can accurately extract and analyze the text content of them.
    Task: Please identify the signs or banners on the road(please note that it is the road itself, not the buildings beside the road. If the sign is a normal one on the building beside the road, please ignore it!)。 If the text content can be extracted, please determine whether it is related to "transportation affairs" or "personal affairs":
    - If it is related to "personal affairs" (such as "Welcome to **", "Advertisement of **", "Car repair of **", "Recruitment of **", etc.), please return: {
    "result": "yes",
    "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1]...] ,
    "Content": The extracted text content }
    - The coordinates should be based on an image size of 1000x1000.
    - If there are any text related to "transportation matters" (such as "maximum weight ** tons", "prohibited **", "drunk driving **", "traffic **", "driving **", "fasten seat belt", "section **", "be careful **", etc.) or text related to the city (such as Beijing, Shanghai, etc.), please return: {
    "result": "no",
    "Content": The extracted text content }
    If the text in the image cannot be clearly read due to the shooting angle, lighting, or blurriness, or if it is uncertain whether the text comes from an unofficial source, please reply uniformly in the following format: {
    "result": "no"
    """
qusetion = """
Role: You are an artificial intelligence assistant capable of identifying illegal stall setups or temporary street vendors' activities on roads or within road usage areas.
Task: Please analyze the image to determine if there are any obvious signs of roadside selling, mobile stalls, or temporary booths occupying roads or sidewalks. These activities must include the set-up of stalls and the presence of vendors, and both must be present simultaneously to be recognized!
Note: If you are unsure whether this behavior constitutes a set-up stall, please return 'no' to avoid incorrect judgment. If the behavior does not occur in the road area, also return 'no'.
"""+model_result
def get_result(img_name,xingwei,my_qusetion):
    # 1. 配置请求参数
    url = "http://61.49.87.61:31000/v1/chat/completions"
    img_url = "http://60.205.12.90:5002/preview/"+xingwei+"/"+img_name

    payload = {
        "model": "qwenvl",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        # ⚠️ 注意：这里直接给图片的 URL 即可，不需要 HTML 标签
                        "image_url": img_url
                    },
                    {
                        "type": "text",
                        "text": my_qusetion
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
        result_dict = safe_json_parse(result["choices"][0]["message"]["content"])
        # print(result_dict)
        final_answer = result_dict.get("result", "不存在")
        print(f"检测结果：{final_answer}")
        if final_answer == "yes":
            current_time = datetime.now()
            future_time = current_time + timedelta(minutes=10, seconds=52)
            # 生成时间戳文件名
            timestamp = future_time.strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join('./result', xingwei+'/'+img_name)

            normalized_boxes = result_dict.get("bounding_boxes")
            image = Image.open("D:/yunceshi/"+xingwei+"/"+img_name)
            output_image = draw_bounding_boxes(image, normalized_boxes)
            # 确保保存路径的目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 保存结果
            output_image.save(output_path)
            print(f"★ 发现目标，已保存至 linux存放路径：{output_path}")
        
    except requests.exceptions.RequestException as e:
        print("请求失败:", e)
    except (KeyError, IndexError) as e:
        print("解析结果异常:", e, "原始返回:", response.text)
xingwei = "baitan"
folder_path = r"D:\\yunceshi\\"+xingwei
img_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp")

# get_result("camera_11000000001313053014_20250629_073320.jpg",xingwei,my_qusetion=qusetion)
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.lower().endswith(img_extensions):
            print(file)  # 只打印文件名
            get_result(file,xingwei,my_qusetion=qusetion)