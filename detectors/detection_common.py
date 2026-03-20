import ast
import json
import os
import sqlite3
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from detectors.公共方法 import draw_bounding_boxes


def safe_sql_value(value):
    # 将常见 Python/Pandas/Numpy 值统一转换为 SQLite 可写入的基础类型：
    # - dict/list -> JSON 字符串
    # - numpy 数值 -> Python 原生数值
    # - NaN/NaT -> None
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if pd.isna(value):
        return None
    return value


def write_dict_to_sqlite(db_path, table_name, data, drop_keys=("other_data", "模型输出")):
    # 通用写库入口：多个识别模块共享同一套插入逻辑，避免重复维护 SQL 细节。
    # drop_keys 用于剔除不应落库的临时字段（例如 other_data）。
    sqlite_data = data.copy()
    for key in drop_keys:
        sqlite_data.pop(key, None)

    keys = ", ".join(sqlite_data.keys())
    placeholders = ", ".join(["?"] * len(sqlite_data))
    values = [safe_sql_value(v) for v in sqlite_data.values()]

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})",
            values,
        )
        conn.commit()
    finally:
        conn.close()


def validate_boxes(result_dict, min_width=10, min_height=10, max_boxes=4):
    # 通用框校验逻辑：
    # 1) 限制框数量上限，降低误检输出噪声
    # 2) 限制最小宽高，过滤过小/异常框
    # 3) 若所有框都无效则强制改判为 no
    print("模型结果：", result_dict)
    boxes = result_dict.get("bounding_boxes", [])
    all_invalid = True

    if len(boxes) > max_boxes:
        result_dict["result"] = "no"
        print(f"框的数量超过 {max_boxes} 个，已标记为 no")
        return result_dict

    for box in boxes:
        try:
            xmin, ymin, xmax, ymax = box
            width = xmax - xmin
            height = ymax - ymin
            if width >= min_width and height >= min_height:
                all_invalid = False
                print(f"框有效：{box}")
                break
        except Exception as exc:
            print(f"处理 box {box} 时出错：{exc}")

    if all_invalid and boxes:
        result_dict["result"] = "no"
        print("所有框都无效，已标记为 no")

    return result_dict


def save_detection_images(image, output_folder, filename, normalized_boxes, linux_pic_path):
    # 统一保存检测结果：
    # - 原图保存到 shibie_yuantu/<行为目录>
    # - 标注图保存到业务输出目录
    # - 返回 Linux 侧对外上报使用的路径
    os.makedirs(output_folder, exist_ok=True)

    source_dir = os.path.join("./shibie_yuantu", os.path.basename(output_folder))
    os.makedirs(source_dir, exist_ok=True)
    source_path = os.path.join(source_dir, filename)
    image.save(source_path)
    print(f"原图已保存到 {source_path}")

    marked_path = os.path.join(output_folder, filename)
    output_image = draw_bounding_boxes(image.copy(), normalized_boxes or [])
    output_image.save(marked_path)

    linux_path = os.path.join(linux_pic_path + os.path.basename(output_folder), filename)
    print(f"目标图已保存到 linux 路径：{linux_path}")
    return linux_path



def load_polygon_points_from_csv(csv_path, target_location):
    # 从配置 CSV 中读取某个点位对应的多边形区域点，供马赛克遮罩复用。
    # CSV 约定字段：
    # - 点位: 监控点位名称
    # - 区域: 字符串化的点位列表，如 "[(x1,y1),(x2,y2),...]"
    df = pd.read_csv(csv_path)
    target_row = df[df["点位"] == target_location]
    if target_row.empty:
        print(f"未找到指定位置: {target_location}")
        return None

    region_str = target_row["区域"].values[0]
    try:
        return ast.literal_eval(region_str)
    except (SyntaxError, ValueError) as exc:
        print(f"区域字段解析失败: {exc}")
        return None
def handle_sixiang_write_and_upload(
    data,
    db_path,
    chongfu_time_hours,
    query_permissions_fn,
    write_to_sqlite_fn,
    upload_data_fn,
):
    """处理 sixiang_weifa 的去重写入与上报。"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sixiang_weifa
        (
            工单编号 TEXT,
            违法类型 TEXT,
            发生地点 TEXT,
            发生时间 TEXT,
            处理状态 TEXT,
            处理人 TEXT,
            path TEXT,
            处理备注 TEXT
        )
        """
    )
    conn.commit()

    history_df = pd.read_sql_query("SELECT * FROM sixiang_weifa", conn)
    history_df["发生时间"] = pd.to_datetime(history_df["发生时间"], format="%Y%m%d_%H%M%S")
    data_time = datetime.strptime(data["发生时间"], "%Y%m%d_%H%M%S")
    time_diff = timedelta(hours=chongfu_time_hours)

    filtered_df = history_df[
        (history_df["发生地点"] == data["发生地点"])
        & (history_df["违法类型"] == data["违法类型"])
        & ((history_df["发生时间"] - data_time).abs() <= time_diff)
    ]

    try:
        query_results = query_permissions_fn()
        if data["违法类型"] == "擅自占用、挖掘公路":
            matched_addresses = [
                item for item in query_results.get("zhanwagonglu", [])
                if item.get("constructaddress") == data["发生地点"]
            ]
            if matched_addresses:
                filtered_df = pd.DataFrame(columns=history_df.columns)
                print("已经有许可信息，不是违法行为")
            else:
                print("没有许可信息")
        elif data["违法类型"] == "在公路用地范围内设置公路标志以外的其他标志":
            matched_addresses = [
                item for item in query_results.get("feigongbiao", [])
                if item.get("constructaddress") == data["发生地点"]
            ]
            if matched_addresses:
                filtered_df = pd.DataFrame(columns=history_df.columns)
                print("已经有许可信息，不是违法行为")
            else:
                print("没有许可信息")
    except Exception as exc:
        print(f"校验 query_results 出错: {exc}")

    if filtered_df.empty:
        write_to_sqlite_fn(data)
        print("开始往太极传数据")
        upload_data_fn(data)
        return True

    print(f"{chongfu_time_hours}小时内已上传过该行为")
    return False

