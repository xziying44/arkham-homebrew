# RichTextRenderer.py
import re
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
# 假设 Card.py 在上一级目录
import sys

from ResourceManager import FontManager, ImageManager

sys.path.append('..')
# ---

# 假设这些文件在同一目录下
from rich_text_render.HtmlTextParser import RichTextParser, TextType
from rich_text_render.VirtualTextBox import VirtualTextBox, TextObject, ImageObject
# ---

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
        if not isinstance(default_font, FreeTypeFont):
            raise TypeError("default_font 必须是 PIL.ImageFont.FreeTypeFont 对象")
        self._stack = [default_font]

    def push(self, font: FreeTypeFont):
        if not isinstance(font, FreeTypeFont):
            raise TypeError("压入的 font 必须是 PIL.ImageFont.FreeTypeFont 对象")
        self._stack.append(font)

    def get_top(self) -> FreeTypeFont:
        return self._stack[-1]

    def pop(self) -> Optional[FreeTypeFont]:
        if len(self._stack) > 1:
            return self._stack.pop()
        else:
            return None
    # ... 其他方法保持不变 ...


class FontCache:
    """字体缓存类，用于缓存字体对象以提高性能"""

    def __init__(self, font_manager: 'FontManager'):
        self.font_manager: 'FontManager' = font_manager
        self._cache: Dict[Tuple[str, int], Any] = {}

    def get_font(self, font_name: str, font_size: int):
        cache_key = (font_name, font_size)
        if cache_key in self._cache:
            return self._cache[cache_key]
        font_obj = self.font_manager.get_font(font_name, font_size)
        self._cache[cache_key] = font_obj
        return font_obj
    # ... 其他方法保持不变 ...


@dataclass
class DefaultFonts:
    """默认字体配置"""
    regular: str
    bold: str
    italic: str
    trait: str


class TextAlignment(Enum):
    """文本对齐方式"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


@dataclass
class DrawOptions:
    """通用绘制选项"""
    font_name: str = ""
    font_size: int = 12
    font_color: str = "#000000"
    has_border: bool = False
    border_color: str = "#000000"
    border_width: int = 1
    has_underline: bool = False


class RichTextRenderer:
    # ==================== 修改 __init__ 方法 ====================
    def __init__(self, font_manager: 'FontManager', image_manager: 'ImageManager',
                 image: Image.Image, lang='zh'):
        """
        富文本渲染器

        Args:
            font_manager: FontManager对象
            image_manager: ImageManager对象
            image: PIL图片对象
            default_fonts: 默认字体配置对象
            line_spacing_multiplier (float): 行间距倍率，基于字体大小计算行高。默认为 1.1。
            lang (str): 语言，默认为 "zh"。
        """
        self.font_manager: 'FontManager' = font_manager
        self.image_manager: 'ImageManager' = image_manager
        self.image: Image.Image = image
        self.draw = ImageDraw.Draw(self.image)
        self.rich_text_parser = RichTextParser()
        if lang == 'zh':
            self.font_manager.set_lang('zh')
            self.default_fonts: DefaultFonts = DefaultFonts(
                regular='simfang',
                bold='思源黑体',
                italic='simfang-Italic',
                trait='方正舒体'
            )
            self.line_spacing_multiplier = 1.2
        else:
            self.font_manager.set_lang('en')
            self.default_fonts: DefaultFonts = DefaultFonts(
                regular='ArnoPro-Regular',
                bold='NimbusRomNo9L-Med',
                italic='ArnoPro-Italic',
                trait='NimbusRomNo9L-MedIta'
            )
            self.line_spacing_multiplier = 1.1

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocesses card text to replace special tags and icons with HTML-like font tags.
        This method consolidates multiple forms of input (Emojis, Chinese tags, SE tags)
        into a single, unified regex substitution pipeline.

        The rules are ordered to handle formatting tags first, then all icon types.
        """
        # The replacement string for the icon font
        font_tpl = r'<font name="arkham-icons">{char}</font>'
        preprocessing_rules = [
            # 1. Formatting and Keyword Rules (Non-icon)
            (r'【([^】]*)】', r'<b>\1</b>'),  # Bold text within 【】
            (r'{([^}]*)}', r'<trait>\1</trait>'),
            (r'<relish>(.*)</relish>', r'<flavor>\1</flavor> -'),
            (r'<强制>', r'<b>强制</b> -'),
            (r'<显现>', r'<b>显现</b> -'),
            (r'<攻击>', r'<b>攻击</b>'),
            (r'<躲避>', r'<b>躲避</b>'),
            (r'<谈判>', r'<b>躲避</b>'),  # As per original code, Parley maps to Evade
            # 2. Icon Rules (Emoji | CN Tag | SE Tag | Other Alias) -> Font Icon
            # Faction Icons
            (r'🛡️|<守护者>|<gua>️', font_tpl.format(char='e')),
            (r'🔍|<探求者>|<see>', font_tpl.format(char='f')),
            (r'🚶|<流浪者>|<rog>', font_tpl.format(char='g')),
            (r'🧘|<潜修者>|<mys>', font_tpl.format(char='h')),
            (r'🏕️|<生存者>|<sur>', font_tpl.format(char='i')),
            (r'🕵️|<调查员>|<per>', font_tpl.format(char='v')),
            # Action Icons
            (r'⭕|<反应>|<rea>', font_tpl.format(char='l')),
            (r'➡️|<启动>|<箭头>|<act>️', font_tpl.format(char='j')),
            (r'⚡|<免费>|<fre>️', font_tpl.format(char='k')),
            # Chaos Token Icons
            (r'💀|<骷髅>|<sku>️', font_tpl.format(char='m')),
            (r'👤|<异教徒>|<cul>️', font_tpl.format(char='n')),
            (r'📜|<石板>|<tab>️', font_tpl.format(char='o')),
            (r'👹|<古神>|<mon>️', font_tpl.format(char='p')),
            (r'🐙|<触手>|<大失败>|<ten>️', font_tpl.format(char='r')),
            (r'⭐|<旧印>|<大成功>|<eld>️', font_tpl.format(char='q')),
            # Stat Icons
            (r'🧠|<脑>|<wil>️', font_tpl.format(char='.')),
            (r'📚|<书>|<int>️', font_tpl.format(char='a')),
            (r'👊|<拳>|<com>️', font_tpl.format(char='b')),
            (r'🦶|<脚>|<agi>️', font_tpl.format(char='c')),
            (r'❓|<\?>', font_tpl.format(char='d')),  # '?' is a special regex char, so escaped as '\?'
            # Other Game Icons
            (r'🏅|<独特>', font_tpl.format(char='w')),
            (r'<一>', font_tpl.format(char='x')),
            (r'🔵|<点>|<bul>', font_tpl.format(char='y')),
            (r'🌟|<祝福>|<ble>', font_tpl.format(char='s')),
            (r'🌑|<诅咒>|<cur>', font_tpl.format(char='t')),
            (r'❄️|<雪花>', font_tpl.format(char='u')),
        ]

        processed_text = text
        for pattern, replacement in preprocessing_rules:
            processed_text = re.sub(pattern, replacement, processed_text)

        return processed_text

    def _get_text_box(self, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        bbox = font.getbbox(text)
        return int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1])

    def find_best_fit_font_size(
            self,
            text: str,
            polygon_vertices: List[Tuple[int, int]],
            padding: int,
            options: DrawOptions,
            min_font_size: int = 8
    ) -> Optional[VirtualTextBox]:
        """
        使用二分法查找能容纳所有文本的最大字体大小，并返回填充好的VirtualTextBox。
        （此方法现在是内部核心逻辑，由 draw_complex_text 调用）
        """
        low = min_font_size
        high = options.font_size
        best_vbox = None

        print(f"开始二分查找最佳字体大小，范围: [{low}, {high}], 行距倍率: {self.line_spacing_multiplier}")

        while low <= high:
            mid_size = (low + high) // 2
            if mid_size == 0:
                break

            # 尝试使用当前字体大小进行渲染模拟
            fits, vbox_instance = self._try_render_with_font_size(
                text, polygon_vertices, padding, options, mid_size
            )

            if fits:
                # 成功: 保存结果, 尝试更大的字体
                best_vbox = vbox_instance
                low = mid_size + 1
            else:
                # 失败: 字体太大, 减小字体
                high = mid_size - 1

        if best_vbox:
            font_size = high  # 'high' holds the last successful size
            print(f"查找结束。找到的最佳字体大小为: {font_size}")
        else:
            print("查找结束。未找到任何可行的字体大小。")

        return best_vbox

    # ==================== 修改 _try_render_with_font_size 方法 ====================
    def _try_render_with_font_size(
            self,
            text: str,
            polygon_vertices: List[Tuple[int, int]],
            padding: int,
            base_options: DrawOptions,
            size_to_test: int
    ) -> Tuple[bool, Optional[VirtualTextBox]]:
        """
        辅助函数，测试给定的字体大小是否能容纳全部文本。
        """

        parsed_items = self.rich_text_parser.parse(text)

        # 使用构造函数中传入的行距倍率来计算行高
        if size_to_test < 25 and self.line_spacing_multiplier > 1.15:
            line_height = int(size_to_test * 1.15)
        elif size_to_test < 20 and self.line_spacing_multiplier > 1.1:
            line_height = int(size_to_test * 1.1)
        elif size_to_test < 18 and self.line_spacing_multiplier > 1.05:
            line_height = int(size_to_test * 1.05)
        else:
            line_height = int(size_to_test * self.line_spacing_multiplier)

        virtual_text_box = VirtualTextBox(
            polygon_vertices=polygon_vertices,
            default_line_spacing=line_height,
            padding=padding
        )

        font_cache = FontCache(self.font_manager)

        try:
            base_font = font_cache.get_font(base_options.font_name, size_to_test)
        except Exception as e:
            return False, None

        font_stack = FontStack(base_font)

        for item in parsed_items:
            success = True
            if item.tag == "text":
                font = font_stack.get_top()
                if item.type == TextType.OTHER:
                    # 一个一个push
                    for char in item.content:
                        text_box = self._get_text_box(char, font)
                        success = virtual_text_box.push(
                            TextObject(char, font, text_box[1], text_box[0])
                        )
                else:
                    text_box = self._get_text_box(item.content, font)
                    success = virtual_text_box.push(
                        TextObject(item.content, font, text_box[1], text_box[0])
                    )
            elif item.tag == "br":
                success = virtual_text_box.newline()
            elif item.tag == "par":
                success = virtual_text_box.new_paragraph()
            elif item.tag == "font":
                font_name = item.attributes.get('name', base_options.font_name)
                font_stack.push(font_cache.get_font(font_name, size_to_test))
            elif item.tag == "b":
                font_stack.push(font_cache.get_font(self.default_fonts.bold, size_to_test))
            elif item.tag == "i":
                font_stack.push(font_cache.get_font(self.default_fonts.italic, size_to_test))
            elif item.tag == "trait":
                font_stack.push(font_cache.get_font(self.default_fonts.trait, size_to_test))
            elif item.tag == "flavor":
                align = item.attributes.get('align', 'center')
                virtual_text_box.add_flex()
                flavor_font_size = max(1, size_to_test - 2)
                font_stack.push(font_cache.get_font(self.default_fonts.italic, flavor_font_size))
                virtual_text_box.set_line_padding(20)
                # 是否居中
                if align == 'center':
                    virtual_text_box.set_line_center()
            elif item.tag.startswith('/'):
                if item.tag in ["/font", "/b", "/i", '/trait']:
                    font_stack.pop()
                elif item.tag == "/flavor":
                    font_stack.pop()
                    virtual_text_box.cancel_line_padding()
                    virtual_text_box.cancel_line_center()
            elif item.tag == "flex":
                virtual_text_box.add_flex()

            if not success:
                return False, None

        return True, virtual_text_box

    # ==================== 修改 draw_complex_text 方法 ====================
    def draw_complex_text(self, text: str, polygon_vertices: List[Tuple[int, int]],
                          padding: int, options: DrawOptions,
                          draw_debug_frame: bool = False) -> None:
        """
        在指定多边形区域内绘制复杂文本，并自动寻找最佳字体大小。

        Args:
            text: 要绘制的文本。
            polygon_vertices: 多边形顶点坐标列表。
            padding: 内边距。
            options: 绘制选项。options.font_size 将被用作搜索的最大上限。
            draw_debug_frame: 是否绘制虚拟框的线条调试用。
        """
        if draw_debug_frame:
            self.draw.polygon(polygon_vertices, outline="red", width=2)

        text = self._preprocess_text(text)
        print(text)

        # 默认行为：查找最佳字体大小并获取布局好的VirtualTextBox
        final_vbox = self.find_best_fit_font_size(
            text=text,
            polygon_vertices=polygon_vertices,
            padding=padding,
            options=options
        )

        # 如果 final_vbox 为 None，说明文本无法容纳，直接返回
        if final_vbox is None:
            print("错误: 文本内容过多，即使使用最小字体也无法在指定区域内渲染。")
            return

        # 从布局好的VirtualTextBox中获取渲染列表
        render_list = final_vbox.get_render_list()

        # 遍历渲染列表并绘制到图片上
        for render_item in render_list:
            obj = render_item.obj
            x, y = render_item.x, render_item.y

            if isinstance(obj, TextObject):
                self.draw.text((x, y), obj.text, font=obj.font, fill=options.font_color)
            elif isinstance(obj, ImageObject):
                if obj.image.mode == 'RGBA':
                    self.image.paste(obj.image, (x, y), obj.image)
                else:
                    self.image.paste(obj.image, (x, y))
                if draw_debug_frame:
                    self.draw.rectangle([(x, y), (x + obj.width, y + obj.height)], outline="green", width=1)
        pass

    def draw_line(self, text: str, position: Tuple[int, int],
                  alignment: TextAlignment, options: DrawOptions) -> None:
        """
        绘制一行支持HTML语法的文本。
        Args:
            text: 要绘制的文本，支持<b>, <i>, <trait>, <font>等标签。
            position: 位置坐标(x, y)。
                      - Center: (x, y)是整行文本的中心点。
                      - Left: (x, y)是整行文本的左上角顶点。
                      - Right: (x, y)是整行文本的右上角顶点。
            alignment: 对齐方式 (TextAlignment.LEFT, .CENTER, .RIGHT)。
            options: 绘制选项，提供默认字体、大小和颜色。
        """
        # 预处理文本
        text = self._preprocess_text(text)

        # 解析HTML标签
        parsed_items = self.rich_text_parser.parse(text)

        # 创建字体缓存和字体栈
        font_cache = FontCache(self.font_manager)
        try:
            base_font = font_cache.get_font(options.font_name, options.font_size)
        except Exception as e:
            print(f"字体加载失败: {e}")
            return

        font_stack = FontStack(base_font)

        # 第一遍遍历：计算总宽度和高度，收集渲染信息
        render_segments = []  # 存储每个文本片段的渲染信息
        total_width = 0
        max_height = 0

        for item in parsed_items:
            if item.tag == "text":
                font = font_stack.get_top()
                text_content = item.content

                if item.type == TextType.OTHER:
                    # 逐字符处理
                    for char in text_content:
                        text_box = self._get_text_box(char, font)
                        render_segments.append({
                            'text': char,
                            'font': font,
                            'width': text_box[0],
                            'height': text_box[1],
                            'color': options.font_color
                        })
                        total_width += text_box[0]
                        max_height = max(max_height, text_box[1])
                else:
                    # 整块文本处理
                    text_box = self._get_text_box(text_content, font)
                    render_segments.append({
                        'text': text_content,
                        'font': font,
                        'width': text_box[0],
                        'height': text_box[1],
                        'color': options.font_color
                    })
                    total_width += text_box[0]
                    max_height = max(max_height, text_box[1])

            elif item.tag == "font":
                font_name = item.attributes.get('name', options.font_name)
                try:
                    font_stack.push(font_cache.get_font(font_name, options.font_size))
                except Exception as e:
                    print(f"字体切换失败: {e}")

            elif item.tag == "b":
                try:
                    font_stack.push(font_cache.get_font(self.default_fonts.bold, options.font_size))
                except Exception as e:
                    print(f"粗体字体加载失败: {e}")

            elif item.tag == "i":
                try:
                    font_stack.push(font_cache.get_font(self.default_fonts.italic, options.font_size))
                except Exception as e:
                    print(f"斜体字体加载失败: {e}")

            elif item.tag == "trait":
                try:
                    font_stack.push(font_cache.get_font(self.default_fonts.trait, options.font_size))
                except Exception as e:
                    print(f"特质字体加载失败: {e}")

            elif item.tag.startswith('/'):
                if item.tag in ["/font", "/b", "/i", '/trait']:
                    font_stack.pop()

        # 根据对齐方式计算起始位置
        x, y = position

        if alignment == TextAlignment.CENTER:
            # 中心对齐：position是文本中心点
            start_x = x - total_width // 2
            start_y = y - max_height // 2
        elif alignment == TextAlignment.LEFT:
            # 左对齐：position是左上角
            start_x = x
            start_y = y
        elif alignment == TextAlignment.RIGHT:
            # 右对齐：position是右上角
            start_x = x - total_width
            start_y = y
        else:
            # 默认左对齐
            start_x = x
            start_y = y
        print("绘制文本:", text, "位置:", start_x, start_y)

        # 第二遍：实际绘制文本
        current_x = start_x

        for segment in render_segments:
            # 绘制文本
            self.draw.text(
                (current_x, start_y),
                segment['text'],
                font=segment['font'],
                fill=segment['color']
            )

            # 如果有边框效果
            if options.has_border:
                # 绘制边框效果（描边）
                for dx in [-options.border_width, 0, options.border_width]:
                    for dy in [-options.border_width, 0, options.border_width]:
                        if dx != 0 or dy != 0:  # 不重复绘制中心点
                            self.draw.text(
                                (current_x + dx, start_y + dy),
                                segment['text'],
                                font=segment['font'],
                                fill=options.border_color
                            )
                # 重新绘制主文本（覆盖边框）
                self.draw.text(
                    (current_x, start_y),
                    segment['text'],
                    font=segment['font'],
                    fill=segment['color']
                )

            # 更新x坐标
            current_x += segment['width']

        # 如果有下划线效果，在所有文本绘制完成后绘制整条下划线
        if options.has_underline:
            underline_y = start_y + max_height + 2
            y_offset = 12
            self.draw.line(
                (start_x, underline_y + y_offset, start_x + total_width, underline_y + y_offset),
                fill=options.font_color,
                width=1
            )
            y_offset = 18
            self.draw.line(
                (start_x, underline_y + y_offset, start_x + total_width, underline_y + y_offset),
                fill=options.font_color,
                width=2
            )


if __name__ == '__main__':
    font_manager = FontManager(font_folder='../fonts')
    image_manager = ImageManager(image_folder='../images')
    image = Image.open('test.png')
    renderer = RichTextRenderer(font_manager, image_manager, image, lang='zh')
    # body = "You begin the game with 4 copies of Herta Puppet in play. When any amount of damage( would be placed on " \
    #        "you, place those damage on Herta Puppet (Online) instead.<par>【Forced】 – When Herta Puppet (Online) is dealt " \
    #        "damage: You take 1 direct horror.<par>⚡Exhaust a copy of Herta Puppet at your location: You get +2 skill " \
    #        "value during this test.<par>⭐effect: +X. X is the number of Herta Puppet assets in play.<par>" \
    #        "<flavor>Test flavor You begin the game with 4 copies of Herta Puppet in play. !</flavor><flex>"
    body = "【强制】 - 你所在地点的一个{怪物}敌人被击败后：你获得2点资源或在你的一个法术支援上放置1充能。(" \
           "每轮限一次）<par>⭐效果：+1。你+2<脑>直到本轮结束。<par><flavor>“对连身为王与神的法老之座都敢玩弄的不敬，降下惩罚。”</flavor>"
    renderer.draw_complex_text(
        body,
        polygon_vertices=[
            (596, 178), (1016, 178),
            (1016, 600), (596, 600)
        ],
        padding=10,
        options=DrawOptions(
            font_name='simfang',
            font_size=34,
            font_color='#000000'
        ),
        draw_debug_frame=False
    )

    renderer.draw_line(
        text='测试测试',
        position=(320, 38),
        alignment=TextAlignment.CENTER,
        options=DrawOptions(
            font_name='汉仪小隶书简',
            font_size=48,
            font_color='#000000'
        ),
    )

    image.show()
