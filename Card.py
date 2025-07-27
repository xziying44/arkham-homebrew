import json
import os
import random
import re

from PIL import Image, ImageDraw, ImageFont


def generate_random_braille(size, seed=None, dot_color=(0, 0, 0, 255)):
    """
    生成随机盲文图片 - 真正贴边版本

    参数:
    size: 图片大小 (生成正方形图片)
    seed: 随机种子，相同种子生成相同图片
    dot_color: 点的颜色，RGBA格式元组，默认黑色 (0, 0, 0, 255)

    返回:
    PIL Image对象，透明背景
    """
    if seed is not None:
        random.seed(seed)

    # 将图片均匀分成7行，计算每一行的高度
    row_height = size // 7

    # 创建一个透明背景的图片
    img = Image.new('RGBA', (row_height * 5, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 计算点的大小
    dot_size = int(row_height * 0.6)
    small_dot_size = int(dot_size * 0.5)  # 中间分隔行点的大小

    # 绘制上三行的盲文点
    for row in range(3):
        for col in range(5):
            # 随机决定是否绘制点（50%的概率）
            if random.random() > 0.6:
                x = col * row_height
                y = row * row_height
                # 绘制一个实心圆点
                draw.ellipse((x, y, x + dot_size, y + dot_size), fill=dot_color)

    # 绘制中间一行分割点，大小要小一半，位置要居中
    mid_row = 3

    for col in range(5):
        # 计算x轴中心对齐的位置
        normal_dot_center_x = col * row_height + dot_size // 2  # 正常点的中心x坐标
        small_dot_x = normal_dot_center_x - small_dot_size // 2  # 小点的起始x坐标

        # y轴也要居中
        small_dot_y = mid_row * row_height + (row_height - small_dot_size) // 2

        draw.ellipse((small_dot_x, small_dot_y,
                      small_dot_x + small_dot_size, small_dot_y + small_dot_size),
                     fill=dot_color)

    # 绘制下三行的盲文点
    for row in range(4, 7):  # 第4、5、6行（索引4、5、6）
        for col in range(5):
            # 随机决定是否绘制点
            if random.random() > 0.6:
                x = col * row_height
                y = row * row_height
                draw.ellipse((x, y, x + dot_size, y + dot_size), fill=dot_color)

    return img


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
            is_self_closing = tag_part.endswith('/>') or tag_name in {'hr', 'lr', 'br', 'cyber'}
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
        # self.image_folder = image_folder
        self.load_images(image_folder)

    def load_images(self, image_folder):
        """加载图片目录下所有支持的图像文件"""
        supported_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        try:
            for filename in os.listdir(image_folder):
                name, ext = os.path.splitext(filename)
                if ext.lower() in supported_ext:
                    # 统一使用小写文件名作为键
                    self.image_map[name.lower()] = self.open(os.path.join(image_folder, filename))
        except FileNotFoundError:
            print(f"错误：图片目录 {image_folder} 不存在")
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


icon_dict = {
    '🏅': '<独特>',
    '⭕': '<反应>',
    '➡️': '<启动>',
    '⚡': '<免费>',
    '💀': '<骷髅>',
    '👤': '<异教徒>',
    '📜': '<石板>',
    '👹': '<古神>',
    '🐙': '<触手>',
    '⭐': '<旧印>',
    '👊': '<拳>',
    '📚': '<书>',
    '🦶': '<脚>',
    '🧠': '<脑>',
    '❓': '<?>',
    '🔵': '<点>',
    '🌑': '<诅咒>',
    '🌟': '<祝福>',
    '❄️': '<雪花>',
    '🕵️': '<调查员>',
    '🚶': '<流浪者>',
    '🏕️': '<生存者>',
    '🛡️': '<守护者>',
    '🧘': '<潜修者>',
    '🔍': '<探求者>'
}


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


symbol_list = ['，', '。', '：', ':', '“', '”', '.', ')']


class Card:
    def __init__(
            self,
            width,
            height,
            font_manager=None,
            image_manager=None,
            card_type='default',
            card_class='default',
            is_back=False
    ):
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
        self.text_mark = []  # 文字标记
        self.icon_mark = []  # 图标标记
        self.subclass_num = 0  # 子类数量
        self.is_back = is_back  # 是否背面

    def final_processing(self):
        """生成卡图后最后要处理的操作"""
        if self.subclass_num == 0 and self.card_class in ['探求者', '潜修者', '生存者', '流浪者', '守护者']:
            # 框选本身的职介
            start_ps = (0, 0)
            if self.card_type == '支援卡':
                start_ps = (634, 4)
            elif self.card_type == '事件卡':
                start_ps = (324, 494)
            if start_ps != (0, 0):
                self.optimization_icon_mark({
                    'points': [
                        (start_ps[0], start_ps[1] + 10),
                        (start_ps[0] + 89, start_ps[1] + 10),
                        (start_ps[0] + 89, start_ps[1] + 89 + 10),
                        (start_ps[0], start_ps[1] + 89 + 10)
                    ],
                    'text': self.card_class
                }, True)

    def _extend_image_right(self, source_img, extension=800):
        # 确保源图像是RGBA模式（如果原本不是，先转换）
        if source_img.mode != 'RGBA':
            source_img = source_img.convert('RGBA')

        # 截取右边5%的像素
        right_crop = 15
        img = source_img.crop((source_img.width - right_crop, 0, source_img.width, source_img.height))

        # 计算新尺寸（宽度翻倍）
        new_size = (img.width + extension, img.height)
        img = img.resize(new_size, resample=Image.BILINEAR)

        # 拼接source_img和img，使用RGBA模式保留透明度
        result_img = Image.new('RGBA', (source_img.width + extension, source_img.height))
        result_img.paste(source_img, (0, 0))
        result_img.paste(img, (source_img.width - 15, 0))

        return result_img

    def paste_image(self, img, region, resize_mode='stretch', transparent_list=None, extension=0):
        """
        在指定区域粘贴图片

        :param img: 图片
        :param region: 目标区域坐标和尺寸 (x, y, width, height)
        :param resize_mode: 调整模式，可选 'stretch'(拉伸)/'contain'(适应)/'cover'(覆盖)
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
        text = text.replace('</img>\n', '</img>')
        text = text.replace('\n', '<lr>')

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
        # 替换emoji
        for emoji_item in icon_dict:
            text = text.replace(emoji_item, icon_dict[emoji_item])
        # text = text.replace('·', "<fonts name='SourceHanSansSC-Regular' offset='-25'>\uff65</fonts>")
        text = text.replace('】。', "】<fonts name='SourceHanSansSC-Bold' offset='-30'>\uff61</fonts>")
        return text

    def draw_centered_text(
            self, position,
            text,
            font_name,
            font_size,
            font_color,
            has_border=False,
            border_width=1,
            border_color=(0, 0, 0),
            underline=False
    ):
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
        :param underline: 是否添加下划线
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
            if node['tag'] == 'cyber':
                # 计算文字宽度
                cyber_num = int(node['attrs'].get('num', '1'))
                text_width += cyber_num * font_size * 0.5  # 赛博文宽度估计

            if node['tag'] == 'text' or node['tag'] == 'fonts':
                _font_name, content = node['attrs']['name'] if node['tag'] == 'fonts' else 'default', node['content']

                font = self._get_font(font_name, font_size) if _font_name == 'default' else self._get_font(_font_name,
                                                                                                           font_size)
                char_w, _ = self._get_text_dimensions(content, font)
                text_width += char_w

        x = position[0] - text_width / 2
        y = position[1] - text_height / 2
        line_height = font_size

        current_x = x

        for node in segments:
            if node['tag'] == 'cyber':
                # 处理赛博文
                cyber_num = int(node['attrs'].get('num', '1'))
                seed = node['attrs'].get('seed', None)
                if seed is not None:
                    random.seed(int(seed))
                for i in range(cyber_num):
                    # 生成赛博文
                    cyber_text = generate_random_braille(size=font_size, seed=random.random())

                    # 计算原图的宽高比
                    original_width, original_height = cyber_text.size
                    aspect_ratio = original_width / original_height

                    # 根据line_height计算新的宽度，保持比例
                    new_height = int(line_height * 0.9)
                    new_width = int(new_height * aspect_ratio)

                    # 等比缩放
                    cyber_text = cyber_text.resize((new_width, new_height))

                    # 粘贴到图片上
                    self.image.paste(cyber_text, (int(current_x), int(y + 2)), cyber_text)
                    current_x += cyber_text.width
                pass
            if node['tag'] == 'img':
                content = node['content']
                # 内联模式
                img = self.image_manager.get_image(content)
                if img:
                    print(line_height)
                    # 将img大小等比缩放到line_height
                    img = img.resize((line_height, line_height))
                    self.image.paste(img, (int(current_x + 2), int(y + 3)), img)
                    current_x += img.width + 4
                pass
            if node['tag'] == 'text' or node['tag'] == 'fonts':
                _font_name, content = node['attrs']['name'] if node['tag'] == 'fonts' else 'default', node['content']

                font = self._get_font(font_name, font_size) if _font_name == 'default' else self._get_font(_font_name,
                                                                                                           font_size)
                char_w, char_h = self._get_text_dimensions(content, font)
                line_height = max(line_height, char_h)
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
        # 是否添加下划线
        if underline:
            underline_y = y + text_height + 2
            y_offset = 12
            self.draw.line(
                (x, underline_y + y_offset, x + text_width, underline_y + y_offset),
                fill=font_color,
                width=1
            )
            y_offset = 18
            self.draw.line(
                (x, underline_y + y_offset, x + text_width, underline_y + y_offset),
                fill=font_color,
                width=2
            )

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
        line_height = font_size

        segments = self._parse_text_segments(text)
        for node in segments:
            if node['tag'] == 'img':
                content = node['content']
                # 内联模式
                img = self.image_manager.get_image(content)
                if img:
                    # 将img大小等比缩放到line_height
                    img = img.resize((line_height, line_height))
                    self.image.paste(img, (int(current_x + 2), int(y + 3)), img)
                    current_x += img.width + 4
                pass
            if node['tag'] == 'text' or node['tag'] == 'fonts':
                _font_name, content = node['attrs']['name'] if node['tag'] == 'fonts' else 'default', node['content']

                font = self._get_font(font_name, font_size) if _font_name == 'default' else self._get_font(_font_name,
                                                                                                           font_size)
                char_w, char_h = self._get_text_dimensions(content, font)
                line_height = char_h
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

    def create_left_text_mark(
            self,
            width,
            text,
            font_name,
            font_size,
            font_color=(0, 0, 0)
    ):
        """制作靠左文本透明图层"""
        text = self.unified_text_processing(text)
        segments = self._parse_text_segments(text)
        x = 0
        y = 0
        current_x = x
        line_start_x = x
        line_end_x = width
        line_height = int(font_size * 1.2)
        line_number = 1
        # 创建行高透明图层画板
        line_height_img = Image.new('RGBA', (width, line_height), (0, 0, 0, 0))
        line_height_draw = ImageDraw.Draw(line_height_img)

        for node in segments:
            _font_name, content = node['attrs']['name'] if node['tag'] == 'fonts' else 'default', node['content']
            if node['tag'] == 'img':
                if 'inline' in node['attrs'] and node['attrs']['inline'] == 'true':
                    # 内联模式
                    img = self.image_manager.get_image(content)
                    if img:
                        # 将img大小等比缩放到line_height
                        img = img.resize((line_height, line_height))
                        line_height_img.paste(img, (current_x + 2, y - 2), img)
                        current_x += img.width + 4
                    pass

            if node['tag'] == 'text' or node['tag'] == 'fonts':
                font = self._get_font(font_name, font_size) if _font_name == 'default' else self._get_font(_font_name,
                                                                                                           font_size)
                for char in list(content):
                    char_w, char_h = self._get_text_dimensions(char, font)
                    if current_x + char_w > width and char not in symbol_list:
                        # 如果字符宽度大于宽度，换行
                        current_x = 0
                        y += line_height
                        line_number += 1
                        # 创建一个新的行高透明图层画板
                        line_height_img_new = Image.new('RGBA', (width, line_height * line_number), (0, 0, 0, 0))
                        # 将旧的粘贴到新的图片上
                        line_height_img_new.paste(line_height_img, (0, 0))
                        line_height_img = line_height_img_new
                        line_height_draw = ImageDraw.Draw(line_height_img)
                    offset = 0
                    if 'attrs' in node and 'offset' in node['attrs']:
                        offset = int(int(node['attrs']['offset']) / 100 * font_size)
                    offset += self.font_manager.get_font_offset(font_name)
                    line_height_draw.text((current_x, y + offset), char, font=font, fill=font_color)
                    current_x += char_w
        return line_height_img

    def _get_draw_scenario_card_token(self, name):
        """获取画冒险参考卡的图标"""
        if name == 'skull':
            return self.image_manager.get_image('冒险参考卡-骷髅')
        elif name == 'cultist':
            return self.image_manager.get_image('冒险参考卡-异教徒')
        elif name == 'tablet':
            return self.image_manager.get_image('冒险参考卡-石碑')
        elif name == 'elder_thing':
            return self.image_manager.get_image('冒险参考卡-古神')
        return None

    def draw_scenario_card(self, scenario_card, resource_name=''):
        """画冒险参考卡"""
        scenario_card_object = []
        for token_type in ['skull', 'cultist', 'tablet', 'elder_thing']:
            if scenario_card.get(token_type, '') != '':
                img = self.create_left_text_mark(
                    width=450,
                    text=scenario_card[token_type],
                    font_name="simfang",
                    font_size=32,
                    font_color=(0, 0, 0)
                )
                scenario_card_object.append({
                    'token': token_type,
                    'img': img,
                })
        # 计算坐标
        remaining_height = 630
        if resource_name != '':
            remaining_height = 500
            # 画资源名称
            self.draw_centered_text(
                (self.width // 2, 807),
                text=resource_name,
                font_name="汉仪小隶书简",
                font_size=36,
                font_color=(0, 0, 0)
            )
        for token_object in scenario_card_object:
            img = token_object['img']
            remaining_height -= max(img.height, 84)
            pass
        if remaining_height < 0:
            remaining_height = 0
        gap = remaining_height // len(scenario_card_object)
        # 开始画
        start_x = 88
        start_y = 300
        current_x = 0
        current_y = 0
        for token_object in scenario_card_object:
            img = token_object['img']
            token = token_object['token']
            # 计算坐标
            current_x = 0
            height = max(img.height, 84)
            token_img = self._get_draw_scenario_card_token(token)
            # 粘贴token
            token_gap = (height - 84) // 2
            self.paste_image(
                token_img,
                (start_x + current_x, start_y + current_y + token_gap, token_img.width, token_img.height),
                resize_mode='contain',
                extension=0
            )
            current_x += 94
            # 粘贴文本
            text_gap = (height - img.height) // 2
            self.paste_image(
                img,
                (start_x + current_x, start_y + current_y + text_gap, img.width, img.height),
                resize_mode='contain',
                extension=0
            )
            current_y += height
            current_y += gap

    def optimization_icon_mark(self, mark_object, join_directly=False):
        text = mark_object.get('text', '')
        if not join_directly and text not in [
            '🏅', '⭕', '➡️', '⚡', '💀', '👤', '📜', '👹', '🐙',
            '⭐', '👊', '📚', '🦶', '🧠', '❓', '🔵', '🌑', '🌟',
            '❄️', '🕵️', '🚶', '🏕️', '🛡️', '🧘', '🔍'
        ]:
            return
        # 将mark_object的坐标都转为整数
        mark_object['points'] = [(int(point[0]), int(point[1])) for point in mark_object['points']]
        self.icon_mark.append(mark_object)

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
        # 优化图标标记
        self.optimization_icon_mark(mark_object)

    @staticmethod
    def get_font_text_emoji(font_name, text):
        if font_name == 'arkham-icons':
            if text == 'w':
                return '🏅'
            elif text == 'x':
                return '➖'
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
            if node['tag'] == 'cyber':
                # 处理赛博文
                cyber_num = int(node['attrs'].get('num', '1'))
                seed = node['attrs'].get('seed', None)
                if seed is not None:
                    random.seed(int(seed))
                for i in range(cyber_num):
                    # 生成赛博文
                    cyber_text = generate_random_braille(size=size, seed=random.random())

                    # 计算原图的宽高比
                    original_width, original_height = cyber_text.size
                    aspect_ratio = original_width / original_height

                    # 根据line_height计算新的宽度，保持比例
                    new_height = int(line_height * 0.9)
                    new_width = int(new_height * aspect_ratio)

                    # 等比缩放
                    cyber_text = cyber_text.resize((new_width, new_height))

                    # 计算是否换行
                    if current_x + new_width > line_end_x:
                        current_y += line_height
                        last_text = ''
                        eof_is_br = True
                        # 计算新一行开始和结束
                        line_start_x, line_end_x = self.calculate_padding_x(vertices, current_y,
                                                                            current_y + line_height,
                                                                            padding)
                        last_line_start_x, last_line_end_x = line_start_x, line_end_x
                        current_x = line_start_x

                    # 粘贴到图片上
                    self.image.paste(cyber_text, (current_x, current_y + 2), cyber_text)
                    current_x += cyber_text.width

                print(f"Processing node: {node['tag']} with num: {node['attrs']['num']}")
                pass
            if node['tag'] == 'img':
                if 'inline' in node['attrs'] and node['attrs']['inline'] == 'true':
                    # 内联模式
                    img = self.image_manager.get_image(content)
                    if img:
                        # 将img大小等比缩放到line_height
                        img = img.resize((line_height, line_height))
                        self.image.paste(img, (current_x + 2, current_y - 2), img)
                        current_x += img.width + 4
                    pass
                else:
                    scale = 1
                    if 'attrs' in node and 'scale' in node['attrs']:
                        scale = float(node['attrs']['scale'])
                    # 画图片
                    img_names = content.split('|')
                    # 读取图片
                    img_list = []
                    for img_name in img_names:
                        img = self.image_manager.get_image(img_name)
                        if img:
                            # 将图片缩放比例
                            img = img.resize((int(img.width * scale), int(img.height * scale)))
                            img_list.append(img)
                    # 生成合并图片
                    if img_list:  # 确保有图片需要处理
                        gap = 8  # 设置图片之间的间隙大小，可以根据需要调整

                        # 计算总宽度和最大高度（总宽度需要加上间隙）
                        total_width = sum(img.width for img in img_list) + (len(img_list) - 1) * gap
                        max_height = max(img.height for img in img_list)

                        # 创建透明背景的新图片
                        new_img = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))

                        # 逐个粘贴图片，保持垂直居中
                        x_offset = 0
                        for img in img_list:
                            # 计算垂直居中的y坐标
                            y_offset = (max_height - img.height) // 2
                            new_img.paste(img, (x_offset, y_offset))
                            x_offset += img.width + gap  # 每次增加图片宽度和间隙

                        # 粘贴到图片上
                        # 计算在大图上的粘贴位置（水平居中）
                        line_width = line_end_x - line_start_x
                        x_position = line_start_x + (line_width - new_img.width) // 2
                        # 确保位置不超出边界（可选）
                        x_position = max(0, x_position)
                        # 将合并后的图片粘贴到大图上
                        self.image.paste(new_img, (x_position, current_y), new_img)  # 最后一个参数是蒙版，用于透明背景
                        # 增加y值
                        current_y += new_img.height + 8
                        current_x = line_start_x

            if node['tag'] == 'hr' or node['tag'] == 'lr':
                last_current_y = current_y
                if node['tag'] == 'hr':
                    current_y += line_height + line_height
                    # 画横线
                    self.draw.line(
                        [(line_start_x, current_y - line_height // 2), (line_end_x, current_y - line_height // 2)],
                        fill=color,
                        width=2
                    )
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
                        pass
                    # 将单个字符加入标记数据
                    self.optimization_icon_mark({
                        'points': [
                            (current_x, current_y),
                            (current_x + char_w, current_y),
                            (current_x + char_w, current_y + size),
                            (current_x, current_y + size)
                        ],
                        'text': self.get_font_text_emoji(font_name, char)
                    })
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
                border_width = None
                border_color = None
                if 'center' in node['attrs'] and node['attrs']['center'] == 'false':
                    center = False
                    pass
                if 'blood' in node['attrs'] and node['attrs']['blood'] == 'true':
                    border_width = 1
                    border_color = (125, 40, 38)

                if self.card_type in ['场景卡', '密谋卡', '故事卡', '冒险参考卡']:
                    center = False
                relish_font_name = default_font_name
                if 'font' in node['attrs']:
                    relish_font_name = node['attrs']['font']

                relish_font = self._get_font(relish_font_name, size - 2)

                line_str = ''
                for char in list(content):
                    char_w, char_h = self._get_text_dimensions(char, relish_font)
                    if current_x + char_w > line_end_x and char not in symbol_list:
                        # 靠左对齐
                        temp_line_start_x = line_start_x
                        if self.card_type in ['场景卡', '密谋卡', '故事卡', '冒险参考卡'] and self.is_back:
                            temp_line_start_x = line_start_x + 20
                            # 在行行前画双竖线
                            self.draw.line(
                                [(line_start_x, current_y - 7), (line_start_x, current_y + size + 7)],
                                fill=color,
                                width=2
                            )
                            self.draw.line(
                                [(line_start_x + 6, current_y - 7), (line_start_x + 6, current_y + size + 7)],
                                fill=color,
                                width=2
                            )
                        self._draw_italic_text(
                            text=line_str,
                            left_x=temp_line_start_x,
                            left_y=current_y,
                            font=relish_font,
                            fill=color,
                            border_width=border_width,
                            border_color=border_color
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
                            fill=color,
                            border_width=border_width,
                            border_color=border_color
                        )
                    else:
                        # 靠左对齐
                        temp_line_start_x = line_start_x
                        if self.card_type in ['场景卡', '密谋卡', '故事卡', '冒险参考卡'] and self.is_back:
                            temp_line_start_x = line_start_x + 20
                            # 在行行前画双竖线
                            self.draw.line(
                                [(line_start_x, current_y - 7), (line_start_x, current_y + size + 7)],
                                fill=color,
                                width=2
                            )
                            self.draw.line(
                                [(line_start_x + 6, current_y - 7), (line_start_x + 6, current_y + size + 7)],
                                fill=color,
                                width=2
                            )
                        self._draw_italic_text(
                            text=line_str,
                            left_x=temp_line_start_x,
                            left_y=current_y,
                            font=relish_font,
                            fill=color,
                            border_width=border_width,
                            border_color=border_color
                        )
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

    def _draw_italic_text(
            self,
            text,
            font,
            fill,
            center_x=None,
            center_y=None,
            left_x=0,
            left_y=0,
            shear_factor=0.2,
            border_width=None,
            border_color=None
    ):
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
        temp_draw.text(
            (-left + text_width // 2, -top + text_height // 2),
            text,
            font=font,
            fill=fill,
            stroke_width=border_width,
            stroke_fill=border_color
        )

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
        if center_x is not None and center_y is not None:
            paste_x = center_x - sheared_img.width // 2
            paste_y = center_y - sheared_img.height // 2
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
        # 加入标记数据
        self.optimization_icon_mark({
            'points': [
                (20, 167 + self.submit_index * 85 + 11),
                (72, 167 + self.submit_index * 85 + 11),
                (72, 167 + self.submit_index * 85 + 65),
                (20, 167 + self.submit_index * 85 + 65)
            ],
            'text': name
        }, True)
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
        # 加入标记数据
        level_text = str(level) if level is not None else '无'
        self.optimization_icon_mark({
            'points': [
                (position_level[0] - 5, position_level[1] - 8),
                (position_level[0] + 98, position_level[1] - 8),
                (position_level[0] + 98, position_level[1] + 45),
                (position_level[0] - 5, position_level[1] + 45)
            ],
            'text': f'等级-{level_text}'
        }, True)

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
        # 加入标记数据
        cost_text = str(cost)
        if cost == -2:
            cost_text = 'X'
        elif cost == -1:
            cost_text = '无'

        self.optimization_icon_mark({
            'points': [
                (default_position[0][0] - 30, default_position[0][1] - 20),
                (default_position[0][0] + 30, default_position[0][1] - 20),
                (default_position[0][0] + 30, default_position[0][1] + 30),
                (default_position[0][0] - 30, default_position[0][1] + 30)
            ],
            'text': f'数字-{cost_text}'
        }, True)
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
        # 加入标记数据
        self.optimization_icon_mark({
            'points': [
                (603 - self.slots_index * 105, 900),
                (603 - self.slots_index * 105 + 112, 900),
                (603 - self.slots_index * 105 + 112, 900 + 112),
                (603 - self.slots_index * 105, 900 + 112)
            ],
            'text': slots
        }, True)
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
        elif self.card_type == '地点卡':
            curve = [(42, 623), (10, 653), (90, 610)]
            if 0 < health < 4:
                for i in range(health):
                    img = self.image_manager.get_image('UI-伤害')
                    self.paste_image(img, curve[i], 'contain')
                pass
            if 0 < horror < 4:
                for i in range(horror):
                    img = self.image_manager.get_image('UI-恐惧')
                    # 计算curve[i]左右镜像坐标
                    temp_curve = (self.image.width - curve[i][0] - img.width, curve[i][1])
                    self.paste_image(img, temp_curve, 'contain')
                pass
            return
        elif self.card_type == '敌人卡':
            curve = [15, 6, 0, 4, 12]
            if 0 < health < 6:
                for i in range(health):
                    img = self.image_manager.get_image('UI-伤害')
                    self.paste_image(img, (260 - i * 45, 583 - i * 23 - curve[i]), 'contain')
                    # 加入标记数据
                    self.optimization_icon_mark({
                        'points': [
                            (260 - i * 45, 583 - i * 23 - curve[i]),
                            (260 - i * 45 + 40, 583 - i * 23 - curve[i]),
                            (260 - i * 45 + 40, 583 - i * 23 + 40 - curve[i]),
                            (260 - i * 45, 583 - i * 23 + 40 - curve[i])
                        ],
                        'text': '🫀'
                    }, True)
                pass
            if 0 < horror < 6:
                for i in range(horror):
                    img = self.image_manager.get_image('UI-恐惧')
                    self.paste_image(img, (440 + i * 45, 583 - i * 23 - curve[i] + 4), 'contain')
                    # 加入标记数据
                    self.optimization_icon_mark({
                        'points': [
                            (440 + i * 45, 583 - i * 23 - curve[i] + 4),
                            (440 + i * 45 + 40, 583 - i * 23 - curve[i] + 4),
                            (440 + i * 45 + 40, 583 - i * 23 + 40 - curve[i] + 4),
                            (440 + i * 45, 583 - i * 23 + 40 - curve[i] + 4)
                        ],
                        'text': '💙'
                    }, True)
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
        # 加入标记数据
        self.optimization_icon_mark({
            'points': [
                (323 - 25, 930),
                (323 + 25, 930),
                (323 + 25, 963 + 40),
                (323 - 25, 963 + 40)
            ],
            'text': f'数字-{health if health > 0 else "无"}'
        }, True)
        self.optimization_icon_mark({
            'points': [
                (430 - 25, 930),
                (430 + 25, 930),
                (430 + 25, 963 + 40),
                (430 - 25, 963 + 40)
            ],
            'text': f'数字-{horror if horror > 0 else "无"}'
        }, True)
        pass

    def set_number_value(self, position, text, font_size=1, color=(255, 255, 255), stroke_color=(0, 0, 0)):
        """画数值"""
        font = self._get_font('Bolton', font_size)
        # 取出text中的数字
        number = ''
        r = re.findall(r'\d+', text)
        if r and '赛博' in text:
            # 渲染赛博数字
            number = r[0]
            cyber_text = generate_random_braille(45, seed=number, dot_color=(255, 255, 255, 255))
            # 粘贴到图片上
            x = position[0] - cyber_text.width // 2
            y = position[1] - cyber_text.height // 2 + 5
            self.image.paste(cyber_text, (x, y), cyber_text)
            return
        if r:
            number = r[0]
        if 'X' in text or 'x' in text:
            number = 'X'
        if '?' in text or '？' in text:
            number = '?'
        if '*' in text:
            number = '*'
            font_size = 42
            font = self._get_font('simfang', font_size)
        if '-' in text or '一' in text or '无' in text:
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
        if number == 'X':
            y -= 4
        self.draw.text((x, y), number, font=font, fill=color, stroke_width=1, stroke_fill=stroke_color)
        # 加入标记数据
        if number == 'x':
            number = '无'
        self.optimization_icon_mark({
            'points': [
                (x, y),
                (x + number_width, y),
                (x + number_width, y + text_height + 8),
                (x, y + text_height + 8)
            ],
            'text': '数字-' + number
        }, True)
        # 画调查员
        if investigator_font is not None:
            x = position[0] + number_width // 2 - investigator_width // 2 + 4
            self.draw.text((x, y + 3), 'v', font=investigator_font, fill=color, stroke_width=1,
                           stroke_fill=stroke_color)
            # 加入标记数据
            self.optimization_icon_mark({
                'points': [
                    (x, y + 3),
                    (x + investigator_width, y + 3),
                    (x + investigator_width, y + 3 + investigator_width),
                    (x, y + 3 + investigator_width)
                ],
                'text': self.get_font_text_emoji('arkham-icons', 'v')
            }, True)

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
        self.subclass_num = len(subclass)
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
            # 加入标记数据
            self.optimization_icon_mark({
                'points': [
                    (start_ps[0] - i * 89, start_ps[1] + 10),
                    (start_ps[0] - i * 89 + 89, start_ps[1] + 10),
                    (start_ps[0] - i * 89 + 89, start_ps[1] + 89 + 10),
                    (start_ps[0] - i * 89, start_ps[1] + 89 + 10)
                ],
                'text': item
            }, True)

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
                                       encounter_count=-1, encounter_position=1, font=None):
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
                font_name='ArnoPro-Bold' if font is None else font,
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
            # 加入标记数据
            self.optimization_icon_mark({
                'points': [
                    (20, 13),
                    (20 + 70, 13),
                    (20 + 70, 13 + 70),
                    (20, 13 + 70)
                ],
                'text': icon
            }, True)
        elif 0 < index < 7:
            self.paste_image(im, link_position[index - 1], 'contain')
            # 加入标记数据
            self.optimization_icon_mark({
                'points': [
                    (link_position[index - 1][0], link_position[index - 1][1]),
                    (link_position[index - 1][0] + 70, link_position[index - 1][1]),
                    (link_position[index - 1][0] + 70, link_position[index - 1][1] + 70),
                    (link_position[index - 1][0], link_position[index - 1][1] + 70)
                ],
                'text': icon
            }, True)

    def set_encounter_icon(self, icon_name):
        """画遭遇组"""
        if icon_name is None:
            return
        im = self.image_manager.get_image(f'{icon_name}')
        if self.card_type == '地点卡':
            self.paste_image(im, (340, 487, 60, 60), 'contain')
        elif self.card_type == '敌人卡':
            self.paste_image(im, (338, 542, 60, 60), 'contain')
        elif self.card_type == '诡计卡':
            self.paste_image(im, (340, 502, 60, 60), 'contain')
        elif self.card_type == '故事卡':
            self.paste_image(im, (608, 54, 72, 72), 'contain')
        elif self.card_type == '冒险参考卡':
            self.paste_image(im, (339, 120, 60, 60), 'contain')
        elif self.card_type == '密谋卡' and self.is_back is False:
            self.paste_image(im, (731, 48, 60, 60), 'contain')
        elif self.card_type == '场景卡' and self.is_back is False:
            self.paste_image(im, (259, 48, 60, 60), 'contain')
        elif self.card_type == '密谋卡' and self.is_back is True:
            self.paste_image(im, (62, 103, 72, 72), 'contain')
        elif self.card_type == '场景卡' and self.is_back is True:
            self.paste_image(im, (62, 103, 72, 72), 'contain')
