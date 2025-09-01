import requests
import json
import urllib3

# 忽略 HTTPS 证书警告
urllib3.disable_warnings()

BASE_URL = "https://10.212.160.158:8101/nvms8100/apploginVideo/initCameraTree.action"
PARAMS = {
    "signName": "bjjzdx",
    "userPwd": "ZFZDwxglwf@2025",
    "page": 1,
    "pageSize": 100,
    "deptId": ""  # 第一次请求为空，取根节点
}

all_nodes = []  # 存储所有节点信息


def fetch_nodes(dept_id=""):
    """递归抓取指定 deptId 下的节点信息"""
    params = PARAMS.copy()
    params["deptId"] = dept_id

    resp = requests.get(BASE_URL, params=params, verify=False)
    if resp.status_code != 200:
        print(f"请求失败: {resp.status_code}")
        return

    data = resp.json()
    if data.get("code") != 0:
        print(f"接口返回错误: {data}")
        return

    # 先取 titleList（通常是当前层的父节点）
    for node in data["data"].get("titleList", []):
        all_nodes.append({
            "id": node.get("id", ""),
            "name": node.get("name", ""),
            "cameraId": node.get("cameraId", ""),
            "type": node.get("type", "")
        })

    # 再取 list（子节点或摄像头列表）
    for node in data["data"].get("list", []):
        all_nodes.append({
            "id": node.get("id", ""),
            "name": node.get("name", ""),
            "cameraId": node.get("cameraId", ""),
            "type": node.get("type", "")
        })

        # 如果 type != 设备类型（例如 1 表示目录/分组），递归取子节点
        if node.get("type") == "1" and node.get("id"):
            fetch_nodes(node["id"])


if __name__ == "__main__":
    fetch_nodes("")  # 从根节点开始递归
    print(f"共抓取 {len(all_nodes)} 个节点")

    # 保存成 JSON 文件
    with open("camera_tree.json", "w", encoding="utf-8") as f:
        json.dump(all_nodes, f, ensure_ascii=False, indent=2)

    print("已保存到 camera_tree.json")
