import os
import pandas as pd
import requests

from config.数据库配置 import DISTRICT_CODE
from config.配置 import CAMERA_DATA, BASE_URL, CAMERA_RESULT_DATA
# 设置显示所有行和列
pd.set_option('display.max_rows', None)       # 显示所有行
pd.set_option('display.max_columns', None)    # 显示所有列
pd.set_option('display.width', 1000)          # 设置横向宽度，避免换行
pd.set_option('display.max_colwidth', None)   # 显示所有列内容，尤其是长字符串

# 获取摄像头id
def get_camera_id(camera_name: str) -> str:
    # 构造 URL
    base_url = BASE_URL + "/searchCamera.action"
    params = {
        "signName": "bjjzdx",
        "userPwd": "ZFZDwxglwf@2025",
        "page": 1,
        "pageSize": 10,
        "cameraName": camera_name
    }

    try:
        # 发出 GET 请求（忽略证书验证）
        response = requests.get(base_url, params=params, verify=False)
        response.raise_for_status()
        result = response.json()

        # 提取 cameraId
        cameras = result.get("data", {}).get("list", [])
        if cameras:
            camera_id = cameras[0].get("cameraId", "")
            print(f"摄像机ID: {camera_id}")
            return camera_id
        else:
            print("未找到摄像机")
            return ""
    except Exception as e:
        print(f"请求失败: {e}")
        return ""
def extract_district_code(s):
    for name, code in DISTRICT_CODE.items():
        if name in str(s):
            return code
    return ''  # 没匹配上返回空
def get_dianwei_data():
    if os.path.exists(CAMERA_RESULT_DATA):
        print("文件已存在，直接读取")
        # 例如读取已有数据
        df = pd.read_csv(CAMERA_RESULT_DATA)
        # print("整合数据后的摄像头点位表",df)
        return df
    else:
        print("文件不存在，执行新的查询逻辑")
        # 例如重新生成 DataFrame 和调用 get_camera_id()
        df = pd.read_excel(CAMERA_DATA)

        # 用前一个非空值填充合并单元格带来的空值
        df = df.ffill()
        # 提取指定列
        cols = ['所属支队', '具备视频分析条件的点位', '可能会存在的违法行为', '是否可用']
        df_selected = df[cols]


        # 添加辖区编码列
        df_selected['辖区编码'] = df_selected['所属支队'].apply(extract_district_code)

        # 添加监控id列
        # 初始化缓存
        camera_id_cache = {}

        # 存储每行对应的摄像机ID
        camera_id_list = []

        for name in df_selected['具备视频分析条件的点位']:
            if pd.isna(name) or str(name).strip() == '':
                camera_id_list.append(None)
                continue

            name_str = str(name).strip()

            if name_str not in camera_id_cache:

                # 请求接口并缓存
                camera_id = get_camera_id(name_str)
                camera_id_cache[name_str] = camera_id
            else:
                camera_id = camera_id_cache[name_str]

            camera_id_list.append(camera_id)

        # 添加新列
        df_selected['camera_id'] = camera_id_list #camera_id_list是长度和df_selected行数一致的列表,会填充到df_selected的列中

        # 可选：保存结果
        df_selected.to_csv(CAMERA_RESULT_DATA, index=False)

        # 查看结果
        # print("整合数据后的摄像头点位表",df_selected)
        return df_selected

if __name__ == '__main__':
    get_dianwei_data()
