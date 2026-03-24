import ast
import json

import pandas as pd

from 公共方法 import *
from services.整合数据 import get_data
from datetime import timedelta
import os

from 给图像打马赛克 import apply_mosaic_on_polygon
from services.查询许可数据库 import job
from services.从数据库获取图片 import *

def write_to_csv(data):
    # 【第一关：合法性校验】 查达梦许可库
    try:
        query_results = job()

        if data["违法类型"] == "擅自占用、挖掘公路":
            matched_addresses = [
                item for item in query_results.get("zhanwagonglu", [])
                if item.get("constructaddress") == data["发生地点"]
            ]
            if matched_addresses:
                print("已经有许可信息，合法，不是违法行为，中止上报")
                return None

        elif data["违法类型"] == "在公路用地范围内设置公路标志以外的其他标志":
            matched_addresses = [
                item for item in query_results.get("feigongbiao", [])
                if item.get("constructaddress") == data["发生地点"]
            ]
            if matched_addresses:
                print("已经有许可信息，合法，不是违法行为，中止上报")
                return None
    except Exception as e:
        print(f"校验许可 query_results 出错: {e}")
    # 【第二关：防重复上报校验】 查本地 SQLite
    # 👇 直接调用公共方法
    if check_and_log_sixiang_weifa(data, TEMPORARY_RECORD, CHONGFU_TIME):
        print("开始往太极传数据")
        get_data(data)
    else:
        msg = f"{CHONGFU_TIME}小时内已上传过该行为"
        print(msg)
        return msg
def process_images(
        the_path,
        action,
        monitor_point,
        output_folder="output",
        camera_id="",
        action_time = '未知',
        other_data = None,
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
    if other_data is None:
        other_data = []
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
        # # 加载图像
        if not isinstance(image_data, Image.Image):
            # 如果不是 PIL 图像，记录错误并跳过该图像
            print(f"图像不是有效的 PIL 图像对象")
            return  # 跳过当前迭代，继续下一个图像

        print(f"\n处理第 {idx}/{len(image_list)} 个图像...")

        def get_points_from_csv(csv_path, target_location):
            # 读取 CSV 文件
            df = pd.read_csv(csv_path)

            # 查找目标位置的行
            target_row = df[df['点位'] == target_location]  # 假设列名是 '位置'

            if not target_row.empty:
                # 获取 '区域' 列的值（假设列名是 '区域'）
                region_str = target_row['区域'].values[0]

                # 将字符串转换为 Python 列表
                points = ast.literal_eval(region_str)
                return points
            else:
                print(f"未找到指定位置: {target_location}")
                return None
        print('点位名称：',monitor_point)
        try:
            if action_name == '遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全':
                points = get_points_from_csv(XVANGUA_TICHU, monitor_point)
                if points:
                    image = apply_mosaic_on_polygon(the_path,points,5)
                else:
                    image = image_data
            else:
                image = image_data
        except Exception as e:
            print(f"打马赛克时发生错误: {e}")  # ✅ 打印出错误，排查是格式问题还是坐标问题
            image = image_data

        # 调用模型识别模块输入提示词进行图像的识别，返回识别结果output_text
        from services.模型识别_docker import pattern_recognition
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

            # 绘制边界框
            original_width, original_height = image.size
            normalized_boxes = result_dict.get("bounding_boxes")

            if not normalized_boxes:
                print("没有 bounding_boxes，直接跳出循环")
                break
            rescaled_boxes = rescale_bounding_boxes(
                normalized_boxes,
                original_width,
                original_height
            )

            # 保存这个没标框的违法图像
            # 假设 image 是你的PIL Image对象
            save_dir = './shibie_yuantu/'+output_folder.rsplit('/', 1)[-1] #提取出违法行为保存的路径

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
                'other_data': other_data,
            }
            write_to_csv(data)
    print("\n处理完成。")
    print(f"共发现 {matched_count} 个符合检测条件的图像")
    print(f"结果保存路径：{os.path.abspath(output_folder)}")
    return '成功'
# def poll_cameras(camera_list, question, output_folder):
#     """
#     轮询监控摄像头并处理图像。
#
#     参数：
#         camera_list (list): 包含摄像头信息的列表，每个元素是一个字典，包含以下键：
#             - "camera_id": 摄像头 ID。
#             - "monitor_point": 监控点名称。
#         question (str): 当前需要处理的问题类型（例如 "wajue_question"）。
#         output_folder (str): 输出文件夹路径，用于保存处理后的图像。
#     """
#     print("\n工标、井盖、悬挂物识别...")
#
#     for camera in camera_list:
#
#         camera_id = camera.get("camera_id")
#         monitor_point = camera.get("monitor_point")
#         if not camera_id or not monitor_point:
#             print(f"跳过无效的摄像头配置: {camera}")
#             continue
#
#
#         frame = process_violations(list(question.keys())[0], camera_id)
#         if frame == None:
#             print(f"{camera_id}点位没有图片")
#             continue
#         # # 获取摄像头的一帧图像
#         # frame = capture_frame_from_camera(camera_id)
#         # if frame is None:
#         #     print(f"网络问题，无法从摄像头 {camera_id} 获取图像")
#         #     continue
#
#         # 处理图像并保存到指定输出文件夹
#         process_images(frame, question, output_folder=output_folder, monitor_point=monitor_point, camera_id=camera_id)