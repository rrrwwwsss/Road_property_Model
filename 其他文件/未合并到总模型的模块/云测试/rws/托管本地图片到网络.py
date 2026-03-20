from flask import Flask, send_from_directory, abort
import os

# 需要托管的根文件夹
BASE_DIR = './pic_pack'

app = Flask(__name__)

@app.route('/')
def list_images():
    """列出 pic_pack 下所有子文件夹的图片"""
    image_links = []

    for root, dirs, files in os.walk(BASE_DIR):
        # folder_name 只取相对于 BASE_DIR 的子文件夹名
        folder_name = os.path.relpath(root, BASE_DIR)  # 相对路径
        if folder_name == '.':
            folder_name = ''  # 根目录的图片不加文件夹
        for img in files:
            if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
                url_path = f'/preview/{folder_name}/{img}' if folder_name else f'/preview/{img}'
                display_path = f'{folder_name}/{img}' if folder_name else img
                image_links.append(f'<a href="{url_path}">{display_path}</a><br>')

    return "<h1>图片列表</h1>" + "".join(image_links)


@app.route('/preview/<path:folder>/<path:filename>')
@app.route('/preview/<path:filename>', defaults={'folder': ''})
def preview_image(folder, filename):
    """返回图片文件"""
    file_path = os.path.join(BASE_DIR, folder, filename)

    if not os.path.isfile(file_path):
        abort(404)

    return send_from_directory(os.path.join(BASE_DIR, folder), filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
