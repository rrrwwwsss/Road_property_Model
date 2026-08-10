import dmPython
# import schedule
import json
import re
from datetime import datetime, timedelta
from config.配置 import *
# 达梦数据库配置
db_config = XVKE_DB_CONFIG
# 全局变量存储查询结果
query_results = {
    'feigongbiao': [],
    'zhanwagonglu': [],
    'xuanguawu': []
}
def calculate_end_date(applytime, projecttime):
    """
    根据许可期限计算截止日期
    支持：
    1个月、设置期限为：1年、276天、2年、3月
    排除：
    2023年3月31日至...
    """

    if "至" in projecttime:
        return None

    match = re.search(r'(\d+)\s*(年|个月|月|天)', projecttime)

    if not match:
        return None

    number = int(match.group(1))
    unit = match.group(2)

    if unit == "年":
        days = number * 365
    elif unit in ["月", "个月"]:
        days = number * 30
    elif unit == "天":
        days = number
    else:
        return None

    try:
        apply_date = datetime.strptime(applytime, "%Y年%m月%d日")
        end_date = apply_date + timedelta(days=days)
        return end_date.strftime("%Y年%m月%d日")
    except:
        return None


def dameng_connection(business_name, today):

    connection = None
    cursor = None

    try:
        if isinstance(today, str):
            today = datetime.strptime(today, "%Y-%m-%d %H:%M:%S")

        connection = dmPython.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password']
        )

        print("数据库连接成功！")

        cursor = connection.cursor()

        query = """
        SELECT DECISIONINFORMATION
        FROM GXJTW.ADMINISTRATIVE_LICENSE_APPLICATION
        WHERE BUSINESS_NAME = ?
        """

        cursor.execute(query, (business_name,))
        results = cursor.fetchall()
        print(f"查询到 {len(results)} 条记录, 业务名称: {business_name}")
        print(f"查询结果: {results}")
        if not results:
            print("未找到符合条件的数据")
            return []

        extracted_results = []

        for row in results:

            try:
                decision_info = json.loads(row[0])

                applytime = decision_info.get('applytime')
                projecttime = decision_info.get('projecttime')
                constructaddress = decision_info.get('constructaddress')

                if not applytime or not projecttime:
                    continue

                # 永久许可
                if projecttime.strip() == "永久":
                    end_date_str = "永久"

                else:
                    end_date_str = calculate_end_date(
                        applytime,
                        projecttime
                    )
                    print()

                    if not end_date_str:
                        print("跳过无法解析期限:", projecttime)
                        continue

                # 判断是否过期
                if end_date_str == "永久":
                    is_expired = False
                else:
                    end_date = datetime.strptime(
                        end_date_str,
                        "%Y年%m月%d日"
                    )
                    is_expired = end_date.date() < today.date()

                if not is_expired:
                    extracted_results.append({
                        "end_date": end_date_str,
                        "constructaddress": constructaddress
                    })

            except Exception as e:
                print("处理数据异常:", e)
                continue

        return extracted_results

    except Exception as e:
        print("程序执行异常:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
            print("数据库连接已关闭")



def job():
     # 获取当前时间并格式化
    current_time = datetime.now()
    print(f"{current_time} 开始执行查询任务...")
    # 调用测试函数
     # 调用测试函数
    query_results['feigongbiao'] = dameng_connection('设置非公路标志审批', current_time)
    query_results['zhanwagonglu'] = dameng_connection('占用、挖掘公路、公路用地或者使公路改线审批（普通）', current_time)
    query_results['xuanguawu'] = dameng_connection('跨越、穿越公路及在公路用地范围内架设、埋设管线及电缆等设施或者利用公路桥梁、公路隧道、涵洞铺设电缆等设施许可', current_time)
    print(f"{current_time} 查询任务执行完成。")
    # 打印每个审批类型的结果
    print(f"设置非公路标志审批: {query_results['feigongbiao']}")
    print(f"占用、挖掘公路、公路用地或者使公路改线审批（普通）: {query_results['zhanwagonglu']}")
    print(f"跨越、穿越公路及在公路用地范围内架设、埋设管线及电缆等设施或者利用公路桥梁、公路隧道、涵洞铺设电缆等设施许可: {query_results['xuanguawu']}")
    return query_results

# def main():
#     # 调用 job 函数执行查询任务
    

if __name__ == "__main__":
    job()
    # 安排每隔一天定时执行任务
# schedule.every().day.at("00:00").do(job)  # 每隔一天午夜00:00执行
# while True:
#         # 检查是否有待执行的任务
#         schedule.run_pending()
#         # 稍作延迟，避免 CPU 占用过高
#         time.sleep(600)
