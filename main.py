import traceback
import threading

import pandas as pd
from services.获取摄像头点位数据 import get_dianwei_data
from config.配置 import *
from services.从接口获取数据并分配给模型 import *
from services.清理图片 import clear_begin
from services.托管本地图片到网络 import run_flask_server
from services.定期推送数据库 import tuisong_main

import sys

from utils.prompt_loader import load_wajue_prompts, load_jinggai_prompts, load_gongbiao_prompts, load_xuangua_prompts, \
    load_duifang_prompts, load_baitai_prompts

# 关闭输出缓冲，解决打印堵塞问题
sys.stdout.reconfigure(line_buffering=True)


# model_result = 'Output : If the above behavior can be identified, then the following result will be returned: {"result": "yes", "bounding_boxes": [[xmin1, ymin1, xmax1, ymax1], ...]}, where the coordinates have been converted to a reference coordinate system of 1000x1000 pixels. Otherwise, return {"result": "no"}.'
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
            # 占用挖掘公路
            wajue_question = load_wajue_prompts()
            try:
                # wajue_list = updata_dianList("擅自占用、挖掘公路")
                print("开始轮询擅自占用、挖掘公路", flush=True)
                chuli({'擅自占用、挖掘公路': wajue_question}, WAJUE_PATH)
            except Exception as e:
                print(f"[异常] 擅自占用、挖掘公路：{e}", flush=True)
                traceback.print_exc()
            print("占掘路点位已轮询一遍")
            time.sleep(60)




    def zhongpin():
        while True:
            wupin_question = load_duifang_prompts()
            try:
                # duifang_list = updata_dianList("在公路上及公路用地范围内堆放物品")
                print("开始轮询堆放物品", flush=True)
                chuli({'在公路上及公路用地范围内堆放物品': wupin_question}, WUPIN_PATH)
            except Exception as e:
                print(f"[异常] 堆放物品：{e}", flush=True)
                traceback.print_exc()
            print("堆放物品点位已轮询一遍")
            time.sleep(60)

            baitan_question = load_baitai_prompts()
            try:
                # baitan_list = updata_dianList("在公路上及公路用地范围内摆摊设点")
                print("开始轮询摆设摊位", flush=True)
                chuli({'在公路上及公路用地范围内摆摊设点': baitan_question}, BAITAN_PATH)
            except Exception as e:
                print(f"[异常] 摆设摊位：{e}", flush=True)
                traceback.print_exc()
            print("摆设摊位点位已轮询一遍")
            time.sleep(60)

    def dipin():
        while True:
            # 设置悬挂物
            xuangua_question = load_xuangua_prompts()
            try:
                # xuangua_list = updata_dianList("遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全")
                print("开始轮询利用设施悬挂物", flush=True)
                chuli({'遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全': xuangua_question }, XVANGUA_PATH)
            except Exception as e:
                print(f"[异常] 利用附属设施悬挂物品：{e}", flush=True)
                traceback.print_exc()
            print("悬挂物点位已轮询一遍")
            time.sleep(60)

            # 井盖缺失
            jinggai_question = load_jinggai_prompts()
            try:
                # jinggai_list = updata_dianList("在公路范围内擅自移动井盖")
                print("开始轮询井盖移动或缺失", flush=True)
                chuli( {'在公路范围内擅自移动井盖': jinggai_question}, JINGGAI_PATH)
            except Exception as e:
                print(f"[异常] 井盖移动或缺失：{e}", flush=True)
                traceback.print_exc()
            print("井盖缺失点位已轮询一遍")
            time.sleep(60)

            gongbiao_question = load_gongbiao_prompts()
            try:
                # gongbiao_list = updata_dianList("在公路用地范围内设置公路标志以外的其他标志")
                print("开始轮询设置非公路标志", flush=True)
                chuli( {'在公路用地范围内设置公路标志以外的其他标志': gongbiao_question}, GONGBIAO_PATH)
            except Exception as e:
                print(f"[异常] 设置非公路标志：{e}", flush=True)
                traceback.print_exc()
            print("非公路标志点位已轮询一遍")
            time.sleep(60)



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
    from infra.my_logger import Logger
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


