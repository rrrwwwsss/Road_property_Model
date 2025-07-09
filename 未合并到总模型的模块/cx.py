import dmPython

def test_dm_table_access(db_config):
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

        # # 查询 OFFSITE_RULE 表的前五行内容
        # query_sql = "SELECT * FROM OFFSITE_EVIDENCE_CONSTANT LIMIT 5"
        # cursor.execute(query_sql)

        # # 获取查询结果
        # rows = cursor.fetchall()
        # 
        # # 获取列名
        # columns = [desc[0] for desc in cursor.description]
        # print("列名如下：")
        # print(columns)
        # 
        # print("\nOFFSITE_RULE 表的前五行内容如下：")
        # for row in rows:
        #     print(row)

    except Exception as e:
        print(f"数据库连接失败或查询失败：{e}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            print("数据库连接已关闭。")

# 假设 db_config 是一个包含数据库连接信息的字典
db_config = {
    'host': '172.26.76.79',   # 数据库地址
    'port': 5236,          # 数据库端口，达梦默认5236
    'user': 'sjtb',      # 数据库用户名
    'password': 'sjtb#_2024',  # 数据库密码
}

test_dm_table_access(db_config)