"""
export_helper - 高级导出功能模块

本模块提供Arkham Horror卡牌生成工具的高级导出功能，
包括AI出血处理、图像优化和导出增强等特性。

主要组件:
- main.py: 导出助手主程序入口
- LamaCleaner.py: AI出血和图像清理功能

特性:
- AI驱动的图像出血处理
- 智能背景清理和优化
- 高质量图像导出
- 批量处理支持

作者: Arkham Horror DIY Team
版本: v2.9+
"""

__version__ = "2.9.0"
__author__ = "Arkham Horror DIY Team"

# 导出主要组件以便外部访问
from .LamaCleaner import LamaCleaner

__all__ = [
    'LamaCleaner'
]