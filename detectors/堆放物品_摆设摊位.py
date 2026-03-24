from detectors.公共方法 import *
from services.整合数据 import get_data
from datetime import timedelta
import os
import json
import pandas as pd
from services.从数据库获取图片 import *
# 设置显示所有行和列
pd.set_option('display.max_rows', None)       # 显示所有行
pd.set_option('display.max_columns', None)    # 显示所有列
pd.set_option('display.width', 1000)          # 设置横向宽度，避免换行
pd.set_option('display.max_colwidth', None)   # 显示所有列内容，尤其是长字符串


# 判断化的框是否是相同的函数
# IOU 计算函数
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

# 判断所有框是否都匹配
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
    sqlite_data = data.copy()  # 👈 关键修改在这里！
    sqlite_data.pop('other_data', None)
    conn = sqlite3.connect(TEMPORARY_RECORD)
    cursor = conn.cursor()

    placeholders = ', '.join(['?'] * len(sqlite_data))
    keys = ', '.join(sqlite_data.keys())
    values = list(sqlite_data.values())
    # 把传入数据库的值转化为安全的字符串
    def safe_sql_value(v):
        import numpy as np
        import pandas as pd
        if isinstance(v, (dict, list)):
            return json.dumps(v, ensure_ascii=False)  # 转为 JSON 字符串
        elif isinstance(v, (np.integer, np.floating)):
            return v.item()
        elif pd.isna(v):
            return None
        return v

    safe_values = [safe_sql_value(v) for v in values]
    cursor.execute(f"INSERT INTO wupin_tanwei ({keys}) VALUES ({placeholders})", safe_values)#placeholders：占位符字符串，表示参数位,用？表示。 safe_values：实际的值，传给 ?
    conn.commit()
    conn.close()
def write_to_csv(data):

    # 创建SQLite数据库,存储临时监测数据
    conn = sqlite3.connect(TEMPORARY_RECORD)
    cursor = conn.cursor()

    # 如果表不存在则创建
    cursor.execute("""
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
    """)
    conn.commit()


    # 读取堆放物品摆摊两个违法行为临时 SQLite 数据库表
    wupin_tanwei_pd = pd.read_sql_query("SELECT * FROM wupin_tanwei", conn)
    #TODO 1.筛选发生地点、违法类型一致的元组
    wupin_tanwei_pd = wupin_tanwei_pd[wupin_tanwei_pd["发生地点"] == data["发生地点"]]

    # print("发生地点一致的行：",wupin_tanwei_pd)
    if wupin_tanwei_pd.empty:
        print("没有发生地点一致的记录")
        # 写入临时文件
        write_to_sqlite(data)
        return "文件已写入临时表"

    wupin_tanwei_pd = wupin_tanwei_pd[wupin_tanwei_pd["违法类型"] == data["违法类型"]]

    # print("违法类型一致的行：",wupin_tanwei_pd)
    if wupin_tanwei_pd.empty:
        print("没有违法类型一致的记录")
        # 写入临时文件
        write_to_sqlite(data)
        return "文件已写入临时表"
    #TODO 2.筛选符合同样物品或摊位的元组（按照框的位置判断 90%覆盖）
    matched_rows = []
    for idx, row in wupin_tanwei_pd.iterrows():
        try:
            prev_boxes = json.loads(row["框位置"])  # json.loads可以解析字符串为列表
            if all_boxes_match(data["框位置"], prev_boxes):
                matched_rows.append(row)
        except Exception as e:
            print(f"解析错误 in row {idx}: {e}")

    # 输出匹配结果
    matched_df = pd.DataFrame(matched_rows)
    print("地点、框位置一致的行：",matched_df)
    # 如果没有符合条件的行，直接返回
    if matched_df.empty:
        print("没有框位置一致的记录")
        # 写入临时文件
        write_to_sqlite(data)
        return "文件已写入临时表"
    #TODO 3.筛选出符合时间的元组
    time = datetime.strptime(data["发生时间"], "%Y%m%d_%H%M%S")

    # 加载你的 DataFrame
    df = matched_df

    # 解析“发生时间”列为 datetime
    df["发生时间_dt"] = pd.to_datetime(df["发生时间"], format="%Y%m%d_%H%M%S", errors="coerce")
    hours = 48
    # 筛选与 time 相差不超过 24 小时的元组（绝对差值）
    df_filtered = df[df["发生时间_dt"].apply(lambda t: abs(t - time) <= timedelta(hours=hours))].copy()

    # 如果没有符合条件的行，直接返回
    if df_filtered.empty:
        print(f"没有在{hours}小时内的记录")
        # 写入临时文件
        write_to_sqlite(data)
        return "文件已写入临时表"
    else:
        # 计算所有时间与基准 time 的差值（单位：小时）
        df_filtered["时间差_小时"] = df_filtered["发生时间_dt"].apply(lambda t: abs((t - time).total_seconds()) / 3600)

        # 找出最大时间差
        max_diff = df_filtered["时间差_小时"].max()

        print("最大时间差（小时）:", max_diff)
        if max_diff > 1:
            print(f"存在距离超过{max_diff}小时的记录 ✅")
            print('历史记录：',df_filtered)
            print('最新抓拍到的堆物/摆摊记录：', pd.DataFrame([data]))
            df_filtered = pd.concat([df_filtered, pd.DataFrame([data])], ignore_index=True)#data是一个字典，所以要把这个字典放进列表里，这样才会被识别成一条记录，新增1行。
            # 删除不需要的列
            df_filtered = df_filtered.drop(
                columns=[col for col in ["框位置", "时间差_小时", "发生时间_dt"] if col in df_filtered.columns])

            print("最终的该行为的历史记录表：",df_filtered)
            print("共计行数：", len(df_filtered))

            print("开始往太极传数据")
            for _, row in df_filtered.iterrows():
                item = {
                    "工单编号": row.get("工单编号", ""),
                    "违法类型": row.get("违法类型", ""),
                    "发生地点": row.get("发生地点", ""),
                    "发生时间": row.get("发生时间", ""),
                    "处理状态": row.get("处理状态", ""),
                    "处理人": row.get("处理人", ""),
                    "path": row.get("path", ""),
                    "处理备注": row.get("处理备注", "")
                }
                print("正在处理：",item)
                # 👇 这里加上防重复上报的公共方法闸门
                if check_and_log_sixiang_weifa(item, TEMPORARY_RECORD, CHONGFU_TIME):
                    get_data(item)
                    print("✅ 未发现重复，成功推送到太极")
                else:
                    print(f"❌ 拦截推送：{CHONGFU_TIME}小时内已上报过地点 [{item['发生地点']}] 的堆放物品行为。")
                break  # 终止循环，只执行一次


            # 读取SQLite 的数据（如果还没读）
            conn = sqlite3.connect(TEMPORARY_RECORD)
            cursor = conn.cursor()
            # 删掉数据库所有相关条目
            for gid in df_filtered["工单编号"]:
                cursor.execute("DELETE FROM wupin_tanwei WHERE 工单编号 = ?", (gid,))
            conn.commit()
            conn.close()

            return "临时存放数据库已更新"
        else:
            print("所有记录距离都在 4 小时以内 ❌")
            write_to_sqlite(data)
            return "文件已写入临时表"


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
    # if isinstance(the_path, (Image.Image, np.ndarray)):
    #     image_list.append((the_path, None))  # 仅存储图像数据
    # elif isinstance(the_path, str):
    #     if os.path.isdir(the_path):
    #         for f in os.listdir(the_path):
    #             ext = os.path.splitext(f)[1].lower()
    #             if ext in image_extensions:
    #                 image_list.append((None, os.path.join(the_path, f)))
    #     elif os.path.isfile(the_path):
    #         ext = os.path.splitext(the_path)[1].lower()
    #         if ext in image_extensions:
    #             image_list.append((None, the_path))
    #     else:
    #         raise ValueError(f"路径不存在：{the_path}")
    # else:
    #     raise TypeError("输入类型必须是路径或图像对象")

    # 检查有效输入
    if not image_list:
        print(f"错误：未找到有效图像数据（支持格式：{', '.join(image_extensions)}）")
        return

    print(f"发现 {len(image_list)} 个图像需要处理...")

    # 处理每个图像
    matched_count = 0
    for idx, (image_data) in enumerate(image_list, 1):
        print(f"\n处理第 {idx}/{len(image_list)} 个图像...")
        # # 加载图像
        if not isinstance(image_data, Image.Image):
            # 如果不是 PIL 图像，记录错误并跳过该图像
            print(f"图像不是有效的 PIL 图像对象")
            return  # 跳过当前迭代，继续下一个图像

        # 如果已经确认 image_data 是 PIL 图像，则直接使用
        image = image_data
        # 调用模型识别模块输入提示词进行图像的识别，返回识别结果output_text
        from services.模型识别_docker import pattern_recognition
        output_text = pattern_recognition(question,image)
        # # 构建消息
        # messages = [
        #     {
        #         "role": "user",
        #         "content": [
        #             {"type": "image", "image": image},
        #             {"type": "text", "text": question}
        #         ]
        #     }
        # ]
        # from 模型识别 import pattern_recognition
        # output_text = pattern_recognition(model,processor,messages)
        result_dict = safe_json_parse(output_text)
        final_answer = result_dict.get("result", "不存在")
        print('监控点位:', monitor_point)
        print(f"检测结果：{final_answer}")
        # 尝试解析 JSON

        # result_dict = json.loads(output_text)
        # final_answer = result_dict.get("result", "no")
        # print(f"检测结果：{final_answer}")

        # 处理阳性结果
        if final_answer == "yes":
            # current_time = datetime.now()
            # future_time = current_time + timedelta(minutes=10, seconds=52)
            # 生成时间戳文件名
            timestamp = action_time
            filename = f"camera_{camera_id}_{timestamp}.jpg"
            output_path = os.path.join(output_folder, filename)

            # 保存这个没标框的违法图像
            # 假设 image 是你的PIL Image对象
            save_dir = './shibie_yuantu/' + output_folder.rsplit('/', 1)[-1]  # 提取出违法行为保存的路径

            # 判断文件夹是否存在，不存在就创建
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # 拼接保存路径，文件名可以自己定，比如用“output.png”
            save_path = os.path.join(save_dir, filename)

            # 保存图片
            image.save(save_path)
            print(f"图片已保存到 {save_path}")

            # 绘制边界框
            original_width, original_height = image.size
            normalized_boxes = result_dict.get("bounding_boxes", [])
            rescaled_boxes = rescale_bounding_boxes(
                normalized_boxes,
                original_width,
                original_height
            )
            # rescaled_boxes是根据大模型返回的1000*1000标准坐标处理得到的原始坐标，但72b大模型不会返回1000*1000的标准坐标，只返回原始坐标，
            # 因此使用72b大模型时不用转换，直接使用normalized_boxes
            output_image = draw_bounding_boxes(image, normalized_boxes)


            output_image.save(output_path)
            # 提取出linux实际的存储路径（不是dockers路径）
            last_part = os.path.basename(output_folder)
            output_path = os.path.join(LINUX_PIC_PAT + last_part, filename)
            print(f"★ 堆放物品、摆设摊位发现目标，已保存至临时文件：{output_path}")
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
                "框位置": normalized_boxes,
                'other_data': other_data,
            }
            print(write_to_csv(data))
    print("\n处理完成。")
    print(f"共发现 {matched_count} 个符合检测条件的图像")
    print(f"结果保存路径：{os.path.abspath(output_folder)}")
    return '成功'
# def poll_cameras1(camera_list, action, output_folder):
#     """
#     轮询监控摄像头并处理图像。
#
#     参数：
#         camera_list (list): 包含摄像头信息的列表，每个元素是一个字典，包含以下键：
#             - "camera_id": 摄像头 ID。
#             - "monitor_point": 监控点名称。
#         action {key:value}: key:违法行为名称  value当前需要处理违法行为的描述。
#         output_folder (str): 输出文件夹路径，用于保存处理后的图像。
#     """
#     print("\n堆放物品、摆设摊位识别...")
#
#     for camera in camera_list:
#         camera_id = camera.get("camera_id")
#         monitor_point = camera.get("monitor_point")
#         if not camera_id or not monitor_point:
#             print(f"跳过无效的摄像头配置: {camera}")
#             continue
#
#         frame = process_violations(list(action.keys())[0], camera_id)
#         if frame == None:
#             print(f"{camera_id}点位没有图片")
#             continue
#         process_images(frame, action, output_folder=output_folder,monitor_point=monitor_point,camera_id = camera_id)
        # 处理图像并保存到指定输出文件夹
    # process_images("./图片", action,model=model,processor=processor, output_folder=output_folder, monitor_point="G101京沈线K39+350下行富各庄")