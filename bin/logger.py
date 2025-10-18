import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class LoggerManager:
    """日志管理器，提供统一的日志记录功能"""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self):
        """设置日志系统"""
        # 创建日志目录
        log_dir = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 生成日志文件名（按日期命名）
        log_filename = datetime.now().strftime('%Y-%m-%d.log')
        log_path = os.path.join(log_dir, log_filename)

        # 创建logger
        self._logger = logging.getLogger('Arkham')
        self._logger.setLevel(logging.DEBUG)

        # 清除已存在的handlers（避免重复）
        if self._logger.handlers:
            self._logger.handlers.clear()

        # 创建文件handler（支持日志轮转，单个文件最大10MB，保留5个备份）
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # 创建控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 创建formatter
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 设置formatter
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)

        # 添加handler
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    def get_logger(self):
        """获取logger实例"""
        return self._logger

    def debug(self, message):
        """记录DEBUG级别日志"""
        self._logger.debug(message)

    def info(self, message):
        """记录INFO级别日志"""
        self._logger.info(message)

    def warning(self, message):
        """记录WARNING级别日志"""
        self._logger.warning(message)

    def error(self, message, exc_info=False):
        """记录ERROR级别日志"""
        self._logger.error(message, exc_info=exc_info)

    def critical(self, message, exc_info=False):
        """记录CRITICAL级别日志"""
        self._logger.critical(message, exc_info=exc_info)

    def exception(self, message):
        """记录异常信息（包含堆栈）"""
        self._logger.exception(message)


# 全局日志管理器实例
logger_manager = LoggerManager()
