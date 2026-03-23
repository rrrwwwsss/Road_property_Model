import sqlite3
from PIL import Image
from datetime import datetime
from config.配置 import *

# 连接到 SQLite 数据库
def connect_to_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # ←←← 关键！启用列名访问
    return conn


# 获取符合条件的元组
def get_violations(conn, key, camera_id):
    cursor = conn.cursor()

    # 查找符合key的元组
    query = """
            SELECT * \
            FROM data_records
            WHERE violation_type = ?
              AND camera_id = ?
              AND is_detected = 0
              AND is_deleted = 0\
            """
    cursor.execute(query, (str(key), str(camera_id)))
    rows = cursor.fetchall()

    return rows


# 获取时间最晚的元组并更新
def get_latest_violation_and_update(conn, violations):
    latest_row = None
    latest_time = None
    for row in violations:
        discovery_time = row['capture_time']  # 假设字段名是'发现时间'
        time_obj = datetime.strptime(discovery_time, "%Y%m%d_%H%M%S")  # 转换为datetime对象
        if latest_time is None or time_obj > latest_time:
            latest_time = time_obj
            latest_row = row

    # 获取path字段
    if latest_row:
        # path = latest_row['image_path']
        # 拼接字符串，拼接为容器中的路径
        path = IMAGE_QIEPIAN_PATH + latest_row['name']
        print('图片名称：',path)
        # 更新该元组的'是否处理'字段为'true'
        cursor = conn.cursor()
        update_query = """
                       UPDATE data_records
                       SET is_detected = 1
                       WHERE id = ?
                       """
        cursor.execute(update_query, (latest_row['id'],))
        conn.commit()
        print(f"{latest_row['id']}号数据更新为已处理")
        return path
    return None


# 使用路径加载图片为PIL Image对象
def load_image(path):
    try:
        image = Image.open(path)
        return image
    except Exception as e:
        print(f"加载图片时出错: {e}")
        return None


# 主流程
def process_violations(xingwei, camera_id):
    # 示例调用
    db_path = IMAGE_DB
    conn = connect_to_db(db_path)


    if xingwei:
        # 获取符合条件的元组
        violations = get_violations(conn, xingwei, camera_id)

        if violations:
            # 获取时间最晚的记录并更新
            path = get_latest_violation_and_update(conn, violations)

            if path:
                # 加载图片并返回
                image = load_image(path)
                if image:

                    return image
                else:
                    print("图片加载失败，点位：",camera_id)
        else:
            print("没有找到符合条件的记录，点位：",camera_id)
    else:
        print("未能从字典中找到对应的key，点位：",camera_id)

    conn.close()
    return None