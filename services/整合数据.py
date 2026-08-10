import csv
import os
import sqlite3

from config.配置 import TEMPORARY_RECORD
from services.获取摄像头点位数据 import get_dianwei_data
from config.数据库配置 import *
from services.提交数据库 import insert_database
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
    # df = get_dianwei_data()
    target = model_data['发生地点']
    unit_code = model_data['other_data']['area_number']
    print("辖区编码:",unit_code)
    try:
        unit_code = str(int(float(unit_code)))
    except (ValueError, TypeError):
        unit_code = "未知"
    data = {
        "TJ_NAME": TJ_NAME_LIST[model_data["违法类型"]],
        # 违法行为描述
        "MEASURE": AUTHORITY_CODE[model_data["违法类型"]],  # 职权编码
        "UNIT_CODE": unit_code,  # 辖区编码
        "工单编号": model_data["工单编号"],
        "违法类型": model_data["违法类型"],
        "发生地点": model_data["发生地点"],
        "发生时间": model_data["发生时间"],
        "图片路径": IMG_URL+model_data["path"].replace("/data1/qwen2v/pic/", ""),
        "OffsiteRule_id" : VIOLATION_DICT[model_data["违法类型"]],
    }
    # 针对特定违法类型替换 OffsiteRule_id
    if model_data["违法类型"] in ("在公路上及公路用地范围内堆放物品", "在公路上及公路用地范围内摆摊设点"):
        data["OffsiteRule_id"] = VIOLATION_DICT['造成公路路面损坏、污染或者影响公路畅通']
    if model_data["违法类型"] in ("在公路范围内擅自移动井盖"):
        data["OffsiteRule_id"] = VIOLATION_DICT['公路范围内擅自移动井盖']
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
    allowed_violations = [
        '遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全',
        '在公路范围内擅自移动井盖',
        '在公路用地范围内设置公路标志以外的其他标志'
    ]

    if model_data['违法类型'] not in allowed_violations:
        insert_database(data)
        commit_flag = True  # bool
    else:
        commit_flag = False

    # 额外将信息存储到数据库
    print('存储进本地数据库')

    # 提取额外字段
    model_output_str = model_data['other_data'].get("model_output", "")  # str (使用 get 防报错)
    belong_team_str = model_data['other_data'].get("belong_team", "")  # 新增：所属支队

    # 连接数据库
    import sqlite3  # 如果上面没导入的话
    conn = sqlite3.connect(TEMPORARY_RECORD)
    cursor = conn.cursor()

    # 1. 创建表（如果不存在，直接在建表语句里带上新字段，照顾全新的数据库）
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS results
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       TJ_NAME TEXT,
                       MEASURE TEXT,
                       UNIT_CODE TEXT,
                       工单编号 TEXT UNIQUE,
                       违法类型 TEXT,
                       发生地点 TEXT,
                       发生时间 TEXT,
                       图片路径 TEXT,
                       OffsiteRule_id TEXT,
                       model_output TEXT,
                       is_committed BOOLEAN,
                       所属支队 TEXT
                   )
                   ''')
    # 2. 动态检查旧表是否缺少新列，如果缺少则自动新增
    cursor.execute("PRAGMA table_info(results)")
    # table_info 返回的每行格式为: (cid, name, type, notnull, dflt_value, pk)
    # 取出所有的列名 (索引为 1 的位置)
    existing_columns = [col[1] for col in cursor.fetchall()]

    if "所属支队" not in existing_columns:
        print("检测到 results 表中缺少 '所属支队' 列，正在自动新增该列...")
        cursor.execute("ALTER TABLE results ADD COLUMN 所属支队 TEXT")
    # 2. 插入数据
    # 增加了 所属支队 字段和对应的占位符 ?
    cursor.execute('''
                   INSERT INTO results (TJ_NAME, MEASURE, UNIT_CODE, 工单编号, 违法类型,
                                        发生地点, 发生时间, 图片路径, OffsiteRule_id,
                                        model_output, is_committed, 所属支队)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ''', (
                       data["TJ_NAME"],
                       data["MEASURE"],
                       data["UNIT_CODE"],
                       data["工单编号"],
                       data["违法类型"],
                       data["发生地点"],
                       data["发生时间"],
                       data["图片路径"],
                       data["OffsiteRule_id"],
                       model_output_str,
                       int(commit_flag),  # SQLite 没有原生 BOOLEAN，用 0/1 存储
                       belong_team_str  # 👈 新增传入的值
                   ))

    # 3. 提交并关闭
    conn.commit()
    conn.close()

    print("✅ 数据已成功写入数据库！")