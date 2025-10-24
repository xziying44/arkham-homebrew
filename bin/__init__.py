"""
bin - 后端核心业务逻辑模块

本模块包含Arkham Horror卡牌生成工具的核心后端功能，
负责文件管理、工作空间管理、卡牌导出和图像处理等任务。

主要组件:
- file_manager: 文件系统操作管理
- workspace_manager: 工作空间和项目管理
- deck_exporter: 卡组导出功能
- tts_card_converter: TTS格式转换
- gitHub_image: GitHub图像资源管理
- image_uploader: 图像上传处理
- content_package_manager: 内容包管理
- card2arkhamdb: 卡牌数据转换
- logger: 日志记录管理

作者: Arkham Horror DIY Team
版本: v2.9+
"""

__version__ = "2.9.0"
__author__ = "Arkham Horror DIY Team"

# 导出主要组件以便外部访问
from .file_manager import QuickStart
from .workspace_manager import WorkspaceManager
from .deck_exporter import DeckExporter
from .tts_card_converter import TTSCardConverter
from .content_package_manager import ContentPackageManager
from .config_directory_manager import ConfigDirectoryManager

__all__ = [
    'QuickStart',
    'WorkspaceManager',
    'DeckExporter',
    'TTSCardConverter',
    'ContentPackageManager',
    'ConfigDirectoryManager',
]
