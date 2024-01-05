from loguru import logger as loguru_logger
import sys

class TestLogger:
    def __init__(self, log_path="logs"):

        self.errors = []
        self.logs = []
        self.special_logs = []
        self.step_counter = 0
        loguru_logger.remove()
        t = "today"  # 这里可以设置成您需要的日期格式
        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <red>{message}</red>"
        loguru_logger.add(f"{log_path}/interface_log_{t}.log",
                          rotation="10MB",
                          encoding="utf-8",
                          enqueue=True,
                          retention="10 Days",
                          format=log_format)
        loguru_logger.add(f"{log_path}/special_log_{t}.log",
                          level="INFO",
                          rotation="1MB",
                          encoding="utf-8",
                          enqueue=True,
                          retention="7 Days",
                          format=log_format)
        loguru_logger.add(sys.stderr, format=log_format, level="INFO")

    def error(self, message):
        """记录错误消息"""
        self.step_counter += 1
        self.errors.append("步骤:{}".format(self.step_counter)+ message + "<br>")
        #self.log(f"ERROR: {message}")
        loguru_logger.error(message)

    def log(self, message):
        """记录常规日志消息"""
        self.step_counter += 1
        loguru_logger.info(message)  # 使用loguru的info方法记录日志
        self.logs.append("步骤:{}-".format(self.step_counter)+message + "<br>")

    def special(self, message):
        loguru_logger.info(message)  # 使用loguru的info方法记录日志
        self.special_logs.append(message + "<br>")  # 仅添加到special_logs

    def get_logs(self):
        """返回所有常规日志条目"""
        return "\n".join(self.logs)
    def has_errors(self):
        """检查是否有错误消息"""
        return bool(self.errors)

    def display_errors(self):
        """打印所有错误消息"""
        for error in self.errors:
            print(error)

    def set_device_description(self, description):
        self.device_description = description

    def get_device_description(self):
        return getattr(self, 'device_description', '未知设备')

    def clear(self):
        """清除所有日志和错误消息"""
        self.errors = []
        self.logs = []
        self.special_logs = []
        self.step_counter = 0
loger = TestLogger()