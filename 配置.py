# 服务器相关配置
BASE_URL = "https://10.212.160.158:8101/nvms8100/apploginVideo" #监控摄像头地址
USER_NAME = "bjjzdx"
USER_PWD = "ZFZDwxglwf@2025"
# 数据存储相关配置
LINUX_PIC_PAT = "/data1/qwen2v/pic/" # linux里数据存储基础路径
DATA_BASE_PATH = "/app/pic" # 容器里数据存储基础路径
TEMPORARY_RECORD = DATA_BASE_PATH + "/database/wupin_tanwei_dabt.db"  # 视频信息数据库文件名
YUANTU_PATH = DATA_BASE_PATH + "/yuantu"
WUPIN_PATH = DATA_BASE_PATH + "/wupin"
BAITAN_PATH = DATA_BASE_PATH + "/baitan"
GONGBIAO_PATH = DATA_BASE_PATH + "/gongbiao"
WAJUE_PATH = DATA_BASE_PATH + "/wajue"
JINGGAI_PATH = DATA_BASE_PATH + "/jinggai"
XVANGUA_PATH = DATA_BASE_PATH + "/xuangua"
RESULT_PATH = "/app/result.csv"
CAMERA_DATA = "./data/《视频点位确认表》 0620.xlsx" # 摄像头点位信息，相对路径
CAMERA_RESULT_DATA = "./data/result_with_camera_id.csv"# 整合数据后的摄像头点位信息，相对路径
# 模型服务
MODEL_SERVE_URL = "http://htc-qwen2vl:8000/generate"  # qwen2vl服务地址

# 摄像头列表
# 示例数据

# wajue_list = [
#     {"camera_id": 11000000001317480152, "monitor_point": "G101京沈线K22+290上行火神营交调站"},
#     {"camera_id": 11000000001317193402, "monitor_point": "G101京沈线K39+350下行富各庄"},
#     {"camera_id": 11000000001314706001, "monitor_point": "S201通顺路K22+000上行燕京桥下"},
#     {"camera_id": 11000000001319399586, "monitor_point": "S203顺密路K17+400下行木林道班"},
#     {"camera_id": 11000000001316185552, "monitor_point": "S214壁富路K8+900上行机场专线"},
#     {"camera_id": 11000000001313053014, "monitor_point": "S321顺沙路K15+100下行高白路口西"},
#     {"camera_id": 11000000001313113338, "monitor_point": "S332龙塘路K10+150下行苏庄闸桥西"},
#     {"camera_id": 11000000001314819953, "monitor_point": "X021木燕辅线K3+700马庄检查站 (出京)"},
#     {"camera_id": 11000000001319753987, "monitor_point": "X213木邵路K6+700上行龙尹路口西"},
#     {"camera_id": 11000000001313023975, "monitor_point": "G234兴阳线K102+460黑龙潭"},
#     {"camera_id": 11000000001313731852, "monitor_point": "S204密三路K0+010汽车站路口"},
#     {"camera_id": 11000000001312966376, "monitor_point": "G103京滨线K24+680张采路口"},
#
# ]

# gongbiao_list = [
#     {"camera_id": 11000000001314788804, "monitor_point": "X013京榆旧线K2+815结核泵站"},
#     {"camera_id": 11000000001312735597, "monitor_point": "X038庞安路K2+300京九铁路西"},
#     {"camera_id": 11000000001314375767, "monitor_point": "S209石担路K9+900龙泉雾村"},
#     {"camera_id": 11000000001315378966, "monitor_point": "G109京拉线K87+600新高铺"},
#     {"camera_id": 11000000001317193402, "monitor_point": "G101京沈线K39+350下行富各庄"},
#     {"camera_id": 11000000001314706001, "monitor_point": "S201通顺路K22+000上行燕京桥下"},
#     {"camera_id": 11000000001316185552, "monitor_point": "S214壁富路K8+900上行机场专线"},
#     {"camera_id": 11000000001313113338, "monitor_point": "S332龙塘路K10+150下行苏庄闸桥西"},
#     {"camera_id": 11000000001319753987, "monitor_point": "X213木邵路K6+700上行龙尹路口西"},
#     {"camera_id": 11000000001313033622, "monitor_point": "S203顺密路K32+175建材市场西口 密云方向"},
# ]

# jinggai_list = [
#     {"camera_id": 11000000001318667757, "monitor_point": "S229通怀路K5+380运河东大街路口东南侧03"},
# ]

# xuangua_list = [
#     {"camera_id": 11000000001314991452, "monitor_point": "X202左堤路K15+200潮河新桥"},
#     {"camera_id": 11000000001316165898, "monitor_point": "S205密关路K11+925溪翁庄"},
#     {"camera_id": 11000000001319149035, "monitor_point": "X202左堤路K31+700单平路路北 顺义方向"}
# ]

duifang_list = [
    {"camera_id": 11000000001317480152, "monitor_point": "G101京沈线K22+290上行火神营交调站"},
    {"camera_id": 11000000001317193402, "monitor_point": "G101京沈线K39+350下行富各庄"},
    {"camera_id": 11000000001314706001, "monitor_point": "S201通顺路K22+000上行燕京桥下"},
    {"camera_id": 11000000001319399586, "monitor_point": "S203顺密路K17+400下行木林道班"},
    {"camera_id": 11000000001316185552, "monitor_point": "S214壁富路K8+900上行机场专线"},
    {"camera_id": 11000000001313053014, "monitor_point": "S321顺沙路K15+100下行高白路口西"},
    {"camera_id": 11000000001313113338, "monitor_point": "S332龙塘路K10+150下行苏庄闸桥西"},
    {"camera_id": 11000000001314819953, "monitor_point": "X021木燕辅线K3+700马庄检查站 (出京)"},
    {"camera_id": 11000000001319753987, "monitor_point": "X213木邵路K6+700上行龙尹路口西"},
    {"camera_id": 11000000001313023975, "monitor_point": "G234兴阳线K102+460黑龙潭"},
    {"camera_id": 11000000001313731852, "monitor_point": "S204密三路K0+010汽车站路口"},
    {"camera_id": 11000000001312966376, "monitor_point": "G103京滨线K24+680张采路口"},
]
baitan_list = [
    {"camera_id": 11000000001317480152, "monitor_point": "G101京沈线K22+290上行火神营交调站"},
    {"camera_id": 11000000001317193402, "monitor_point": "G101京沈线K39+350下行富各庄"},
    {"camera_id": 11000000001314706001, "monitor_point": "S201通顺路K22+000上行燕京桥下"},
    {"camera_id": 11000000001319399586, "monitor_point": "S203顺密路K17+400下行木林道班"},
    {"camera_id": 11000000001316185552, "monitor_point": "S214壁富路K8+900上行机场专线"},
    {"camera_id": 11000000001313053014, "monitor_point": "S321顺沙路K15+100下行高白路口西"},
    {"camera_id": 11000000001313113338, "monitor_point": "S332龙塘路K10+150下行苏庄闸桥西"},
    {"camera_id": 11000000001314819953, "monitor_point": "X021木燕辅线K3+700马庄检查站 (出京)"},
    {"camera_id": 11000000001319753987, "monitor_point": "X213木邵路K6+700上行龙尹路口西"},
    {"camera_id": 11000000001313023975, "monitor_point": "G234兴阳线K102+460黑龙潭"},
    {"camera_id": 11000000001313731852, "monitor_point": "S204密三路K0+010汽车站路口"},
    {"camera_id": 11000000001312966376, "monitor_point": "G103京滨线K24+680张采路口"},
]

