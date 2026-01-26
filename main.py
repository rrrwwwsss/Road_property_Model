import traceback
import threading

import pandas as pd
from 获取摄像头点位数据 import get_dianwei_data
from 配置 import *
from 从接口获取数据并分配给模型 import *
from 清理图片 import clear_begin
from 托管本地图片到网络 import run_flask_server
from 定期推送数据库 import tuisong_main

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
**Role:**
You are an intelligent assistant capable of accurately identifying road occupation or excavation activities in images.

**Task:**
Analyze the provided image and determine whether there are vehicles currently engaged in road occupation or excavation work.
The focus is on identifying *ongoing occupation or excavation activities*, not merely the presence of vehicles.

**To be recognized as an occupation or excavation activity, the following three conditions must all be met:**

1. The occupation or excavation activity itself is visibly taking place.
2. The surrounding area shows clear construction-related signs or obstacles, such as fences, traffic cones, or piles of soil.
   *(Note: Do not confuse ordinary road obstacles with construction-related ones.)*
3. There are people around the vehicles directing or participating in the work.

**Exclusion criteria:**

1. Ignore large vehicles that are parked or driving within safe zones and not participating in construction.
2. Ignore buildings, pedestrians, toll booths, and road dividers.
3. If the picture is unclear and affects your judgment, please ignore it.
4. Ignoring normal road maintenance behaviors
   If the image is too blurry, obscured, or poorly lit to make an accurate judgment, respond with **“no.”**

"""

# 井盖缺失
jinggai_question = """
Role: You are an intelligent assistant capable of accurately identifying instances of missing or removed manhole covers on roads or within road land areas in images.

Task: Analyze the image to precisely identify and locate abnormal situations of **missing manhole covers (exposed shafts)** on the road surface or curb areas.
- Please identify and mark manhole openings that should be covered but are currently exposed. Features include:
1. Distinct circular, rectangular, or square dark voids (traps).
2. Manhole covers that are displaced, flipped, or partially collapsed, resulting in the shaft being partially or fully exposed.
3. The opening is usually accompanied by a clear edge contour, with the interior appearing as deep shadow or standing water.

Note: If the lighting is extremely dark, the image is severely blurred, or reflections from accumulated water make it impossible to determine the presence of a hole with certainty, you must return {"result": "no"} to avoid false positives.
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
Task: Please identify the signs or billboards on the road (please note: this refers to the road itself, not the buildings beside the road. If the sign is a common one on buildings, please ignore it! Also, ignore vehicle advertisements or signs). Extract the text content and determine whether it is related to "public affairs" or "personal affairs":
Words related to "personal affairs" include: "Welcome to **", "Advertisement of **", "Vehicle Maintenance of **", "Recruitment of **", etc.
Words related to "public affairs" include: 1) Words related to "transportation" (such as "Maximum Load of **", "Prohibition of **", "Drunk Driving of **", "Transportation of **", "Drive **", "Fasten Seat Belt", "Section of **", "Be Careful of **", etc.); 
2) Place names (such as Beijing, Shanghai, Xicheng District, Yao Guantun, Huangcun, etc.); 
3) Indicative words (such as "Parking Lot of **", "Gas Station of **", etc.)
Note: There may be text annotations related to the road name in the upper left corner of the picture. These are not related to the recognition task, please ignore them! Do not recognize them as text on the sign! If the text in the picture is difficult to recognize due to the shooting angle, light, or blurriness, or if you are unsure whether the text comes from an unofficial source, please reply "no" in all cases.
Output: If the text is of personal affairs nature, return: {"result": "yes",
"bounding_boxes": [[xmin1, ymin1, xmax1, ymax1]... ]},
"Content": The extracted text content }
If related to transportation or official business, reply:
{ "result": "no",
"Content": The extracted text content } 
- The coordinates should be based on a 1000x1000 image size.
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

# Role
您是一位道路安全AI检测员，请分析图像，识别并定位位于行车道正上方且可能危及交通安全的非法悬挂物。

# Detection Target (Positive Class)
请寻找悬挂在道路上方空间的异常物品，包括但不限于：
1. 私人悬挂物（如横幅、私人装饰、灯笼、衣物等）。
2. 非交通用途的掉落悬挂物或未固定的建筑材料。
*注意：仅关注物理位置处于道路上方（Overhead）且可能造成掉落风险或视线遮挡的物体。注意：如果是那种道路上面有桥的要忽略桥上正常行驶的车辆以及桥上正常的横幅*

# Exclusion Criteria (Negative Class) - *必须严格忽略*
1. 合法交通设施：交通信号灯、标志牌、龙门架、路灯、监控摄像头、官方电缆/电线、交通诱导屏。
2. 背景物体：仅附着在路边建筑物墙面上的物体（未延伸至道路上方）、路边的树木（包括伸出的树枝和树叶）、路面杂物。
3. 合法基建：桥梁附属的排水管、紧贴桥梁结构的固定管道（除非管道呈断裂或异常悬垂状态）。
4. 无关细节：光斑、阴影、雨雾干扰、对交通安全无威胁的细微物体（如桥梁垂下的一小段无害绳头）。
5. 移动目标：行人、车辆（含停放车辆）。
6. 桥梁相关正常现象：
   - **在立交桥/桥梁上正常行驶的车辆。**
   - **固定在桥梁护栏或结构上的官方标语、宣传横幅。**
7. **图像人工处理痕迹：**
   - **纯黑色的方框、遮盖块、人工涂抹区域或后期处理的标注框。**

# Text Analysis Logic
如果检测对象包含文字，执行OCR分析：
- 若内容为交通指令、地名、公共标语或官方公告 -> 忽略（视为合法设施）。
- 若内容为商业广告、私人信息或无法识别的非官方文本 -> 保留（视为非法悬挂物）。

# Quality Control
如果图像因模糊、过暗、过曝或恶劣天气（雨/雾）导致无法做出可靠判断，必须直接返回 {"result": "no"}。

# Output Format
- 如果检测到目标：
  {"result": "yes", "bounding_boxes": [[xmin, ymin, xmax, ymax], ...], "xvanguawu": "物品名称"}
  *注：坐标需归一化并映射到 1000x1000 像素参考系。*
- 如果未检测到目标或图像质量差：
  {"result": "no"}
"""
#
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
Role: You are an intelligent assistant capable of accurately identifying the act of stacking items on or within the road area.
Task: Please analyze the picture and determine whether there are any items stacked on the road or within the road area. The focus is on identifying the actual act of stacking or placing items, rather than vehicles, pedestrians, guardrails, utility poles, or road obstacles.
Please ignore the following items:
1. Items present at a construction site during construction
2. Isolation barriers, roadblocks, crash barrels, etc. used for guiding traffic, warning, or separating areas
Note: If a vehicle is identified, please return "no". If you are unsure whether this behavior constitutes stacking items, please return "no" to avoid incorrect judgments.
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
Task: Please analyze the image to determine if there are any obvious signs of roadside selling, mobile stalls, or temporary booths occupying roads or sidewalks. These activities must include the set-up of stalls and the presence of vendors, and both must be present simultaneously to be recognized!Please ignore the goods on the vehicles that are moving normally!
Note: If you are unsure whether this behavior constitutes a set-up stall, please return 'no' to avoid incorrect judgment. If the behavior does not occur in the road area, also return 'no'.
"""

model_result = 'Output : If the above behavior can be identified, then the following result will be returned: {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]}, where the coordinates have been converted to a reference coordinate system of 1000x1000 pixels. Otherwise, return {"result": "no"}.'
# 更新 配置.py的变量(全局变量)
def updata_dianList(action):
    print('获取监控点位id')
    # 从"result_with_camera_id.csv"获取要轮询的点位
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

    def gaopin():
        while True:
            try:
                # wajue_list = updata_dianList("擅自占用、挖掘公路")
                print("开始轮询擅自占用、挖掘公路", flush=True)
                chuli({'擅自占用、挖掘公路': wajue_question + model_result}, WAJUE_PATH)
            except Exception as e:
                print(f"[异常] 擅自占用、挖掘公路：{e}", flush=True)
                traceback.print_exc()
            time.sleep(60)
            print("占掘路点位已轮询一遍")



    def zhongpin():
        while True:
            try:
                # duifang_list = updata_dianList("在公路上及公路用地范围内堆放物品")
                print("开始轮询堆放物品", flush=True)
                chuli({'在公路上及公路用地范围内堆放物品': wupin_question + model_result}, WUPIN_PATH)
            except Exception as e:
                print(f"[异常] 堆放物品：{e}", flush=True)
                traceback.print_exc()
            time.sleep(60)

            print("堆放物品点位已轮询一遍")

            try:
                # baitan_list = updata_dianList("在公路上及公路用地范围内摆摊设点")
                print("开始轮询摆设摊位", flush=True)
                chuli({'在公路上及公路用地范围内摆摊设点': baitan_question + model_result}, BAITAN_PATH)
            except Exception as e:
                print(f"[异常] 摆设摊位：{e}", flush=True)
                traceback.print_exc()
            time.sleep(60)
            print("摆设摊位点位已轮询一遍")
    def dipin():
        while True:
            try:
                # xuangua_list = updata_dianList("遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全")
                print("开始轮询利用设施悬挂物", flush=True)
                chuli({'遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全': xuangua_question }, XVANGUA_PATH)
            except Exception as e:
                print(f"[异常] 利用附属设施悬挂物品：{e}", flush=True)
                traceback.print_exc()
            time.sleep(60)
            print("悬挂物点位已轮询一遍")

            try:
                # jinggai_list = updata_dianList("在公路范围内擅自移动井盖")
                print("开始轮询井盖移动或缺失", flush=True)
                chuli( {'在公路范围内擅自移动井盖': jinggai_question + model_result}, JINGGAI_PATH)
            except Exception as e:
                print(f"[异常] 井盖移动或缺失：{e}", flush=True)
                traceback.print_exc()
            time.sleep(60)
            print("井盖缺失点位已轮询一遍")

            try:
                # gongbiao_list = updata_dianList("在公路用地范围内设置公路标志以外的其他标志")
                print("开始轮询设置非公路标志", flush=True)
                chuli( {'在公路用地范围内设置公路标志以外的其他标志': gongbiao_question}, GONGBIAO_PATH)
            except Exception as e:
                print(f"[异常] 设置非公路标志：{e}", flush=True)
                traceback.print_exc()
            time.sleep(60)
            print("非公路标志点位已轮询一遍")


        # === 关键：使用 threading.Thread 并设置为守护线程 ===

    tasks = [
        gaopin,
        zhongpin,
        dipin,
    ]

    threads = []
    for task in tasks:
        t = threading.Thread(target=task, name=task.__name__, daemon=True)  # daemon=True
        t.start()
        threads.append(t)
        print(f"已启动线程: {t.name}")



    print("所有监控线程已启动，主程序不再阻塞...")
    while True:
        time.sleep(3600)
    # 主线程可以继续做别的事，比如健康检查、接收信号等
if __name__ == '__main__':
    import multiprocessing
    import time
    from my_logger import Logger
    from logging.handlers import QueueListener
    log_queue = multiprocessing.Queue()

    # 主进程 logger
    logger = Logger(name="AppLogger").get_logger()
    queue_listener = QueueListener(log_queue, *logger.handlers)
    queue_listener.start()

    print("开始运行")

    # 开启托管本地图片进程
    server_process = multiprocessing.Process(target=run_flask_server, name="ServerImg")
    server_process.start()

    # 开启删除图片进程
    clear_process = multiprocessing.Process(target=clear_begin, name="ClearImg")
    clear_process.start()

    # 开启推送太极进程
    tuisong_process = multiprocessing.Process(target=tuisong_main, name="tuisong_main", args=(log_queue,))
    tuisong_process.start()


    run_loop()


