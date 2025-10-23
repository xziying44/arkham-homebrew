# RichTextRenderer.py
import re
# 假设 Card.py 在上一级目录
import sys
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from PIL import Image, ImageDraw

from ResourceManager import FontManager, ImageManager

sys.path.append('..')
# ---

# 假设这些文件在同一目录下
from rich_text_render.HtmlTextParser import RichTextParser, TextType
from rich_text_render.VirtualTextBox import VirtualTextBox, TextObject, ImageObject, RenderItem
# ---

from typing import Dict, Tuple, Any

from PIL import ImageFont

# 定义一个类型别名，让代码更清晰
FreeTypeFont = ImageFont.FreeTypeFont


@dataclass
class FontStackObject:
    """字体对象"""
    font: FreeTypeFont
    font_name: str


class FontStack:
    """
    一个管理 PIL.ImageFont.FreeTypeFont 对象的栈结构。

    这个栈的特点是它总有一个默认的“栈底”字体，该字体永远不会被弹出。
    """

    def __init__(self, default_font: FreeTypeFont, font_name: str):
        if not isinstance(default_font, FreeTypeFont):
            raise TypeError("default_font 必须是 PIL.ImageFont.FreeTypeFont 对象")
        self._stack = [FontStackObject(default_font, font_name)]

    def push(self, font: FreeTypeFont, font_name: str):
        if not isinstance(font, FreeTypeFont):
            raise TypeError("压入的 font 必须是 PIL.ImageFont.FreeTypeFont 对象")
        self._stack.append(FontStackObject(font, font_name))

    def get_top(self) -> FreeTypeFont:
        return self._stack[-1].font

    def get_top_font_name(self) -> str:
        return self._stack[-1].font_name

    def pop(self) -> Optional[FreeTypeFont]:
        if len(self._stack) > 1:
            return self._stack.pop().font
        else:
            return None


class HtmlTagStack:
    """
    一个管理 HTML 标签的栈结构。
    这个栈的特点是它总有一个默认的"栈底"标签，该标签永远不会被弹出。
    通常用于跟踪嵌套的 HTML 标签结构。
    """

    def __init__(self, default_tag: str = "body"):
        if not isinstance(default_tag, str):
            raise TypeError("default_tag 必须是字符串")
        if not default_tag.strip():
            raise ValueError("default_tag 不能为空字符串")
        self._stack = [default_tag.strip().lower()]

    def push(self, tag: str):
        """压入一个新的 HTML 标签"""
        if not isinstance(tag, str):
            raise TypeError("压入的 tag 必须是字符串")
        if not tag.strip():
            raise ValueError("tag 不能为空字符串")
        self._stack.append(tag.strip().lower())

    def get_top(self) -> str:
        """获取栈顶的 HTML 标签"""
        return self._stack[-1]

    def pop(self) -> Optional[str]:
        """
        弹出栈顶的 HTML 标签。
        如果只剩下默认标签，则返回 None 而不弹出。
        """
        if len(self._stack) > 1:
            return self._stack.pop()
        else:
            return None

    def get_current_path(self) -> str:
        """获取当前的标签路径，用 > 连接"""
        return " > ".join(self._stack)

    def size(self) -> int:
        """返回栈的大小（包括默认标签）"""
        return len(self._stack)

    def depth(self) -> int:
        """返回当前嵌套深度（不包括默认标签）"""
        return len(self._stack) - 1

    def is_empty(self) -> bool:
        """检查是否只有默认标签"""
        return len(self._stack) == 1

    def get_default_tag(self) -> str:
        """获取默认标签"""
        return self._stack[0]

    def clear_to_default(self):
        """清空栈直到只剩默认标签"""
        self._stack = [self._stack[0]]

    def contains(self, tag: str) -> bool:
        """检查栈中是否包含指定标签"""
        if not isinstance(tag, str):
            return False
        return tag.strip().lower() in self._stack

    def get_all_tags(self) -> list[str]:
        """获取栈中所有标签的副本"""
        return self._stack.copy()

    def __str__(self) -> str:
        return f"HtmlTagStack({self.get_current_path()})"

    def __repr__(self) -> str:
        return f"HtmlTagStack(stack={self._stack})"


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
        self.default_fonts: DefaultFonts = DefaultFonts(
            regular=self.font_manager.get_lang_font('正文字体').name,
            bold=self.font_manager.get_lang_font('加粗字体').name,
            italic=self.font_manager.get_lang_font('风味文本字体').name,
            trait=self.font_manager.get_lang_font('特性字体').name
        )
        if lang == 'zh':
            self.line_spacing_multiplier = 1.2
        else:
            self.line_spacing_multiplier = 1.1

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocesses card text to replace special tags and icons with HTML-like font tags.
        This method consolidates multiple forms of input (Emojis, Chinese tags, SE tags)
        into a single, unified regex substitution pipeline.

        The rules are ordered to handle formatting tags first, then all icon types.
        """

        # 首先合并相邻的flavor标签
        text = self._merge_adjacent_flavor_tags(text)

        # The replacement string for the icon font
        font_tpl = r'<font name="arkham-icons">{char}</font>'
        preprocessing_rules = [
            # 1. Formatting and Keyword Rules (Non-icon)
            (r'【([^】]*)】', r'<b>\1</b>'),  # Bold text within 【】
            (r'<t>(.*?)</t>', r'<trait>\1</trait>'),
            (r'<relish>(.*)</relish>', r'<flavor>\1</flavor>'),
            # 2. Icon Rules (Emoji | CN Tag | SE Tag | Other Alias) -> Font Icon
            # Faction Icons
            (r'🛡️|<守护者>|<守卫者>|<gua>', font_tpl.format(char='e')),
            (r'🔍|<探求者>|<see>', font_tpl.format(char='f')),
            (r'🚶|<流浪者>|<rog>', font_tpl.format(char='g')),
            (r'🧘|<潜修者>|<mys>', font_tpl.format(char='h')),
            (r'🏕️|<生存者>|<求生者>|<sur>', font_tpl.format(char='i')),
            (r'🕵️|<调查员>|<per>', font_tpl.format(char='v')),
            # Action Icons
            (r'⭕|<反应>|<rea>', font_tpl.format(char='l')),
            (r'➡️|<启动>|<箭头>|<act>', font_tpl.format(char='j')),
            (r'⚡|<免费>|<fre>️', font_tpl.format(char='k')),
            # Chaos Token Icons
            (r'💀|<骷髅>|<sku>', font_tpl.format(char='m')),
            (r'👤|<异教徒>|<cul>', font_tpl.format(char='n')),
            (r'📜|<石板>|<tab>', font_tpl.format(char='o')),
            (r'👹|<古神>|<mon>', font_tpl.format(char='p')),
            (r'🐙|<触手>|<大失败>|<ten>', font_tpl.format(char='r')),
            (r'⭐|<旧印>|<大成功>|<eld>', font_tpl.format(char='q')),
            # Stat Icons
            (r'🧠|<脑>|<wil>', font_tpl.format(char='.')),
            (r'📚|<书>|<int>', font_tpl.format(char='a')),
            (r'👊|<拳>|<com>', font_tpl.format(char='b')),
            (r'🦶|<脚>|<agi>', font_tpl.format(char='c')),
            (r'❓|<\?>', font_tpl.format(char='d')),  # '?' is a special regex char, so escaped as '\?'
            # Other Game Icons
            (r'🏅|<独特>', font_tpl.format(char='w')),
            (r'<一>', font_tpl.format(char='x')),
            (r'🔵|<点>|<bul>', font_tpl.format(char='y')),
            (r'🌟|<祝福>|<ble>', font_tpl.format(char='s')),
            (r'🌑|<诅咒>|<cur>', font_tpl.format(char='t')),
            (r'❄️|<雪花>|<frost>', font_tpl.format(char='u')),
        ]

        processed_text = text
        for pattern, replacement in preprocessing_rules:
            processed_text = re.sub(pattern, replacement, processed_text)

        return processed_text

    def _merge_adjacent_flavor_tags(self, text: str) -> str:
        """
        合并相邻的具有相同属性的flavor标签

        Args:
            text: 输入文本
        Returns:
            合并后的文本
        """
        import re

        # 正则表达式匹配flavor标签
        flavor_pattern = r'<flavor([^>]*)>(.*?)</flavor>'

        def merge_flavors(text):
            matches = list(re.finditer(flavor_pattern, text, re.DOTALL))
            if len(matches) < 2:
                return text

            # 用于跟踪需要合并的标签组
            merge_groups = []
            current_group = [matches[0]]

            # 解析属性的辅助函数
            def parse_attributes(attr_string):
                if not attr_string:
                    return {}

                attrs = {}
                # 匹配 key="value" 格式的属性
                attr_pattern = r'(\w+)="([^"]*)"'
                for match in re.finditer(attr_pattern, attr_string):
                    key, value = match.groups()
                    attrs[key] = value
                return attrs

            # 检查两个属性字典是否相同
            def attributes_equal(attrs1, attrs2):
                return attrs1 == attrs2

            # 分组相邻且属性相同的flavor标签
            for i in range(1, len(matches)):
                prev_match = matches[i - 1]
                curr_match = matches[i]

                # 检查是否相邻（中间只有空白字符）
                between_text = text[prev_match.end():curr_match.start()].strip()

                if between_text == "":  # 相邻
                    prev_attrs = parse_attributes(prev_match.group(1))
                    curr_attrs = parse_attributes(curr_match.group(1))

                    if attributes_equal(prev_attrs, curr_attrs):
                        # 属性相同，加入当前组
                        current_group.append(curr_match)
                    else:
                        # 属性不同，开始新组
                        if len(current_group) > 1:
                            merge_groups.append(current_group)
                        current_group = [curr_match]
                else:
                    # 不相邻，开始新组
                    if len(current_group) > 1:
                        merge_groups.append(current_group)
                    current_group = [curr_match]

            # 处理最后一组
            if len(current_group) > 1:
                merge_groups.append(current_group)

            # 如果没有需要合并的组，返回原文本
            if not merge_groups:
                return text

            # 从后往前替换，避免索引偏移问题
            result_text = text
            for group in reversed(merge_groups):
                # 合并内容
                merged_content = []
                for match in group:
                    content = match.group(2).strip()
                    if content:
                        merged_content.append(content)

                # 构建合并后的标签
                first_match = group[0]
                last_match = group[-1]

                merged_text = '\n'.join(merged_content)
                new_tag = f'<flavor{first_match.group(1)}>{merged_text}</flavor>'

                # 替换原始文本中的整个区域
                start_pos = first_match.start()
                end_pos = last_match.end()

                result_text = result_text[:start_pos] + new_tag + result_text[end_pos:]

            return result_text

        # 持续合并直到没有更多可合并的标签
        prev_text = ""
        current_text = text

        while current_text != prev_text:
            prev_text = current_text
            current_text = merge_flavors(current_text)

        return current_text

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

        # print(f"开始二分查找最佳字体大小，范围: [{low}, {high}], 行距倍率: {self.line_spacing_multiplier}")

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
            # print(f"查找结束。找到的最佳字体大小为: {font_size}")
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

        parsed_items = self.rich_text_parser.parse(text, self.font_manager.lang)

        # 使用构造函数中传入的行距倍率来计算行高
        if size_to_test < 27 and self.line_spacing_multiplier > 1.05:
            line_height = int(size_to_test * 1.05)
        elif size_to_test < 29 and self.line_spacing_multiplier > 1.1:
            line_height = int(size_to_test * 1.1)
        elif size_to_test < 32 and self.line_spacing_multiplier > 1.15:
            line_height = int(size_to_test * 1.15)
        else:
            # print("使用默认行高")
            line_height = int(size_to_test * self.line_spacing_multiplier)
        # print(f"行高: {line_height}")
        # print(f"行距倍率: {self.line_spacing_multiplier}")
        # print(f"字体大小: {size_to_test}")

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

        font_stack = FontStack(base_font, base_options.font_name)
        html_tag_stack = HtmlTagStack('body')
        simfang_font = font_cache.get_font('simfang', size_to_test)

        # 字体偏移量
        font_offset_y = 0
        font_addsize = 0

        # push缓存
        push_cache = []

        for item in parsed_items:
            success = True
            if item.tag == "text":
                font = font_stack.get_top()
                font_name = font_stack.get_top_font_name()
                if item.type == TextType.OTHER:
                    # 一个一个push
                    for char in item.content:
                        if font_name == 'simfang-Italic':
                            # 使用仿宋计算字体
                            text_width, text_height = self._get_text_box(char, simfang_font)
                            text_width = int(text_width * 0.95)
                        else:
                            text_width, text_height = self._get_text_box(char, font)
                        offset_y = 0 + font_offset_y
                        offset_x = 0
                        if font_name == '方正舒体':
                            offset_y = -2
                        elif font_name == 'SourceHanSansSC-Regular':
                            offset_y = -9

                        if char == '﹒':
                            text_width = int(text_width * 0.5)
                            offset_x = -int(text_width * 0.5)
                        success = virtual_text_box.push(
                            TextObject(char, font, font_name, font.size + font_addsize, text_height, text_width,
                                       base_options.font_color, offset_x=offset_x, offset_y=offset_y)
                        )
                else:
                    text_box = self._get_text_box(item.content, font)
                    text_object = TextObject(item.content, font, font_name, font.size, text_box[1], text_box[0],
                                             base_options.font_color)
                    if self.font_manager.lang == 'zh':
                        virtual_text_box.push(text_object)
                    else:
                        if item.content == ' ':
                            # 释放缓存
                            success = virtual_text_box.push(push_cache)
                            success = virtual_text_box.push(text_object)
                            push_cache.clear()
                        else:
                            # 暂存
                            push_cache.append(text_object)
            elif item.tag == "nbsp":
                # 不断行空格
                font = font_stack.get_top()
                font_name = font_stack.get_top_font_name()
                text_box = self._get_text_box(' ', font)
                text_object = TextObject(' ', font, font_name, font.size, text_box[1], text_box[0],
                                         base_options.font_color)
                push_cache.append(text_object)
            elif item.tag == "br":
                if len(push_cache) > 0:
                    success = virtual_text_box.push(push_cache)
                    push_cache.clear()
                if html_tag_stack.get_top() == 'body':
                    success = virtual_text_box.new_paragraph()
                else:
                    success = virtual_text_box.newline()
            elif item.tag == "par":
                if len(push_cache) > 0:
                    success = virtual_text_box.push(push_cache)
                    push_cache.clear()
                success = virtual_text_box.new_paragraph()
            elif item.tag == "font":
                font_name = item.attributes.get('name', base_options.font_name)
                font_offset_y = int(item.attributes.get('offset', '0'))
                font_addsize = int(item.attributes.get('addsize', '0'))
                font_name = self.font_manager.get_lang_font(font_name).name
                font_stack.push(font_cache.get_font(font_name, size_to_test + font_addsize), font_name)
            elif item.tag == "b":
                font_stack.push(font_cache.get_font(self.default_fonts.bold, size_to_test), self.default_fonts.bold)
            elif item.tag == "i":
                font_stack.push(font_cache.get_font(self.default_fonts.italic, size_to_test), self.default_fonts.italic)
            elif item.tag == "trait":
                font_stack.push(font_cache.get_font(self.default_fonts.trait, size_to_test), self.default_fonts.trait)
            elif item.tag == "hr":
                virtual_text_box.draw_line_to_end()
            elif item.tag == "p":
                html_tag_stack.push("p")
            elif item.tag == "/p":
                html_tag_stack.pop()
            elif item.tag == "flavor":
                html_tag_stack.push("flavor")
                # 是否添加引用线
                if item.attributes.get('quote', 'false') == 'true':
                    virtual_text_box.set_guide_lines()
                # 是否响应布局
                if item.attributes.get('flex', 'true') == 'true':
                    virtual_text_box.add_flex()
                flavor_font_size = max(1, size_to_test - 2)
                font_stack.push(font_cache.get_font(self.default_fonts.italic, flavor_font_size),
                                self.default_fonts.italic)
                virtual_text_box.set_line_padding(int(item.attributes.get('padding', 15)))
                # 是否居中
                if item.attributes.get('align', 'center') == 'center':
                    virtual_text_box.set_line_center()
            elif item.tag.startswith('/'):
                if item.tag == "/font":
                    font_offset_y = 0
                    font_addsize = 0
                    font_stack.pop()
                elif item.tag in ["/b", "/i", '/trait']:
                    font_stack.pop()
                elif item.tag == "/flavor":
                    html_tag_stack.pop()
                    font_stack.pop()
                    virtual_text_box.cancel_line_padding()
                    virtual_text_box.cancel_line_center()
                    virtual_text_box.cancel_guide_lines()
            elif item.tag == "flex":
                virtual_text_box.add_flex()

            if not success:
                return False, None
        if len(push_cache) > 0:
            virtual_text_box.push(push_cache)

        return True, virtual_text_box

    # ==================== 修改 draw_complex_text 方法 ====================
    def draw_complex_text(self, text: str, polygon_vertices: List[Tuple[int, int]],
                          padding: int, options: DrawOptions,
                          draw_debug_frame: bool = False,
                          ignore_silence=False) -> list[RenderItem]:
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
        # print(text)

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

        # 首先获取所有辅助线线段的坐标
        guide_line_segments = final_vbox.get_guide_line_segments()
        # 遍历并绘制每一条线段
        for segment in guide_line_segments:
            # segment 是一个 ((x1, y1), (x2, y2)) 元组
            self.draw.line(segment, fill=options.font_color, width=2)

        # ==================== 新增代码开始 ====================
        # 获取并绘制由 <hr> 标签生成的线条
        drawn_lines = final_vbox.get_drawn_lines()
        for line_segment in drawn_lines:
            # line_segment is a ((x1, y1), (x2, y2)) tuple
            # 通常 <hr> 的线宽可以设为1
            self.draw.line(line_segment, fill=options.font_color, width=2)
        # ==================== 新增代码结束 ====================

        # 遍历渲染列表并绘制到图片上
        if not self.font_manager.silence or ignore_silence:
            for render_item in render_list:
                obj = render_item.obj
                x, y = render_item.x, render_item.y
                offset_y = 0
                offset_x = 0
                if obj.font_name == 'arkham-icons' and self.font_manager.lang != 'zh':
                    offset_y += -2
                if obj.font_name == '江城斜宋体':
                    offset_y = -9

                if isinstance(obj, TextObject):
                    self.draw.text((x, y + offset_y), obj.text, font=obj.font, fill=options.font_color)
                elif isinstance(obj, ImageObject):
                    if obj.image.mode == 'RGBA':
                        self.image.paste(obj.image, (x, y), obj.image)
                    else:
                        self.image.paste(obj.image, (x, y))
                    if draw_debug_frame:
                        self.draw.rectangle([(x, y), (x + obj.width, y + obj.height)], outline="green", width=1)
        return render_list

    def draw_line(self, text: str, position: Tuple[int, int],
                  alignment: TextAlignment, options: DrawOptions,
                  vertical: bool = False, vertical_line_spacing: float = 1.2) -> list[RenderItem]:
        """
        绘制一行支持HTML语法的文本，支持水平和垂直两种模式。

        Args:
            text: 要绘制的文本，支持<b>, <i>, <trait>, <font>等标签。
            position: 位置坐标(x, y)。
                      水平模式：
                      - Center: (x, y)是整行文本的中心点。
                      - Left: (x, y)是整行文本的左上角顶点。
                      - Right: (x, y)是整行文本的右上角顶点。
                      垂直模式：
                      - Center: (x, y)是整列文本的中心点。
                      - Left: (x, y)是整列文本的底部中心点。
                      - Right: (x, y)是整列文本的顶部中心点。
            alignment: 对齐方式 (TextAlignment.LEFT, .CENTER, .RIGHT)。
            options: 绘制选项，提供默认字体、大小和颜色。
            vertical: 是否为垂直文本模式，默认为False（水平模式）。
            vertical_line_spacing: 垂直模式下的行间距倍率，默认为1.2。

        Returns:
            list[RenderItem]: 渲染项列表，包含绘制的文本对象及其位置信息
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
            return []

        font_stack = FontStack(base_font, options.font_name)

        # 第一遍遍历：计算总宽度和高度，收集渲染信息
        render_segments = []  # 存储每个文本片段的渲染信息
        total_width = 0
        total_height = 0
        max_height = 0
        max_width = 0

        for item in parsed_items:
            if item.tag == "text":
                font = font_stack.get_top()
                font_name = font_stack.get_top_font_name()
                text_content = item.content

                if item.type == TextType.OTHER or (vertical & (item.type == TextType.ENGLISH)):
                    # 逐字符处理
                    for char in text_content:
                        text_box = self._get_text_box(char, font)
                        char_height = text_box[1]
                        char_width = text_box[0]

                        # 在垂直模式下应用行间距
                        if vertical:
                            spaced_height = int(char_height * vertical_line_spacing)
                        else:
                            spaced_height = char_height

                        render_segments.append({
                            'text': char,
                            'font': font,
                            'font_name': font_name,
                            'width': char_width,
                            'height': char_height,  # 原始高度，用于绘制
                            'spaced_height': spaced_height,  # 带间距的高度，用于布局
                            'color': options.font_color
                        })

                        if vertical:
                            total_height += spaced_height
                            max_width = max(max_width, char_width)
                        else:
                            total_width += char_width
                            max_height = max(max_height, char_height)
                else:
                    # 整块文本处理
                    text_box = self._get_text_box(text_content, font)
                    char_height = text_box[1]
                    char_width = text_box[0]

                    # 在垂直模式下应用行间距
                    if vertical:
                        spaced_height = int(char_height * vertical_line_spacing)
                    else:
                        spaced_height = char_height

                    render_segments.append({
                        'text': text_content,
                        'font': font,
                        'font_name': font_name,
                        'width': char_width,
                        'height': char_height,  # 原始高度，用于绘制
                        'spaced_height': spaced_height,  # 带间距的高度，用于布局
                        'color': options.font_color
                    })

                    if vertical:
                        total_height += spaced_height
                        max_width = max(max_width, char_width)
                    else:
                        total_width += char_width
                        max_height = max(max_height, char_height)

            elif item.tag == "font":
                font_name = item.attributes.get('name', options.font_name)
                font_name = self.font_manager.get_lang_font(font_name).name
                try:
                    font_stack.push(font_cache.get_font(font_name, options.font_size), font_name)
                except Exception as e:
                    print(f"字体切换失败: {e}")

            elif item.tag == "b":
                try:
                    font_stack.push(font_cache.get_font(self.default_fonts.bold, options.font_size),
                                    self.default_fonts.bold)
                except Exception as e:
                    print(f"粗体字体加载失败: {e}")

            elif item.tag == "i":
                try:
                    font_stack.push(font_cache.get_font(self.default_fonts.italic, options.font_size),
                                    self.default_fonts.italic)
                except Exception as e:
                    print(f"斜体字体加载失败: {e}")

            elif item.tag == "trait":
                try:
                    font_stack.push(font_cache.get_font(self.default_fonts.trait, options.font_size),
                                    self.default_fonts.trait)
                except Exception as e:
                    print(f"特质字体加载失败: {e}")

            elif item.tag.startswith('/'):
                if item.tag in ["/font", "/b", "/i", '/trait']:
                    font_stack.pop()

        # 根据对齐方式和垂直/水平模式计算起始位置
        x, y = position

        if vertical:
            # 垂直文本模式
            if alignment == TextAlignment.CENTER:
                # 中心点对齐：position是文本中心点
                start_x = x - max_width // 2
                start_y = y - total_height // 2
            elif alignment == TextAlignment.LEFT:
                # 底部对齐：position是底部中心点
                start_x = x - max_width // 2
                start_y = y - total_height
            elif alignment == TextAlignment.RIGHT:
                # 顶部对齐：position是顶部中心点
                start_x = x - max_width // 2
                start_y = y
            else:
                # 默认中心对齐
                start_x = x - max_width // 2
                start_y = y - total_height // 2
        else:
            # 水平文本模式（原有逻辑）
            if alignment == TextAlignment.CENTER:
                # 中心对齐：position是文本中心点
                start_x = x - total_width // 2
                start_y = y - (options.font_size * 0.8) // 2
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

        # 第二遍：实际绘制文本，同时创建RenderItem列表
        current_x = start_x
        current_y = start_y
        render_items = []  # 用于存储RenderItem对象
        border_width = 0
        border_color = None
        if options.has_border:
            border_width = options.border_width
            border_color = options.border_color

        for segment in render_segments:
            # 创建TextObject
            text_obj = TextObject(
                text=segment['text'],
                font=segment['font'],
                font_name=segment['font_name'],
                font_size=segment['font'].size,
                height=segment['height'],  # 使用原始高度
                width=segment['width'],
                color=segment['color'],
                border_width=border_width,
                border_color=border_color
            )
            if not self.font_manager.silence:
                if vertical:
                    # 垂直模式：每个字符居中对齐在列中
                    char_x = start_x + (max_width - segment['width']) // 2
                    char_y = current_y

                    # 创建RenderItem并添加到列表
                    render_item = RenderItem(
                        obj=text_obj,
                        x=char_x,
                        y=char_y
                    )
                    render_items.append(render_item)

                    # 绘制文本
                    self.draw.text(
                        (char_x, char_y),
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
                                        (char_x + dx, char_y + dy),
                                        segment['text'],
                                        font=segment['font'],
                                        fill=options.border_color
                                    )
                        # 重新绘制主文本（覆盖边框）
                        self.draw.text(
                            (char_x, char_y),
                            segment['text'],
                            font=segment['font'],
                            fill=segment['color']
                        )

                    # 更新y坐标（垂直移动），使用带间距的高度
                    current_y += segment['spaced_height']
                else:
                    # 水平模式（原有逻辑）
                    # 创建RenderItem并添加到列表
                    render_item = RenderItem(
                        obj=text_obj,
                        x=current_x,
                        y=start_y
                    )
                    render_items.append(render_item)

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
            if vertical:
                # 垂直模式的下划线（实际是侧边线）
                underline_x = start_x + max_width + 2
                x_offset = 12
                self.draw.line(
                    (underline_x + x_offset, start_y, underline_x + x_offset, start_y + total_height),
                    fill=options.font_color,
                    width=1
                )
                x_offset = x_offset + 6
                self.draw.line(
                    (underline_x + x_offset, start_y, underline_x + x_offset, start_y + total_height),
                    fill=options.font_color,
                    width=2
                )
            else:
                # 水平模式的下划线
                underline_y = start_y + max_height + 2
                if self.font_manager.lang == 'zh':
                    y_offset = 12
                else:
                    y_offset = 0
                self.draw.line(
                    (start_x, underline_y + y_offset, start_x + total_width, underline_y + y_offset),
                    fill=options.font_color,
                    width=1
                )
                y_offset = y_offset + 6
                self.draw.line(
                    (start_x, underline_y + y_offset, start_x + total_width, underline_y + y_offset),
                    fill=options.font_color,
                    width=2
                )

        return render_items


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
