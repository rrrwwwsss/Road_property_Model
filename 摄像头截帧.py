from datetime import datetime, timedelta
import requests
import cv2
import os
from PIL import Image, ImageDraw
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from 配置 import *


def close_video(invite_id):
    """
    关闭指定的视频流。

    参数:
        invite_id (str): 播放句柄。
    """

    url = f"{BASE_URL}/closeVideo.action"


    params = {
        # "inviteId": invite_id,
        "playType": 1
    }
    requests.get(url, params=params, verify=False)
    print("录像回放已关闭")


    params = {
        # "inviteId": invite_id,
        "playType": 0
    }
    requests.get(url, params=params, verify=False)
    print("实时视频已关闭")


    params = {
        "inviteId": invite_id,
    }
    try:
        response = requests.get(url, params = params,verify=False)
        if response.status_code == 200:
            try:
                data = response.json()
                # print(data)
                if "code" in data and data["code"] == 0:
                    print(f"视频流已成功关闭！播放句柄: {data['data']['inviteId']}")
                else:
                    print(
                        f"关闭视频流失败！错误代码: {data.get('code', '未知')}, 错误信息: {data.get('message', '无消息')}")
            except ValueError:
                print("返回的内容不是有效的JSON格式：")
                print(response.text)
        else:
            print(f"HTTP请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    except requests.exceptions.SSLError as ssl_err:
        print(f"SSL验证错误: {ssl_err}")
    except requests.exceptions.RequestException as e:
        print(f"请求过程中发生异常: {e}")


def capture_frame_from_camera(camera_id):
    """
    根据 camera_id 获取视频流并截取一帧。

    参数:
        camera_id (str): 摄像机编号。

    返回:
        frame (numpy.ndarray or None): 截取的帧数据（如果成功），否则返回 None。
    """
    video_stream_url, invite_id = None, None
    try:
        # 第一步：获取视频流 URL 和播放句柄
        url = f"{BASE_URL}/queryVideoUrl.action"
        params = {
            "signName": USER_NAME,
            "userPwd": USER_PWD,
            "clientSN": "",
            "protocolType": "4",
            "streamType": "0",
            "cameraId": camera_id
        }
        response = requests.get(url, params=params, verify=False)
        if response.status_code == 200:
            try:
                data = response.json()
                if "code" in data and data["code"] == 0 and "data" in data:
                    video_stream_url = data["data"].get("videoStream", "")
                    invite_id = data["data"].get("inviteId", "")
                    print(f"视频流URL: {video_stream_url}")
                    print(f"播放句柄: {invite_id}")
                else:
                    print(f"操作失败！错误代码: {data.get('code', '未知')}, 错误信息: {data.get('message', '无消息')}")
                    return None
            except ValueError:
                print("返回的内容不是有效的JSON格式：")
                print(response.text)
                return None
        else:
            print(f"HTTP请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None

        # 第二步：从视频流中截帧
        if video_stream_url:
            cap = cv2.VideoCapture(video_stream_url)
            if not cap.isOpened():
                print("无法打开视频流，请检查URL是否正确。")
                return None

            ret, frame = cap.read()
            if not ret:
                print("无法读取视频流帧，请检查网络或视频流是否可用。")
                return None

            print("成功截取一帧。")
            cap.release()  # 释放视频流资源
        else:
            print("未获取到视频流URL，跳过截帧操作。")
            return None

        # 第三步：关闭视频流
        if invite_id:
            close_video(invite_id)

        # 返回截取的帧
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # 定义文件名和完整路径
        file_name = f"camera_{camera_id}_{current_time}.jpg"
        file_path = os.path.join(YUANTU_PATH, file_name)

        # 保存 PIL 图像到指定路径
        pil_image.save(file_path)
        # 提取出linux实际的存储路径（不是dockers路径）
        last_part = os.path.basename(YUANTU_PATH)
        output_path = os.path.join(LINUX_PIC_PAT + last_part, file_name)
        print("保存图片linux路径：", output_path)
        return pil_image

    except requests.exceptions.SSLError as ssl_err:
        print(f"SSL验证错误: {ssl_err}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求过程中发生异常: {e}")
        return None
    finally:
        # 确保即使发生异常也会尝试关闭视频流
        if invite_id:
            close_video(invite_id)
