from datetime import datetime, timedelta
import time
import traceback

import pandas as pd

from config.配置 import PUSH_CSV_PATH
from services.提交数据库 import insert_database


def tuisong(csv_file_path):
    """读取结果 CSV，逐条推送后清空内容（保留表头）。"""

    def read_csv_to_dict(file_path):
        df = pd.read_csv(file_path)
        # 模型输出列仅用于留档，不参与后续推送逻辑。
        # 这里对“推送视图”做列剔除，不影响源文件原始列。
        push_df = df.drop(columns=["模型输出"], errors="ignore")
        data_list = push_df.to_dict(orient='records')
        return df, data_list

    def clear_csv_data(file_path):
        df, _ = read_csv_to_dict(file_path)
        empty_df = pd.DataFrame(columns=df.columns)
        empty_df.to_csv(file_path, index=False)

    data_list = read_csv_to_dict(csv_file_path)[1]
    for data in data_list:
        print(data)
        insert_database(data)

    clear_csv_data(csv_file_path)


def tuisong_main(_queue):
    """每天固定时间触发一次推送任务。"""
    hour = 1
    minute = 0
    print("定期推送数据程序运行")

    while True:
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)

        sleep_seconds = (next_run - now).total_seconds()
        time.sleep(sleep_seconds)

        try:
            print("开始推送数据", flush=True)
            tuisong(PUSH_CSV_PATH)
            print("推送数据库并清理csv完成", flush=True)
        except Exception:
            print("清理过程中出现异常：", flush=True)
            traceback.print_exc()
