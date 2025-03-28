import json
import os
import re

from PIL import Image, ImageDraw, ImageFont


def parse_html(text):
    """
    解析HTML格式的文本，提取标签和内容

    :param text: 包含HTML标签的输入文本
    :return: 包含标签信息的字典列表，每个元素包含tag(标签名)、attrs(属性字典)、content(内容)
    """
    split_pattern = re.compile(r'(<[^>]+>)|([^<]+)')
    tag_parser = re.compile(r'</?([^\s/>]+)(\s+([^>]*))?/?>')
    attr_pattern = re.compile(r'''([^\s=]+)\s*=\s*['"]([^'"]*)['"]''')

    result = []
    stack = []
    current_content = []

    for match in split_pattern.finditer(text):
        tag_part, text_part = match.groups()

        if tag_part:
            tag_match = tag_parser.match(tag_part)
            if not tag_match:
                continue

            tag_name = tag_match.group(1).lower()
            is_end = tag_part.startswith('</')
            is_self_closing = tag_part.endswith('/>') or tag_name in {'hr', 'lr', 'br', 'img'}
            attrs_str = tag_match.group(3) or ''
            attrs = dict(attr_pattern.findall(attrs_str))

            if is_end:
                if stack and stack[-1]['tag'] == tag_name:
                    opened_tag = stack.pop()
                    result.append({
                        'tag': opened_tag['tag'],
                        'attrs': opened_tag['attrs'],
                        'content': ''.join(current_content).strip()
                    })
                    current_content = []

            elif is_self_closing:
                result.append({
                    'tag': tag_name,
                    'attrs': attrs,
                    'content': ''
                })

            else:
                stack.append({
                    'tag': tag_name,
                    'attrs': attrs
                })
                current_content = []

        elif text_part:
            if stack:
                current_content.append(text_part)
            else:
                if text_part.strip():
                    result.append({
                        'tag': 'text',
                        'content': text_part.strip('\n')
                    })

    return result


class ImageManager:
    """图像资源管理器，用于预加载和管理图片文件"""

    def __init__(self, image_folder='images'):
        """
        初始化图像管理器

        :param image_folder: 图片文件存放目录，默认为'images'
        """
        self.image_map = {}
        self.image_folder = image_folder
        self._load_images()

    def _load_images(self):
        """加载图片目录下所有支持的图像文件"""
        supported_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        try:
            for filename in os.listdir(self.image_folder):
                name, ext = os.path.splitext(filename)
                if ext.lower() in supported_ext:
                    # 统一使用小写文件名作为键
                    self.image_map[name.lower()] = self.open(os.path.join(self.image_folder, filename))
        except FileNotFoundError:
            print(f"错误：图片目录 {self.image_folder} 不存在")
        except Exception as e:
            print(f"图片加载失败: {str(e)}")

    def open(self, path, **kwargs):
        """
        打开指定图片文件（支持PIL.Image.open参数）

        :param path: 图片路径
        :param kwargs: 传递给Image.open的额外参数
        :return: PIL.Image对象，如果找不到返回None
        """
        try:
            img = Image.open(path, **kwargs)
            # 自动将图片转换为RGB模式（如果需要）
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            return img
        except Exception as e:
            print(f"无法打开图片 {path}: {str(e)}")
            return None

    def get_image(self, image_name):
        """
        获取图片

        :param image_name: 图片名称（不带扩展名）
        :return: 图片对象
        """
        return self.image_map.get(image_name.lower())


class FontManager:
    """字体管理器，用于预加载和管理字体文件"""

    def __init__(self, font_folder='fonts', lang='zh'):
        """
        初始化字体管理器

        :param font_folder: 字体文件存放目录，默认为'fonts'
        """
        if lang == 'en':
            self.font_dict = {
                '思源黑体': 'NimbusRomNo9L-Med',
                '方正舒体': 'NimbusRomNo9L-MedIta',
                'simfang': 'ArnoPro-Regular',
                '汉仪小隶书简': 'Teutonic',
                '副标题': 'ArnoPro-Smbd',
                '小字': 'ArnoPro-Smbd'
            }
        else:
            self.font_dict = {
                '副标题': '汉仪小隶书简',
                '小字': '汉仪小隶书简',
            }
        self.font_map = {}
        self.font_folder = font_folder
        self._load_fonts()
        self.lang = lang

    def _load_fonts(self):
        """加载字体目录下所有支持的字体文件"""
        supported_ext = ['.ttf', '.otf', '.ttc']
        try:
            for filename in os.listdir(self.font_folder):
                name, ext = os.path.splitext(filename)
                if ext.lower() in supported_ext:
                    self.font_map[name.lower()] = os.path.join(self.font_folder, filename)
        except Exception as e:
            print(f"字体加载失败: {str(e)}")

    def get_font_path(self, font_name):
        """
        获取字体文件路径

        :param font_name: 字体名称（不带扩展名）
        :return: 字体文件完整路径，如果找不到返回None
        """
        return self.font_map.get(self.font_dict.get(font_name, font_name).lower())

    def get_font_offset(self, font_name):
        """
        获取字体偏移量

        :param font_name: 字体名称（不带扩展名）
        :return: 字体偏移量，如果找不到返回0
        """
        if self.lang == 'en' and font_name == '汉仪小隶书简':
            return 6
        if self.lang == 'en' and font_name == '副标题':
            return 3
        if self.lang == 'en' and font_name == '小字':
            return 5
        return 0

    def get_font_text(self, text):
        """
        获取字体文本

        :param text: 文本
        :return: 文本
        """
        if self.lang == 'en':
            if text == '技能':
                return 'SKILL'
            elif text == '地点':
                return 'LOCATION'
            elif text == '事件':
                return 'EVENT'
            elif text == '支援':
                return 'ASSET'
            elif text == '诡计':
                return 'TREACHERY'
            elif text == '敌人':
                return 'ENEMY'

        return text


symbol_list = ['，', '。', '：', ':', '“', '”', '.']


class Card:
    def __init__(self, width, height, font_manager=None, image_manager=None, card_type='default', card_class='default'):
        """
        初始化卡牌对象

        :param width: 卡牌宽度（像素）
        :param height: 卡牌高度（像素）
        :param font_manager: 字体管理器实例，如果未提供则新建默认实例
        :param image_manager: 图像管理器实例，如果未提供则新建默认实例
        :param card_type: 卡牌类型 技能卡、支援卡、事件卡
        :param lang:语言 zh 中文 en 英文
        """
        self.width = width
        self.height = height
        self.image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.font_manager = font_manager if font_manager else FontManager()
        self.image_manager = image_manager if image_manager else ImageManager()
        self.default_font = ImageFont.load_default()
        self.submit_index = 0  # 投入图标索引
        self.slots_index = 0  # 槽位索引
        self.card_type = card_type
        self.card_class = card_class
        self.text_mark = []

    def _extend_image_right(self, source_img, extension=800):
        # 截取右边5%的像素
        right_crop = 15
        img = source_img.crop((source_img.width - right_crop, 0, source_img.width, source_img.height))
        # 计算新尺寸（宽度翻倍）
        new_size = (img.width + extension, img.height)
        img = img.resize(new_size, resample=Image.BILINEAR)
        # 拼接source_img和img
        result_img = Image.new('RGB', (source_img.width + extension, source_img.height))
        result_img.paste(source_img, (0, 0))
        result_img.paste(img, (source_img.width - 15, 0))
        return result_img

    def paste_image(self, img, region, resize_mode='stretch', transparent_list=None, extension=0):
        """
        在指定区域粘贴图片

        :param img: 图片
        :param region: 目标区域坐标和尺寸 (x, y, width, height)
        :param resize_mode: 调整模式，可选'stretch'(拉伸)/'contain'(适应)/'cover'(覆盖)
        :param transparent_list: 透明区域圆，为(x, y, r)
        """
        if transparent_list is None:
            transparent_list = []
        if transparent_list and not isinstance(transparent_list[0], tuple):
            transparent_list = [transparent_list]
        try:
            target_w, target_h = img.width, img.height
            if len(region) == 4:
                target_w, target_h = region[2], region[3]

            if resize_mode == 'stretch':
                img = img.resize((target_w, target_h))
            else:
                ratio = (min if resize_mode == 'contain' else max)(target_w / img.width, target_h / img.height)
                img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
                if resize_mode == 'cover':
                    left = (img.width - target_w) // 2
                    top = (img.height - target_h) // 2
                    img = img.crop((left, top, left + target_w, top + target_h))

            for transparent in transparent_list:
                draw = ImageDraw.Draw(img)
                # 定义圆形参数
                x, y, r = transparent  # 圆心坐标半径

                # 绘制透明圆形（RGBA中A=0表示完全透明）
                draw.ellipse(
                    [(x - r, y - r), (x + r, y + r)],  # 边界框坐标
                    fill=(0, 0, 0, 0)  # 透明黑色
                )

            if extension > 0:
                img = self._extend_image_right(img, extension)
            if img.mode == 'RGBA':
                self.image.paste(img, (region[0], region[1], region[0] + target_w + extension, region[1] + target_h),
                                 img)
            else:
                self.image.paste(img, (region[0], region[1], region[0] + target_w + extension, region[1] + target_h))
        except Exception as e:
            print(f"贴图失败: {str(e)}")

    def _parse_text_segments(self, text):
        """预处理文本并解析为带标签的段列表"""
        text = text.replace('\n<hr>\n', '<hr>')
        text = text.replace('\n<hr>', '<hr>')
        text = text.replace('\n', '<lr>')

        # 将全角符号转换为半角符号
        text = text.replace('＜', '<').replace('＞', '>').replace('？', '?').replace('｛', '{').replace('｝', '}')

        text = re.sub(r'【(.*?)】', r"<fonts name='思源黑体'>\1</fonts>", text)
        text = re.sub(r'\{(.*?)}', r"<fonts name='方正舒体'>\1</fonts>", text)

        # 字形替换
        text = text.replace('<强制>', "<fonts name='思源黑体'>强制</fonts> -")
        text = text.replace('<显现>', "<fonts name='思源黑体'>显现</fonts> -")
        text = text.replace('<攻击>', "<fonts name='思源黑体'>攻击</fonts>")
        text = text.replace('<躲避>', "<fonts name='思源黑体'>躲避</fonts>")
        text = text.replace('<谈判>', "<fonts name='思源黑体'>躲避</fonts>")

        text = text.replace('<独特>', "<fonts name='arkham-icons'>w</fonts>")
        text = text.replace('<一>', "<fonts name='arkham-icons'>x</fonts>")
        text = text.replace('<反应>', "<fonts name='arkham-icons'>l</fonts>")
        text = text.replace('<启动>', "<fonts name='arkham-icons'>j</fonts>")
        text = text.replace('<箭头>', "<fonts name='arkham-icons'>j</fonts>")
        text = text.replace('<免费>', "<fonts name='arkham-icons'>k</fonts>")

        text = text.replace('<骷髅>', "<fonts name='arkham-icons'>m</fonts>")
        text = text.replace('<异教徒>', "<fonts name='arkham-icons'>n</fonts>")
        text = text.replace('<石板>', "<fonts name='arkham-icons'>o</fonts>")
        text = text.replace('<古神>', "<fonts name='arkham-icons'>p</fonts>")
        text = text.replace('<触手>', "<fonts name='arkham-icons'>r</fonts>")
        text = text.replace('<大失败>', "<fonts name='arkham-icons'>r</fonts>")
        text = text.replace('<大成功>', "<fonts name='arkham-icons'>q</fonts>")
        text = text.replace('<旧印>', "<fonts name='arkham-icons'>q</fonts>")

        text = text.replace('<拳>', "<fonts name='arkham-icons'>b</fonts>")
        text = text.replace('<书>', "<fonts name='arkham-icons'>a</fonts>")
        text = text.replace('<脚>', "<fonts name='arkham-icons'>c</fonts>")
        text = text.replace('<脑>', "<fonts name='arkham-icons'>.</fonts>")
        text = text.replace('<?>', "<fonts name='arkham-icons'>d</fonts>")

        text = text.replace('<点>', "<fonts name='arkham-icons'>y</fonts>")
        text = text.replace('<诅咒>', "<fonts name='arkham-icons'>t</fonts>")
        text = text.replace('<祝福>', "<fonts name='arkham-icons'>s</fonts>")
        text = text.replace('<雪花>', "<fonts name='arkham-icons'>u</fonts>")
        text = text.replace('<调查员>', "<fonts name='arkham-icons'>v</fonts>")

        text = text.replace('<流浪者>', "<fonts name='arkham-icons'>g</fonts>")
        text = text.replace('<生存者>', "<fonts name='arkham-icons'>i</fonts>")
        text = text.replace('<守护者>', "<fonts name='arkham-icons'>e</fonts>")
        text = text.replace('<潜修者>', "<fonts name='arkham-icons'>h</fonts>")
        text = text.replace('<探求者>', "<fonts name='arkham-icons'>f</fonts>")

        return parse_html(text)

    def _get_text_dimensions(self, text, font):
        """
        获取文本尺寸

        :param text: 要测量的文本
        :param font: 字体对象
        :return: (宽度, 高度)元组
        """
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def _calculate_font_size(self, segments, vertices, padding, default_font_name, default_size):
        """
        计算适合多边形区域的最大字体尺寸

        :param segments: 解析后的文本段列表
        :param vertices: 多边形顶点坐标列表
        :param padding: 内边距
        :param default_font_name: 默认字体名称
        :param default_size: 初始字体大小
        :return: (最佳字体大小, 字体缓存字典)
        """
        min_y = min(v[1] for v in vertices)
        max_y = max(v[1] for v in vertices)
        max_height = max(0, max_y - min_y) - padding * 2

        top = min_y + padding

        max_size = min(default_size, max_height)
        for size in range(max_size, 2, -1):
            line_height = int(size * 1.2)
            current_y = min_y + padding
            line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y, current_y + line_height, padding)
            current_x = line_start_x
            valid = True
            temp_cache = {'default': self._get_font(default_font_name, size)}
            for node in segments:
                font_name, content = node['attrs']['name'] if node['tag'] == 'fonts' else 'default', node['content']

                font = temp_cache.get(font_name) or self._get_font(font_name, size)
                temp_cache[font_name] = font
                if node['tag'] == 'hr' or node['tag'] == 'lr':
                    if node['tag'] == 'lr':
                        current_y += line_height + line_height // 4
                    else:
                        current_y += line_height + line_height // 4
                    line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y,
                                                                        current_y + line_height,
                                                                        padding)
                    current_x = line_start_x
                    continue
                if node['tag'] == 'br':
                    current_y += line_height
                    line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y, current_y + line_height,
                                                                        padding)
                    current_x = line_start_x
                    continue
                for char in list(content):
                    char_w, _ = self._get_text_dimensions(char, font)

                    if current_x + char_w > line_end_x and char not in symbol_list:
                        current_y += line_height
                        line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y,
                                                                            current_y + line_height, padding)
                        current_x = line_start_x
                        if current_y + line_height > top + max_height:
                            valid = False
                            break
                    current_x += char_w
                if not valid:
                    break

            if valid and current_y + line_height <= top + max_height:
                return size, temp_cache

        return 3, {'default': self._get_font(default_font_name, 1)}

    def calculate_padding_x(self, vertices, line_y1, line_y2, padding):
        """
        计算给定Y轴区间的左右边距（忽略水平边）

        :param vertices: 多边形顶点坐标列表
        :param line_y1: Y轴起始位置
        :param line_y2: Y轴结束位置
        :param padding: 内边距
        :return: (起始x坐标, 结束x坐标)
        """
        y_low = min(line_y1, line_y2)
        y_high = max(line_y1, line_y2)
        x_candidates = []
        effective_vertices = []

        # 检测线段在有效高度内的线段
        n = len(vertices)
        for i in range(n):
            _, _y1 = vertices[i]
            _, _y2 = vertices[(i + 1) % n]
            y1 = min(_y1, _y2)
            y2 = max(_y1, _y2)
            if y_low <= y1 <= y_high or y_low <= y2 <= y_high:
                # 任意一点在区间内
                effective_vertices.append((vertices[i], vertices[(i + 1) % n]))
            elif y1 <= y_low and y2 >= y_high:
                # 两端点在区间外
                effective_vertices.append((vertices[i], vertices[(i + 1) % n]))
            pass

        for item in effective_vertices:
            p1, p2 = item
            x1, y1 = p1
            x2, y2 = p2
            item_y_low = min(y1, y2)
            item_y_high = max(y1, y2)

            # 跳过水平线段
            if y1 == y2:
                continue

            # 计算交点
            # 从line_y1遍历到line_y2
            for y in range(int(line_y1), int(line_y2), 3):
                if item_y_low < y < item_y_high:
                    x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                    x_candidates.append(x)

        # 处理无交点情况
        if not x_candidates:
            min_x = min(v[0] for v in vertices)
            max_x = max(v[0] for v in vertices)
            return min_x, max_x
        # 计算有效区间
        # 将x_candidates从小到大排序
        x_candidates.sort()
        x_min = 0
        x_max = 0
        w_max = 0
        for i in range(len(x_candidates) - 1):
            w = x_candidates[i + 1] - x_candidates[i]
            if w > w_max:
                w_max = w
                x_min = x_candidates[i]
                x_max = x_candidates[i + 1]

        if x_min == 0 and x_max == 0:
            x_min = min(x_candidates)
            x_max = max(x_candidates)

        start_x = x_min + padding
        end_x = x_max - padding // 3

        # 处理无效padding情况
        if start_x > end_x:
            min_x = min(v[0] for v in vertices)
            max_x = max(v[0] for v in vertices)
            return min_x, max_x

        return round(start_x), round(end_x)

    def unified_text_processing(self, text):
        """统一文本处理"""
        text = text.replace('·', "<fonts name='SourceHanSansSC-Regular' offset='-25'>\uff65</fonts>")
        text = text.replace('】。', "】<fonts name='SourceHanSansSC-Bold' offset='-30'>\uff61</fonts>")
        return text

    def draw_centered_text(self, position, text, font_name, font_size, font_color,
                           has_border=False, border_width=1, border_color=(0, 0, 0)):
        """
        在指定位置居中绘制文字，可选外边框

        :param position: 中心坐标 (x, y)
        :param text: 要绘制的文本
        :param font_name: 字体名称
        :param font_size: 字体大小
        :param font_color: 文字颜色
        :param has_border: 是否添加外边框
        :param border_width: 边框粗细
        :param border_color: 边框颜色
        """
        text = self.unified_text_processing(text)
        font = self._get_font(font_name, font_size)
        _, text_height = self._get_text_dimensions(text, font)
        text_width = 0
        if self.font_manager.lang == 'en' and '胜利' in text:
            text = text.replace('胜利', 'Victory')
            text = text.replace('。', '.')

        segments = self._parse_text_segments(text)
        for node in segments:
            if node['tag'] == 'text' or node['tag'] == 'fonts':
                _font_name, content = node['attrs']['name'] if node['tag'] == 'fonts' else 'default', node['content']

                font = self._get_font(font_name, font_size) if _font_name == 'default' else self._get_font(_font_name,
                                                                                                           font_size)
                char_w, _ = self._get_text_dimensions(content, font)
                text_width += char_w

        x = position[0] - text_width / 2
        y = position[1] - text_height / 2

        current_x = x

        for node in segments:
            if node['tag'] == 'text' or node['tag'] == 'fonts':
                _font_name, content = node['attrs']['name'] if node['tag'] == 'fonts' else 'default', node['content']

                font = self._get_font(font_name, font_size) if _font_name == 'default' else self._get_font(_font_name,
                                                                                                           font_size)
                char_w, char_h = self._get_text_dimensions(content, font)
                offset = 0
                if 'attrs' in node and 'offset' in node['attrs']:
                    offset = int(int(node['attrs']['offset']) / 100 * font_size)
                offset += self.font_manager.get_font_offset(font_name)
                if has_border:
                    self.draw.text((current_x, y + offset), content, font=font, fill=font_color,
                                   stroke_width=border_width, stroke_fill=border_color)
                else:
                    self.draw.text((current_x, y + offset), content, font=font, fill=font_color)
                # 加入标记数据
                self.optimization_mark({
                    'points': [
                        (current_x, y + offset),
                        (current_x + char_w, y + offset),
                        (current_x + char_w, y + offset + char_h),
                        (current_x, y + offset + char_h)
                    ],
                    'text': self.get_font_text_emoji(font_name if _font_name == 'default' else _font_name, content)
                }, font_name if _font_name == 'default' else _font_name)
                current_x += char_w

    def draw_left_text(self, position, text, font_name, font_size, font_color,
                       has_border=False, border_width=1, border_color=(0, 0, 0)):
        """
        在指定位置左对齐绘制文字，可选外边框
        :param position: 左上角坐标 (x, y)
        :param text: 要绘制的文本
        :param font_name: 字体名称
        :param font_size: 字体大小
        :param font_color: 文字颜色
        :param has_border: 是否添加外边框
        :param border_width: 边框粗细
        :param border_color: 边框颜色
        """
        text = self.unified_text_processing(text)
        x = position[0]
        y = position[1]
        current_x = x

        segments = self._parse_text_segments(text)
        for node in segments:
            if node['tag'] == 'text' or node['tag'] == 'fonts':
                _font_name, content = node['attrs']['name'] if node['tag'] == 'fonts' else 'default', node['content']

                font = self._get_font(font_name, font_size) if _font_name == 'default' else self._get_font(_font_name,
                                                                                                           font_size)
                char_w, char_h = self._get_text_dimensions(content, font)
                offset = 0
                if 'attrs' in node and 'offset' in node['attrs']:
                    offset = int(int(node['attrs']['offset']) / 100 * font_size)
                offset += self.font_manager.get_font_offset(font_name)
                if has_border:
                    self.draw.text((current_x, y + offset), content, font=font, fill=font_color,
                                   stroke_width=border_width, stroke_fill=border_color)
                else:
                    self.draw.text((current_x, y + offset), content, font=font, fill=font_color)
                # 加入标记数据
                self.optimization_mark({
                    'points': [
                        (current_x, y + offset),
                        (current_x + char_w, y + offset),
                        (current_x + char_w, y + offset + char_h),
                        (current_x, y + offset + char_h)
                    ],
                    'text': self.get_font_text_emoji(font_name if _font_name == 'default' else _font_name, content)
                }, font_name if _font_name == 'default' else _font_name)
                current_x += char_w

    def optimization_mark(self, mark_object, font_name=None):
        # 微调部分字体
        if font_name:
            offset = 0
            if font_name == 'arkham-icons' and mark_object['text'] == '🏅':
                offset = 10
            if font_name == 'arkham-icons' and mark_object['text'] == '—':
                offset = 10
            if font_name == 'Teutonic' and mark_object['text'] == '—':
                offset = 15
            elif font_name == 'Bolton' or font_name == '汉仪小隶书简':
                offset = 3
            elif font_name == 'Teutonic':
                offset = 6
            if offset != 0:
                for i, point in enumerate(mark_object['points']):
                    mark_object['points'][i] = (point[0], point[1] + offset)
        # 将mark_object的坐标都转为整数
        mark_object['points'] = [(int(point[0]), int(point[1])) for point in mark_object['points']]
        self.text_mark.append(mark_object)

    @staticmethod
    def get_font_text_emoji(font_name, text):
        if font_name == 'arkham-icons':
            if text == 'w':
                return '🏅'
            elif text == 'x':
                return '—'
            elif text == 'l':
                return '⭕'
            elif text == 'j':
                return '➡️'
            elif text == 'k':
                return '⚡'
            elif text == 'm':
                return '💀'
            elif text == 'n':
                return '👤'
            elif text == 'o':
                return '📜'
            elif text == 'p':
                return '👹'
            elif text == 'r':
                return '🐙'
            elif text == 'q':
                return '⭐'
            elif text == 'b':
                return '👊'
            elif text == 'a':
                return '📚'
            elif text == 'c':
                return '🦶'
            elif text == '.':
                return '🧠'
            elif text == 'd':
                return '❓'
            elif text == 'y':
                return '🔵'
            elif text == 't':
                return '🌑'
            elif text == 's':
                return '🌟'
            elif text == 'u':
                return '❄️'
            elif text == 'v':
                return '🕵️'
            elif text == 'g':
                return '🚶'
            elif text == 'i':
                return '🏕️'
            elif text == 'e':
                return '🛡️'
            elif text == 'h':
                return '🧘'
            elif text == 'f':
                return '🔍'

        return text

    def draw_text(self, text, vertices, default_font_name='simfang',
                  default_size=12, color=(0, 0, 0), padding=10, draw_virtual_box=False):
        """
        在多边形区域内绘制格式化文本

        :param text: 包含HTML标签的文本
        :param vertices: 多边形顶点坐标列表
        :param default_font_name: 默认字体名称
        :param default_size: 初始字体大小
        :param color: 文字颜色
        :param padding: 内边距
        :param draw_virtual_box: 是否绘制调试框线
        """
        text = self.unified_text_processing(text)
        if draw_virtual_box:
            self.draw.polygon(vertices, outline="red", width=2)

        segments = self._parse_text_segments(text)
        size, fonts_cache = self._calculate_font_size(
            segments=segments,
            vertices=vertices,
            padding=padding,
            default_font_name=default_font_name,
            default_size=default_size
        )

        line_height = int(size * 1.2)
        current_y = min(v[1] for v in vertices) + padding
        line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y, current_y + line_height, padding)
        current_x = line_start_x
        # 记录标记数据
        last_line_start_x = line_start_x
        last_line_end_x = line_end_x
        last_current_y = current_y
        last_text = ''
        line_offset = int(line_height * 0.1)
        eof_is_br = False  # 结尾是否是换行符

        for node in segments:
            font_name, content = node['attrs']['name'] if node['tag'] == 'fonts' else 'default', node['content']
            if node['tag'] == 'hr' or node['tag'] == 'lr':
                last_current_y = current_y
                if node['tag'] == 'lr':
                    current_y += line_height + line_height // 4
                else:
                    current_y += line_height + line_height // 4
                # 加入标记数据
                self.optimization_mark({
                    'points': [
                        (last_line_start_x, last_current_y - line_offset),
                        (current_x, last_current_y - line_offset),
                        (current_x, last_current_y + size - line_offset),
                        (last_line_start_x, last_current_y + size - line_offset)
                    ],
                    'text': last_text
                })
                last_text = ''
                eof_is_br = True
                # 计算新一行开始和结束
                line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y, current_y + line_height,
                                                                    padding)
                last_line_start_x, last_line_end_x = line_start_x, line_end_x
                current_x = line_start_x

                continue
            if node['tag'] == 'text' or node['tag'] == 'fonts':
                eof_is_br = False
                font = fonts_cache.get(font_name, self.default_font)
                for char in list(content):
                    last_text += self.get_font_text_emoji(font_name, char)
                    last_current_y = current_y
                    char_w, char_h = self._get_text_dimensions(char, font)
                    if current_x + char_w > line_end_x and char not in symbol_list:
                        current_y += line_height
                        # 加入标记数据
                        self.optimization_mark({
                            'points': [
                                (last_line_start_x, last_current_y - line_offset),
                                (last_line_end_x, last_current_y - line_offset),
                                (last_line_end_x, last_current_y + size - line_offset),
                                (last_line_start_x, last_current_y + size - line_offset)
                            ],
                            'text': last_text
                        })
                        last_text = ''
                        line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y,
                                                                            current_y + line_height,
                                                                            padding)
                        last_line_start_x, last_line_end_x = line_start_x, line_end_x
                        current_x = line_start_x
                    offset = 0
                    if 'attrs' in node and 'offset' in node['attrs']:
                        offset = int(int(node['attrs']['offset']) / 100 * size)
                    if font_name == '方正舒体':
                        # 上升一点
                        self.draw.text((current_x, current_y - size // 12 + offset), char, font=font, fill=color)
                        pass
                    else:
                        self.draw.text((current_x, current_y + offset), char, font=font, fill=color)
                    current_x += char_w
            if node['tag'] == 'relish':
                eof_is_br = True
                center = True
                if 'center' in node['attrs'] and node['attrs']['center'] == 'false':
                    center = False
                pass
                relish_font = self._get_font(default_font_name, size - 2)

                line_str = ''
                for char in list(content):
                    char_w, char_h = self._get_text_dimensions(char, relish_font)
                    if current_x + char_w > line_end_x and char not in symbol_list:
                        self._draw_italic_text(
                            text=line_str,
                            left_x=line_start_x,
                            left_y=current_y,
                            font=relish_font,
                            fill=color
                        )
                        line_str = ''

                        current_y += line_height
                        line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y,
                                                                            current_y + line_height,
                                                                            padding)
                        current_x = line_start_x
                    line_str += char
                    current_x += char_w
                if line_str:
                    if center:
                        self._draw_italic_text(
                            text=line_str,
                            center_x=(line_start_x + line_end_x) // 2,
                            center_y=current_y + line_height // 2,
                            font=relish_font,
                            fill=color
                        )
                    else:
                        self._draw_italic_text(
                            text=line_str,
                            left_x=line_start_x,
                            left_y=current_y,
                            font=relish_font,
                            fill=color
                        )
        print(eof_is_br)
        if eof_is_br is False:
            # 加入标记数据
            self.optimization_mark({
                'points': [
                    (last_line_start_x, last_current_y - line_offset),
                    (current_x, last_current_y - line_offset),
                    (current_x, last_current_y + size - line_offset),
                    (last_line_start_x, last_current_y + size - line_offset)
                ],
                'text': last_text
            })
            pass

    def _draw_italic_text(self, text, font, fill, center_x=None, center_y=None, left_x=0, left_y=0, shear_factor=0.2):
        """
        绘制斜体文字

        :param text: 文字内容
        :param center_x: 中心X坐标
        :param center_y: 中心Y坐标
        :param left_x: 左边X坐标
        :param left_y:右边Y坐标
        :param font: 字体对象
        :param fill: 填充颜色
        :param shear_factor: 倾斜因子
        """
        draw = self.draw
        left, top, right, bottom = font.getbbox(text)
        text_width = right - left
        text_height = bottom - top

        temp_img = Image.new('RGBA', (text_width * 2, text_height * 2), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((-left + text_width // 2, -top + text_height // 2), text, font=font, fill=fill)

        sheared_img = temp_img.transform(
            (int(temp_img.width + text_height * shear_factor), temp_img.height),
            Image.AFFINE,
            (1, shear_factor, 0, 0, 1, 0),
            resample=Image.BICUBIC,
            fillcolor=(0, 0, 0, 0)
        )

        bbox = sheared_img.getbbox()
        if bbox:
            sheared_img = sheared_img.crop(bbox)

        paste_x = left_x
        paste_y = left_y
        if center_x != None and center_y != None:
            paste_x = center_x - sheared_img.width // 2
            paste_y = center_y - sheared_img.height // 2
        print(paste_x, paste_y)
        img_w, img_h = sheared_img.size
        # 加入标记数据
        self.optimization_mark({
            'points': [
                (paste_x, paste_y),
                (paste_x + img_w, paste_y),
                (paste_x + img_w, paste_y + img_h),
                (paste_x, paste_y + img_h)
            ],
            'text': text
        })
        draw._image.alpha_composite(sheared_img, (int(paste_x), int(paste_y)))

    def _get_font(self, font_name, size):
        """
        获取字体对象

        :param font_name: 字体名称
        :param size: 字体大小
        :return: 字体对象
        """
        try:
            if font_name == 'default':
                return ImageFont.load_default(size)

            font_path = self.font_manager.get_font_path(font_name)
            if font_path:
                return ImageFont.truetype(font_path, size)
            return ImageFont.truetype(font_name, size)
        except:
            return ImageFont.load_default(size)

    def add_submit_icon(self, name):
        """
        添加投入图标

        :param name: 名称
        """
        if name not in ['意志', '战力', '敏捷', '智力', '狂野']:
            return
        img = self.image_manager.get_image(f'投入-{self.card_class}-{name}')
        self.paste_image(img, (0, 167 + self.submit_index * 85), 'contain')
        self.submit_index += 1

    def set_card_level(self, level=None):
        """
        设置卡牌等级

        :param level: 等级
        """
        position_level = (25, 77)
        position_none = (15, 55)
        if self.card_type == '事件卡':
            position_level = (25, 73)
            position_none = (12, 12)
        if self.card_type == '支援卡':
            position_level = (25, 77)
            position_none = (12, 12)
        img = self.image_manager.get_image(f'{self.card_type}-无等级')
        if level is not None and 0 < level < 6:
            img = self.image_manager.get_image(f'{self.card_type}-等级{level}')
            self.paste_image(img, position_level, 'contain')
        elif level != 0:
            self.paste_image(img, position_none, 'contain')

    def set_card_cost(self, cost=-1):
        """
        设置卡牌费用

        :param cost: 费用
        """
        default_position = [(70, 50), (70, 40)]
        if self.card_class == '弱点':
            default_position = [(74, 50), (74, 40)]
        if 0 <= cost < 100:
            self.draw_centered_text(
                position=default_position[0],
                text=str(cost),
                font_name='Teutonic',
                font_size=62,
                font_color=(255, 255, 255),
                has_border=True,
                border_width=2,
                border_color=(0, 0, 0)
            )
        elif cost == -2:
            """X费用"""
            self.draw_centered_text(
                position=default_position[0],
                text='X',
                font_name='Teutonic',
                font_size=62,
                font_color=(255, 255, 255),
                has_border=True,
                border_width=2,
                border_color=(0, 0, 0)
            )
        else:
            # 无费用
            self.draw_centered_text(
                position=default_position[1],
                text='—',
                font_name='Teutonic',
                font_size=68,
                font_color=(255, 255, 255),
                has_border=True,
                border_width=2,
                border_color=(0, 0, 0)
            )
        pass

    def add_slots(self, slots):
        """
        添加槽位

        :param slots: 槽位列表
        """
        if slots not in ['双手', '双法术', '塔罗', '手部', '法术', '盟友', '身体', '饰品']:
            return
        img = self.image_manager.get_image(f'槽位-{slots}')
        self.paste_image(img, (603 - self.slots_index * 105, 900), 'contain')
        self.slots_index += 1

    def set_health_and_horror(self, health, horror):
        """
        设置生命值和恐怖值
        :param health:  生命值
        :param horror:  恐怖值
        :return:
        """
        if self.card_type == '调查员卡':
            self.draw_centered_text(
                position=(760, 635),
                text=str(health),
                font_name='Bolton',
                font_size=58,
                font_color=(255, 255, 255),
                has_border=True,
                border_width=3,
                border_color=(182, 31, 35)
            )
            self.draw_centered_text(
                position=(870, 635),
                text=str(horror),
                font_name='Bolton',
                font_size=58,
                font_color=(255, 255, 255),
                has_border=True,
                border_width=3,
                border_color=(1, 63, 114)
            )
            return
        elif self.card_type == '敌人卡':
            curve = [15, 6, 0, 4, 12]
            if 0 < health < 6:
                for i in range(health):
                    img = self.image_manager.get_image('UI-伤害')
                    self.paste_image(img, (260 - i * 45, 583 - i * 23 - curve[i]), 'contain')
                    # 加入标记数据
                    self.optimization_mark({
                        'points': [
                            (260 - i * 45, 583 - i * 23 - curve[i]),
                            (260 - i * 45 + 40, 583 - i * 23 - curve[i]),
                            (260 - i * 45 + 40, 583 - i * 23 + 40 - curve[i]),
                            (260 - i * 45, 583 - i * 23 + 40 - curve[i])
                        ],
                        'text': '🫀'
                    })
                pass
            if 0 < horror < 6:
                for i in range(horror):
                    img = self.image_manager.get_image('UI-恐惧')
                    self.paste_image(img, (440 + i * 45, 583 - i * 23 - curve[i] + 4), 'contain')
                    # 加入标记数据
                    self.optimization_mark({
                        'points': [
                            (440 + i * 45, 583 - i * 23 - curve[i] + 4),
                            (440 + i * 45 + 40, 583 - i * 23 - curve[i] + 4),
                            (440 + i * 45 + 40, 583 - i * 23 + 40 - curve[i] + 4),
                            (440 + i * 45, 583 - i * 23 + 40 - curve[i] + 4)
                        ],
                        'text': '💙'
                    })
                pass
            return
        # 画底图
        img = self.image_manager.get_image('UI-生命恐惧')
        self.paste_image(img, (293, 925), 'contain')
        # 画生命值
        if 0 < health < 100:
            self.draw_centered_text(
                position=(323, 963),
                text=str(health),
                font_name='Bolton',
                font_size=58,
                font_color=(255, 255, 255),
                has_border=True,
                border_width=3,
                border_color=(182, 31, 35)
            )
        else:
            self.draw_centered_text(
                position=(323, 952),
                text='x',
                font_name='arkham-icons',
                font_size=58,
                font_color=(255, 255, 255),
                has_border=True,
                border_width=3,
                border_color=(182, 31, 35)
            )
        # 画恐惧值
        if 0 < horror < 100:
            self.draw_centered_text(
                position=(430, 963),
                text=str(horror),
                font_name='Bolton',
                font_size=58,
                font_color=(255, 255, 255),
                has_border=True,
                border_width=3,
                border_color=(1, 63, 114)
            )
        else:
            self.draw_centered_text(
                position=(433, 952),
                text='x',
                font_name='arkham-icons',
                font_size=58,
                font_color=(255, 255, 255),
                has_border=True,
                border_width=3,
                border_color=(1, 63, 114)
            )
        pass

    def set_number_value(self, position, text, font_size=1, color=(255, 255, 255), stroke_color=(0, 0, 0)):
        """画数值"""
        font = self._get_font('Bolton', font_size)
        # 取出text中的数字
        number = ''
        r = re.findall(r'\d+', text)
        if r:
            number = r[0]
        if 'X' in text or 'x' in text:
            number = 'X'
        if '?' in text or '？' in text:
            number = '?'
        if '-' in text or '一' in text:
            number = 'x'
            font = self._get_font('arkham-icons', font_size)
        # 计算数字
        number_width, text_height = self._get_text_dimensions(number, font)
        investigator_width = 0
        investigator_font = None
        # 画调查员标
        if '<调查员>' in text:
            try:
                if int(number) > 0:
                    investigator_font = self._get_font('arkham-icons', 24)
                    investigator_width, _ = self._get_text_dimensions('v', investigator_font)
            except:
                pass
        # 画中间
        x = position[0] - number_width // 2 - investigator_width // 2
        y = position[1] - text_height // 2
        if number == 'x':
            y -= 4
        self.draw.text((x, y), number, font=font, fill=color, stroke_width=1, stroke_fill=stroke_color)
        # 加入标记数据
        self.optimization_mark({
            'points': [
                (x, y),
                (x + number_width, y),
                (x + number_width, y + text_height),
                (x, y + text_height)
            ],
            'text': number
        }, 'Bolton')
        # 画调查员
        if investigator_font is not None:
            x = position[0] + number_width // 2 - investigator_width // 2 + 4
            self.draw.text((x, y + 3), 'v', font=investigator_font, fill=color, stroke_width=1,
                           stroke_fill=stroke_color)
            # 加入标记数据
            self.optimization_mark({
                'points': [
                    (x, y + 3),
                    (x + investigator_width, y + 3),
                    (x + investigator_width, y + 3 + investigator_width),
                    (x, y + 3 + investigator_width)
                ],
                'text': self.get_font_text_emoji('arkham-icons', 'v')
            }, 'arkham-icons')

    def set_basic_weakness_icon(self):
        """添加基础弱点图标"""
        im = None
        ps = (0, 0)
        if self.card_type in ['技能卡', '支援卡', '事件卡']:
            im = self.image_manager.get_image('遭遇组-基础弱点-1')
            if self.card_type == '技能卡':
                ps = (631, 15)
            elif self.card_type == '事件卡':
                ps = (324, 495)
            else:
                ps = (637, 3)
            pass
        elif self.card_type == '诡计卡':
            im = self.image_manager.get_image('遭遇组-基础弱点-2')
            ps = (311, 490)
            pass
        if im is not None:
            self.paste_image(im, ps, 'contain')
        pass

    def set_subclass_icon(self, subclass):
        """设置多职阶时子职业图标"""
        # 检查subclass是个数组并且长度不为0
        if not isinstance(subclass, list) or len(subclass) == 0:
            return
        start_ps = (0, 0)
        if self.card_type == '支援卡':
            start_ps = (634, 4)
        elif self.card_type == '事件卡':
            if len(subclass) == 3:
                start_ps = (418, 498)
            else:
                start_ps = (368, 498)
        # 从右到左依次添加图标，倒序遍历数组
        for i in range(len(subclass)):
            item = subclass[len(subclass) - i - 1]
            im = self.image_manager.get_image(f'多职阶-{item}')
            self.paste_image(im, (start_ps[0] - i * 89, start_ps[1]), 'contain')

    def set_bottom_information_by_picture(self, picture_path):
        """根据图片设置底部信息"""
        dp = Image.open(picture_path)
        # 获取图片高度和宽度
        width, height = dp.size
        # 裁剪图片底标
        dp = dp.crop((0, height - 30, width, height))
        # 获取card的高度和宽度
        card_width, card_height = self.image.size
        # 粘贴到指定位置
        self.paste_image(dp, (0, card_height - 30, card_width, 30), 'stretch')

    def set_bottom_information_by_text(self, illustrator='', middle_text='', position=-1, pack_icon=None,
                                       encounter_count=-1, encounter_position=1):
        """写底部信息"""
        card_width, card_height = self.image.size
        # 艺术家
        if illustrator != '':
            self.draw_left_text(
                position=(33, card_height - 30),
                text=f'Illus. {illustrator}',
                font_name='ArnoPro-Bold',
                font_size=20,
                font_color=(255, 255, 255)
            )
        # 写版权
        if middle_text != '':
            self.draw_centered_text(
                position=(card_width // 2, card_height - 25),
                text=middle_text,
                font_name='ArnoPro-Bold',
                font_size=20,
                font_color=(255, 255, 255)
            )
        # 写序号
        if position > 0:
            self.draw_centered_text(
                position=(card_width - 60, card_height - 25),
                text=f'{position}',
                font_name='ArnoPro-Bold',
                font_size=20,
                font_color=(255, 255, 255)
            )
        # 画底标
        if pack_icon is not None:
            im = self.image_manager.get_image(f'底标图标-{pack_icon}')
            self.paste_image(im, (card_width - 103, card_height - 34, 23, 23), 'stretch')
        # 写遭遇组序号
        if encounter_count > 0 \
                and (self.card_type == '诡计卡'):
            self.draw_centered_text(
                position=(card_width - 140, card_height - 25),
                text=f"{encounter_position}/{encounter_count}",
                font_name='ArnoPro-Bold',
                font_size=20,
                font_color=(255, 255, 255)
            )
            pass
        pass

    def set_ellipse_empty(self, position, r):
        """
        画圆形空洞
        """
        x, y = position

        # 绘制透明圆形（RGBA中A=0表示完全透明）
        self.draw.ellipse(
            [(x - r, y - r), (x + r, y + r)],  # 边界框坐标
            fill=(0, 0, 0, 0)  # 透明黑色
        )

    def set_location_icon(self, index, icon):
        """
        设置地点图标
        :param index 0为地点 1-6为连接符号
        """
        link_position = [
            (129, 932),
            (211, 917),
            (293, 910),
            (375, 910),
            (457, 917),
            (539, 932)
        ]
        im = self.image_manager.get_image(f'地点标识-{icon}')
        if index == 0:
            self.paste_image(self.image_manager.get_image(f'地点标识-标识底'), (15, 8), 'contain')
            self.paste_image(im, (20, 13), 'contain')
        elif 0 < index < 7:
            self.paste_image(im, link_position[index - 1], 'contain')
