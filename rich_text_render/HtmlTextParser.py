import re
from enum import Enum
from typing import List, Dict
import unicodedata


class TextType(Enum):
    """文本类型枚举"""
    ENGLISH = "english"  # 英文字母
    NUMBER = "number"  # 数字
    PUNCTUATION = "punctuation"  # 标点符号
    SPACE = "space"  # 空格
    OTHER = "other"  # 其他字符（如中文）
    HTML_START = "html_start"  # HTML开始标签
    HTML_END = "html_end"  # HTML结束标签
    HTML_SELF_CLOSE = "html_self_close"  # HTML自闭合标签
    ENGLISH_BLOCK = "english_block"  # 英文块（简单解析模式）


class ParsedItem:
    """解析结果项"""

    def __init__(self, tag: str, type_: TextType, attributes: Dict[str, str] = None, content: str = ''):
        self.tag = tag
        self.type = type_
        self.attributes = attributes or {}
        self.content = content

    def __repr__(self):
        return f"ParsedItem(tag={self.tag!r}, type={self.type}, attributes={self.attributes}, content={self.content!r})"

    def __str__(self):
        type_info = f"({self.type.value})" if isinstance(self.type, TextType) else f"({self.type})"
        content_display = repr(self.content) if len(self.content) <= 30 else repr(self.content[:27] + '...')
        return f"{self.tag:15} {type_info:18} | 属性: {str(self.attributes):20} | 内容: {content_display}"


class RichTextParser:
    def __init__(self):
        # HTML标签模式
        self.html_tag_pattern = r'<(/?)([a-zA-Z][a-zA-Z0-9]*)\s*([^>]*?)>'
        # 有效的HTML标签 - 新增par标签
        self.valid_tags = ['b', 'i', 'u', 'p', 'font', 'flavor', 'em', 'br', 'hr', 'par', 'flex', 'trait', 'nbsp']

        # 英文单词模式 - 改进版本，支持更多特殊字符
        self.english_word_pattern = r'\b[\w\'\-]+\b'
        # 特殊字符模式：匹配重音字符、撇号、连字符等
        self.special_chars_pattern = r'[^\w\s]'  # 非字母数字和空白字符

        # &nbsp;占位符
        self.nbsp_placeholder = '\x00'

    def parse_attributes(self, attr_string: str) -> Dict[str, str]:
        """解析标签属性"""
        attributes = {}
        if not attr_string.strip():
            return attributes

        # 匹配属性模式：name="value" 或 name='value' 或 name=value
        attr_pattern = r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))'
        matches = re.findall(attr_pattern, attr_string)

        for match in matches:
            name = match[0]
            value = match[1] or match[2] or match[3]
            attributes[name] = value

        return attributes

    def classify_character(self, char: str) -> TextType:
        """分类字符类型 - 改进版本，支持更多Unicode字符"""
        if char == '\n':
            return None  # \n将被特殊处理为br标签
        elif char.isspace():
            return TextType.SPACE
        elif self.is_english_character(char):
            return TextType.ENGLISH
        elif char.isdigit():
            return TextType.NUMBER
        elif char in '.,!?;:()[]{}""\'`~@#$%^&*_+=|\\/<>':
            return TextType.PUNCTUATION
        else:
            return TextType.OTHER

    def is_english_character(self, char: str) -> bool:
        """判断是否为英文字符（包括带重音的字符）"""
        if len(char) != 1:
            return False

        # 基本拉丁字母
        if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            return True

        # 扩展拉丁字母（包含重音符号）
        if ord(char) >= 192 and ord(char) <= 255:
            return True

        # 检查Unicode类别
        try:
            category = unicodedata.category(char)
            # 字母类别：Ll, Lm, Lo, Lt, Lu
            if category.startswith('L'):
                # 对于非基本拉丁字母，检查是否包含在常见英语特殊字符中
                return char in "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ"
        except:
            pass

        return False

    def is_valid_english_word(self, word: str) -> bool:
        """检查是否是有效的英文单词"""
        if not word:
            return False

        # 必须包含至少一个字母
        if not any(self.is_english_character(c) for c in word):
            return False

        # 检查单词格式（可以包含字母、数字、撇号、连字符）
        pattern = r'^[a-zA-ZÀ-ÿ][\w\'\-]*[a-zA-ZÀ-ÿ]$|^[a-zA-ZÀ-ÿ]$'
        return bool(re.match(pattern, word, re.UNICODE))

    def extract_english_words(self, text: str) -> List[str]:
        """从文本中提取所有英文单词"""
        words = re.findall(self.english_word_pattern, text, re.UNICODE)
        return [word for word in words if self.is_valid_english_word(word)]

    def simple_split_text(self, text: str) -> List[ParsedItem]:
        """简单模式的文本分割（用于非zh语言）

        只分为英文块和空格块，支持&nbsp;作为连接符
        """
        if not text:
            return []

        result = []

        # 处理换行符
        if '\n' in text:
            parts = text.split('\n')
            for i, part in enumerate(parts):
                if i > 0:
                    # 在每个换行处添加br标签
                    result.append(ParsedItem(
                        tag='br',
                        type_=TextType.HTML_SELF_CLOSE,
                        attributes={},
                        content=''
                    ))
                if part:
                    result.extend(self.simple_split_text(part))
            return result

        # 第一步：将&nbsp;替换为占位符
        text_with_placeholder = text.replace('&nbsp;', self.nbsp_placeholder)

        # 第二步：按空格分割
        i = 0
        current_block = ""

        while i < len(text_with_placeholder):
            char = text_with_placeholder[i]

            if char.isspace():
                # 遇到空格，保存当前块
                if current_block:
                    # 将占位符还原为空格
                    content = current_block.replace(self.nbsp_placeholder, ' ')
                    result.append(ParsedItem(
                        tag='text',
                        type_=TextType.ENGLISH_BLOCK,
                        attributes={},
                        content=content
                    ))
                    current_block = ""

                # 添加空格块
                result.append(ParsedItem(
                    tag='text',
                    type_=TextType.SPACE,
                    attributes={},
                    content=' '
                ))
            else:
                # 非空格字符，累积到当前块
                current_block += char

            i += 1

        # 保存最后的块
        if current_block:
            content = current_block.replace(self.nbsp_placeholder, ' ')
            result.append(ParsedItem(
                tag='text',
                type_=TextType.ENGLISH_BLOCK,
                attributes={},
                content=content
            ))

        return result

    def split_text_by_type(self, text: str) -> List[ParsedItem]:
        """按字符类型分割文本，并处理换行符、连字符和数字范围 - 改进版本"""
        if not text:
            return []

        result = []
        current_text = ""
        current_type = None

        i = 0
        while i < len(text):
            char = text[i]

            # 处理换行符
            if char == '\n':
                # 先保存当前累积的文本
                if current_text:
                    result.append(ParsedItem(
                        tag='text',
                        type_=current_type,
                        attributes={},
                        content=current_text
                    ))
                    current_text = ""
                    current_type = None

                # 添加br标签
                result.append(ParsedItem(
                    tag='br',
                    type_=TextType.HTML_SELF_CLOSE,
                    attributes={},
                    content=''
                ))

                i += 1
                continue

            char_type = self.classify_character(char)

            # 特殊处理连字符：如果连字符前后都是数字，将其视为数字范围的一部分
            if char == '-' and 0 < i < len(text) - 1:
                prev_char = text[i - 1]
                next_char = text[i + 1]

                # 数字范围检测：前后都是数字
                if (prev_char.isdigit() and next_char.isdigit() and
                        current_type == TextType.NUMBER):
                    # 连字符被视为数字范围的一部分
                    char_type = TextType.NUMBER
                    current_text += char
                    i += 1
                    continue

                # 英文单词内部的连字符
                elif (self.is_english_character(prev_char) and
                      self.is_english_character(next_char)):
                    char_type = TextType.ENGLISH

            # 特殊处理撇号：如果撇号在单词内部，将其视为英文单词的一部分
            if char == "'" and 0 < i < len(text) - 1:
                prev_char = text[i - 1]
                next_char = text[i + 1]
                if (self.is_english_character(prev_char) and
                        self.is_english_character(next_char)):
                    char_type = TextType.ENGLISH

            if current_type is None:
                current_type = char_type
                current_text = char
            elif current_type == char_type:
                current_text += char
            else:
                # 类型变化，保存当前文本
                if current_text:
                    result.append(ParsedItem(
                        tag='text',
                        type_=current_type,
                        attributes={},
                        content=current_text
                    ))
                current_text = char
                current_type = char_type

            i += 1

        # 保存最后的文本
        if current_text:
            result.append(ParsedItem(
                tag='text',
                type_=current_type,
                attributes={},
                content=current_text
            ))

        return result

    def find_matching_close_tag(self, html_text: str, start_pos: int, tag_name: str) -> int:
        """查找匹配的闭合标签位置"""
        pos = start_pos
        tag_count = 1  # 已经遇到了一个开始标签

        while pos < len(html_text) and tag_count > 0:
            # 查找下一个标签
            match = re.search(self.html_tag_pattern, html_text[pos:])
            if not match:
                break

            full_match = match.group(0)
            is_closing = bool(match.group(1))
            found_tag_name = match.group(2).lower()

            # 只关心同名标签
            if found_tag_name == tag_name:
                if is_closing:
                    tag_count -= 1
                else:
                    tag_count += 1

            pos += match.start() + len(full_match)

            if tag_count == 0:
                return pos - len(full_match)

        return -1  # 没找到匹配的闭合标签

    def parse(self, html_text: str, lang: str = 'zh') -> List[ParsedItem]:
        """解析富文本

        Args:
            html_text: 要解析的HTML文本
            lang: 语言模式，默认'zh'。
                  'zh': 使用完整解析（按字符类型分割）
                  其他值: 使用简单解析（只分英文块和空格块）

        Returns:
            解析结果列表
        """
        result = []
        i = 0

        while i < len(html_text):
            # 查找下一个可能的标签
            tag_match = re.search(self.html_tag_pattern, html_text[i:])

            if tag_match:
                # 获取标签前的文本
                text_before = html_text[i:i + tag_match.start()]
                if text_before:
                    # 根据lang参数选择解析方式
                    if lang == 'zh':
                        text_items = self.split_text_by_type(text_before)
                    else:
                        text_items = self.simple_split_text(text_before)
                    result.extend(text_items)

                # 解析标签
                full_match = tag_match.group(0)
                is_closing = bool(tag_match.group(1))
                tag_name = tag_match.group(2).lower()
                attr_string = tag_match.group(3)

                # 检查是否是有效的HTML标签
                if tag_name in self.valid_tags and not is_closing:
                    # 解析开始标签
                    attributes = self.parse_attributes(attr_string)

                    # 自闭合标签 - 新增par标签到自闭合标签列表
                    if tag_name in ['br', 'hr', 'par', 'flex', 'nbsp'] or full_match.endswith('/>'):
                        result.append(ParsedItem(
                            tag=tag_name,
                            type_=TextType.HTML_SELF_CLOSE,
                            attributes=attributes,
                            content=''
                        ))
                        i += tag_match.start() + len(full_match)
                    else:
                        # 查找匹配的闭合标签
                        close_tag_pos = self.find_matching_close_tag(
                            html_text, i + tag_match.start() + len(full_match), tag_name
                        )

                        if close_tag_pos != -1:
                            # 找到了匹配的闭合标签
                            content_start = i + tag_match.start() + len(full_match)
                            content_end = close_tag_pos
                            tag_content = html_text[content_start:content_end]

                            # 添加开始标签
                            result.append(ParsedItem(
                                tag=tag_name,
                                type_=TextType.HTML_START,
                                attributes=attributes,
                                content=''
                            ))

                            # 递归解析标签内容，传递lang参数
                            if tag_content:
                                inner_parsed = self.parse(tag_content, lang=lang)
                                result.extend(inner_parsed)

                            # 添加结束标签
                            result.append(ParsedItem(
                                tag=f'/{tag_name}',
                                type_=TextType.HTML_END,
                                attributes={},
                                content=''
                            ))

                            # 移动到闭合标签之后
                            close_tag_match = re.search(self.html_tag_pattern, html_text[close_tag_pos:])
                            if close_tag_match:
                                i = close_tag_pos + close_tag_match.start() + len(close_tag_match.group(0))
                            else:
                                i = len(html_text)
                        else:
                            # 没找到匹配的闭合标签，当作普通文本处理
                            if lang == 'zh':
                                text_items = self.split_text_by_type(full_match)
                            else:
                                text_items = self.simple_split_text(full_match)
                            result.extend(text_items)
                            i += tag_match.start() + len(full_match)
                else:
                    # 无效标签或闭合标签，当作文本处理
                    if lang == 'zh':
                        text_items = self.split_text_by_type(full_match)
                    else:
                        text_items = self.simple_split_text(full_match)
                    result.extend(text_items)
                    i += tag_match.start() + len(full_match)
            else:
                # 没有更多标签，处理剩余文本
                remaining_text = html_text[i:]
                if remaining_text:
                    if lang == 'zh':
                        text_items = self.split_text_by_type(remaining_text)
                    else:
                        text_items = self.simple_split_text(remaining_text)
                    result.extend(text_items)
                break

        return result


# 测试代码
def test_parser():
    parser = RichTextParser()

    print("=" * 100)
    print("测试1: 中文模式 (lang='zh')")
    print("=" * 100)

    # 测试包含特殊字符的英文单词
    test_text_zh = (
        "aëroplane location's café naïve résumé coöperate façade "
        "It's a well-known fact that piñatas are fun at fiestas. "
        "<b>Herta's special ability</b> works with coördination. "
        "The naïve coöperation between teams was impressive. "
        "Let's test email addresses: user@example.com and phone numbers: +1-555-1234.哈哈你好"
    )

    parsed_result = parser.parse(test_text_zh, lang='zh')
    print("解析结果：")
    for i, item in enumerate(parsed_result):
        print(f"{i + 1:2d}. {item}")

    print("\n" + "=" * 100)
    print("测试2: 英文简单模式 (lang='en')")
    print("=" * 100)

    test_text_en = "i am a <b>good</b> student. Hello world!"
    parsed_result_en = parser.parse(test_text_en, lang='en')
    print("解析结果：")
    for i, item in enumerate(parsed_result_en):
        print(f"{i + 1:2d}. {item}")

    print("\n" + "=" * 100)
    print("测试3: &nbsp;连接符测试")
    print("=" * 100)

    test_text_nbsp = "i&nbsp;am a student"
    parsed_result_nbsp = parser.parse(test_text_nbsp, lang='en')
    print("解析结果：")
    for i, item in enumerate(parsed_result_nbsp):
        print(f"{i + 1:2d}. {item}")

    print("\n" + "=" * 100)
    print("测试4: 复杂&nbsp;测试")
    print("=" * 100)

    test_text_complex = "Hello&nbsp;World i am <b>good&nbsp;student</b> test"
    parsed_result_complex = parser.parse(test_text_complex, lang='en')
    print("解析结果：")
    for i, item in enumerate(parsed_result_complex):
        print(f"{i + 1:2d}. {item}")

    print("\n" + "=" * 100)
    print("测试5: 换行符测试")
    print("=" * 100)

    test_text_newline = "Hello World<br>i am student"
    parsed_result_newline = parser.parse(test_text_newline, lang='en')
    print("解析结果：")
    for i, item in enumerate(parsed_result_newline):
        print(f"{i + 1:2d}. {item}")


# 额外的工具函数，更新为使用ParsedItem
def filter_by_type(parsed_result: List[ParsedItem], text_type: TextType) -> List[ParsedItem]:
    """按类型过滤解析结果"""
    return [item for item in parsed_result if item.type == text_type]


def get_all_english_words(parsed_result: List[ParsedItem]) -> List[str]:
    """获取所有英文单词"""
    english_items = filter_by_type(parsed_result, TextType.ENGLISH)
    return [item.content for item in english_items]


def get_all_numbers(parsed_result: List[ParsedItem]) -> List[str]:
    """获取所有数字"""
    number_items = filter_by_type(parsed_result, TextType.NUMBER)
    return [item.content for item in number_items]


def get_all_html_tags(parsed_result: List[ParsedItem]) -> List[ParsedItem]:
    """获取所有HTML标签"""
    return [item for item in parsed_result if
            item.type in [TextType.HTML_START, TextType.HTML_END, TextType.HTML_SELF_CLOSE]]


def get_paragraph_tags(parsed_result: List[ParsedItem]) -> List[ParsedItem]:
    """获取所有段落标签"""
    return [item for item in parsed_result if item.tag == 'par']


def get_all_english_blocks(parsed_result: List[ParsedItem]) -> List[str]:
    """获取所有英文块（简单模式）"""
    english_blocks = filter_by_type(parsed_result, TextType.ENGLISH_BLOCK)
    return [item.content for item in english_blocks]


if __name__ == "__main__":
    test_parser()
