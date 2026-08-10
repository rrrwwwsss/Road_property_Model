from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional
from datetime import datetime

# 本地图片在网络上的地址
IMG_URL = "http://10.212.160.162:5000/preview/"
# 数据库连接配置
DB_CONFIG = {
    'host': '172.26.76.79',   # 数据库地址
    'port': 5236,          # 数据库端口，达梦默认5236
    'user': 'sjtb',      # 数据库用户名
    'password': 'sjtb#_2024',  # 数据库密码
}
# 控制提交六个违法行为类型到数据库的变量
IS_SUBMIT = True
# 违法行为ID
VIOLATION_DICT = {
    "造成公路路面损坏、污染或者影响公路畅通": "a3f1b9c8d4e7426fa8b1c0d9e5f3a2b4",
    "擅自占用、挖掘公路": "6b50c0ae92ef4b94880443a6b362e731",
    "在公路用地范围内设置公路标志以外的其他标志": "219df49be1d44d639fe1f8e9d3aa2e5b",
    "在公路范围内擅自移动井盖": "dbd1987e748c45ceb5f701345e2c7dd0",
    "遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全": "0cc1ea428e61471a8f7969e047774e9e",
    "在公路上及公路用地范围内堆放物品": "2cf9aa7a9c9d42bb99916f6f379e94a2",
    "在公路上及公路用地范围内摆摊设点": "792409a397d04c3a9252d3f61f0b91fc",
    "公路范围内擅自移动井盖": "dbd1987e748c45ceb5f701345e2c7dd0",
    
}
# 违法行为详情
TJ_NAME_LIST = {
    "擅自占用、挖掘公路": "擅自占用、挖掘公路",

    "在公路用地范围内设置公路标志以外的其他标志": "在公路用地范围内设置公路标志以外的其他标志",

    "在公路范围内擅自移动井盖": "公路范围内擅自移动井盖",

    "遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全": "遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全",

    "在公路上及公路用地范围内堆放物品": "造成公路路面损坏、污染或者影响公路畅通",

    "在公路上及公路用地范围内摆摊设点": "造成公路路面损坏、污染或者影响公路畅通"
}

# 职权编码
AUTHORITY_CODE = {
    "擅自占用、挖掘公路": "C1900100",
    "在公路用地范围内设置公路标志以外的其他标志": "C1901500",
    "在公路范围内擅自移动井盖": "C1913400",
    "遮挡公路附属设施或者利用公路附属设施架设管道、悬挂物品，可能危及公路安全": "C1901000",
    "在公路上及公路用地范围内堆放物品": "C1901100",
    "在公路上及公路用地范围内摆摊设点": "C1901100"
}
# 区对应编码
DISTRICT_CODE = {
    "东城": "110101",
    "西城": "110102",
    "朝阳": "110105",
    "海淀": "110108",
    "丰台": "110106",
    "石景山": "110107",
    "大兴": "110115",
    "房山": "110111",
    "昌平": "110114",
    "门头沟": "110109",
    "延庆": "110119",
    "通州": "110112",
    "顺义": "110113",
    "怀柔": "110116",
    "密云": "110118",
    "平谷": "110117",
}
@dataclass
class OffsiteRule:  # OFFSITE_RULE：规则表
    ID: str #UUID
    QUESTION_NAME: str  # 某种违法行为名称
    CREATE_TIME: Optional[datetime] #创建时间
    UPDATE_TIME: Optional[datetime] #更新时间
    IS_DEL : str
    MEASURE : str # 职权编码(怎么填)

@dataclass
class OffsiteWarnsHb:  # OFFSITE_WARNS_HB：合并线索表
    ID : str
    ERROR_HB_ID: str # OFFSITE_INTELLECT_ERRORS_HB表的id
    RULE_ID: str # OFFSITE_RULE 表的id
    UNIT_CODE : str # 辖区编码(怎么填)
    TRADE : str # 行业编码 '36'
    DATA_SOURCE : str #数据来源，传公司名称
    YEHU_ID : str # 业户id,任意生成一个
    YEHU_NAME : str #业户名称。写“无法确定当事人”
    FIND_TIME : Optional[datetime] #发现时间
    UPDATE_TIME: Optional[datetime] #更新时间
    CREATE_TIME: Optional[datetime] #创建时间
    IS_DEL: str = field(default='0')  #状态 :0未删除、1删除 默认'0'
    # field 是 Python dataclasses 模块里的一个函数，用于对某个字段进行更精细的控制。
    ERROR_NUM: Decimal = field(default=Decimal('1')) #错误数 默认1

@dataclass
class OffsiteIntellectErrorsHb:  # OFFSITE_INTELLECT_ERRORS_HB：问题预警表
    ID: str
    QUESTION_DATA: str # 问题数据详情，json格式
    EVIDENCE_TYPE : str #问题类型 注：（默认YJ） YJ：预警；CZZ：超资质；YJDD：预警订单；
    QUESTION_ID : str #同OFFSITE_WARNS_HB表中RULE_ID,即OFFSITE_RULE表的id
    YEHU_ID : str # 企业ID
    UPDATE_TIME: Optional[datetime]  # 更新时间
    CREATE_TIME: Optional[datetime]  # 创建时间
    IS_DEL: str = field(default='0')  # 状态 :0未删除、1删除 默认'0'
@dataclass
class OffsiteIntellectDetailsHb:  # OFFSITE_INTELLECT_DETAILS_HB：问题详情信息表
    ID: str
    ERROR_HB_ID : str #OFFSITE_INTELLECT_ERRORS_HB表的id
    QUESTION_ID : str #OFFSITE_RULE表的id
    YEHU_ID : str
    ERROR_ID: str # OFFSITE_INTELLECT_ERRORS_HB表QUESTION_DATA字段中json中封装的错误类型(如违法行为类型)
    QUESTION_DATA: str #跟OFFSITE_INTELLECT_ERRORS_HB的QUESTION_DATA一样
    EVIDENCE_TYPE: str #同ERROR_ID
    CREATE_TIME: Optional[datetime]  # 创建时间

@dataclass
class OffsiteEvidenceConstant:  # OFFSITE_EVIDENCE_CONSTANT：常量信息表
    ID: str
    QUESTION_ID : str # OFFSITE_RULE表的id
    NAME: str #OFFSITE_INTELLECT_ERRORS_HB表的QUESTION_DATA中的字段名字，也就是json的key
    TRANSLATION : str #NAME字段对应的中文名字
    CONSTANT_TYPE: str #内容类型，默认EVIDENCE
    ORDER_NO: Decimal #排序号（自己生成）
    IS_SHOW: Decimal = field(default=Decimal('1'))