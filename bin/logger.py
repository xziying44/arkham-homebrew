import logging
import os
import platform
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


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

    def _get_log_directory(self):
        """
        获取日志目录（兼容开发和打包环境）
        - macOS: 使用系统标准目录，更新安全
        - Windows: 使用运行目录，便携模式
        Returns:
            str: 日志目录的绝对路径
        """
        if getattr(sys, 'frozen', False):
            # 打包后的应用
            if platform.system() == 'Darwin':  # macOS
                # 使用系统标准目录，更新时不会被删除
                log_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'ArkhamCardMaker')
                os.makedirs(log_dir, exist_ok=True)

            elif platform.system() == 'Windows':  # Windows
                # Windows：便携模式，使用exe同级目录
                if hasattr(sys, '_MEIPASS'):
                    # PyInstaller 打包：exe 所在目录
                    exe_dir = os.path.dirname(sys.executable)
                else:
                    exe_dir = os.path.dirname(os.path.abspath(__file__))
                log_dir = os.path.join(exe_dir, 'logs')

            else:  # Linux 或其他系统
                log_dir = os.path.expanduser('~/Documents/ArkhamCardMaker/logs')
        else:
            # 开发环境
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            log_dir = project_root / 'logs'
        # 确保目录存在
        os.makedirs(log_dir, exist_ok=True)
        return str(log_dir)

    def _setup_logger(self):
        """设置日志系统"""
        try:
            # 获取日志目录
            log_dir = self._get_log_directory()

            # 确保日志目录存在
            os.makedirs(log_dir, exist_ok=True)

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

            # 记录日志系统初始化成功
            self._logger.info(f"日志系统初始化成功，日志目录: {log_dir}")

        except Exception as e:
            # 如果无法创建文件日志，回退到只使用控制台日志
            self._logger = logging.getLogger('Arkham')
            self._logger.setLevel(logging.INFO)

            # 清除handlers
            if self._logger.handlers:
                self._logger.handlers.clear()

            # 只使用控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            simple_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(simple_formatter)

            self._logger.addHandler(console_handler)

            # 记录警告
            self._logger.warning(f"无法初始化文件日志系统: {e}")
            self._logger.warning("回退到仅控制台日志模式")

    def get_logger(self):
        """获取logger实例"""
        return self._logger

    def debug(self, message):
        """记录DEBUG级别日志"""
        if self._logger:
            self._logger.debug(message)

    def info(self, message):
        """记录INFO级别日志"""
        if self._logger:
            self._logger.info(message)

    def warning(self, message):
        """记录WARNING级别日志"""
        if self._logger:
            self._logger.warning(message)

    def error(self, message, exc_info=False):
        """记录ERROR级别日志"""
        if self._logger:
            self._logger.error(message, exc_info=exc_info)

    def critical(self, message, exc_info=False):
        """记录CRITICAL级别日志"""
        if self._logger:
            self._logger.critical(message, exc_info=exc_info)

    def exception(self, message):
        """记录异常信息（包含堆栈）"""
        if self._logger:
            self._logger.exception(message)


# 全局日志管理器实例
logger_manager = LoggerManager()
