from detectors.公共方法 import safe_json_parse
from services.整合数据 import get_data
from config.配置 import LINUX_PIC_PAT, TEMPORARY_RECORD
import sqlite3
from datetime import datetime, timedelta
import os
from PIL import Image
import json
import pandas as pd
# 统一复用：写库与图片落盘，减少重复代码。
from detectors.detection_common import write_dict_to_sqlite, save_detection_images
# IOU 计算：用于判断两次检测框是否指向同一批物体。
def compute_iou(box1, box2):
    xmin1, ymin1, xmax1, ymax1 = box1
    xmin2, ymin2, xmax2, ymax2 = box2

    inter_xmin = max(xmin1, xmin2)
    inter_ymin = max(ymin1, ymin2)
    inter_xmax = min(xmax1, xmax2)
    inter_ymax = min(ymax1, ymax2)

    inter_w = max(0, inter_xmax - inter_xmin)
    inter_h = max(0, inter_ymax - inter_ymin)
    inter_area = inter_w * inter_h

    area1 = (xmax1 - xmin1) * (ymax1 - ymin1)
    area2 = (xmax2 - xmin2) * (ymax2 - ymin2)
    union_area = area1 + area2 - inter_area

    if union_area == 0:
        return 0
    return inter_area / union_area

# 当前帧里的每个框，是否都能在历史框里找到一个高重叠匹配。
def all_boxes_match(current_boxes, previous_boxes, iou_threshold=0.5):
    for cur in current_boxes:
        matched = False
        for prev in previous_boxes:
            if compute_iou(cur, prev) >= iou_threshold:
                matched = True
                break
        if not matched:
            return False
    return True
def write_to_sqlite(data):
    # 重构后统一走公共写库逻辑，保留原函数名以兼容现有调用。
    write_dict_to_sqlite(
        db_path=TEMPORARY_RECORD,
        table_name="wupin_tanwei",
        data=data,
    )

def ensure_wupin_table(conn):
    # 初始化临时表：只在不存在时创建，不影响已有数据。
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS wupin_tanwei (
            工单编号 TEXT,
            违法类型 TEXT,
            发生地点 TEXT,
            发生时间 TEXT,
            处理状态 TEXT,
            处理人 TEXT,
            path TEXT,
            处理备注 TEXT,
            框位置 TEXT
        )
        """
    )
    conn.commit()


def filter_same_location_and_type(history_df, data):
    # 第一层去重：地点 + 违法类型一致才认为是同类事件候选。
    filtered = history_df[history_df["发生地点"] == data["发生地点"]]
    if filtered.empty:
        print("没有发生地点一致的记录")
        return filtered

    filtered = filtered[filtered["违法类型"] == data["违法类型"]]
    if filtered.empty:
        print("没有违法类型一致的记录")
    return filtered


def filter_same_boxes(candidate_df, current_boxes):
    # 第二层去重：通过历史框与当前框的 IOU 匹配，过滤“不是同一堆物体/摊位”的记录。
    matched_rows = []
    for idx, row in candidate_df.iterrows():
        try:
            prev_boxes = json.loads(row["框位置"])
            if all_boxes_match(current_boxes, prev_boxes):
                matched_rows.append(row)
        except Exception as exc:
            print(f"解析错误 in row {idx}: {exc}")

    return pd.DataFrame(matched_rows)


def filter_within_hours(matched_df, base_time, hours):
    # 第三层去重：时间窗口内才视为同一事件链。
    df = matched_df.copy()
    df["发生时间_dt"] = pd.to_datetime(df["发生时间"], format="%Y%m%d_%H%M%S", errors="coerce")
    return df[df["发生时间_dt"].apply(lambda t: abs(t - base_time) <= timedelta(hours=hours))]


def upload_first_record(df_filtered):
    # 保持原行为：仅上传一条，避免一次性推送过多重复事件。
    for _, row in df_filtered.iterrows():
        item = {
            "工单编号": row.get("工单编号", ""),
            "违法类型": row.get("违法类型", ""),
            "发生地点": row.get("发生地点", ""),
            "发生时间": row.get("发生时间", ""),
            "处理状态": row.get("处理状态", ""),
            "处理人": row.get("处理人", ""),
            "path": row.get("path", ""),
            "处理备注": row.get("处理备注", ""),
            "模型输出": row.get("模型输出", ""),
        }
        print("正在处理：", item)
        get_data(item)
        break


def delete_temp_records(conn, ids):
    # 上传后删除对应临时记录，避免下次再次命中。
    cursor = conn.cursor()
    for gid in ids:
        cursor.execute("DELETE FROM wupin_tanwei WHERE 工单编号 = ?", (gid,))
    conn.commit()


def write_to_csv(data):
    # 该函数是“是否立即上报”的总控流程：
    # 1) 先做地点/类型/框/时间的多层去重
    # 2) 命中上报条件则上传并清理临时记录
    # 3) 否则只写入临时表，等待后续帧佐证
    conn = sqlite3.connect(TEMPORARY_RECORD)
    try:
        ensure_wupin_table(conn)
        history_df = pd.read_sql_query("SELECT * FROM wupin_tanwei", conn)
        same_location_type_df = filter_same_location_and_type(history_df, data)
        if same_location_type_df.empty:
            write_to_sqlite(data)
            return "文件已写入临时表"

        matched_df = filter_same_boxes(same_location_type_df, data["框位置"])
        print("地点、框位置一致的行：", matched_df)
        if matched_df.empty:
            print("没有框位置一致的记录")
            write_to_sqlite(data)
            return "文件已写入临时表"

        event_time = datetime.strptime(data["发生时间"], "%Y%m%d_%H%M%S")
        hours = 48
        df_filtered = filter_within_hours(matched_df, event_time, hours)
        if df_filtered.empty:
            print(f"没有在{hours}小时内的记录")
            write_to_sqlite(data)
            return "文件已写入临时表"

        df_filtered["时间差_小时"] = df_filtered["发生时间_dt"].apply(
            lambda t: abs((t - event_time).total_seconds()) / 3600
        )
        max_diff = df_filtered["时间差_小时"].max()
        print("最大时间差（小时）:", max_diff)

        if max_diff <= 1:
            print("所有记录距离都在 1 小时以内，继续写入临时表")
            write_to_sqlite(data)
            return "文件已写入临时表"

        print(f"存在距离超过{max_diff}小时的记录，开始上报")
        df_filtered = pd.concat([df_filtered, pd.DataFrame([data])], ignore_index=True)
        df_filtered = df_filtered.drop(
            columns=[col for col in ["框位置", "时间差_小时", "发生时间_dt"] if col in df_filtered.columns]
        )
        print("最终的该行为的历史记录表：", df_filtered)
        print("共计行数：", len(df_filtered))

        print("开始往太极传数据")
        upload_first_record(df_filtered)
        delete_temp_records(conn, df_filtered["工单编号"])
        return "临时存放数据库已更新"
    finally:
        conn.close()


def process_images(
        the_path,
        action,
        monitor_point,
        camera_id,
        output_folder="output",
        action_time = '未知',
        other_data = None,
        image_extensions=('.jpg', '.jpeg', '.png', '.bmp', '.webp'),
):
    """
    处理图像数据（支持路径/文件夹/实时图像变量）

    Args:
        the_path: 图片路径/文件夹路径/图像对象（PIL.Image/numpy数组）
         action {key:value}: key:违法行为名称  value当前需要处理违法行为的描述。
        monitor_point: 监控点位标识符（用于文件命名）
        output_folder: 保存结果的文件夹路径（默认"output"）
        image_extensions: 支持的图片格式扩展名
    """
    action_name = list(action.keys())[0]
    # question: 自定义检测问题描述
    question = action[action_name]
    # 创建输出目录
    os.makedirs(output_folder, exist_ok=True)

    # 处理输入类型
    image_list = [the_path]

    # 检查有效输入
    if not image_list:
        print(f"错误：未找到有效图像数据（支持格式：{', '.join(image_extensions)}）")
        return

    print(f"发现 {len(image_list)} 个图像需要处理...")

    # 处理每个图像
    matched_count = 0
    for idx, (image_data) in enumerate(image_list, 1):
        print(f"\n处理第 {idx}/{len(image_list)} 个图像...")
        if not isinstance(image_data, Image.Image):
            # 如果不是 PIL 图像，记录错误并跳过该图像
            print(f"图像不是有效的 PIL 图像对象")
            return  # 跳过当前迭代，继续下一个图像

        # 如果已经确认 image_data 是 PIL 图像，则直接使用
        image = image_data
        # 调用模型识别模块输入提示词进行图像的识别，返回识别结果output_text
        from services.模型识别_docker import pattern_recognition
        output_text = pattern_recognition(question,image)

        result_dict = safe_json_parse(output_text)
        final_answer = result_dict.get("result", "不存在")
        print('监控点位:', monitor_point)
        print(f"检测结果：{final_answer}")

        # 处理阳性结果
        if final_answer == "yes":

            # 生成时间戳文件名
            timestamp = action_time
            filename = f"camera_{camera_id}_{timestamp}.jpg"
            normalized_boxes = result_dict.get("bounding_boxes", [])

            # 重构后统一图片保存逻辑（原图+标注图）。
            output_path = save_detection_images(
                image=image,
                output_folder=output_folder,
                filename=filename,
                normalized_boxes=normalized_boxes,
                linux_pic_path=LINUX_PIC_PAT,
            )
            matched_count += 1
            the_type = action_name
            data = {
                "工单编号": filename,
                "违法类型": the_type,
                "发生地点": monitor_point,
                "发生时间": timestamp,
                "处理状态": "待处理",
                "处理人": "执法员",
                "path": output_path,
                "处理备注": "无备注",
                "模型输出": output_text,
                "框位置": normalized_boxes,
                'other_data': other_data,
            }
            print(write_to_csv(data))
    print("\n处理完成。")
    print(f"共发现 {matched_count} 个符合检测条件的图像")
    print(f"结果保存路径：{os.path.abspath(output_folder)}")
    return '成功'






