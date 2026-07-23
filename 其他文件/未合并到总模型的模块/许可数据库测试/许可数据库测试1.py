import dmPython
import json

# 达梦数据库配置
db_config = {
    'host': '172.26.57.210',   # 数据库地址
    'port': 5236,          # 数据库端口，达梦默认5236
    'user': 'GLLWFXM',      # 数据库用户名
    'password': 'zfzdqzj@123456,.',  # 数据库密码
}

business_name = "占用、挖掘公路、公路用地或者使公路改线审批（普通）"

try:
    # 连接数据库
    connection = dmPython.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
    )
    print("数据库连接成功！")

    cursor = connection.cursor()

    cursor = connection.cursor()

    # 使用 DISTINCT 查询 BUSINESS_NAME 的唯一值
    query = """
    SELECT DISTINCT BUSINESS_NAME 
    FROM GXJTW.ADMINISTRATIVE_LICENSE_APPLICATION
    """
    
    cursor.execute(query)
    
    # 获取所有唯一值结果
    unique_business_names = cursor.fetchall()
    
    print(f"共找到 {len(unique_business_names)} 个唯一的业务名称：")
    for row in unique_business_names:
        print(row[0])  # row[0] 即为 BUSINESS_NAME 的值
# 
# 数据库连接成功！
# 共找到 20 个唯一的业务名称：
# 在公路增设或改造平面交叉道口审批
# 设置非公路标志审批
# 占用、挖掘公路、公路用地或者使公路改线审批（普通）
# 跨越、穿越公路及在公路用地范围内架设、埋设管线及电缆等设施或者利用公路桥梁、公路隧道、涵洞铺设电缆等设施许可
# 公路建筑控制区内埋设管线、电缆等设施许可
# 在公路周边一定范围内因抢险、防汛需要修筑堤坝、压缩或者拓宽河床许可
# 利用跨越公路的设施悬挂非公路标志许可（县级权限）
# 利用跨越公路的设施悬挂非公路标志许可（省级权限）
# 因修建铁路、机场、供电、水利、通信等建设工程需要占用、挖掘公路、公路用地或者使公路改线许可（省级权限）
# 跨越、穿越公路修建桥梁、渡槽或者架设、埋设管道、电缆等设施许可（县级权限）
# 跨越、穿越公路修建桥梁、渡槽或者架设、埋设管道、电缆等设施许可（省级权限）
# 在公路建筑控制区内埋设管道、电缆等设施许可（省级权限）
# 因修建铁路、机场、供电、水利、通信等建设工程需要占用、挖掘公路、公路用地或者使公路改线许可（县级权限）
# 在公路上增设或者改造平面交叉道口许可（县级权限）
# 在公路上增设或者改造平面交叉道口许可（省级权限）
# 在公路用地范围内架设、埋设管道、电缆等设施许可（县级权限）
# 在公路用地范围内架设、埋设管道、电缆等设施许可（省级权限）
# 在公路建筑控制区内埋设管道、电缆等设施许可（县级权限）
# 公路周边修筑堤坝、压缩或者拓宽河床许可
# 利用公路桥梁、公路隧道、涵洞铺设电缆等设施许可（县级权限）

except Exception as e:
    print("查询出错：", e)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()
