from flask import Flask, send_from_directory, abort
from config.配置 import *
# 初始化 Flask 应用
app = Flask(__name__)

# 定义图片存储目录（多个文件夹）
IMAGE_DIRS = [
    YUANTU_PATH,
    WUPIN_PATH ,
    BAITAN_PATH ,
    GONGBIAO_PATH ,
    WAJUE_PATH,
    JINGGAI_PATH,
    XVANGUA_PATH
]

# 路由：访问根路径时列出所有图片及其链接
@app.route('/')
def list_images():
    import os
    image_links = []

    for folder in IMAGE_DIRS:
        if os.path.exists(folder):  # 确保文件夹存在
            images = os.listdir(folder)  # 获取文件夹中的所有文件
            folder_name = os.path.basename(folder)  # 获取文件夹名称
            for img in images:
                if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # 生成图片链接，包含文件夹路径信息
                    image_links.append(f'<a href="/preview/{folder_name}/{img}">{img}</a><br>')

    return "<h1>图片列表</h1>" + "".join(image_links)

@app.route('/preview/<path:folder>/<path:filename>')
def preview_image(folder, filename):
    import os
    # 拼接完整的文件路径
    base_dir = DATA_BASE_PATH
    file_path = os.path.join(base_dir, folder, filename)

    # 检查文件是否存在
    if not os.path.isfile(file_path):
        abort(404)  # 如果文件不存在，返回 404 错误

    # 返回图片文件
    return send_from_directory(os.path.join(base_dir, folder), filename)
def run_flask_server():
    app.run(host='0.0.0.0', port=5000)
# 启动应用
if __name__ == '__main__':
    run_flask_server()