import ast

import cv2
import numpy as np
import pandas as pd
from PIL import Image

def apply_mosaic_on_polygon(pil_image, points, kernel_size=(15, 15)):

        # 读取图像
    # image = cv2.imread(image_path)
    # 将 Pillow 图像转换为 OpenCV 图像
    image = np.array(pil_image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # 转换为 BGR 格式
    # 创建一个与原图大小相同的空白掩膜
    mask = np.zeros_like(image)

    # 将四边形区域填充为白色
    cv2.fillPoly(mask, [np.array(points, dtype=np.int32)], (255, 255, 255))

    # 提取需要处理的区域
    masked_image = cv2.bitwise_and(image, mask)

    # 获取需要处理区域的边界框
    x, y, w, h = cv2.boundingRect(np.array(points))

    # 提取不规则区域
    region = masked_image[y:y + h, x:x + w]
    region[:] = (0, 0, 0)
    # 对该区域进行高斯模糊处理
    # blurred_region = cv2.GaussianBlur(region, kernel_size, 4)
    # print(blurred_region)
    # 将模糊后的区域合并回原图
    image[y:y + h, x:x + w] = cv2.bitwise_and(image[y:y + h, x:x + w], ~mask[y:y + h, x:x + w]) + region

    # 转换 OpenCV 图像到 Pillow 图像
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    pil_image.save("加黑框.jpg")
    print("已对该区域做遮挡处理")
    # # 显示处理后的图片
    # cv2.imshow("Mosaic Image", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    #
    # # 保存处理后的图片
    # cv2.imwrite("mosaic_image.jpg", image)
    return pil_image

if __name__ == "__main__":
    def get_points_from_csv(csv_path, target_location):
        # 读取 CSV 文件
        df = pd.read_csv(csv_path)

        # 查找目标位置的行
        target_row = df[df['点位'] == target_location]  # 假设列名是 '位置'

        if not target_row.empty:
            # 获取 '区域' 列的值（假设列名是 '区域'）
            region_str = target_row['区域'].values[0]

            # 将字符串转换为 Python 列表
            points = ast.literal_eval(region_str)
            return points
        else:
            print(f"未找到指定位置: {target_location}")
            return None


    # 示例使用
    csv_path = 'data/悬挂物剔除区域.csv'  # 替换为你的 CSV 文件路径
    target_location = 'S219南雁路K0+000上行西大桥西'

    points = get_points_from_csv(csv_path, target_location)
    # 使用示例
    # 定义四边形的四个顶点 (不规则形状)
    # points = [(0, 110), (0, 450), (1910, 584), (1905, 14)]#按顺序点点

    pil_image = apply_mosaic_on_polygon("未合并到总模型的模块/camera_11000000001319850899_20251116_074837.jpg", points, kernel_size=(15, 15))
    pil_image.show()
