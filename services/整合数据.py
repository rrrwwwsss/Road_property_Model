import csv
import os

from config.数据库配置 import AUTHORITY_CODE, IMG_URL, TJ_NAME_LIST, VIOLATION_DICT
from config.配置 import RESULT_WITH_MODEL_OUTPUT_CSV_PATH
from services.提交数据库 import insert_database


def get_data(model_data):
    # 获取辖区编码：部分历史流程没有 other_data，统一兜底。
    print(model_data)
    other_data = model_data.get("other_data") or {}
    unit_code = other_data.get("area_number")
    print("辖区编码:", unit_code)
    try:
        unit_code = str(int(float(unit_code)))
    except (ValueError, TypeError):
        unit_code = "未知"

    # 数据库提交字段（保持历史结构不变）。
    submit_data = {
        "TJ_NAME": TJ_NAME_LIST[model_data["违法类型"]],
        "MEASURE": AUTHORITY_CODE[model_data["违法类型"]],
        "UNIT_CODE": unit_code,
        "工单编号": model_data["工单编号"],
        "违法类型": model_data["违法类型"],
        "发生地点": model_data["发生地点"],
        "发生时间": model_data["发生时间"],
        "图片路径": IMG_URL + model_data["path"].replace("/data1/qwen2v/pic/", ""),
        "OffsiteRule_id": VIOLATION_DICT[model_data["违法类型"]],
    }

    # 新版 CSV 备份字段：新增“模型输出”列，便于追溯每次判定的原始回答。
    backup_data = dict(submit_data)
    backup_data["模型输出"] = model_data.get("模型输出", "")

    csv_path = RESULT_WITH_MODEL_OUTPUT_CSV_PATH
    fieldnames = list(backup_data.keys())
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        else:
            with open(csv_path, mode="r", encoding="utf-8-sig") as fr:
                reader = csv.reader(fr)
                try:
                    header = next(reader)
                    if header != fieldnames:
                        raise ValueError("CSV 文件表头不一致")
                except StopIteration:
                    writer.writeheader()
        writer.writerow(backup_data)

    print("传入提交数据库模块数据:", submit_data)
    allowed_violations = [
        "遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全",
        "在公路范围内擅自移动井盖",
        "在公路用地范围内设置公路标志以外的其他标志",
    ]
    if model_data["违法类型"] not in allowed_violations:
        insert_database(submit_data)
