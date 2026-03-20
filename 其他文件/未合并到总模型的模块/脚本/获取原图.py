import os
import re
import shutil
import random
from datetime import datetime

# 原始图片文件夹
src_folder = "/data1/qwen2v/pic/yuantu"
# 保存的目标文件夹
dst_folder = "./selected"
os.makedirs(dst_folder, exist_ok=True)

# 匹配文件名正则
pattern = re.compile(r"camera_(\d+)_([\d\-]+)_(\d{2}-\d{2}-\d{2})\.jpg")

# 日期范围
start_date = datetime.strptime("2025-08-16", "%Y-%m-%d")
end_date   = datetime.strptime("2025-08-24", "%Y-%m-%d")

# 保存结果 {id: {date: [files]}}
id_date_files = {}

for fname in os.listdir(src_folder):
    match = pattern.match(fname)
    if match:
        cam_id, date, time = match.groups()
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            time_obj = datetime.strptime(time, "%H-%M-%S").time()
        except ValueError:
            continue
        if start_date <= date_obj <= end_date:
            id_date_files.setdefault(cam_id, {}).setdefault(date, []).append((fname, time_obj))

# 选择文件：保证白天晚上覆盖
selected_files = []
for cam_id, date_dict in id_date_files.items():
    for date, files in date_dict.items():
        # 拆分白天(06-18)和晚上(18-06)
        day_files = [f for f, t in files if 6 <= t.hour < 18]
        night_files = [f for f, t in files if t.hour < 6 or t.hour >= 18]

        chosen = []
        if day_files:
            chosen.append(random.choice(day_files))
        if night_files:
            chosen.append(random.choice(night_files))
        if not chosen and files:  # 如果没分出来，至少随便选一张
            chosen.append(random.choice([f for f, _ in files]))

        for chosen_file in chosen:
            src_path = os.path.join(src_folder, chosen_file)
            dst_path = os.path.join(dst_folder, chosen_file)
            shutil.copy2(src_path, dst_path)
            selected_files.append(dst_path)

print("已保存到目标文件夹：")
for f in selected_files:
    print(f)
