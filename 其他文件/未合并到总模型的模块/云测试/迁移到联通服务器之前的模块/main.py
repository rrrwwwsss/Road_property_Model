import traceback

import pandas as pd

from services.获取摄像头点位数据 import get_dianwei_data
from config.配置 import *
from 四项违法行为识别 import poll_cameras
from 堆放物品_摆设摊位 import poll_cameras1
from services.清理图片 import clear_begin
from services.托管本地图片到网络 import run_flask_server
from services.定期推送数据库 import tuisong_main
import sys
# 关闭输出缓冲，解决打印堵塞问题
sys.stdout.reconfigure(line_buffering=True)

# 固定问题
# 占用挖掘公路
# wajue_question = """
# Role: You are an intelligent assistant capable of accurately identifying road occupation/digging activities in images. Your task is to detect road occupation/digging activities in the images and return the positions of these activities within the images.
#
# Task: Please analyze this image and determine whether there is any ongoing road excavation work. The key lies in detecting the actual construction and excavation activities, rather than vehicles and machinery.
#
# Note: Ignore large commercial vehicles, pedestrians and road obstacles; do not pay attention to the guardrails in the middle of the road.
#
# Output format: If it is detected that there is an act of occupying the road for excavation, please return: {"Result": "Yes", "Bounding Box": [[xmin1, ymin1, xmax1, ymax1], ...]}, where the coordinates are based on the 1000x1000 size of the image. Otherwise, please return: {"Result": "No"}.
# """
# 测试用提示词：框出整个图片
# wajue_question = """
# Role: All you need to do is to frame the entire image.
#
# Output format: Please return: {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]} with the coordinates based on the 1000x1000 size of the image. Otherwise, return: {"result": "no"}.
# """
wajue_question = """
Role: You are an intelligent assistant capable of accurately identifying road excavation activities in images.
Task: Please analyze the image and determine whether there is any ongoing road excavation activity. These activities must include the excavation behavior and construction obstacles, and both must be present simultaneously to be recognized! The focus is on detecting actual construction and actions, rather than vehicles and machinery. Ignore normal large vehicles, pedestrians, toll stations, buildings, and road obstacles.
Note: If it cannot be recognized due to lighting or camera issues, please return "no". If you are unsure, always return "no" instead of making a wrong judgment! If normal large moving vehicles are identified, also return "no".
"""
# 井盖缺失
jinggai_question = """
You are an intelligent assistant capable of accurately identifying instances of missing or removed manhole covers on roads or within the road land area in images. Your task is to detect whether there is a manhole cover absence incident and return the coordinate range of the missing position in the image. Please analyze the image and determine whether there is a situation where the manhole cover has been removed, exposing the manhole opening. Focus on the locations on the road surface where the manhole cover should be but is now clearly missing (such as circular or square voids). Ignore the manhole covers that are already properly covered, pedestrians, vehicles (including parked vehicles). 
"""
# 设置非公路标志
# gongbiao_question = """
# Role: You are an intelligent assistant capable of accurately identifying instances of non-standard road signs being placed on roads or within road-related areas. Your task is to detect the presence of such non-standard road signs and return their positions within the image.
# Task: Please analyze the image and determine whether any non-road signs are set on the road or within the road area. These include: banners, billboards, private signs, or any other signs that are clearly not set by the traffic management department. Please ignore pedestrians, vehicles (including parked vehicles), and legal road accessories (such as lamp posts, traffic signs, monitoring poles, guardrails, etc.).
# Note: If an off-road sign is detected, please analyze the text on it and recheck whether it is an off-road sign. If you are unable to clearly see the content on the sign due to camera or lighting issues, please return "no" to avoid incorrect judgment. If the sign is clearly part of an official traffic facility, also return "no".
# Output format: If non-road marking behavior is detected, please return: {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]} with the coordinates based on the 1000x1000 image size. Otherwise, please return: {"result": "no"}.
# """
gongbiao_question = """
Role: You are an intelligent assistant with the ability to recognize road signs or billboards. You can accurately extract and analyze the text content.
Task: Please identify the signs or billboards on the road (please note that this refers to the road itself, not the buildings along the road. If the sign is a common one on the buildings, please ignore it!) 。 If the text content can be extracted, please determine whether it is related to "public affairs" or "personal affairs":
Vocabulary related to "personal affairs" includes: "Welcome to **", "Advertisement of **", "Car maintenance of **", "Recruitment of **", etc.
Vocabulary related to "public affairs" includes: 1) Vocabulary related to "transportation" (such as "Maximum load of ** tons", "Prohibition of **", "Drunk driving of **", "Transportation of **", "Drive **", "Fasten seat belt", "Section of **", "Be careful of **", etc.);
2) Place names (such as Beijing, Shanghai, Xicheng District, Yao Guantun, Huangcun, etc.);
3) Indicative words (such as "** parking lot", "** gas station", etc.)
Note: There may be annotation texts related to road names in the upper left corner of the picture. These are irrelevant to the recognition task, so please ignore them! Do not recognize them as the text on the sign! If the text in the picture is difficult to recognize due to the shooting angle, lighting, or blurriness, or if you are unsure whether the text comes from an unofficial source, please reply "no" in all cases.
Output: If the text is of personal affairs nature, please return:
{"result": "yes",
"bounding_boxes": [[xmin1, ymin1, xmax1, ymax1]...] ，
"Content": The extracted text content } 
If it is related to transportation or official matters, please return: 
{ "result": "no", 
"Content": The extracted text content }
- The coordinates should be based on an image size of 1000x1000.
"""
# 设置悬挂物
# xuangua_question = """
# Role: You are an intelligent assistant capable of accurately identifying instances of illegal items being hung above roads or within the road area. Your task is to detect the presence of non-standard and illegal hanging objects and return their positions in the image.
#
# Task: Analyze the image and determine if there are any illegal items suspended above the road, such as banners, ropes, decorations, or other non-road infrastructure objects. Ignore pedestrians, vehicles (including parked vehicles), and legal road accessories (such as traffic signals, traffic signs, lamp posts, surveillance cameras, traffic guidance devices, etc.).
#
# Note: These items must first be hung from the highway infrastructure before they can be detected. If the hanging object is clearly an official facility, please reply "no". Or if it is impossible to determine whether it is legal or not, also reply "no" to avoid a wrong judgment.
#
# Output format: If illegal items are detected hanging above the road or within the road area, please return: {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]} with the coordinates based on the 1000x1000 image size. Otherwise, please return: {"result": "no"}.
# """
xuangua_question = """
Role: You are an intelligent assistant capable of accurately identifying illegal items hanging above roads or within road areas. Your task is to detect the presence of non-standard and illegal hanging items and return their positions in the image.
Task: Analyze the image and determine if there are any illegal items hanging above the road, such as banners, ropes, decorations, or other non-road infrastructure items. Ignore pedestrians, vehicles (including parked vehicles), and legal road infrastructure (such as traffic signals, traffic signs, lamp posts, surveillance cameras, traffic guidance devices, etc.).
Note: If the image is blurry, obstructed, or has severely insufficient lighting, making it impossible to make an accurate judgment, reply "no".
"""
# 堆放物品
# wupin_question = """
# Role: You are an intelligent assistant capable of accurately identifying the act of stacking items on the roads or within the road land area in an image. Your task is to detect whether there are any illegal stacking or placement of items, and return the positions of these items in the image.
#
# Task: Analyze the image and determine if there are any items piled up on the road or within the road area. These items should clearly not be vehicles or pedestrians, such as construction materials, tools, debris, stored items, etc. Please ignore pedestrians, vehicles (including parked vehicles), and legal road accessories (such as traffic signs, lamp posts, guardrails, etc.).
#
# Note: If the item is clearly part of the contents during transportation (such as being loaded onto a truck), please return "no".
#
# Output format:
#
# If stall setup or vending behavior is detected, please return
# {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]}
# where the coordinates are based on a reference size of 1000x1000 pixels.
# Otherwise, return {"result": "no"}.
# """
wupin_question = """
Role: You are an intelligent assistant capable of accurately identifying the act of stacking items on the road or within the road area.
Task: Please analyze the image and determine whether there are any items stacked on the road or within the road area. The focus is on identifying the actual act of stacking or placing the items, rather than vehicles or pedestrians, nor guardrails, power poles, or road obstacles.
Note: If you identify a vehicle, please return 'no'. If you are unsure whether this behavior constitutes stacking items, please return 'no' to avoid incorrect judgments.
"""
# 摆设摊位
# baitan_question = """
# Role: You are an intelligent assistant capable of accurately identifying the act of setting up roadside stalls or stands near or within the road land area in an image. Your task is to detect whether there are any illegal vending activities or stall setups close to the road. These should clearly be unauthorized vendor stands, portable tables, umbrellas, carts, or temporary setups used for selling items or providing services.
#
# Task: Analyze the image and determine if there is any evidence of stall setup or vending behavior occurring near the road area. Ignore legal infrastructure, pedestrians, and vehicles. If the stall appears to be part of a temporary setup (e.g., roadside vending, small stands selling goods), it should be flagged. Do not flag permanent shops attached to buildings or clearly legal market zones.
#
# Note: Ignore normal pedestrian activity or any item clearly being transported, loaded, or in legal parking/storage areas.
#
# Output format:
#
# If stall setup or vending behavior is detected, please return
# {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]}
# where the coordinates are based on a reference size of 1000x1000 pixels.
# Otherwise, return {"result": "no"}.
# """
# baitan_question = """
# You are such an artificial intelligence assistant that can identify illegal stall setups or temporary street vendors' activities on the roads or within the road usage areas. Please analyze the images to determine if there are any obvious signs of roadside sales, mobile stalls, or temporary booths occupying the roads or sidewalks. This includes tables, trolleys, umbrellas, signs, goods for sale, canopies, or any temporary setups clearly set up within the road or sidewalk areas for sales or services.
#
# The key lies in monitoring the actual parking arrangements and charging practices, rather than irrelevant individuals or parked vehicles.
#
# If the act of setting up a stall can be identified, then please handle it according to the following requirements: {"Result": "Yes", "Bounding Box": [[xmin1, ymin1, xmax1, ymax1], ...]}, where the coordinates have been converted to a reference frame of 1000x1000 pixels.
#
# Otherwise, return {"Result": "No"}.
#
# Ignore normal traffic, pedestrians, road signs, and infrastructure unrelated to the sales activities.
# """
baitan_question = """
Role: You are an artificial intelligence assistant capable of identifying illegal stall setups or temporary street vendors' activities on roads or within road usage areas.
Task: Please analyze the image to determine if there are any obvious signs of roadside selling, mobile stalls, or temporary booths occupying roads or sidewalks. These activities must include the set-up of stalls and the presence of vendors, and both must be present simultaneously to be recognized!
Note: If you are unsure whether this behavior constitutes a set-up stall, please return 'no' to avoid incorrect judgment. If the behavior does not occur in the road area, also return 'no'.
"""

model_result = 'Output : If the above behavior can be identified, then the following result will be returned: {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]}, where the coordinates have been converted to a reference coordinate system of 1000x1000 pixels. Otherwise, return {"result": "no"}.'
# 更新 配置.py的变量(全局变量)
def updata_dianList(action):
    print('获取监控点位id')

    df = get_dianwei_data()
    # 第一步：筛选“是”
    df_filtered = df[df['是否可用'] == '是']

    # 第二步：包含“擅自占用、挖掘公路”
    df_filtered = df_filtered[df_filtered['可能会存在的违法行为'].str.contains(action, na=False)]
    # 第三步：筛选“具备视频分析条件的点位”不为空
    df_filtered = df_filtered[
        df_filtered['camera_id'].notna() & (df_filtered['camera_id'] != '')]
    # 第四步：提取列并构造字典列表
    action_list = [
        {"camera_id": int(row["camera_id"]), "monitor_point": row["具备视频分析条件的点位"]}
        for _, row in df_filtered.iterrows()
        if pd.notna(row["camera_id"]) and pd.notna(row["具备视频分析条件的点位"])
    ]

    # 去掉 camera_id 缺失或为 None/空字符串 的项
    cleaned_list = [item for item in action_list if item.get("camera_id") not in [None, "", float('nan')]]

    # 去重：按 camera_id 保留第一个
    seen = set()
    unique_list = []
    for item in cleaned_list:
        cid = item["camera_id"]
        if cid not in seen:
            seen.add(cid)
            unique_list.append(item)

    return unique_list
def run_loop():
    wajue_question_action = {'擅自占用、挖掘公路': wajue_question+model_result}
    gongbiao_action = {'在公路用地范围内设置公路标志以外的其他标志': gongbiao_question}
    jinggai_action = {'在公路范围内擅自移动井盖': jinggai_question+model_result}
    xuangua_action = {'遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全': xuangua_question+model_result}
    duifang_action = {'在公路上及公路用地范围内堆放物品': wupin_question+model_result}
    baitan_action = {'在公路上及公路用地范围内摆摊设点': baitan_question+model_result}
    # 在模型运行前,先更新摄像头点位:id列表

    try:
        print("开始轮询擅自占用、挖掘公路", flush=True)
        poll_cameras(updata_dianList("擅自占用、挖掘公路"), wajue_question_action, WAJUE_PATH)
    except Exception as e:
        print(f"[异常] 擅自占用、挖掘公路：{e}", flush=True)
        traceback.print_exc()

    try:
        print("开始轮询设置非公路标志", flush=True)
        poll_cameras(updata_dianList("在公路用地范围内设置公路标志以外的其他标志"), gongbiao_action, GONGBIAO_PATH)
    except Exception as e:
        print(f"[异常] 设置非公路标志：{e}", flush=True)
        traceback.print_exc()

    try:
        print("开始轮询井盖移动或缺失", flush=True)
        poll_cameras(updata_dianList("在公路范围内擅自移动井盖"), jinggai_action, JINGGAI_PATH)
    except Exception as e:
        print(f"[异常] 井盖移动或缺失：{e}", flush=True)
        traceback.print_exc()

    try:
        print("开始轮询利用设施悬挂物", flush=True)
        poll_cameras(updata_dianList("遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全"), xuangua_action, XVANGUA_PATH)
    except Exception as e:
        print(f"[异常] 利用附属设施悬挂物品：{e}", flush=True)
        traceback.print_exc()

    try:
        print("开始轮询堆放物品", flush=True)
        poll_cameras1(duifang_list, duifang_action, WUPIN_PATH)
    except Exception as e:
        print(f"[异常] 堆放物品：{e}", flush=True)
        traceback.print_exc()

    try:
        print("开始轮询摆设摊位", flush=True)
        poll_cameras1(baitan_list, baitan_action, BAITAN_PATH)
    except Exception as e:
        print(f"[异常] 摆设摊位：{e}", flush=True)
        traceback.print_exc()

if __name__ == '__main__':
    import multiprocessing
    import time
    from infra.my_logger import Logger

    # 初始化日志
    logger = Logger(name="AppLogger").get_logger()

    print("开始运行")

    # 开启托管本地图片进程
    server_process = multiprocessing.Process(target=run_flask_server, name="ServerImg")
    server_process.start()

    # 开启删除图片进程
    clear_process = multiprocessing.Process(target=clear_begin, name="ClearImg")
    clear_process.start()

    # 开启推送太极进程
    tuisong_process = multiprocessing.Process(target=tuisong_main, name="tuisong_main")
    tuisong_process.start()

    # 主循环
    while True:
        run_loop()
        print("等待5分钟后继续下一轮操作...")
        time.sleep(300)  # 5分钟


