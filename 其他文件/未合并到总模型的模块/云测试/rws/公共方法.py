import json
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