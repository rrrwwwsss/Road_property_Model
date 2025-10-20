import subprocess
import time
from datetime import datetime

log_file = "npu_usage_log.txt"

def get_npu_info(npu_id):
    """获取单个NPU的Aicore与HBM占用率"""
    cmd = f"npu-smi info -t usages -i {npu_id}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout

    aicore, hbm = None, None
    for line in output.splitlines():
        if "Aicore Usage Rate" in line:
            aicore = line.split(":")[-1].strip().replace("%", "")
        elif "HBM Usage Rate" in line:
            hbm = line.split(":")[-1].strip().replace("%", "")
    return aicore, hbm


def log_npu_usage():
    """循环监控所有NPU"""
    with open(log_file, "a") as f:
        f.write("时间, NPU_ID, Aicore使用率(%), HBM使用率(%)\n")
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for npu_id in range(8):  # 假设8张卡
                aicore, hbm = get_npu_info(npu_id)
                if aicore is not None:
                    line = f"{timestamp}, {npu_id}, {aicore}, {hbm}\n"
                    f.write(line)
                    f.flush()
                    print(line.strip())
            time.sleep(2)


if __name__ == "__main__":
    print("开始监控所有 NPU 的资源使用情况，按 Ctrl+C 停止。")
    try:
        log_npu_usage()
    except KeyboardInterrupt:
        print("\n监控已停止，日志已保存到 npu_usage_log.txt")
