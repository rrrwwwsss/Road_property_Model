import json
import os
import re
from PIL import Image, ImageDraw
# 从文本中安全解析出 [xmin, ymin, xmax, ymax] 的边框数据
def safe_json_parse(output_text):
    print("大模型返回值：", output_text)
    if isinstance(output_text, dict):
        # 已经是字典了，直接返回
        return output_text
    if isinstance(output_text, str):
        output_text = output_text.strip()

        # 提取所有完整的 [..., ..., ..., ...] 结构
        boxes = re.findall(r'\[\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\]', output_text)

        # 重新构建 JSON
        if boxes:
            valid_json = f'{{"result": "yes", "bounding_boxes": [{",".join(boxes)}]}}'
            try:
                return json.loads(valid_json)
            except json.JSONDecodeError:
                pass

    # 默认返回
    return {"result": "no", "bounding_boxes": []}
# 在图像上绘制边框
def draw_bounding_boxes(image, bounding_boxes, outline_color="red", line_width=3):
    draw = ImageDraw.Draw(image)
    for box in bounding_boxes:
        try:
            xmin, ymin, xmax, ymax = box
            draw.rectangle([xmin, ymin, xmax, ymax], outline=outline_color, width=line_width)
        except Exception as e:
            # 可选打印调试信息
            # print(f"Error drawing box {box}: {e}")
            continue  # 跳过当前出错的框
    return image

# 将缩放后的框坐标还原到原图尺度
def rescale_bounding_boxes(bounding_boxes, original_width, original_height, scaled_width=1000, scaled_height=1000):
    x_scale = original_width / scaled_width
    y_scale = original_height / scaled_height
    rescaled_boxes = []
    for box in bounding_boxes:
        xmin, ymin, xmax, ymax = box
        rescaled_box = [
            xmin * x_scale,
            ymin * y_scale,
            xmax * x_scale,
            ymax * y_scale
        ]
        rescaled_boxes.append(rescaled_box)
    return rescaled_boxes

def jiance_imgtype(frame):
    # 情况1: 是字符串（路径）
    if isinstance(frame, str):
        if os.path.isfile(frame) and frame.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
            image_list = [frame]
        else:
            print(f"无效图像路径: {frame}")
            return  # 或 raise

    # 情况2: 是单个 PIL Image
    elif isinstance(frame, Image.Image):
        image_list = [frame]

    # 情况3: 是图像列表（路径或 PIL Image）
    elif isinstance(frame, (list, tuple)):
        image_list = []
        for item in frame:
            if isinstance(item, str) and os.path.isfile(item) and item.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                image_list.append(item)
            elif isinstance(item, Image.Image):
                image_list.append(item)
            else:
                print(f"跳过无效图像项: {item}")

    # 情况4: None 或其他无效类型
    else:
        print(f"无法处理的输入类型: {type(frame)}, 值: {frame}")
        return  # 安静退出，不报错

    if not image_list:
        print("未找到有效图像，跳过处理")
        return

    print(f"发现 {len(image_list)} 个图像需要处理...")
    return image_list
