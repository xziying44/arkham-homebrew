"""
rich_text_render - 富文本渲染模块

本模块提供Arkham Horror卡牌文本的高级渲染功能，
支持HTML富文本解析、虚拟文本框和复杂的文本布局处理。

主要组件:
- HtmlTextParser.py: HTML富文本解析器
- RichTextRenderer.py: 富文本渲染核心引擎
- VirtualTextBox.py: 虚拟文本框和布局管理

特性:
- HTML标签解析和渲染
- 复杂文本布局支持
- 动态文本框调整
- 多语言文本处理
- 卡牌规则文本格式化

作者: Arkham Horror DIY Team
版本: v2.9+
"""

__version__ = "2.9.0"
__author__ = "Arkham Horror DIY Team"

# 导出主要组件以便外部访问
from .HtmlTextParser import TextType
from .HtmlTextParser import ParsedItem
from .HtmlTextParser import RichTextParser
from .RichTextRenderer import RichTextRenderer
from .VirtualTextBox import VirtualTextBox

__all__ = [
    'TextType',
    'ParsedItem',
    'RichTextParser',
    'RichTextRenderer',
    'VirtualTextBox'
]