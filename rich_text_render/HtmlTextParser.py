import re
from enum import Enum
from typing import List, Dict, Any


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
        self.valid_tags = ['b', 'i', 'u', 'font', 'flavor', 'em', 'br', 'hr', 'par', 'flex']

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
        """分类字符类型"""
        if char == '\n':
            return None  # \n将被特殊处理为br标签
        elif char.isspace():
            return TextType.SPACE
        elif char.isalpha() and ord(char) < 128:  # 英文字母
            return TextType.ENGLISH
        elif char.isdigit():
            return TextType.NUMBER
        elif char in '.,!?;:()[]{}""\'`~@#$%^&*-_+=|\\/<>':
            return TextType.PUNCTUATION
        else:
            return TextType.OTHER

    def split_text_by_type(self, text: str) -> List[ParsedItem]:
        """按字符类型分割文本，并处理换行符"""
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

    def parse(self, html_text: str) -> List[ParsedItem]:
        """解析富文本"""
        result = []
        i = 0

        while i < len(html_text):
            # 查找下一个可能的标签
            tag_match = re.search(self.html_tag_pattern, html_text[i:])

            if tag_match:
                # 获取标签前的文本
                text_before = html_text[i:i + tag_match.start()]
                if text_before:
                    text_items = self.split_text_by_type(text_before)
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
                    if tag_name in ['br', 'hr', 'par', 'flex'] or full_match.endswith('/>'):
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

                            # 递归解析标签内容
                            if tag_content:
                                inner_parsed = self.parse(tag_content)
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
                            text_items = self.split_text_by_type(full_match)
                            result.extend(text_items)
                            i += tag_match.start() + len(full_match)
                else:
                    # 无效标签或闭合标签，当作文本处理
                    text_items = self.split_text_by_type(full_match)
                    result.extend(text_items)
                    i += tag_match.start() + len(full_match)
            else:
                # 没有更多标签，处理剩余文本
                remaining_text = html_text[i:]
                if remaining_text:
                    text_items = self.split_text_by_type(remaining_text)
                    result.extend(text_items)
                break

        return result


# 测试代码
def test_parser():
    test_text = (
        "这是第一段文本内容。<par>这是第二段文本内容。<par>"
        "这是一个复杂的中英文<测试>混排测试文本。Here we have <b>English words</b> mixed with 中文文字，"
        "以及各种标点符号：逗号，句号。问号？感叹号！分号；冒号：引号\"测试\"和括号（内容）。<par>"
        "<font size=\"+4\" color=\"blue\">This is a very long English sentence</font>，"
        "而是应该在单词边界处换行。同时，标点符号也不应该出现在行尾，"
        "比如这个长句子后面的逗号，应该和前面的内容一起换行。<par>"
        "让我们测试一些更复杂的情况：<i>supercalifragilisticexpialidocious</i> 这是一个超长的英文单词。"
        "还有一些数字和符号：12345、67890、email@example.com、www.website.com等。"
        "\n这里有一个手动换行。\n<par>"
        "最后，让我们看看程序如何处理各种边界情况和特殊字符：©®™€£¥等。<par>"
        "You begin the game with 4 copies of Herta Puppet in play. When any amount of damage would be placed on you, "
        "place those damage on Herta Puppet (Online) instead.\n【Forced】 – When Herta Puppet (Online) is dealt damage: "
        "You take 1 direct horror."
    )

    parser = RichTextParser()
    parsed_result = parser.parse(test_text)

    print("解析结果：")
    print("=" * 100)
    for i, item in enumerate(parsed_result):
        print(f"{i + 1:2d}. {item}")

    # 演示新的用法
    print("\n" + "=" * 50)
    print("使用 .tag 调用示例：")
    for i, item in enumerate(parsed_result[:15]):  # 显示前15个
        print(f"项目 {i + 1}: 标签={item.tag}, 类型={item.type.value}, 内容={repr(item.content)}")


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


if __name__ == "__main__":
    test_parser()

    print("\n" + "=" * 50)
    print("额外测试：")

    # 测试换行符和段落标签处理
    test_newline_and_par = "第一行\n第二行<par>第一段<par>第二段\n\n第三行"
    parser = RichTextParser()
    result = parser.parse(test_newline_and_par)

    print("换行符和段落标签测试结果：")
    for i, item in enumerate(result):
        print(f"{i + 1}. {item}")

    # 演示工具函数和新的属性访问方式
    print("\n所有英文单词：", get_all_english_words(result))
    print("所有数字：", get_all_numbers(result))
    print("所有段落标签：", get_paragraph_tags(result))

    # 新的用法示例
    print("\n使用点语法访问属性：")
    for item in result[:8]:
        print(f"标签: {item.tag}, 类型: {item.type.value}, 属性: {item.attributes}, 内容: {repr(item.content)}")
