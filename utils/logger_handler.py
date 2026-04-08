import logging
from utils.path_tool import get_abs_path
import os
from datetime import datetime
import logging.handlers  # 👈 新增导入

# 日志保存的根目录
LOG_ROOT = get_abs_path("logs")
os.makedirs(LOG_ROOT, exist_ok=True)

# 日志格式
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)


def get_logger(
    name: str = "agent",
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加 Handler
    if logger.handlers:
        return logger

    # 控制台 Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)

    # ✅ 使用 TimedRotatingFileHandler 实现每日新文件
    log_file = os.path.join(LOG_ROOT, f"{name}.log")  # 不需要手动加日期！
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',      # 每天午夜（00:00）轮转
        interval=1,           # 每1个单位时间轮转一次
        backupCount=30,       # 保留最近30天的日志文件
        encoding='utf-8',
        utc=False             # 使用本地时间（非UTC）
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    file_handler.suffix = "%Y%m%d"  # 轮转后的文件后缀格式，如 agent.log.20260401

    # 可选：让日志文件名更干净（去掉点）
    # file_handler.namer = lambda name: name.replace(".log.", ".log_")

    logger.addHandler(file_handler)

    return logger


logger = get_logger()


if __name__ == '__main__':
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告日志")
    logger.debug("调试日志")