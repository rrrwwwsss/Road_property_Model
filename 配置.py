# 服务器相关配置
BASE_URL = "https://10.212.160.158:8101/nvms8100/apploginVideo" #监控摄像头地址
# USER_NAME = "bjjzdx"
# USER_PWD = "ZFZDwxglwf@2025"
USER_NAME = "bhwfxm05"
USER_PWD = "c6QKJrTtuT"
# 联通服务器72b模型接口
LIANTONG_MODEL = "http://192.168.0.161:1025/v1/chat/completions"
# LIANTONG_MODEL = "http://192.168.0.92:3025/v1/chat/completions"
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
DUOZHEN_PATH = DATA_BASE_PATH + "/duozhen"
# RESULT_PATH = "/app/result.csv"
CAMERA_DATA = "./data/《视频点位确认表》 0620.xlsx" # 摄像头点位信息，相对路径
CAMERA_RESULT_DATA = "./data/result_with_camera_id.csv"# 整合数据后的摄像头点位信息，相对路径
XVANGUA_TICHU = "./data/悬挂物剔除区域.csv"

# 图片文件夹信息数据库
IMAGE_DB = '/app/qiepian/image_information.db'
# 图片文件夹信息接口
IMAGE_API= "http://10.212.160.162:18000"
# 图片存储位置信息
IMAGE_QIEPIAN_PATH = '/app/screenshots/'
#  许可数据库配置
XVKE_DB_CONFIG = {
    'host': '172.26.57.210',   # 数据库地址
    'port': 5236,          # 数据库端口，达梦默认5236
    'user': 'GLLWFXM',      # 数据库用户名
    'password': 'zfzdqzj@123456,.',  # 数据库密码
}
# 模型服务
MODEL_SERVE_URL = "http://htc-qwen2vl:8000/generate"  # qwen2vl服务地址

# 重复预警推送间隔时间
CHONGFU_TIME = 360
# CHONGFU_TIME = 360
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
linshi_list = [{'camera_id': '11011101071328110008', 'monitor_point': 'G5京昆高速广场K25+000夏村收费站入口双向（可控）'},
               {'camera_id': '11011101071328110007', 'monitor_point': 'G5京昆高速广场K25+000夏村收费站出口双向（可控）'},
               {'camera_id': '11010701071328230003', 'monitor_point': 'G4501六环路广场K132+800广宁双向入口广场反向（可控）'},
               {'camera_id': '11000000001314375767', 'monitor_point': 'S209石担路K9+900龙泉雾村'},
               {'camera_id': '11000000001312814604', 'monitor_point': 'G108京昆线K22+250小园立交桥'},
               {'camera_id': '11000000001315973478', 'monitor_point': 'G108京昆线K30+170鲁家滩二桥'},
               {'camera_id': '11000000001318701885', 'monitor_point': 'G109京拉线K110+770张马路口'},
               # {'camera_id': '11000000001315959615', 'monitor_point': 'G109京拉线K35+930担礼隧道'},
               {'camera_id': '11000000001315378966', 'monitor_point': 'G109京拉线K87+600新高铺'},
               {'camera_id': '11000000001315432555', 'monitor_point': 'G234兴阳线K342+890鲁家滩环岛'},
               {'camera_id': '11000000001315023163', 'monitor_point': 'S210三温路K1+550与X906交叉口'},
               {'camera_id': '11000000001313208456', 'monitor_point': 'X015杨东路K0+850东杨坨村'},
               {'camera_id': '11010701071328230004', 'monitor_point': 'G4501六环路广场K132+800广宁双向入口广场正向（可控）'},
               {'camera_id': '11000000001315829866', 'monitor_point': 'G110京青线K98+350下营村西'},
               {'camera_id': '11000000001314634205', 'monitor_point': 'G110京青线K99+090下营'},
               {'camera_id': '11000000001318180501', 'monitor_point': 'S212昌赤路K50+400永宁服务站'},
               {'camera_id': '11000000001313408721', 'monitor_point': 'S212昌赤路K32+000大庄科'},
               {'camera_id': '11000000001311823396', 'monitor_point': 'G110京青线K52+390黄土嘴桥'},
               {'camera_id': '11000000001313670338', 'monitor_point': 'G110京青线K52+900山京沟'},
               {'camera_id': '11000000001316880846', 'monitor_point': 'G234兴阳线K231+660兴阳线铁路桥'},
               {'camera_id': '11000000001315146877', 'monitor_point': 'S217康张路K10+860张山营桥'},
               {'camera_id': '11000000001314427730', 'monitor_point': 'S213安四路K80+780海字口'},
               {'camera_id': '11000000001313515334', 'monitor_point': 'S232妫川路K17+150米家堡桥'},
               {'camera_id': '11000000001315918584', 'monitor_point': 'X017康草路K0+150铁路桥'},
               {'camera_id': '11000000001313307753', 'monitor_point': 'X031东岔路K0+630东曹营'},
               {'camera_id': '11000000001314235556', 'monitor_point': 'S216G6辅路K57+400八达岭消防队'},
               {'camera_id': '11000000001319719872', 'monitor_point': 'S216G6辅路K58+230红叶岭停车场'},
               {'camera_id': '11000000001314907633', 'monitor_point': 'G234兴阳线K237+100过水路面北侧'},
               {'camera_id': '11011401071328230058', 'monitor_point': 'G4501六环路匝道K180+500马坊出口外环'},
               {'camera_id': '11010801071328230025', 'monitor_point': 'G4501六环路广场K150+200北清入口广场东'},
               {'camera_id': '11011401071328230034', 'monitor_point': 'G4501六环路道路K164+200楼自庄桥东内环'},
               {'camera_id': '11011401071328030087', 'monitor_point': 'G7京新高速道路K15+820京新沙阳北出京'},
               {'camera_id': '11011401071328030095', 'monitor_point': 'G7京新高速道路K19+650六环路南出京'},
               {'camera_id': '11011401071328030086', 'monitor_point': 'G7京新高速道路K14+610京新沙河主站进京'},
               {'camera_id': '11011401071328170101', 'monitor_point': 'G6京藏高速广场K22+670小汤山出京入口'},
               {'camera_id': '11011401071328090019', 'monitor_point': 'S3801京礼高速K13+810出京'},
               {'camera_id': '11011401071328090011', 'monitor_point': 'S3801京礼高速K8+970进京'},
               {'camera_id': '11000000001316766372', 'monitor_point': 'G110京青线K41+750下行德胜口桥'},
               {'camera_id': '11000000001319804874', 'monitor_point': 'S216G6辅路K22+650下行沙阳路'},
               {'camera_id': '11000000001319850899', 'monitor_point': 'S219南雁路K0+000上行西大桥西'},
               {'camera_id': '11000000001319325196', 'monitor_point': 'S321顺沙路K23+250上行大柳树环岛'},
               {'camera_id': '11000000001316925337', 'monitor_point': 'S324沙阳路K0+150上行铁路桥'},
               {'camera_id': '11000000001312663858', 'monitor_point': 'S330昌金路K5+100下行安四路'},
               {'camera_id': '11000000001312588152', 'monitor_point': 'S337北清路K25+900下行立汤路'},
               {'camera_id': '11000000001317376509', 'monitor_point': 'X033昌崔路K15+950上行安四路'},
               {'camera_id': '11000000001314317407', 'monitor_point': 'G104京岚线K18+200京岚线与兴亦路交叉口'},
               {'camera_id': '11000000001313703362', 'monitor_point': 'G104京岚线K33+700马朱路口'},
               {'camera_id': '11000000001318199767', 'monitor_point': 'G105京澳线K35+500上行京澳线与黄徐路桥北'},
               {'camera_id': '11000000001314074100', 'monitor_point': 'G230通武线K1149+200通武线与南中轴交叉路口'},
               {'camera_id': '11000000001315288646', 'monitor_point': 'S215京开东辅路K6+600西红门桥东侧'},
               {'camera_id': '11000000001318987086', 'monitor_point': 'S226马朱路K5+000青采路口北'},
               {'camera_id': '11011501071328440096', 'monitor_point': 'G106京开高速道路K28+170薛营入口收费站北200米出京（可控）'},
               {'camera_id': '11011501071328440035', 'monitor_point': 'G106京开高速广场K24+200三融入口出京1（可控）'},
               {'camera_id': '11011501071328220019', 'monitor_point': 'S3300大兴机场北线K15+395下行内环新机场互通西'},
               {'camera_id': '11011501071328220065', 'monitor_point': 'S3300大兴机场北线K6+610下行'},
               {'camera_id': '11011501071328230008', 'monitor_point': 'G4501南六环道路K74+550南大红门2.5公里外环(可控)'},
               {'camera_id': '11011501071328230056', 'monitor_point': 'G4501南六环广场K85+500念坛收费站入口内环(可控)'},
               {'camera_id': '11011501071328160265', 'monitor_point': 'G45大广高速广场K1349+950求贤入口进京2（可控）'},
               {'camera_id': '11011501071328210050', 'monitor_point': 'S3501大兴机场高速K15+247进京-中心路01'},
               {'camera_id': '11000000001315030570', 'monitor_point': 'G107京港线K41+600京广线铁路'},
               {'camera_id': '11000000001311125069', 'monitor_point': 'G107京港线K53+400琉璃河大桥'},
               {'camera_id': '11000000001311523919', 'monitor_point': 'G107京港线K55+200琉璃河检查站（出京）'},
               {'camera_id': '11000000001314007362', 'monitor_point': 'G107京港线K55+200琉璃河检查站（进京）'},
               {'camera_id': '11000000001313872319', 'monitor_point': 'G108京昆线K48+000东庄子桥'},
               {'camera_id': '11000000001317455018', 'monitor_point': 'G230通武线K1178+700下穿京广高铁桥北'},
               {'camera_id': '11000000001316769609', 'monitor_point': 'G230通武线K1180+100常舍村（出京）'},
               {'camera_id': '11000000001311020418', 'monitor_point': 'G230通武线K1180+100常舍村（进京）'},
               {'camera_id': '11000000001319087302', 'monitor_point': 'G230通武线K1180+134通武线与琉陶路交叉口南'},
               {'camera_id': '11000000001319309175', 'monitor_point': 'G234兴阳线K402+010兴阳线坟庄村非限全景'},
               {'camera_id': '11000000001317589880', 'monitor_point': 'G234兴阳线K386+350周支铁路'},
               {'camera_id': '11000000001312470790', 'monitor_point': 'S313岳琉路K11+650水泥厂泵站'},
               {'camera_id': '11000000001315544554', 'monitor_point': 'S313岳琉路K9+100李庄泵站'},
               {'camera_id': '11000000001312446525', 'monitor_point': 'S326大件路K9+710丁家洼桥东'}]





# if __name__ == '__main__':
#     print(len(linshi_list))
