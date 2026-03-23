import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler


class Logger:
    """
    自定义日志类：
    1. 支持文件日志（每天轮转，保留指定天数）
    2. 支持控制台日志
    3. 可选：重定向 print() 和错误输出到日志文件
    """

    def __init__(self, name="MyLogger", log_dir="logs",
                 level=logging.INFO, redirect_print=True):
        """
        初始化日志系统
        :param name: 日志记录器名称（不同模块可用不同名字区分）
        :param log_dir: 日志存放目录
        :param level: 日志等级（默认 INFO）
        :param redirect_print: 是否把 print() 也写入日志
        """
        # 获取 Logger 对象（全局唯一，根据 name 区分）
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)  # 设置最低日志等级

        # 避免重复添加 handler（防止多次初始化时重复写日志）
        if not self.logger.handlers:
            # 1. 确保日志目录存在
            os.makedirs(log_dir, exist_ok=True)

            # 日志文件路径
            log_file = os.path.join(log_dir, f"{name}.log")

            # 2. 文件日志（每天 0 点生成新日志，保留 7 天）
            file_handler = TimedRotatingFileHandler(
                filename=log_file,
                when="midnight",     # 每天轮转
                interval=1,          # 时间间隔（1 天）
                backupCount=180,       # 保留 7 个旧日志文件
                encoding="utf-8"     # 支持中文
            )

            # 3. 设置日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)

            # 4. 控制台日志（同时在终端输出）
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            # 5. 把两个 handler 加到 logger 上
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        # 6. 是否重定向 print()
        if redirect_print:
            sys.stdout = self.PrintLogger(self.logger, logging.INFO)   # 普通输出 → INFO
            sys.stderr = self.PrintLogger(self.logger, logging.ERROR)  # 错误输出 → ERROR

    class PrintLogger:
        """
        替代 sys.stdout / sys.stderr 的类，
        把 print() 输出的内容写到日志里
        """
        def __init__(self, logger, level):
            self.logger = logger
            self.level = level

        def write(self, message):
            message = message.strip()
            if message:  # 避免空行
                self.logger.log(self.level, message)

        def flush(self):
            # 标准输出需要 flush()，这里保留接口即可
            pass

    def get_logger(self):
        """返回 logger 对象"""
        return self.logger
