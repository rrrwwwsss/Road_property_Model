import json
import requests
from 配置 import *
from io import BytesIO
import base64
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def detect_frame(question,image_base64):
    data = {"prompt": question, "image_base64": image_base64}
    try:
        response = requests.post(MODEL_SERVE_URL, json=data, verify=False)
        print('大模型响应数据', response.json())
        return response.json()
    except Exception as e:
        print(f"[detect_frame] 调用异常: {type(e).__name__} - {e}")
        return ['{"result": "no"}']

def pil_image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")  # 或 JPEG，看你需求
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str
def pattern_recognition(question,image):
    # 假设 image 是 PIL Image 对象
    img_b64 = pil_image_to_base64(image)
    response = detect_frame(question,img_b64)
    # 解析响应
    result_data = json.loads(response[0])
    return result_data