import gradio as gr
import time
from datetime import datetime

from utils.order import (
    get_orders,
    update_order_list,
    on_select_order,
    update_order_details,
)
from utils.panel import create_trend_plot, create_heatmap, update_stats

with gr.Blocks(theme=gr.themes.Soft()) as app:

    with gr.Tabs() as tabs:

        # 首页仪表盘
        with gr.Tab("首页仪表盘"):

            # 上方统计表
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 总体统计")
                    with gr.Group():
                        total_cases = gr.Number(label="违法行为总数")
                        total_videos = gr.Number(label="监控视频数")
                        total_orders = gr.Number(label="工单总数")

                    refresh_btn = gr.Button("刷新数据", every=60, variant="primary")

                with gr.Column(scale=2):
                    gr.Markdown("### 违法行为趋势")
                    trend_plot = gr.Plot()

            # 下方地理分布图
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 地理分布")
                    map_plot = gr.Plot(value=create_heatmap())

            # 设置更新事件
            refresh_btn.click(
                fn=update_stats,
                outputs=[total_cases, total_videos, total_orders, trend_plot],
            )

        # 视频监控
        with gr.Tab("视频监控"):
            with gr.Row():
                # 4 路视频监控
                for i in range(4):
                    with gr.Column():
                        gr.Video(label=f"摄像头 {i+1}")

        # 非现场执法工单
        with gr.Tab("非现场执法工单"):
            with gr.Row():
                # 左侧筛选面板
                with gr.Column(scale=1):
                    gr.Markdown("### 筛选条件")
                    with gr.Row():
                        search_text = gr.Textbox(
                            label="搜索关键词", placeholder="输入工单编号、地点等..."
                        )
                    with gr.Row():
                        status_filter = gr.Dropdown(
                            choices=["全部", "待处理", "处理中", "已完成", "已驳回"],
                            value="全部",
                            label="处理状态",
                        )
                    with gr.Row():
                        start_date = gr.Textbox(
                            label="开始日期",
                            placeholder="YYYY-MM-DD",
                            value=datetime.now().strftime("%Y-%m-%d"),
                        )
                        end_date = gr.Textbox(
                            label="结束日期",
                            placeholder="YYYY-MM-DD",
                            value=datetime.now().strftime("%Y-%m-%d"),
                        )
                    filter_btn = gr.Button("应用筛选", variant="primary")
                    refresh_btn = gr.Button("刷新违法行为列表", variant="primary")
                    gr.HTML("</div>")

                # 右侧工单列表
                with gr.Column(scale=3):
                    gr.Markdown("### 违法行为列表")
                    # 工单数据表格
                    orders_table = gr.Dataframe(value=get_orders(), interactive=False)

                    gr.HTML("</div>")

            # 工单详情面板
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 案件详情")
                    with gr.Row():
                        # 左侧违法图片
                        violation_image = gr.Image(
                            label="违法图片", interactive=False, value=None
                        )

                        # 右侧工单信息
                        with gr.Column():
                            order_id = gr.Textbox(label="工单编号", interactive=False)
                            violation_type = gr.Textbox(
                                label="违法类型", interactive=False
                            )
                            location = gr.Textbox(label="发生地点", interactive=False)
                            time = gr.Textbox(label="发生时间", interactive=False)
                            status = gr.Dropdown(
                                choices=["待处理", "处理中", "已完成", "已驳回"],
                                label="处理状态",
                            )
                            handler = gr.Textbox(label="处理人", interactive=True)
                            remark = gr.Textbox(label="处理备注", lines=3)
                            update_btn = gr.Button("更新工单", variant="primary")
                            update_result = gr.Text(label="更新结果")

                    gr.HTML("</div>")

            # 应用筛选按钮事件
            filter_btn.click(
                fn=update_order_list,
                inputs=[search_text, status_filter, start_date, end_date],
                outputs=[orders_table],
            )

            # 刷新工单列表按钮事件
            refresh_btn.click(fn=get_orders, outputs=[orders_table])

            # 点击表格行显示详情
            orders_table.select(
                fn=on_select_order,
                inputs=[orders_table],
                outputs=[
                    violation_image,
                    order_id,
                    violation_type,
                    location,
                    time,
                    status,
                    handler,
                    remark,
                ],
            )

            # 更新工单事件
            update_btn.click(
                fn=update_order_details,
                inputs=[order_id, status, handler, remark],
                outputs=[update_result, orders_table],
            )

    # 当页面加载时更新统计数据和趋势图
    def on_page_load():
        orders = get_orders()
        stats = update_stats()
        return [orders, *stats]

    app.load(
        fn=on_page_load,
        outputs=[orders_table, total_cases, total_videos, total_orders, trend_plot],
    )

app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    allowed_paths=["/data1/qwen2v/"],
)
