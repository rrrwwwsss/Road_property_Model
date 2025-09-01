from datetime import datetime, timedelta
import pandas as pd
import gradio as gr

order_path = "../result.csv"

def read_csv(file_path):
    #try:
        # 尝试使用 GBK 编码读取文件
    #    df = pd.read_csv(file_path, encoding='gbk')
    #except UnicodeDecodeError:
        # 如果GBK失败，尝试使用 UTF-8 编码读取
    df = pd.read_csv(file_path, encoding='utf-8')
    return df

def get_orders():
    orders = read_csv(order_path)
    return orders


def filter_orders(orders, search_text="", status_filter="全部", start_date=None, end_date=None):
    """筛选工单"""
    filtered = orders.copy()

    if search_text:
        mask = filtered.apply(lambda row: search_text.lower() in ' '.join(row.astype(str)).lower(), axis=1)
        filtered = filtered[mask]

    if status_filter != "全部":
        filtered = filtered[filtered["处理状态"] == status_filter]

    if start_date and end_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            filtered = filtered[
                (pd.to_datetime(filtered["发生时间"], format="%Y%m%d_%H%M%S") >= start_datetime) &
                (pd.to_datetime(filtered["发生时间"], format="%Y%m%d_%H%M%S") < end_datetime)
            ]
        except ValueError:
            # 如果日期格式不正确，忽略日期筛选
            pass

    return filtered

def update_order_details(order_id, new_status, handler, remark):
    """更新工单状态和处理信息"""
    if not order_id:
        return "请先选择工单"

    # 这里应该是数据库更新操作，现在用打印模拟
    update_info = f"""
    工单更新:
    - 工单号: {order_id}
    - 新状态: {new_status}
    - 处理人: {handler}
    - 备注: {remark}
    """
    df = read_csv(order_path)
    # 修改 "处理状态"、"处理人" 和 "处理备注"
    df.loc[df["工单编号"] == order_id, ["处理状态", "处理人", "处理备注"]] = [new_status, handler, remark]
    
    # 保存更新后的数据到 CSV 文件
    df.to_csv(order_path, index=False)
     #从csv重新加载数据
    new_orders = get_orders()
    
    return "工单更新成功", new_orders

def update_order_list(search_text, status_filter, start_date, end_date):
    """更新工单列表"""

    orders = get_orders()  # 实际应用中从数据库获取
    filtered_orders = filter_orders(orders, search_text, status_filter, start_date, end_date)
    return filtered_orders

def on_select_order(evt: gr.SelectData, orders_table):
    """当选择表格行时触发"""
    selected_row = orders_table.iloc[evt.index[0]]
    
    return [
        selected_row["path"],
        selected_row["工单编号"],
        selected_row["违法类型"],
        selected_row["发生地点"],
        selected_row["发生时间"],
        selected_row["处理状态"],
        selected_row["处理人"],
        selected_row["处理备注"]
    ]
