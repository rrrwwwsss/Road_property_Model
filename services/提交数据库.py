import json
from datetime import datetime
import uuid
from config.数据库配置 import DB_CONFIG, OffsiteRule, OffsiteWarnsHb, OffsiteIntellectErrorsHb, OffsiteEvidenceConstant, VIOLATION_DICT,AUTHORITY_CODE

from decimal import Decimal
import dmPython
from dataclasses import asdict
from typing import Any
def insert_object(obj: Any, table_name: str):
    data = asdict(obj)

    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    values = list(data.values())

    sql = f"INSERT INTO offsite.{table_name} ({columns}) VALUES ({placeholders})"
    print("sql",sql)
    conn = dmPython.connect(
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        server=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )
    cursor = conn.cursor()
    try:
        cursor.execute(sql, values)
        conn.commit()
        print(f"插入 {table_name} 成功")
    except Exception as e:
        conn.rollback()
        print(f"插入失败: {e}")
    finally:
        cursor.close()
        conn.close()
def insert_database(data):
    #公共变量

    OffsiteRule_id = data['OffsiteRule_id']
    OffsiteWarnsHb_id = str(uuid.uuid4().hex)
    OffsiteIntellectErrorsHb_id = str(uuid.uuid4().hex)
    OffsiteIntellectDetailsHb_id = str(uuid.uuid4().hex)
    # OffsiteEvidenceConstant_id = str(uuid.uuid4())

    UPDATE_TIME = datetime.now()
    CREATE_TIME = datetime.now()
    FIND_TIME = datetime.now()
    YEHU_ID = str(uuid.uuid4().hex)

    QUESTION_DATA = [
      {
        "TJ_NAME": data["TJ_NAME"],
        "TJ_CHECK_RESULT": "0",#检查结果
        "TJ_ID": "",
        "NEXT_LEVEL": [
          {
            # "WORK_ORDER_ID": data['工单编号'],
            "VIOLATION_TYPE": data['违法类型'],
            "LOCATION": data['发生地点'],
            "VIOLATION_TIME": datetime.strptime(data['发生时间'], "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S"),
            "IMAGE_PATH": data['图片路径'],
            "LEVEL":'中'
          }
        ]
      }
    ]
    # QUESTION_DATA的NEXT_LEVEL原始中文字段与对应英文字段的映射
    field_map = {
        "WORK_ORDER_ID": "工单编号",
        "VIOLATION_TYPE": "违法类型",
        "LOCATION": "发生地点",
        "VIOLATION_TIME": "发生时间",
        "STATUS": "处理状态",
        "HANDLER": "处理人",
        "IMAGE_PATH": "图片路径",
        "REMARK": "处理备注",
        "LEVEL":"推送分级分类"
    }
    import 数据库配置
    if 数据库配置.IS_SUBMIT == True:
        print("开始提交六项违法行为到数据库")
        # 先把六个违法行为存储到数据库中，后面就不用存了
        for k, v in VIOLATION_DICT.items():
            print(k, v)
            try:
                # 插入OFFSITE_RULE表
                offsiteRule = OffsiteRule(ID=v, QUESTION_NAME=k,
                                          CREATE_TIME=CREATE_TIME,
                                          UPDATE_TIME=UPDATE_TIME,
                                          IS_DEL="0",
                                          MEASURE=AUTHORITY_CODE[k])
                print(offsiteRule)
                insert_object(offsiteRule, table_name='OFFSITE_RULE')
            except Exception as e:
                print(e)

        数据库配置.IS_SUBMIT = False  # 这样才修改了模块的全局变量
    # 插入OFFSITE_WARNS_HB表
    offsiteWarnsHb = OffsiteWarnsHb(ID=OffsiteWarnsHb_id,
                                    ERROR_HB_ID=OffsiteIntellectErrorsHb_id,
                                    RULE_ID=OffsiteRule_id,
                                    UNIT_CODE=data['UNIT_CODE'],
                                    TRADE='36',
                                    DATA_SOURCE='中路高科',
                                    YEHU_ID=YEHU_ID,
                                    YEHU_NAME="无法确定当事人",
                                    FIND_TIME=FIND_TIME,
                                    CREATE_TIME=CREATE_TIME,
                                    UPDATE_TIME=UPDATE_TIME,
                                    IS_DEL="0",
                                    ERROR_NUM=Decimal('1'))
    insert_object(offsiteWarnsHb, table_name='OFFSITE_WARNS_HB')

    # OFFSITE_INTELLECT_ERRORS_HB
    offsiteIntellectErrorsHb = OffsiteIntellectErrorsHb(ID=OffsiteIntellectErrorsHb_id,
                                                        QUESTION_DATA = json.dumps(QUESTION_DATA, ensure_ascii=False),#转为字符串
                                                        # QUESTION_DATA=QUESTION_DATA,
                                                        EVIDENCE_TYPE = 'YJ',
                                                        QUESTION_ID = OffsiteRule_id,
                                                        YEHU_ID = YEHU_ID,
                                                        CREATE_TIME=CREATE_TIME,
                                                        UPDATE_TIME=UPDATE_TIME,
                                                        IS_DEL="0")
    insert_object(offsiteIntellectErrorsHb, table_name='OFFSITE_INTELLECT_ERRORS_HB')

    # #OFFSITE_INTELLECT_DETAILS_HB
    # offsiteIntellectDetailsHb = OffsiteIntellectDetailsHb(ID=OffsiteIntellectDetailsHb_id,
    #                                                       ERROR_HB_ID = OffsiteIntellectErrorsHb_id,
    #                                                       QUESTION_ID = OffsiteRule_id,
    #                                                       YEHU_ID=YEHU_ID,
    #                                                       ERROR_ID = data['违法类型'],
    #                                                       QUESTION_DATA=json.dumps(QUESTION_DATA, ensure_ascii=False),
    #                                                       EVIDENCE_TYPE=data['违法类型'],
    #                                                       CREATE_TIME=CREATE_TIME,
    #                                                       )
    # insert_object(offsiteIntellectDetailsHb, table_name='OFFSITE_INTELLECT_DETAILS_HB')

    #OFFSITE_EVIDENCE_CONSTANT 对这个表存储的是QUESTION_DATA的NEXT_LEVEL信息，因此要把其每个字段都当作一行输入数据库

    import 数据库配置
    if 数据库配置.IS_SUBMIT == True:
        print("开始提交六项违法行为到数据库")
        # 先把六个违法行为存储到数据库中，后面就不用存了
        for i, j in VIOLATION_DICT.items():
            indexs = 0
            for k, v in QUESTION_DATA[0]['NEXT_LEVEL'][0].items():
                offsiteEvidenceConstant = OffsiteEvidenceConstant(ID=str(uuid.uuid4().hex),
                                                                  QUESTION_ID=j,
                                                                  NAME=k,
                                                                  TRANSLATION=field_map[k],
                                                                  CONSTANT_TYPE="EVIDENCE",
                                                                  ORDER_NO=Decimal(indexs),
                                                                  IS_SHOW=Decimal('1'),
                                                                  )
                insert_object(offsiteEvidenceConstant, table_name='OFFSITE_EVIDENCE_CONSTANT')
                indexs += 1



if __name__ == '__main__':
    data = {
        "TJ_NAME": "摆设摊位行为：是指在公路及其用地范围内擅自设置售卖摊位，占用道路资源，扰乱正常交通秩序，存在较大安全与管理风险。",#违法行为描述
        "MEASURE": "C1900100", #职权编码
        "UNIT_CODE": "110113",#辖区编码
        "工单编号": "G101京沈线K39+350下行富各庄_20250517_092339.jpg",
        "违法类型": "摆设摊位",
        "发生地点": "G101京沈线K39+350下行富各庄",
        "发生时间": "20250517_092339",
        "图片路径": "http://10.212.160.162:5000/preview/baitan/camera_11000000001317193402_20250701_190708.jpg",
        "OffsiteRule_id": "792409a397d04c3a9252d3f61f0b91fc",
    }
    insert_database(data)
