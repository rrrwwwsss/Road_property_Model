import multiprocessing
import sys
import threading
import time
import traceback
from logging.handlers import QueueListener

from infra.my_logger import Logger
from services.从接口获取数据并分配给模型 import chuli
from services.定期推送数据库 import tuisong_main
from services.托管本地图片到网络 import run_flask_server
from services.清理图片 import clear_begin
from config.task_config import TASK_GROUPS

# 关闭输出缓冲，避免多线程/多进程场景下日志长时间不刷新。
sys.stdout.reconfigure(line_buffering=True)


def run_worker(group_name, tasks):
    """执行一个线程组内的轮询任务。

    参数说明：
    - group_name: 线程名称（如 gaopin/zhongpin/dipin）。
    - tasks: 任务列表，结构见 task_config.TASK_GROUPS。

    行为说明：
    1. 顺序执行本组所有任务。
    2. 每个任务执行失败只记录异常，不影响同组后续任务。
    3. 每个任务结束后按任务配置 sleep，控制轮询频率。
    """
    while True:
        for task in tasks:
            display_name = task["display_name"]
            violation_key = task["violation_key"]
            prompt_text = task["prompt_text"]
            output_path = task["output_path"]
            sleep_seconds = task["sleep_seconds"]

            try:
                print(f"[{group_name}] 开始轮询：{display_name}", flush=True)
                chuli({violation_key: prompt_text}, output_path)
            except Exception as exc:
                print(f"[{group_name}] 异常：{display_name} -> {exc}", flush=True)
                traceback.print_exc()

            print(f"[{group_name}] 本轮完成：{display_name}")
            time.sleep(sleep_seconds)


def run_loop():
    """按配置启动识别线程组并保持主线程常驻。"""
    threads = []
    for group_name, tasks in TASK_GROUPS.items():
        # 设为守护线程：主进程退出时线程自动结束，避免僵尸线程。
        thread = threading.Thread(
            target=run_worker,
            args=(group_name, tasks),
            name=group_name,
            daemon=True,
        )
        thread.start()
        threads.append(thread)
        print(f"已启动线程组: {group_name}")

    print("所有检测线程已启动，主线程进入常驻状态")
    while True:
        # 主线程仅负责保活，避免空转占用 CPU。
        time.sleep(3600)


def start_background_processes(log_queue):
    """启动主流程依赖的后台进程。"""
    process_list = [
        multiprocessing.Process(target=run_flask_server, name="ServerImg"),
        multiprocessing.Process(target=clear_begin, name="ClearImg"),
        multiprocessing.Process(target=tuisong_main, name="tuisong_main", args=(log_queue,)),
    ]

    for process in process_list:
        process.start()
        print(f"已启动进程: {process.name}")

    return process_list


if __name__ == '__main__':
    # 统一日志队列：把多进程日志汇总到主进程的 logger handlers。
    log_queue = multiprocessing.Queue()
    logger = Logger(name="AppLogger").get_logger()
    queue_listener = QueueListener(log_queue, *logger.handlers)
    queue_listener.start()

    print("开始运行")
    start_background_processes(log_queue)
    run_loop()

