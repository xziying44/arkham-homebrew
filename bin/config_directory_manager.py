# bin/config_directory_manager.py
import os
import platform
import sys
from typing import Optional


class ConfigDirectoryManager:
    """
    配置目录管理器
    统一管理应用的各种配置和数据目录
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigDirectoryManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._system = platform.system()
        self._is_frozen = getattr(sys, 'frozen', False)
        self._app_name = "ArkhamCardMaker"

        # 初始化所有目录路径
        self._init_directories()

    def _init_directories(self):
        """初始化所有目录路径"""
        try:
            # 确保所有目录都存在
            self._ensure_directory_exists(self.get_global_config_dir())
            self._ensure_directory_exists(self.get_logs_dir())
        except Exception as e:
            print(f"初始化配置目录失败: {e}")

    def _ensure_directory_exists(self, directory: str) -> bool:
        """确保目录存在，不存在则创建"""
        try:
            os.makedirs(directory, exist_ok=True)

            # 检查目录是否可写
            if not os.access(directory, os.W_OK):
                print(f"警告: 目录没有写入权限: {directory}")
                return False

            return True
        except Exception as e:
            print(f"创建目录失败 {directory}: {e}")
            return False

    def _get_user_data_dir(self) -> str:
        """获取用户数据目录的基础路径"""
        if self._is_frozen:
            # 打包应用
            if self._system == 'Darwin':  # macOS
                return os.path.join(os.path.expanduser('~'), 'Documents', self._app_name)
            elif self._system == 'Windows':  # Windows
                # Windows便携模式：使用exe同级目录
                exe_dir = os.path.abspath(".")
                return exe_dir
            else:  # Linux
                return os.path.expanduser(f'~/.config/{self._app_name.lower()}')
        else:
            return os.path.abspath(".")

    def get_global_config_dir(self) -> str:
        """获取全局配置目录"""
        return self._get_user_data_dir()

    def get_global_config_file_path(self) -> str:
        """获取全局配置文件路径"""
        return os.path.join(self.get_global_config_dir(), 'global_config.json')

    def get_logs_dir(self) -> str:
        """获取日志目录"""
        return os.path.join(self._get_user_data_dir(), 'logs')

    def get_recent_directories_file_path(self) -> str:
        """获取最近目录记录文件路径"""
        return os.path.join(self.get_global_config_dir(), 'recent_directories.json')

    def get_tts_save_directory(self) -> Optional[str]:
        """获取TTS保存目录，不存在则创建"""
        try:
            if self._system != 'Windows':
                return None

            # 获取我的文档路径
            user_home = os.path.expanduser("~")
            documents_path = os.path.join(user_home, "Documents")

            # 如果Documents目录不存在，尝试中文版本
            if not os.path.exists(documents_path):
                documents_path = os.path.join(user_home, "文档")

            if not os.path.exists(documents_path):
                print("无法找到我的文档目录")
                return None

            # 构建完整路径
            tts_path = os.path.join(
                documents_path,
                "My Games",
                "Tabletop Simulator",
                "Saves",
                "Saved Objects",
                "阿卡姆姬制作"
            )

            # 创建目录
            if self._ensure_directory_exists(tts_path):
                return tts_path
            else:
                return None

        except Exception as e:
            print(f"获取TTS保存目录失败: {e}")
            return None

    def get_system_info(self) -> dict:
        """获取系统信息"""
        return {
            'system': self._system,
            'is_frozen': self._is_frozen,
            'app_name': self._app_name,
            'user_data_dir': self._get_user_data_dir(),
            'config_dir': self.get_global_config_dir(),
            'logs_dir': self.get_logs_dir()
        }


# 创建全局实例
config_dir_manager = ConfigDirectoryManager()
