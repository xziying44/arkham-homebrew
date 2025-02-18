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
            is_self_closing = tag_part.endswith('/>') or tag_name in {'hr', 'br', 'img'}
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

    def __init__(self, font_folder='fonts'):
        """
        初始化字体管理器

        :param font_folder: 字体文件存放目录，默认为'fonts'
        """
        self.font_map = {}
        self.font_folder = font_folder
        self._load_fonts()

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
        return self.font_map.get(font_name.lower())


symbol_list = ['，', '。', '：', ':', '“', '”']


class Card:
    def __init__(self, width, height, font_manager=None, image_manager=None, card_type='default', card_class='default'):
        """
        初始化卡牌对象

        :param width: 卡牌宽度（像素）
        :param height: 卡牌高度（像素）
        :param font_manager: 字体管理器实例，如果未提供则新建默认实例
        :param image_manager: 图像管理器实例，如果未提供则新建默认实例
        :param card_type: 卡牌类型 技能卡、支援卡、事件卡
        """
        self.width = width
        self.height = height
        self.image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.font_manager = font_manager if font_manager else FontManager()
        self.image_manager = image_manager if image_manager else ImageManager()
        self.default_font = ImageFont.load_default()
        self.submit_index = 0  # 投入图标索引
        self.card_type = card_type
        self.card_class = card_class

    def paste_image(self, img, region, resize_mode='stretch'):
        """
        在指定区域粘贴图片

        :param img: 图片
        :param region: 目标区域坐标和尺寸 (x, y, width, height)
        :param resize_mode: 调整模式，可选'stretch'(拉伸)/'contain'(适应)/'cover'(覆盖)
        """
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

            if img.mode == 'RGBA':
                self.image.paste(img, (region[0], region[1], region[0] + target_w, region[1] + target_h), img)
            else:
                self.image.paste(img, (region[0], region[1], region[0] + target_w, region[1] + target_h))
        except Exception as e:
            print(f"贴图失败: {str(e)}")

    def _parse_text_segments(self, text):
        """预处理文本并解析为带标签的段列表"""
        text = text.replace('\n<hr>\n', '<hr>')
        text = text.replace('\n<hr>', '<hr>')
        text = text.replace('\n', '<br>')

        text = re.sub(r'【(.*?)】', r"<fonts name='思源黑体'>\1</fonts>", text)
        text = re.sub(r'\{(.*?)}', r"<fonts name='方正舒体'>\1</fonts>", text)

        # 字形替换
        text = text.replace('<强制>', "<fonts name='思源黑体'>强制</fonts> -")
        text = text.replace('<显现>', "<fonts name='思源黑体'>显现</fonts> -")
        text = text.replace('<独特>', "<fonts name='arkham-icons'>w</fonts>")
        text = text.replace('<一>', "<fonts name='arkham-icons'>x</fonts>")
        text = text.replace('<反应>', "<fonts name='arkham-icons'>l</fonts>")
        text = text.replace('<启动>', "<fonts name='arkham-icons'>j</fonts>")
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
                if node['tag'] == 'hr':
                    current_y += line_height + line_height / 3
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
        end_x = x_max - padding

        # 处理无效padding情况
        if start_x > end_x:
            min_x = min(v[0] for v in vertices)
            max_x = max(v[0] for v in vertices)
            return min_x, max_x

        return round(start_x), round(end_x)

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
        font = self._get_font(font_name, font_size)
        _, text_height = self._get_text_dimensions(text, font)
        text_width = 0
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
                char_w, _ = self._get_text_dimensions(content, font)
                if has_border:
                    self.draw.text((current_x, y), content, font=font, fill=font_color,
                                   stroke_width=border_width, stroke_fill=border_color)
                else:
                    self.draw.text((current_x, y), content, font=font, fill=font_color)
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
        x = position[0]
        y = position[1]
        current_x = x

        segments = self._parse_text_segments(text)
        for node in segments:
            if node['tag'] == 'text' or node['tag'] == 'fonts':
                _font_name, content = node['attrs']['name'] if node['tag'] == 'fonts' else 'default', node['content']

                font = self._get_font(font_name, font_size) if _font_name == 'default' else self._get_font(_font_name,
                                                                                                           font_size)
                char_w, _ = self._get_text_dimensions(content, font)
                if has_border:
                    self.draw.text((current_x, y), content, font=font, fill=font_color,
                                   stroke_width=border_width, stroke_fill=border_color)
                else:
                    self.draw.text((current_x, y), content, font=font, fill=font_color)
                current_x += char_w

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
        print(f"最佳字体大小: {size}")

        line_height = int(size * 1.2)
        current_y = min(v[1] for v in vertices) + padding
        line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y, current_y + line_height, padding)
        current_x = line_start_x
        print(f"calculate_padding_x: ({line_start_x}, {line_end_x})")

        for node in segments:
            font_name, content = node['attrs']['name'] if node['tag'] == 'fonts' else 'default', node['content']
            if node['tag'] == 'br':
                current_y += line_height
                line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y, current_y + line_height,
                                                                    padding)
                current_x = line_start_x
                continue
            if node['tag'] == 'hr':
                current_y += line_height + line_height / 3
                line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y, current_y + line_height,
                                                                    padding)
                current_x = line_start_x
                continue
            if node['tag'] == 'text' or node['tag'] == 'fonts':
                font = fonts_cache.get(font_name, self.default_font)
                for char in list(content):
                    char_w, char_h = self._get_text_dimensions(char, font)
                    if current_x + char_w > line_end_x and char not in symbol_list:
                        current_y += line_height
                        line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y,
                                                                            current_y + line_height,
                                                                            padding)
                        current_x = line_start_x
                    if font_name == '方正舒体':
                        # 上升一点
                        self.draw.text((current_x, current_y - size // 12), char, font=font, fill=color)
                        pass
                    else:
                        self.draw.text((current_x, current_y), char, font=font, fill=color)
                        pass
                    current_x += char_w
            if node['tag'] == 'relish':
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
        default_position = [(70, 50), (70, 48)]
        if self.card_class == '弱点':
            default_position = [(74, 50), (74, 48)]
        if 0 <= cost < 100:
            self.draw_centered_text(
                position=default_position[0],
                text=str(cost),
                font_name='Teutonic',
                font_size=58,
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
                font_size=58,
                font_color=(255, 255, 255),
                has_border=True,
                border_width=2,
                border_color=(0, 0, 0)
            )
        else:
            # 无费用
            self.draw_centered_text(
                position=default_position[1],
                text='x',
                font_name='arkham-icons',
                font_size=58,
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
        self.paste_image(img, (603, 900), 'contain')

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
                pass
            if 0 < horror < 6:
                for i in range(horror):
                    img = self.image_manager.get_image('UI-恐惧')
                    self.paste_image(img, (440 + i * 45, 583 - i * 23 - curve[i] + 4), 'contain')
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

    def set_enemy_value(self, position, text, font_size=1):
        """画敌人数值"""
        font = self._get_font('Bolton', font_size)
        # 取出text中的数字
        number = ''
        r = re.findall(r'\d+', text)
        if r:
            number = r[0]
        if 'X' in text or 'x' in text:
            number = 'X'
        if '-' in text or '一' in text:
            number = 'x'
            font = self._get_font('arkham-icons', font_size)
        # 计算数字
        number_width, text_height = self._get_text_dimensions(number, font)
        investigator_width = 0
        investigator_font = None
        # 画调查员标
        if '<调查员>' in text:
            investigator_font = self._get_font('arkham-icons', 24)
            investigator_width, _ = self._get_text_dimensions('v', investigator_font)
        # 画中间
        x = position[0] - number_width // 2 - investigator_width // 2
        y = position[1] - text_height // 2
        if number == 'x':
            y -= 4
        self.draw.text((x, y), number, font=font, fill=(255, 255, 255), stroke_width=1, stroke_fill=(0, 0, 0))
        # 画调查员
        if investigator_font is not None:
            x = position[0] + number_width // 2 - investigator_width // 2 + 4
            self.draw.text((x, y + 3), 'v', font=investigator_font, fill=(255, 255, 255), stroke_width=1,
                           stroke_fill=(0, 0, 0))

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
            start_ps = (368, 498)
        # 从右到左依次添加图标，倒序遍历数组
        for i in range(len(subclass)):
            item = subclass[len(subclass) - i - 1]
            im = self.image_manager.get_image(f'多职阶-{item}')
            self.paste_image(im, (start_ps[0] - i * 89, start_ps[1]), 'contain')

    class TestCard:
        @staticmethod
        def test():
            fm = FontManager('fonts')
            im = ImageManager('images')
            card = Card(
                width=739,
                height=1049,
                font_manager=fm,
                image_manager=im,
                card_type='技能卡'
            )

            # 贴底图
            dp = Image.open(r'C:\Users\xziyi\Desktop\java.png')
            card.paste_image(dp, (0, 88, 739, 600), 'cover')

            # 贴牌框
            card.paste_image(im.get_image('技能卡-流浪者'), (0, 0), 'contain')

            test_text = (
                "<fonts name='思源黑体'>强制</fonts> - 检定<fonts name='arkham-icons'>.</fonts>(3)。你检定失败且每低于难度1点，受到1点恐惧。\n"
                "<hr>\n"
                "默认<fonts name='arkham-icons'>a</fonts>字体混合排版字体混合排版测试默认字体混合排版测试默认字体混合排版测试默认字体混合排版测试默认测试默认字体混合排版测试默认\n"
                "<hr>\n"
                "<relish>这是一段风味内容这是一段风味内容</relish>\n"
                "<relish>这是一段风味内容这是一段风味内容字体混合排版</relish>"
            )
            card.draw_text(
                test_text,
                vertices=[
                    (75, 735), (682, 735), (692, 770), (704, 838), (701, 914), (679, 986),
                    (74, 986), (91, 920), (96, 844)
                ],
                default_font_name='simfang',
                default_size=32,
                padding=8,
                draw_virtual_box=False
            )

            card.draw_centered_text(
                position=(368, 713),
                text="法术，勇气",
                font_name="方正舒体",
                font_size=28,
                font_color=(0, 0, 0)
            )

            card.draw_left_text(
                position=(140, 34),
                text="测试卡名",
                font_name="汉仪小隶书简",
                font_size=48,
                font_color=(0, 0, 0)
            )

            card.draw_centered_text(
                position=(73, 132),
                text="技能",
                font_name="汉仪小隶书简",
                font_size=24,
                font_color=(0, 0, 0)
            )

            card.add_submit_icon('意志')
            card.add_submit_icon('意志')
            card.add_submit_icon('狂野')

            card.set_card_level(-1)

            card.image.save('output_card.png', quality=95)
            print("卡牌生成完成")

        @staticmethod
        def test2():
            """事件卡"""
            fm = FontManager('fonts')
            im = ImageManager('images')
            card = Card(
                width=739,
                height=1046,
                font_manager=fm,
                image_manager=im,
                card_type='事件卡',
                card_class="潜修者"
            )

            # 贴底图
            dp = Image.open(r'C:\Users\xziyi\Desktop\java.png')
            card.paste_image(dp, (0, 0, 739, 589), 'cover')

            # 贴牌框
            card.paste_image(im.get_image('事件卡-潜修者'), (0, 0), 'contain')

            # 写小字
            card.draw_centered_text(
                position=(73, 130),
                text="事件",
                font_name="汉仪小隶书简",
                font_size=24,
                font_color=(0, 0, 0)
            )

            # 写属性
            card.draw_centered_text(
                position=(368, 682),
                text="法术，勇气",
                font_name="方正舒体",
                font_size=32,
                font_color=(0, 0, 0)
            )

            test_text = """{公务员，表演者，社会名流}牌库专用。
<hr>
【谈判】。选择你所在地点的一名调查员。该调查员可以从手牌免费打出一张{盟友}支援。然后，该调查员可以触发该支援上的一个<启动>或<免费>能力，忽略其所有费用。
风味文字：“没错，他们肯定信了。”"""
            card.draw_text(
                test_text,
                vertices=[
                    (43, 700), (694, 700), (706, 757), (704, 817), (680, 887), (670, 952),
                    (598, 980), (135, 980), (77, 949), (61, 907), (31, 793)
                ],
                default_font_name='simfang',
                default_size=32,
                padding=15,
                draw_virtual_box=True
            )

            card.draw_centered_text(
                position=(370, 618),
                text="<独特>测试卡名",
                font_name="汉仪小隶书简",
                font_size=48,
                font_color=(0, 0, 0)
            )

            card.add_submit_icon('意志')
            card.add_submit_icon('意志')
            card.add_submit_icon('狂野')

            card.set_card_level(0)

            card.set_card_cost(-1)

            card.image.save('output_card.png', quality=95)
            print("卡牌生成完成")

        @staticmethod
        def test3():
            """支援卡"""
            fm = FontManager('fonts')
            im = ImageManager('images')
            card = Card(
                width=739,
                height=1049,
                font_manager=fm,
                image_manager=im,
                card_type='支援卡',
                card_class="守护者"
            )

            # 贴底图
            dp = Image.open(r'C:\Users\xziyi\Desktop\java.png')
            card.paste_image(dp, (0, 80, 739, 540), 'cover')

            # 贴牌框
            card.paste_image(im.get_image('支援卡-守护者-副标题'), (0, 0), 'contain')

            # 写小字
            card.draw_centered_text(
                position=(73, 130),
                text="支援",
                font_name="汉仪小隶书简",
                font_size=24,
                font_color=(0, 0, 0)
            )

            # 写属性
            card.draw_centered_text(
                position=(375, 649),
                text="法术，勇气",
                font_name="方正舒体",
                font_size=32,
                font_color=(0, 0, 0)
            )

            test_text = """{公务员，表演者，社会名流}牌库专用。
<hr>
<启动>：【谈判】。选择你所在地点的一名调查员。该调查员可以从手牌免费打出一张{盟友}支援。然后，该调查员可以触发该支援上的一个<启动>或<免费>能力，忽略其所有费用。
<relish>“没错，他们肯定信了。”</relish>"""
            card.draw_text(
                test_text,
                vertices=[
                    (19, 662), (718, 662), (718, 910), (19, 910)
                ],
                default_font_name='simfang',
                default_size=32,
                padding=15,
                draw_virtual_box=True
            )

            # 写标题
            card.draw_centered_text(
                position=(375, 48),
                text="<独特>测试卡名",
                font_name="汉仪小隶书简",
                font_size=48,
                font_color=(0, 0, 0)
            )

            # 写副标题
            card.draw_centered_text(
                position=(375, 101),
                text="测试副标题",
                font_name="汉仪小隶书简",
                font_size=32,
                font_color=(0, 0, 0)
            )

            card.add_submit_icon('意志')
            card.add_submit_icon('意志')
            card.add_submit_icon('狂野')

            card.set_card_level(3)

            card.set_card_cost(-2)

            card.add_slots('双手')

            card.set_health_and_horror(2, 2)

            card.image.save('output_card.png', quality=95)
            print("卡牌生成完成")

        @staticmethod
        def test4():
            """调查员正面"""
            fm = FontManager('fonts')
            im = ImageManager('images')
            card = Card(
                width=1049,
                height=739,
                font_manager=fm,
                image_manager=im,
                card_type='调查员卡'
            )
            # 贴牌框-底
            card.paste_image(im.get_image('调查员-守护者-底图'), (0, 0), 'contain')

            # 贴底图
            dp = Image.open(r'C:\Users\xziyi\Desktop\java2.png')
            card.paste_image(dp, (0, 75, 579, 647), 'cover')

            # 贴牌框-UI
            card.paste_image(im.get_image('调查员-守护者-UI'), (0, 0), 'contain')

            # 写标题
            card.draw_centered_text(
                position=(320, 38),
                text="<独特>测试卡名",
                font_name="汉仪小隶书简",
                font_size=48,
                font_color=(0, 0, 0)
            )

            # 写副标题
            card.draw_centered_text(
                position=(320, 90),
                text="测试副标题",
                font_name="汉仪小隶书简",
                font_size=32,
                font_color=(0, 0, 0)
            )

            # 写四维
            attribute = (1, 2, 3, 4)
            for i, attr in enumerate(attribute):
                card.draw_centered_text(
                    position=(600 + 120 * i, 57),
                    text=str(attr),
                    font_name="Bolton",
                    font_size=48,
                    font_color=(0, 0, 0)
                )

            # 写属性
            card.draw_centered_text(
                position=(810, 168),
                text="法术，勇气",
                font_name="方正舒体",
                font_size=32,
                font_color=(0, 0, 0)
            )

            test_text = """你以通量稳定器(失活)面朝上开始游戏。
<hr>
<免费>：从凯特·温斯洛普上移动1个线索到一张你控制的上面没有线索的科学或工具支援。
<hr>
【强制】 - 当你控制的上面有线索的支援离场时：将其线索放在你所在地点上。
<hr>
<旧印>效果：+0。你可以从你控制的一张支援上移动1个线索返回到凯特·温斯洛普。"""
            card.draw_text(
                test_text,
                vertices=[
                    (586, 178), (1026, 178), (1024, 600), (586, 600)
                ],
                default_font_name='simfang',
                default_size=32,
                padding=15,
                draw_virtual_box=False
            )

            card.set_health_and_horror(6, 8)

            card.image.save('output_card.png', quality=95)
            print("卡牌生成完成")

        @staticmethod
        def test5():
            """调查员卡背"""
            fm = FontManager('fonts')
            im = ImageManager('images')
            card = Card(
                width=1049,
                height=739,
                font_manager=fm,
                image_manager=im,
                card_type='调查员卡'
            )
            # 贴底图
            dp = Image.open(r'C:\Users\xziyi\Desktop\java2.png')
            card.paste_image(dp, (0, 0, 373, 405), 'cover')

            # 贴牌框-UI
            card.paste_image(im.get_image('调查员卡-潜修者-卡背'), (0, 0), 'contain')

            # 写标题
            card.draw_centered_text(
                position=(750, 36),
                text="<独特>测试冴卡名",
                font_name="汉仪小隶书简",
                font_size=48,
                font_color=(0, 0, 0)
            )

            # 写副标题
            card.draw_centered_text(
                position=(750, 88),
                text="测试副标题",
                font_name="汉仪小隶书简",
                font_size=32,
                font_color=(0, 0, 0)
            )

            test_text = """【牌库卡牌张数】: 30。
【牌库构筑选项】: 探求者卡牌(f)等级0-5，科学卡牌等级0-4，洞察卡牌等级0-1，中立卡牌等级0-5。
【牌库构筑需求】(不计入卡牌张数)：通量稳定器、失败的实验、1张随机基础弱点。
<hr>
<relish center='false'>凯特·温斯洛普多年来一直卡托尼克大学科学楼的地下室卡托尼克大学科学楼的地下室卡托尼克大学科学楼的地下室在米斯卡托尼克大学科学楼的地下室里进行研究，为了追求进步，她放弃了资金和学术声望。她一心一意的专注终于得到了回报，她发明了通量稳定器：一种能够引导新形式能量的强大装置。然而，进步的代价是高昂的。这项突破性发明的第一次成功测试夺去了她的朋友兼导师杨教授的生命。从那以后，凯特不知疲倦地研究这些外星电流，希望能找到一种方法来扭转它们的影响。</relish>"""
            card.draw_text(
                test_text,
                vertices=[
                    (385, 141), (1011, 141), (1011, 686), (36, 686),
                    (36, 500), (308, 500), (308, 450), (358, 450)
                ],
                default_font_name='simfang',
                default_size=32,
                padding=15,
                draw_virtual_box=False
            )

            card.image.save('output_card.png', quality=95)
            print("卡牌生成完成")

    if __name__ == '__main__':
        TestCard.test5()
