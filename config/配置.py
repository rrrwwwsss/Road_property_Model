import os

"""系统运行配置。

说明：
1. 本文件仅保留当前项目运行所需配置项。
2. 已删除历史测试示例列表与冗余注释，降低维护成本。
3. 变量名保持不变，兼容现有业务模块导入方式。
"""

# -----------------------------
# 视频平台与模型服务
# -----------------------------

# 监控平台接口地址
BASE_URL = "https://10.212.160.158:8101/nvms8100/apploginVideo"

# 监控平台账号
USER_NAME = "bhwfxm05"
USER_PWD = "c6QKJrTtuT"

# 联通多模态模型接口
LIANTONG_MODEL = "http://192.168.0.161:1025/v1/chat/completions"

# （保留兼容）历史模型服务地址，当前主流程未直接使用
MODEL_SERVE_URL = "http://htc-qwen2vl:8000/generate"


# -----------------------------
# 本地/容器路径配置
# -----------------------------

# Linux 真实图片根路径（用于上报时拼接外部可访问路径）
LINUX_PIC_PAT = "/data1/qwen2v/pic/"

# 容器内数据根目录
DATA_BASE_PATH = "/app/pic"

# 临时去重数据库
TEMPORARY_RECORD = DATA_BASE_PATH + "/database/wupin_tanwei_dabt.db"

# 各类结果图片目录
YUANTU_PATH = DATA_BASE_PATH + "/yuantu"
WUPIN_PATH = DATA_BASE_PATH + "/wupin"
BAITAN_PATH = DATA_BASE_PATH + "/baitan"
GONGBIAO_PATH = DATA_BASE_PATH + "/gongbiao"
WAJUE_PATH = DATA_BASE_PATH + "/wajue"
JINGGAI_PATH = DATA_BASE_PATH + "/jinggai"
XVANGUA_PATH = DATA_BASE_PATH + "/xuangua"

# （保留兼容）多帧目录
DUOZHEN_PATH = DATA_BASE_PATH + "/duozhen"


# -----------------------------
# 摄像头点位与图片接口
# -----------------------------

# 点位源文件（首次生成 camera_id 映射时使用）
CAMERA_DATA = "./data/《视频点位确认表》0620.xlsx"

# 点位映射结果缓存
CAMERA_RESULT_DATA = "./data/result_with_camera_id.csv"

# 悬挂物掩膜区域配置
XVANGUA_TICHU = "./data/悬挂物剔除区域.csv"

# 图片切片数据库
IMAGE_DB = "/app/qiepian/image_information.db"

# 图片服务接口
IMAGE_API = "http://10.212.160.162:18000"

# 本地切片目录
IMAGE_QIEPIAN_PATH = "/app/screenshots/"

# 结果 CSV 路径：
# - RESULT_CSV_PATH: 识别结果写入文件
# - RESULT_WITH_MODEL_OUTPUT_CSV_PATH: 带模型原始输出的识别结果写入文件
# - PUSH_CSV_PATH: 定时推送进程读取文件
# 说明：
# - 容器默认使用 /app/road_property_rightsmodel 下的路径，和你当前挂载保持一致。
# - 本地运行时默认使用项目根目录下同名文件。
RESULT_CSV_PATH = os.getenv(
    "RESULT_CSV_PATH",
    "/app/road_property_rightsmodel/result.csv"
    if os.path.isdir("/app")
    else "result.csv",
)

RESULT_WITH_MODEL_OUTPUT_CSV_PATH = os.getenv(
    "RESULT_WITH_MODEL_OUTPUT_CSV_PATH",
    "/app/road_property_rightsmodel/result_with_model_output.csv"
    if os.path.isdir("/app")
    else "result_with_model_output.csv",
)

PUSH_CSV_PATH = os.getenv(
    "PUSH_CSV_PATH",
    "/app/road_property_rightsmodel/Copy of result.csv"
    if os.path.isdir("/app")
    else "Copy of result.csv",
)

# -----------------------------
# 许可库配置
# -----------------------------

XVKE_DB_CONFIG = {
    "host": "172.26.57.210",
    "port": 5236,
    "user": "GLLWFXM",
    "password": "zfzdqzj@123456,.",
}


# -----------------------------
# 业务策略参数
# -----------------------------

# 重复告警抑制时间（小时）
CHONGFU_TIME = 360




