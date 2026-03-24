import json
import os
import re
from PIL import Image, ImageDraw
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import pandas as pd


def check_and_log_sixiang_weifa(data, db_path, chongfu_hours):
    """
    基于现有的 sixiang_weifa 表进行防重校验：
    检查指定时间内是否已经上报过该地点的同类违法行为。
    如果没有上报过，则将本次记录写入 sixiang_weifa 表，并返回 True（允许上报）。
    如果已经上报过，则返回 False（拦截上报）。
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 确保表存在（与原逻辑结构一致，没有框位置）
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS sixiang_weifa
                   (
                       工单编号
                       TEXT,
                       违法类型
                       TEXT,
                       发生地点
                       TEXT,
                       发生时间
                       TEXT,
                       处理状态
                       TEXT,
                       处理人
                       TEXT,
                       path
                       TEXT,
                       处理备注
                       TEXT
                   )
                   """)
    conn.commit()

    # 读取历史记录并判断
    history_pd = pd.read_sql_query("SELECT * FROM sixiang_weifa", conn)
    data_time = datetime.strptime(data["发生时间"], "%Y%m%d_%H%M%S")

    if not history_pd.empty:
        history_pd["发生时间"] = pd.to_datetime(history_pd["发生时间"], format="%Y%m%d_%H%M%S", errors="coerce")
        time_diff = timedelta(hours=chongfu_hours)

        # 筛选同地点、同违法类型，且在防抖时间内
        filtered_df = history_pd[
            (history_pd["发生地点"] == data["发生地点"]) &
            (history_pd["违法类型"] == data["违法类型"]) &
            ((history_pd["发生时间"] - data_time).abs() <= time_diff)
            ]

        if not filtered_df.empty:
            conn.close()
            return False  # 近期已经上报过，拦截！

    # ==========================================
    # 如果没报过，准备写入 sixiang_weifa 表记账
    # ==========================================
    sqlite_data = data.copy()
    sqlite_data.pop('other_data', None)

    # ⚠️ 关键容错：由于堆放物品传入的 data 可能带 "框位置"，而 sixiang_weifa 没有这个列
    # 我们在写入前必须剔除掉不在表结构里的列，否则会报错 "table has 8 columns but 9 values were supplied"
    sqlite_data.pop('框位置', None)

    placeholders = ', '.join(['?'] * len(sqlite_data))
    keys = ', '.join(sqlite_data.keys())
    values = list(sqlite_data.values())

    def safe_sql_value(v):
        if isinstance(v, (dict, list)):
            return json.dumps(v, ensure_ascii=False)
        elif isinstance(v, (np.integer, np.floating)):
            return v.item()
        elif pd.isna(v):
            return None
        return v

    safe_values = [safe_sql_value(v) for v in values]
    cursor.execute(f"INSERT INTO sixiang_weifa ({keys}) VALUES ({placeholders})", safe_values)
    conn.commit()
    conn.close()

    return True  # 记录成功，允许发送

# 从文本中安全解析出 [xmin, ymin, xmax, ymax] 的边框数据
def safe_json_parse(output_text):
    print("大模型返回值：", output_text)
    if isinstance(output_text, dict):
        # 已经是字典了，直接返回
        return output_text
    if isinstance(output_text, str):
        output_text = output_text.strip()

        # 提取所有完整的 [..., ..., ..., ...] 结构
        boxes = re.findall(r'\[\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\]', output_text)

        # 重新构建 JSON
        if boxes:
            valid_json = f'{{"result": "yes", "bounding_boxes": [{",".join(boxes)}]}}'
            try:
                return json.loads(valid_json)
            except json.JSONDecodeError:
                pass

    # 默认返回
    return {"result": "no", "bounding_boxes": []}
# 在图像上绘制边框
def draw_bounding_boxes(image, bounding_boxes, outline_color="red", line_width=3):
    draw = ImageDraw.Draw(image)
    for box in bounding_boxes:
        try:
            xmin, ymin, xmax, ymax = box
            draw.rectangle([xmin, ymin, xmax, ymax], outline=outline_color, width=line_width)
        except Exception as e:
            # 可选打印调试信息
            # print(f"Error drawing box {box}: {e}")
            continue  # 跳过当前出错的框
    return image

# 将缩放后的框坐标还原到原图尺度
def rescale_bounding_boxes(bounding_boxes, original_width, original_height, scaled_width=1000, scaled_height=1000):
    x_scale = original_width / scaled_width
    y_scale = original_height / scaled_height
    rescaled_boxes = []
    for box in bounding_boxes:
        xmin, ymin, xmax, ymax = box
        rescaled_box = [
            xmin * x_scale,
            ymin * y_scale,
            xmax * x_scale,
            ymax * y_scale
        ]
        rescaled_boxes.append(rescaled_box)
    return rescaled_boxes

def jiance_imgtype(frame):
    # 情况1: 是字符串（路径）
    if isinstance(frame, str):
        if os.path.isfile(frame) and frame.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
            image_list = [frame]
        else:
            print(f"无效图像路径: {frame}")
            return  # 或 raise

    # 情况2: 是单个 PIL Image
    elif isinstance(frame, Image.Image):
        image_list = [frame]

    # 情况3: 是图像列表（路径或 PIL Image）
    elif isinstance(frame, (list, tuple)):
        image_list = []
        for item in frame:
            if isinstance(item, str) and os.path.isfile(item) and item.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                image_list.append(item)
            elif isinstance(item, Image.Image):
                image_list.append(item)
            else:
                print(f"跳过无效图像项: {item}")

    # 情况4: None 或其他无效类型
    else:
        print(f"无法处理的输入类型: {type(frame)}, 值: {frame}")
        return  # 安静退出，不报错

    if not image_list:
        print("未找到有效图像，跳过处理")
        return

    print(f"发现 {len(image_list)} 个图像需要处理...")
    return image_list