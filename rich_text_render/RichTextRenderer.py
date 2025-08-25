from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
from Card import FontManager, ImageManager
from rich_text_render.HtmlTextParser import RichTextParser, TextType
from rich_text_render.VirtualTextBox import VirtualTextBox, TextObject, ImageObject

from typing import Dict, Tuple, Any

from PIL import ImageFont

# 定义一个类型别名，让代码更清晰
FreeTypeFont = ImageFont.FreeTypeFont


class FontStack:
    """
    一个管理 PIL.ImageFont.FreeTypeFont 对象的栈结构。

    这个栈的特点是它总有一个默认的“栈底”字体，该字体永远不会被弹出。
    """

    def __init__(self, default_font: FreeTypeFont):
        """
        使用一个默认的 FreeTypeFont 对象初始化字体栈。

        :param default_font: 作为栈底的默认字体对象。
        """
        if not isinstance(default_font, FreeTypeFont):
            raise TypeError("default_font 必须是 PIL.ImageFont.FreeTypeFont 对象")

        # 使用一个列表来模拟栈，并将默认字体作为第一个元素。
        self._stack = [default_font]

    def push(self, font: FreeTypeFont):
        """
        将一个新的 FreeTypeFont 对象压入栈顶。

        :param font: 要压入的字体对象。
        """
        if not isinstance(font, FreeTypeFont):
            raise TypeError("压入的 font 必须是 PIL.ImageFont.FreeTypeFont 对象")

        self._stack.append(font)

    def get_top(self) -> FreeTypeFont:
        """
        获取栈顶的字体对象，但不会将其移除。

        :return: 位于栈顶的字体对象。
        """
        return self._stack[-1]

    def pop(self) -> FreeTypeFont | None:
        """
        从栈顶弹出一个字体对象。

        如果栈中只剩下默认字体，则不会执行弹出操作，也不会报错。

        :return: 被弹出的字体对象。如果无法弹出（只剩默认字体），则返回 None。
        """
        if len(self._stack) > 1:
            return self._stack.pop()
        else:
            # 当只剩默认字体时，不执行任何操作
            return None

    def __len__(self):
        """允许使用 len(font_stack) 获取栈中元素的数量。"""
        return len(self._stack)

    def __str__(self):
        """
        提供一个易于阅读的字符串表示，显示栈的当前状态。
        特别处理 FreeTypeFont 对象，显示其路径和大小。
        """
        stack_visual = []
        for font in reversed(self._stack):
            # FreeTypeFont 对象有一个 'path' 属性，我们可以用它来识别字体
            try:
                # font.path 在较新 Pillow 版本中可用
                font_name = font.path.split('/')[-1].split('\\')[-1]
                stack_visual.append(f"Font(file='{font_name}', size={font.size})")
            except AttributeError:
                # 兼容旧版本或内存中的字体
                stack_visual.append(f"Font(size={font.size})")

        stack_items = "\n  ".join(stack_visual)
        return f"--- FontStack (Top to Bottom) ---\n  {stack_items}\n---------------------------------"


class FontCache:
    """字体缓存类，用于缓存字体对象以提高性能"""

    def __init__(self, font_manager: 'FontManager'):
        """
        初始化字体缓存

        Args:
            font_manager: 字体管理器实例
        """
        self.font_manager: 'FontManager' = font_manager
        self._cache: Dict[Tuple[str, int], Any] = {}

    def get_font(self, font_name: str, font_size: int):
        """
        获取字体对象，优先从缓存中获取

        Args:
            font_name: 字体名称
            font_size: 字体大小

        Returns:
            字体对象
        """
        # 使用字体名和字体大小作为缓存键
        cache_key = (font_name, font_size)

        # 检查缓存中是否已有该字体
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 缓存中没有，通过font_manager获取字体
        font_obj = self.font_manager.get_font(font_name, font_size)

        # 将字体对象存入缓存
        self._cache[cache_key] = font_obj

        return font_obj

    def clear_cache(self):
        """清空字体缓存"""
        self._cache.clear()

    def cache_size(self) -> int:
        """获取缓存中字体的数量"""
        return len(self._cache)

    def remove_font(self, font_name: str, font_size: int):
        """
        从缓存中移除指定的字体

        Args:
            font_name: 字体名称
            font_size: 字体大小
        """
        cache_key = (font_name, font_size)
        if cache_key in self._cache:
            del self._cache[cache_key]

    def has_font(self, font_name: str, font_size: int) -> bool:
        """
        检查缓存中是否存在指定字体

        Args:
            font_name: 字体名称
            font_size: 字体大小

        Returns:
            True if font exists in cache, False otherwise
        """
        cache_key = (font_name, font_size)
        return cache_key in self._cache


@dataclass
class DefaultFonts:
    """默认字体配置"""
    regular: str  # 常规字体
    bold: str  # 粗体字体
    italic: str  # 斜体字体
    trait: str  # 特性字体


class TextAlignment(Enum):
    """文本对齐方式"""
    LEFT = "left"  # 左对齐
    CENTER = "center"  # 居中对齐
    RIGHT = "right"  # 右对齐


@dataclass
class DrawOptions:
    """通用绘制选项"""
    font_name: str = ""  # 常规默认字体
    font_size: int = 12  # 默认字体大小
    font_color: str = "#000000"  # 字体颜色
    has_border: bool = False  # 是否有外边框
    border_color: str = "#000000"  # 外边框颜色
    border_width: int = 1  # 外边框粗细
    has_underline: bool = False  # 是否加下划线


class RichTextRenderer:
    def __init__(self, font_manager: 'FontManager', image_manager: 'ImageManager',
                 image: Image.Image, default_fonts: DefaultFonts):
        """
        富文本渲染器

        Args:
            font_manager: FontManager对象
            image_manager: ImageManager对象
            image: PIL图片对象
            default_fonts: 默认字体配置对象
        """
        self.font_manager: 'FontManager' = font_manager
        self.image_manager: 'ImageManager' = image_manager
        self.image: Image.Image = image
        self.default_fonts: DefaultFonts = default_fonts
        self.draw = ImageDraw.Draw(self.image)
        self.rich_text_parser = RichTextParser()

    def _preprocess_text(self, text: str) -> str:
        """
        对文本进行预处理，将特殊标记转换为HTML标签

        Args:
            text: 原始文本

        Returns:
            预处理后的文本
        """
        # 定义预处理规则
        preprocessing_rules = [
            # 将【文本】替换为<b>文本</b>
            (r'【([^】]*)】', r'<b>\1</b>'),
            # 将⭐替换为特殊字体标签
            (r'⭐', r'<font name="arkham-icons">q</font>'),
            # 将⚡替换为特殊字体标签
            (r'⚡', r'<font name="arkham-icons">k</font>'),
            # 可以继续添加其他预处理规则
            # (r'其他模式', r'替换内容'),
        ]

        import re
        processed_text = text

        # 依次应用所有预处理规则
        for pattern, replacement in preprocessing_rules:
            processed_text = re.sub(pattern, replacement, processed_text)

        return processed_text

    def draw_line(self, text: str, position: Tuple[int, int],
                  alignment: TextAlignment, options: DrawOptions) -> None:
        """
        绘制一行文本

        Args:
            text: 要绘制的文本
            position: 位置坐标(x, y)
            alignment: 对齐方式
            options: 绘制选项
        """
        pass

    def _get_text_box(self, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        """
        获取文本尺寸

        :param text: 要测量的文本
        :param font: 字体对象
        :return: (宽度, 高度)元组
        """
        bbox = font.getbbox(text)
        return int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1])

    def draw_complex_text(self, text: str, polygon_vertices: List[Tuple[int, int]],
                          padding: int, options: DrawOptions,
                          draw_debug_frame: bool = False) -> None:
        """
        绘制复杂文本框

        Args:
            text: 要绘制的文本
            polygon_vertices: 多边形顶点坐标列表
            padding: 内边距
            options: 绘制选项
            draw_debug_frame: 是否绘制虚拟框的线条调试用
        """
        if draw_debug_frame:
            self.draw.polygon(polygon_vertices, outline="red", width=2)

        # 临时测试
        # 预处理
        text = self._preprocess_text(text)
        parsed_items = self.rich_text_parser.parse(text)

        line_height = int(options.font_size * 1.1)
        print("行高：", line_height)

        virtual_text_box = VirtualTextBox(
            polygon_vertices=polygon_vertices,
            default_line_spacing=line_height,
            padding=padding

        )

        font_cache = FontCache(self.font_manager)
        font_stack = FontStack(font_cache.get_font(options.font_name, options.font_size))

        for i, item in enumerate(parsed_items):
            print(f"{i + 1:2d}. {item}")
            if item.tag == "text":
                font = font_stack.get_top()
                text_box = self._get_text_box(item.content, font)
                virtual_text_box.push(
                    TextObject(
                        text=item.content,
                        font=font,
                        width=text_box[0],
                        height=text_box[1],
                    )
                )
            elif item.tag == "br":
                virtual_text_box.newline()
            elif item.tag == "par":
                result = virtual_text_box.new_paragraph()
            elif item.tag == "font":
                font_stack.push(font_cache.get_font(
                    item.attributes.get('name', options.font_name),
                    options.font_size
                ))
                print(item.type)
            elif item.tag == "/font":
                font_stack.pop()
            elif item.tag == "b":
                font_stack.push(font_cache.get_font(
                    'NimbusRomNo9L-Med',
                    options.font_size
                ))
                print(item.type)
            elif item.tag == "/b":
                font_stack.pop()
            elif item.tag == "i":
                font_stack.push(font_cache.get_font(
                    'ArnoPro-Italic',
                    options.font_size
                ))
                print(item.type)
            elif item.tag == "/i":
                font_stack.pop()
            elif item.tag == "flavor":
                virtual_text_box.set_line_padding(30)
                virtual_text_box.set_line_center()
            elif item.tag == "/flavor":
                virtual_text_box.cancel_line_padding()
                virtual_text_box.cancel_line_center()

        remaining_vertical_distance = virtual_text_box.get_remaining_vertical_distance()
        print(f"剩余垂直距离: {remaining_vertical_distance}")

        # 获取渲染列表
        render_list = virtual_text_box.get_render_list()
        print(f"渲染列表包含 {len(render_list)} 个项目")

        # 遍历渲染列表并绘制到图片上
        for i, render_item in enumerate(render_list):
            obj = render_item.obj
            x = render_item.x
            y = render_item.y

            if isinstance(obj, TextObject):
                # 绘制文本对象

                # 基础文本绘制
                self.draw.text(
                    xy=(x, y),
                    text=obj.text,
                    font=obj.font,
                    fill=options.font_color
                )



            elif isinstance(obj, ImageObject):
                # 绘制图片对象
                print(f"绘制图片 #{i + 1}: 大小 {obj.width}x{obj.height} 在位置 ({x}, {y})")

                # 粘贴图片
                if obj.image.mode == 'RGBA':
                    # 如果图片有透明通道，使用alpha合成
                    self.image.paste(obj.image, (x, y), obj.image)
                else:
                    # 普通图片直接粘贴
                    self.image.paste(obj.image, (x, y))

                # 绘制调试框（可选）
                if draw_debug_frame:
                    self.draw.rectangle(
                        [(x, y), (x + obj.width, y + obj.height)],
                        outline="green",
                        width=1
                    )

            else:
                print(f"未知对象类型 #{i + 1}: {type(obj)}")

        print("渲染完成！")


if __name__ == '__main__':
    font_manager = FontManager(font_folder='../fonts')
    image_manager = ImageManager(image_folder='../images')
    image = Image.open('test.png')
    renderer = RichTextRenderer(font_manager, image_manager, image, DefaultFonts(
        regular='simfang',
        bold='思源黑体',
        italic='simfang',
        trait='方正舒体'
    ))
    body = "You begin the game with 4 copies of Herta Puppet in play. When any amount of damage( would be placed on " \
           "you, place those damage on Herta Puppet (Online) instead.<par>【Forced】 – When Herta Puppet (Online) is dealt " \
           "damage: You take 1 direct horror.<par>⚡Exhaust a copy of Herta Puppet at your location: You get +2 skill " \
           "value during this test.<par>⭐effect: +X. X is the number of Herta Puppet assets in play.<par>" \
           "<flex><flavor>Test flavor !</flavor><flex>"
    renderer.draw_complex_text(
        body,
        polygon_vertices=[
            (596, 178), (1016, 178),
            (1016, 600), (596, 600)
        ],
        padding=10,
        options=DrawOptions(
            font_name='ArnoPro-Regular',
            font_size=24,
            font_color='#000000',
            has_border=True,
            border_color='#000000',
            border_width=1,
            has_underline=False
        ),
        draw_debug_frame=True
    )
    image.show()
