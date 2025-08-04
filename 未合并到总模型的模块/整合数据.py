import csv
import os

from 获取摄像头点位数据 import get_dianwei_data
from 数据库配置 import *
from 提交数据库 import insert_database
def get_data(model_data):
    # model_data = {
    #                 "工单编号": filename,
    #                 "违法类型": the_type,
    #                 "发生地点": monitor_point,
    #                 "发生时间": timestamp,
    #                 "处理状态": "待处理",
    #                 "处理人": "执法员",
    #                 "path": output_path,
    #                 "处理备注": "无备注",
    #             }
    # 获取辖区编码
    print(model_data)
    df = get_dianwei_data()
    target = model_data['发生地点']
    unit_code = df[df['具备视频分析条件的点位'] == target]['辖区编码'].iloc[0]
    print("辖区编码:",unit_code)
    data = {
        "TJ_NAME": TJ_NAME_LIST[model_data["违法类型"]],
        # 违法行为描述
        "MEASURE": AUTHORITY_CODE[model_data["违法类型"]],  # 职权编码
        "UNIT_CODE": str(int(float(unit_code))),  # 辖区编码
        "工单编号": model_data["工单编号"],
        "违法类型": model_data["违法类型"],
        "发生地点": model_data["发生地点"],
        "发生时间": model_data["发生时间"],
        "图片路径": IMG_URL+model_data["path"].replace("/data1/qwen2v/pic/", ""),
        "OffsiteRule_id" : VIOLATION_DICT[model_data["违法类型"]],
    }
    # 写入csv备份
    # 写入的 CSV 文件路径
    csv_path = "result.csv"
    # 字段顺序
    fieldnames = list(data.keys())
    # 判断文件是否存在
    file_exists = os.path.isfile(csv_path)

    # 打开 CSV 文件，追加或写入
    with open(csv_path, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()
        else:
            # 检查表头一致性
            with open(csv_path, mode='r', encoding='utf-8-sig') as fr:
                reader = csv.reader(fr)
                try:
                    header = next(reader)
                    if header != fieldnames:
                        raise ValueError("CSV 文件表头不一致")
                except StopIteration:
                    # 空文件，写入表头
                    writer.writeheader()

        writer.writerow(data)

    print('传入提交数据库模块数据:',data)
    insert_database(data)