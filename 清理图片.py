import os
import time
import traceback
from 配置 import YUANTU_PATH


def clear_old_files(folder_path, days=10):
    # 计算时间阈值：30 天前
    cutoff_time = time.time() - days * 86400  # 86400 秒 = 1 天

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < cutoff_time:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
def clear_begin():
    while True:
        try:
            print("开始清理图片", flush=True)
            clear_old_files(YUANTU_PATH, days=30)
            print("清理完成", flush=True)
        except Exception as e:
            print("清理过程中出现异常：", flush=True)
            traceback.print_exc()  # 打印完整异常堆栈
        time.sleep(86400)  # 每天执行一次
# 用法
if __name__ == "__main__":
    clear_begin()

