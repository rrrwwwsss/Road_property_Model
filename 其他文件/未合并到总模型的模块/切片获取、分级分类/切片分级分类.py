import time
from concurrent.futures import ThreadPoolExecutor
# 导入你的截帧函数
from services.摄像头截帧 import capture_frame_from_camera

# 点位配置
HIGH_FREQ_CAMERAS = ["cam_h_01", "cam_h_02", "cam_h_03"]
MEDIUM_FREQ_CAMERAS = ["cam_m_01", "cam_m_02", "cam_m_03"]
LOW_FREQ_CAMERAS = ["cam_l_01", "cam_l_02", "cam_l_03"]

# 记录每个摄像头的最后一次派发时间 (初始为 0，保证启动时所有点位都属于"极度饥渴"状态，立刻执行)
last_run_time = {cam: 0 for cam in (HIGH_FREQ_CAMERAS + MEDIUM_FREQ_CAMERAS + LOW_FREQ_CAMERAS)}

# 记录当前正在截帧的摄像头，避免同一个摄像头被同时拉流 2 次
running_cams = set()


def task_wrapper(camera_id):
    """包装截帧函数，处理返回值并捕获异常，防止线程池崩溃"""
    try:
        # print(f"[{time.strftime('%H:%M:%S')}] 线程开始截帧 -> {camera_id}")
        result = capture_frame_from_camera(camera_id)
        return camera_id, True, result
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] 摄像头 {camera_id} 截帧出错: {e}")
        return camera_id, False, None


def main():
    print("🚀 启动无等待极速轮询模式，最高并发: 8")

    executor = ThreadPoolExecutor(max_workers=8)
    futures = set()

    try:
        while True:
            # 1. 检查并清理已完成的任务，释放并发槽位
            done_futures = [f for f in futures if f.done()]
            for f in done_futures:
                cam_id, success, result = f.result()
                futures.remove(f)
                running_cams.remove(cam_id)

                # 如果截帧成功（有返回图像），你可以在这里加入送入千问大模型的代码
                if success and result:
                    img, current_time = result
                    # do_something_with_model(img)

            # 2. 只要并发槽位不满 8 个，立刻无缝补充新任务！
            while len(futures) < 8:
                now = time.time()
                next_cam = None

                # 优先级 1: 找出距离上次截帧超过 5 分钟 (这里用 290 秒，留10秒余量) 的【高频】摄像头
                for cam in HIGH_FREQ_CAMERAS:
                    if cam not in running_cams and (now - last_run_time[cam]) >= 290:
                        next_cam = cam
                        break

                # 优先级 2: 如果高频不急，全速狂飙【中频】摄像头
                if not next_cam and MEDIUM_FREQ_CAMERAS:
                    available_medium = [c for c in MEDIUM_FREQ_CAMERAS if c not in running_cams]
                    if available_medium:
                        # 挑选出等待时间最长（last_run_time 最小）的中频摄像头，保证雨露均沾
                        next_cam = min(available_medium, key=lambda c: last_run_time[c])

                # 优先级 3: 如果中频也截完了（或没有中频），全速填补【低频】摄像头
                if not next_cam and LOW_FREQ_CAMERAS:
                    available_low = [c for c in LOW_FREQ_CAMERAS if c not in running_cams]
                    if available_low:
                        next_cam = min(available_low, key=lambda c: last_run_time[c])

                # 分配任务并占据并发槽位
                if next_cam:
                    running_cams.add(next_cam)
                    last_run_time[next_cam] = now  # 更新它的最后派发时间
                    f = executor.submit(task_wrapper, next_cam)
                    futures.add(f)
                else:
                    # 如果所有摄像头都在 running_cams 里，说明任务全在跑，跳出循环
                    break

            # 极短休眠（0.05秒）只为防止 CPU while True 产生 100% 的空转占用，丝毫不影响网络和拉流的速度
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("系统正在关闭...")
        executor.shutdown(wait=False)


if __name__ == "__main__":
    main()