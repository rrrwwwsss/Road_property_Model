import concurrent.futures
import time
from datetime import datetime, timedelta
import requests
import cv2
import os
from PIL import Image, ImageDraw
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BASE_URL = "https://10.212.160.158:8101/nvms8100/apploginVideo" #监控摄像头地址
USER_NAME = "bjjzdx"
USER_PWD = "ZFZDwxglwf@2025"
# 假设你已经定义好了 capture_frame_from_camera(camera_id)
# 并且有以下变量可用：BASE_URL, USER_NAME, USER_PWD, YUANTU_PATH, LINUX_PIC_PAT, close_video, cv2, Image, os, datetime, requests
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
                    print(data["data"])
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
            # VideoCapture 会用 FFmpeg 打开 RTSP 流，开始读取数据包
            #  FFmpeg 解析时发现某些宏块数据损坏 → 打印你看到的 cbp too large、error while decoding MB 等警告。
            cap = cv2.VideoCapture(video_stream_url)
            if not cap.isOpened():
                print("无法打开视频流，请检查URL是否正确。")
                return None
            # 如果当前缓冲区里的帧坏了，FFmpeg 会继续丢掉坏数据，直到遇到一个完整的 I 帧（关键帧）才能解码出图像。
            # 所以你虽然在解码过程中报了一堆“坏帧”错误，但最后还是等到一个关键帧 → 返回 ret=True，frame 里有图像数据。
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
        YUANTU_PATH = './pic'
        # 定义文件名和完整路径
        file_name = f"camera_{camera_id}_{current_time}.jpg"
        file_path = os.path.join(YUANTU_PATH, file_name)

        # 保存 PIL 图像到指定路径
        pil_image.save(file_path)
        # 提取出linux实际的存储路径（不是dockers路径）
        # last_part = os.path.basename(YUANTU_PATH)
        # output_path = os.path.join(LINUX_PIC_PAT + last_part, file_name)
        # print("保存图片linux路径：", output_path)
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

def run_parallel_capture():
    # 定义 5 个摄像头的 ID（根据实际情况修改）
    camera_ids = [
        "11000000001314225729",
        "11000000001318561604",
        "11000000001315581147",
        "11000000001317429773",
        "11000000001312095982",
        "11000000001314744791",
    ]

    start_time = time.time()
    print("=== 开始并行抓帧任务 ===")

    # 使用线程池并行执行
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # 提交任务
        futures = {executor.submit(capture_frame_from_camera, cam_id): cam_id for cam_id in camera_ids}

        # 逐个等待结果
        for future in concurrent.futures.as_completed(futures):
            cam_id = futures[future]
            try:
                result = future.result()
                print(f"[摄像头 {cam_id}] 抓帧完成 ✅")
            except Exception as e:
                print(f"[摄像头 {cam_id}] 抓帧失败 ❌: {e}")

    print(f"=== 全部完成，总耗时: {time.time() - start_time:.2f} 秒 ===")

if __name__ == "__main__":
    run_parallel_capture()
