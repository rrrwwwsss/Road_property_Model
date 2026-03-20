import dmPython
# import schedule
import time
import json
from datetime import datetime, timedelta
from config.配置 import XVKE_DB_CONFIG
# 达梦数据库配置
db_config = XVKE_DB_CONFIG
# 全局变量存储查询结果
query_results = {
    'feigongbiao': [],
    'zhanwagonglu': [],
}
def dameng_connection(business_name):
    try:
        # 连接到达梦数据库
        connection = dmPython.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
        )
        print("数据库连接成功！")
        cursor = connection.cursor()
        # result = cursor.fetchone()
        # print(f"数据库版本：{result[0]}")
        # 执行查询语句
        
        query = """
        SELECT DECISIONINFORMATION FROM GXJTW.ADMINISTRATIVE_LICENSE_APPLICATION
        WHERE BUSINESS_NAME = ?
        """
        cursor.execute(query, (business_name,))
        
        # 获取查询结果
        results = cursor.fetchall()
        if results:
              # 解析 DECISIONINFORMATION 字段并提取信息
            extracted_results = []
            for row in results:
                # 每个row都是json
                decision_info = json.loads(row[0])
                applytime = decision_info.get('applytime')
                projecttime = decision_info.get('projecttime')
                constructaddress = decision_info.get('constructaddress')
                # print(f"applytime: {applytime}, projecttime: {projecttime}, constructaddress: {constructaddress}")
                if applytime and projecttime:
                    # 去掉 projecttime 中的 "年"、"月" 或 "天" 字
                    projecttime = projecttime.replace('年', '').replace('月', '').replace('天', '').strip()
                    if projecttime.isdigit():
                        applytime_date = datetime.strptime(applytime, "%Y年%m月%d日")
                        project_days = int(projecttime)
                         # 根据单位计算结束时间
                        if '年' in decision_info.get('projecttime', ''):
                            project_days *= 365
                        elif '月' in decision_info.get('projecttime', ''):
                            project_days *= 30                            
                        end_date = applytime_date + timedelta(days=project_days)
                        end_date_str = end_date.strftime("%Y年%m月%d日")
                    elif projecttime == "永久":
                        end_date_str = "永久"  
                else:
                    # print(f"跳过无效数据：{decision_info}")
                    continue  
                 # 新增日期筛选逻辑
                today = datetime.now()
                    
                # 处理永久有效的情况
                if end_date_str == "永久":
                    is_expired = False
                else:
                    # 将end_date_str转换为datetime对象进行比较
                    end_date_compare = datetime.strptime(end_date_str, "%Y年%m月%d日")
                    is_expired = end_date_compare < today
 
                    # 只保留未过期的数据
                if not is_expired:
                    extracted_results.append({
                        'end_date': end_date_str,
                        'constructaddress': constructaddress
                    })
                        
            return extracted_results
        else:
            print("未找到符合条件的数据。")
            return []


    except Exception as e:
        print(f"数据库连接失败：{e}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            print("数据库连接已关闭。")


def job():
     # 获取当前时间并格式化
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    print(f"{current_time} 开始执行查询任务...")
    # 调用测试函数
     # 调用测试函数
    query_results['feigongbiao'] = dameng_connection('设置非公路标志审批')
    query_results['zhanwagonglu'] = dameng_connection('占用、挖掘公路、公路用地或者使公路改线审批（普通）')
    print(f"{current_time} 查询任务执行完成。")
    # 打印每个审批类型的结果
    print(f"设置非公路标志审批: {query_results['feigongbiao']}")
    print(f"占用、挖掘公路、公路用地或者使公路改线审批（普通）: {query_results['zhanwagonglu']}")
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

