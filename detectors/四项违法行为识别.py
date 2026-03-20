from detectors.公共方法 import safe_json_parse
from services.整合数据 import get_data
import os
from PIL import Image

from detectors.给图像打马赛克 import apply_mosaic_on_polygon
from config.配置 import CHONGFU_TIME, LINUX_PIC_PAT, TEMPORARY_RECORD, XVANGUA_TICHU
# 统一复用：写库、框校验、图片落盘，避免三份脚本重复维护。
from detectors.detection_common import (
    handle_sixiang_write_and_upload,
    load_polygon_points_from_csv,
    save_detection_images,
    validate_boxes,
    write_dict_to_sqlite,
)
from services.查询许可数据库 import job
def write_to_sqlite(data):
    # 重构后统一走公共写库逻辑，保留原函数名以兼容现有调用。
    write_dict_to_sqlite(
        db_path=TEMPORARY_RECORD,
        table_name="sixiang_weifa",
        data=data,
    )

def write_to_csv(data):
    """统一使用公共去重/许可校验逻辑处理写入与上报。"""
    uploaded = handle_sixiang_write_and_upload(
        data=data,
        db_path=TEMPORARY_RECORD,
        chongfu_time_hours=CHONGFU_TIME,
        query_permissions_fn=job,
        write_to_sqlite_fn=write_to_sqlite,
        upload_data_fn=get_data,
    )
    if not uploaded:
        return "8小时内已上传过该行为"

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

    # 检查有效输入
    if not image_list:
        print(f"错误：未找到有效图像数据（支持格式：{', '.join(image_extensions)}）")
        return

    print(f"发现 {len(image_list)} 个图像需要处理...")

    # 处理每个图像
    matched_count = 0
    for idx, (image_data) in enumerate(image_list, 1):
        if not isinstance(image_data, Image.Image):
            # 如果不是 PIL 图像，记录错误并跳过该图像
            print(f"图像不是有效的 PIL 图像对象")
            return  # 跳过当前迭代，继续下一个图像

        print(f"\n处理第 {idx}/{len(image_list)} 个图像...")
        print('点位名称：',monitor_point)
        try:
            if action_name == '遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全':
                # 读取当前点位的遮罩区域，命中则先马赛克再识别。
                points = load_polygon_points_from_csv(XVANGUA_TICHU, monitor_point)
                if points:
                    image = apply_mosaic_on_polygon(the_path,points,5)
                else:
                    image = image_data
            else:
                image = image_data
        except Exception as e:
            image = image_data

        # 调用模型识别模块输入提示词进行图像的识别，返回识别结果output_text
        from services.模型识别_docker import pattern_recognition
        output_text = pattern_recognition(question, image)

        result_dict = safe_json_parse(output_text)
        # 重构后统一使用公共框校验规则。
        result_dict = validate_boxes(result_dict)
        final_answer = result_dict.get("result", "不存在")
        print(f"检测结果：{final_answer}")

        # 处理阳性结果
        if final_answer == "yes":

            # 生成时间戳文件名
            timestamp = action_time
            filename = f"camera_{camera_id}_{timestamp}.jpg"
            normalized_boxes = result_dict.get("bounding_boxes")
            if not normalized_boxes:
                print("没有 bounding_boxes，直接跳出循环")
                break
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
                'other_data': other_data,
            }
            write_to_csv(data)
    print("\n处理完成。")
    print(f"共发现 {matched_count} 个符合检测条件的图像")
    print(f"结果保存路径：{os.path.abspath(output_folder)}")
    return '成功'










