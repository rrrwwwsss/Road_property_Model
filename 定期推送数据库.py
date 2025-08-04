
import time
import traceback
import pandas as pd
# import schedule

from 提交数据库 import insert_database
def tuisong(csv_file_path):
    # 使用 pandas 读取 CSV 文件
    def read_csv_to_dict(file_path):
        df = pd.read_csv(file_path)
        # 将 DataFrame 转换为字典列表
        data_list = df.to_dict(orient='records')
        return df, data_list

    # 清空数据行，保留标题行
    def clear_csv_data(file_path):
        df, data_list = read_csv_to_dict(file_path)
        # 创建一个新的空 DataFrame，列名与原 DataFrame 相同
        empty_df = pd.DataFrame(columns=df.columns)
        # 保存为空的 CSV 文件
        empty_df.to_csv(file_path, index=False)

    # 读取并处理数据
    data_list = read_csv_to_dict(csv_file_path)[1]

    # 循环字典列表，调用 insert_database
    for data in data_list:
        print(data)
        insert_database(data)

    # 清空数据行
    clear_csv_data(csv_file_path)
def job():
    print("开始推送数据", flush=True)
    tuisong("Copy of result.csv")
    print("推送数据库并清理csv完成", flush=True)
def tuisong_main():
    # # 每天 2 点执行一次
    # schedule.every().day.at("02:00").do(job)
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)  # 每分钟检查一次任务
    while True:
        time.sleep(4000)
        try:
            print("开始推送数据", flush=True)
            tuisong("Copy of result.csv")
            print("推送数据库并清理csv完成", flush=True)
        except Exception as e:
            print("清理过程中出现异常：", flush=True)
            traceback.print_exc()  # 打印完整异常堆栈
        time.sleep(86400)  # 每天执行一次
if __name__ == "__main__":
    tuisong_main()
