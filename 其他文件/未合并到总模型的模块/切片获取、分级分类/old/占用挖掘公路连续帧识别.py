import json
import sqlite3

import pandas as pd
from services.模型识别_docker import pattern_recognition
from detectors.公共方法 import safe_json_parse, rescale_bounding_boxes, draw_bounding_boxes
from services.整合数据 import get_data
from services.摄像头截帧 import capture_frame_from_camera
from datetime import datetime, timedelta
import os
from PIL import Image
from config.配置 import *
from services.查询许可数据库 import job
def write_to_sqlite(data):
    conn = sqlite3.connect(TEMPORARY_RECORD)
    cursor = conn.cursor()

    placeholders = ', '.join(['?'] * len(data))
    keys = ', '.join(data.keys())
    values = list(data.values())
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
    cursor.execute(f"INSERT INTO sixiang_weifa ({keys}) VALUES ({placeholders})", safe_values)#placeholders：占位符字符串，表示参数位,用？表示。 safe_values：实际的值，传给 ?
    conn.commit()
    conn.close()
def write_to_csv(data):
    # 创建SQLite数据库,存储临时监测数据
    conn = sqlite3.connect(TEMPORARY_RECORD)
    cursor = conn.cursor()

    # 如果表不存在则创建
    cursor.execute("""
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
                   """)
    conn.commit()
    # 读取四项违法行为临时 SQLite 数据库表
    wupin_tanwei_pd = pd.read_sql_query("SELECT * FROM sixiang_weifa", conn)

    # 将 data["发生时间"] 转换为 datetime 类型
    data_time = datetime.strptime(data["发生时间"], "%Y%m%d_%H%M%S")

    # 假设 wupin_tanwei_pd 是一个 pandas DataFrame，包含了发生时间、发生地点、违法类型等字段
    # 需要将 wupin_tanwei_pd 中的 发生时间 转换为 datetime 类型
    wupin_tanwei_pd["发生时间"] = pd.to_datetime(wupin_tanwei_pd["发生时间"], format="%Y%m%d_%H%M%S")

    # 计算 8 小时的时间差
    time_diff = timedelta(hours=16)

    # 筛选条件：发生地点、违法类型一致，且发生时间在 8 小时以内
    filtered_df = wupin_tanwei_pd[
        (wupin_tanwei_pd["发生地点"] == data["发生地点"]) &
        (wupin_tanwei_pd["违法类型"] == data["违法类型"]) &
        # 发生时间列各元组 - data[发生时间]（datetime类型） 的绝对值要小于8
        ((wupin_tanwei_pd["发生时间"] - data_time).abs() <= time_diff)
        ]

    try:
        query_results = job()

        if data["违法类型"] == "擅自占用、挖掘公路":
            # 从 query_results['zhanwagonglu'] 中找有没有 constructaddress = data["发生地点"]
            matched_addresses = [
                item for item in query_results.get("zhanwagonglu", [])
                if item.get("constructaddress") == data["发生地点"]
            ]

            if matched_addresses:
                # 如果匹配上，则清空结果
                filtered_df = pd.DataFrame(columns=wupin_tanwei_pd.columns)
                print("已经有许可信息，不是违法行为")
            else:
                print("没有许可信息")

        elif data["违法类型"] == "在公路用地范围内设置公路标志以外的其他标志":
            # 从 query_results['feigongbiao'] 中找有没有 constructaddress = data["发生地点"]
            matched_addresses = [
                item for item in query_results.get("feigongbiao", [])
                if item.get("constructaddress") == data["发生地点"]
            ]

            if matched_addresses:
                # 如果匹配上，则清空结果
                filtered_df = pd.DataFrame(columns=wupin_tanwei_pd.columns)
                print("已经有许可信息，不是违法行为")
            else:
                print("没有许可信息")
    except Exception as e:
        print(f"校验 query_results 出错: {e}")
        # 出错也不影响后续运行

    # 如果临时数据库里没有发生地点、违法类型一致，且发生时间在 8 小时以内的行为，则执行上传逻辑
    if filtered_df.empty:
        # 定义 CSV 文件的表头
        fieldnames = ["工单编号", "违法类型", "发生地点", "发生时间", "处理状态", "处理人", "path", "处理备注"]

        # # 检查文件是否存在，如果不存在则写入表头
        # try:
        #     with open(file_path, mode='x', newline='', encoding='utf-8') as csvfile:  # 'x' 模式会创建新文件
        #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #         writer.writeheader()  # 写入表头
        # except FileExistsError:
        #     pass  # 如果文件已存在，则跳过表头写入
        # 往太极传数据
        print("开始往太极传数据")
        get_data(data)
        print("写入数据到本地")
        # # 追加写入数据
        # with open(file_path, mode='a', newline='', encoding='utf-8') as csvfile:  # 'a' 模式追加写入
        #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #     writer.writerow(data)  # 写入一行数据，data是字典
        # 写入临时数据库
        write_to_sqlite(data)
    else:
        return "8小时内已上传过该行为"
def process_images(
        cv2_img_list,
        action,
        monitor_point,
        output_folder="output",
        camera_id="",
        image_extensions=('.jpg', '.jpeg', '.png', '.bmp', '.webp')
):
    """
    处理图像数据（支持路径/文件夹/实时图像变量）

    Args:
        the_path: 图片路径/文件夹路径/图像对象（PIL.Image/numpy数组）
        question: 自定义检测问题描述
        monitor_point: 监控点位标识符（用于文件命名）
        output_folder: 保存结果的文件夹路径（默认"output"）
        image_extensions: 支持的图片格式扩展名
        camera_id : 摄像头id
    """
    action_name = list(action.keys())[0]
    # question: 自定义检测问题描述
    question = action[action_name]
    # 创建输出目录
    os.makedirs(output_folder, exist_ok=True)

    # 处理输入类型
    image_list = cv2_img_list
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
    resuly_list = []
    result_dict = {}
    image = None
    for idx, (image_data, source_path) in enumerate(image_list, 1):

        print(f"\n处理第 {idx}/{len(image_list)} 个图像...")
        # 加载图像
        if image_data is not None:
            image = image_data
        else:
            image = Image.open(source_path)

        # 调用模型识别模块输入提示词进行图像的识别，返回识别结果output_text

        output_text = pattern_recognition(question, image)

        result_dict = safe_json_parse(output_text)

        def validate_boxes(result_dict, min_width=10, min_height=10):
            """
            验证给定的边界框（bounding boxes）是否有效。
            1. 每个框的宽度和高度都需要大于等于指定的最小值（默认为 10）。
            2. 如果框的数量超过 4 个，视为无效。
            3. 如果所有框都无效，则在结果字典中设置 "result": "no"。

            参数：
            result_dict (dict): 包含边界框和其他信息的字典。
            min_width (int): 最小框宽度（默认为 10）。
            min_height (int): 最小框高度（默认为 10）。

            返回：
            dict: 更新后的结果字典，可能包含 "result": "no"。
            """
            print("模型结果：", result_dict)
            boxes = result_dict.get("bounding_boxes", [])
            all_invalid = True  # 假设一开始全都无效

            # 如果框的数量超过 4 个，立即视为无效
            if len(boxes) > 4:
                result_dict["result"] = "no"
                print("框的数量超过 4 个，已标记为 no")
                return result_dict

            for box in boxes:
                try:
                    xmin, ymin, xmax, ymax = box
                    width = xmax - xmin
                    height = ymax - ymin

                    if width >= min_width and height >= min_height:
                        all_invalid = False  # 只要有一个合法，就标记为不全无效
                        print(f"第框：{box}图像匹配成功")
                        break
                except Exception as e:
                    print(f"处理 box {box} 时出错：{e}")
                    continue  # 出错的框跳过，不影响其他框判断

            if all_invalid and boxes:  # 只有 boxes 不为空且全部都不合格才改为 no
                result_dict["result"] = "no"
                print("所有框都无效，已标记为 no")

            return result_dict
        result_dict = validate_boxes(result_dict)
        final_answer = result_dict.get("result", "不存在")
        print('监控点位:', monitor_point)
        print(f"检测结果：{final_answer}")
        resuly_list.append(final_answer)
        # 处理阳性结果
    if all(x == 'yes' for x in resuly_list):
        # 第一帧图片有对应违法行为时，再次截取一帧
        print('第一帧图片有对应违法行为时，再次截取一帧,以进行验证')
        frame2 = capture_frame_from_camera(camera_id)
        output_text = pattern_recognition(question, frame2)
        result_dict = safe_json_parse(output_text)
        # 检查这一帧是否也是占掘路，若是就继续处理，若不是就退出
        if result_dict["result"] == "no":
            print('第二张图片没有占用挖掘公路行为，程序退出')
            return ##退出
        else:
            print('第二张图片有占用挖掘公路行为，程序继续')
        current_time = datetime.now()
        future_time = current_time + timedelta(minutes=10, seconds=52)
        # 生成时间戳文件名
        timestamp = future_time.strftime("%Y%m%d_%H%M%S")
        filename = f"camera_{camera_id}_{timestamp}.jpg"
        output_path = os.path.join(output_folder, filename)

        # 绘制边界框
        original_width, original_height = image.size
        normalized_boxes = result_dict.get("bounding_boxes")

        if not normalized_boxes:
            print("没有 bounding_boxes，直接跳出循环")
        rescaled_boxes = rescale_bounding_boxes(
            normalized_boxes,
            original_width,
            original_height
        )

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
        # rescaled_boxes是根据大模型返回的1000*1000标准坐标处理得到的原始坐标，但72b大模型不会返回1000*1000的标准坐标，只返回原始坐标，
        # 因此使用72b大模型时不用转换，直接使用normalized_boxes
        # 给图像标框
        output_image = draw_bounding_boxes(image, normalized_boxes)

        # 保存结果
        # csv_file_path = RESULT_PATH
        output_image.save(output_path)
        # 提取出linux实际的存储路径（不是dockers路径）
        last_part = os.path.basename(output_folder)
        output_path = os.path.join(LINUX_PIC_PAT + last_part, filename)
        print(f"★ 发现目标，已保存至 linux存放路径：{output_path}")
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
        }
        write_to_csv(data)
    print("\n处理完成。")
    print(f"共发现 {matched_count} 个符合检测条件的图像")
    print(f"结果保存路径：{os.path.abspath(output_folder)}")

def poll_cameras2(camera_list, question, output_folder):
    """
    轮询监控摄像头并处理图像。

    参数：
        camera_list (list): 包含摄像头信息的列表，每个元素是一个字典，包含以下键：
            - "camera_id": 摄像头 ID。
            - "monitor_point": 监控点名称。
        question (str): 当前需要处理的问题类型（例如 "wajue_question"）。
        output_folder (str): 输出文件夹路径，用于保存处理后的图像。
    """
    print("\n占掘路识别...")

    for camera in camera_list:
        camera_id = camera.get("camera_id")
        monitor_point = camera.get("monitor_point")

        if not camera_id or not monitor_point:
            print(f"跳过无效的摄像头配置: {camera}")
            continue

        # 获取摄像头的一帧图像

        frames = []  # 用于保存捕获的帧


        frame = capture_frame_from_camera(camera_id)
        if frame is None:
            print(f"捕获失败（摄像头 {camera_id}）")
        else:
            frames.append((frame,None))


        print(f"共捕获 {len(frames)} 帧")
        if not frames:  # 等价于 len(frames) == 0
            print(f"网络问题，无法从摄像头 {camera_id} 获取图像")
            continue

        # 处理图像并保存到指定输出文件夹
        process_images(frames, question, output_folder=output_folder, monitor_point=monitor_point, camera_id=camera_id)