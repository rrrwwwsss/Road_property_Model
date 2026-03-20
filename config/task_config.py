"""检测任务配置。

本模块把“线程分组、行为名称、提示词、输出目录、轮询间隔”集中定义，
便于后续新增/调整任务时只改配置，不改调度代码。
"""

from config.配置 import BAITAN_PATH, GONGBIAO_PATH, JINGGAI_PATH, WAJUE_PATH, WUPIN_PATH, XVANGUA_PATH
from config.prompts import (
    BAITAN_PROMPT,
    GONGBIAO_PROMPT,
    JINGGAI_PROMPT,
    MODEL_RESULT,
    WAJUE_PROMPT,
    WUPIN_PROMPT,
    XUANGUA_PROMPT,
)


# 每个任务项字段说明：
# - display_name: 日志中的中文展示名称
# - violation_key: 传给后端接口的违法行为键（必须与后端字典一致）
# - prompt_text: 发送给模型的提示词
# - output_path: 结果图片保存目录
# - sleep_seconds: 本任务完成后等待时间
TASK_GROUPS = {
    "gaopin": [
        {
            "display_name": "擅自占用、挖掘公路",
            "violation_key": "擅自占用、挖掘公路",
            "prompt_text": WAJUE_PROMPT + MODEL_RESULT,
            "output_path": WAJUE_PATH,
            "sleep_seconds": 60,
        }
    ],
    "zhongpin": [
        {
            "display_name": "在公路上及公路用地范围内堆放物品",
            "violation_key": "在公路上及公路用地范围内堆放物品",
            "prompt_text": WUPIN_PROMPT + MODEL_RESULT,
            "output_path": WUPIN_PATH,
            "sleep_seconds": 60,
        },
        {
            "display_name": "在公路上及公路用地范围内摆摊设点",
            "violation_key": "在公路上及公路用地范围内摆摊设点",
            "prompt_text": BAITAN_PROMPT + MODEL_RESULT,
            "output_path": BAITAN_PATH,
            "sleep_seconds": 60,
        },
    ],
    "dipin": [
        {
            "display_name": "遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全",
            "violation_key": "遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全",
            "prompt_text": XUANGUA_PROMPT,
            "output_path": XVANGUA_PATH,
            "sleep_seconds": 60,
        },
        {
            "display_name": "在公路范围内擅自移动井盖",
            "violation_key": "在公路范围内擅自移动井盖",
            "prompt_text": JINGGAI_PROMPT + MODEL_RESULT,
            "output_path": JINGGAI_PATH,
            "sleep_seconds": 60,
        },
        {
            "display_name": "在公路用地范围内设置公路标志以外的其他标志",
            "violation_key": "在公路用地范围内设置公路标志以外的其他标志",
            "prompt_text": GONGBIAO_PROMPT,
            "output_path": GONGBIAO_PATH,
            "sleep_seconds": 60,
        },
    ],
}

