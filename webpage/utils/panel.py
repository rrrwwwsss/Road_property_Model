from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


from .order import get_orders


# 生成模拟数据
def generate_violation_data():
    # 生成最近30天的日期
    dates = [
        (datetime.now() - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(30)
    ]
    dates.reverse()
    df = get_orders()
    df["日期"] = pd.to_datetime(df["发生时间"], format="%Y%m%d_%H%M%S").dt.strftime(
        "%Y-%m-%d"
    )

    # 违法类型映射
    type_map = {
        "占用和挖掘公路": "非法占用或挖掘公路",
        "擅自占用、挖掘公路": "非法占用或挖掘公路",
        "井盖缺失": "移动井盖",
        "井盖移动或缺失": "移动井盖",
        "悬挂非公路标志": "公路附属设施架设管道、悬挂物品",
        "放置公路标志": "放置非公路标志",
        "设置非公路标志": "放置非公路标志",
    }
    df["违法类型映射"] = df["违法类型"].map(type_map)

    # 构造近30天日期列表（从今天往前推）
    recent_dates = [
        (datetime.now() - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(30)
    ]
    recent_dates.reverse()

    # 过滤近30天数据
    df_recent = df[df["日期"].isin(recent_dates)]

    # 按日期和违法类型统计数量
    result = df_recent.groupby(["日期", "违法类型映射"]).size().unstack(fill_value=0)

    # 补全日期（没有记录的日期设为0）
    result = result.reindex(recent_dates, fill_value=0)
    result.reset_index(inplace=True)
    result = result.rename(columns={"index": "日期"})
    return result


# 生成趋势图
def create_trend_plot():
    df = generate_violation_data()
    fig = go.Figure()

    # 添加每种违法类型的线
    for column in df.columns[1:]:
        fig.add_trace(
            go.Scatter(x=df["日期"], y=df[column], name=column, mode="lines+markers")
        )

    fig.update_layout(
        title="近30天违法行为趋势",
        xaxis_title="日期",
        yaxis_title="违法数量",
        height=400,
        template="plotly_white",
        xaxis_tickformat="%Y年%m月%d日",
    )
    return fig


# 生成地理分布热力图
def create_heatmap():
    # 模拟一些地理坐标点和违法数量
    lat = np.random.uniform(39.8, 40.0, 50)  # 北京市的大致纬度范围
    lon = np.random.uniform(116.2, 116.5, 50)  # 北京市的大致经度范围
    violations = np.random.randint(1, 100, 50)

    df = pd.DataFrame({"lat": lat, "lon": lon, "violations": violations})

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        size="violations",  # 使用圆点大小表示违法数量
        color="violations",  # 使用颜色深浅表示违法数量
        color_continuous_scale="Reds",
        zoom=10,
        center=dict(lat=39.9, lon=116.35),
        mapbox_style="open-street-map",
    )  # 使用 OpenStreetMap

    fig.update_layout(
        title="违法行为地理分布图", height=400, margin={"r": 0, "t": 30, "l": 0, "b": 0}
    )
    return fig


# 更新统计数据的函数
def update_stats():
    df = get_orders()
    # 返回统计数据和趋势图
    return len(df), 31, len(df), create_trend_plot()
