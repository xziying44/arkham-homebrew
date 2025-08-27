import random
import re

from PIL import Image, ImageDraw, ImageFont

from ResourceManager import FontManager, ImageManager
from rich_text_render.RichTextRenderer import RichTextRenderer, DrawOptions, TextAlignment


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
        self.rich_renderer = RichTextRenderer(font_manager, image_manager, self.image, lang=font_manager.lang)

    def copy_circle_to_image(self, reference_image: Image, source_params, target_params):
        """
        从参考图复制圆形区域到底图

        Args:
            reference_image (PIL.Image): 参考图
            source_params (tuple): 源圆形参数 (x, y, 半径)
            target_params (tuple): 目标圆形参数 (x, y, 半径)

        Returns:
            PIL.Image: 处理后的图像
        """
        # 复制参考图并拉伸到和card图片大小一致
        reference_copy = reference_image.copy()
        reference_copy = reference_copy.resize((self.width, self.height), Image.Resampling.LANCZOS)

        # 解析参数
        src_x, src_y, src_radius = source_params
        tgt_x, tgt_y, tgt_radius = target_params

        result_image = self.image

        # 计算源圆形的边界框
        src_left = src_x - src_radius
        src_top = src_y - src_radius
        src_right = src_x + src_radius
        src_bottom = src_y + src_radius

        # 从调整大小后的参考图中裁剪出包含圆形的矩形区域
        cropped_reference = reference_copy.crop((src_left, src_top, src_right, src_bottom))

        # 如果目标半径与源半径不同，需要调整大小
        if tgt_radius != src_radius:
            new_size = tgt_radius * 2  # 直径
            cropped_reference = cropped_reference.resize((new_size, new_size), Image.Resampling.LANCZOS)

        # 创建圆形蒙版
        mask_size = tgt_radius * 2  # 直径
        mask = Image.new('L', (mask_size, mask_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, mask_size, mask_size], fill=255)

        # 计算目标位置
        tgt_left = tgt_x - tgt_radius
        tgt_top = tgt_y - tgt_radius

        # 将圆形区域粘贴到底图上
        result_image.paste(cropped_reference, (tgt_left, tgt_top), mask)

        return result_image

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
        offset = self.font_manager.get_font_offset(font_name)
        self.rich_renderer.draw_line(
            text=text,
            position=(position[0], position[1] + offset),
            alignment=TextAlignment.CENTER,
            options=DrawOptions(
                font_name=font_name,
                font_size=self.font_manager.get_font_size_adaptive(font_name, font_size),
                font_color=font_color,
                has_border=has_border,
                border_color=border_color,
                border_width=border_width,
                has_underline=underline
            ),
        )
        pass

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
        offset = self.font_manager.get_font_offset(font_name)
        self.rich_renderer.draw_line(
            text=text,
            position=(position[0], position[1] + offset),
            alignment=TextAlignment.LEFT,
            options=DrawOptions(
                font_name=font_name,
                font_size=self.font_manager.get_font_size_adaptive(font_name, font_size),
                font_color=font_color,
                has_border=has_border,
                border_color=border_color,
                border_width=border_width,
            ),
        )
        pass

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

    def create_left_text_mark(
            self,
            width,
            text,
            font_name,
            font_size,
            font_color=(0, 0, 0)
    ):
        """制作靠左文本透明图层"""
        line_height_img = Image.new('RGBA', (width, self.image.height), (0, 0, 0, 0))
        temp_rich_renderer = RichTextRenderer(
            font_manager=self.font_manager,
            image_manager=self.image_manager,
            image=line_height_img,
            lang=self.font_manager.lang
        )
        temp_rich_renderer.draw_complex_text(
            text=text,
            polygon_vertices=[(0, 0), (width, 0), (width, self.image.height), (0, self.image.height)],
            padding=0,
            options=DrawOptions(
                font_name=font_name,
                font_size=font_size,
                font_color=font_color
            ),
        )
        # 获取图片的主体范围
        bbox = line_height_img.getbbox()
        # 裁剪 图片
        line_height_img = line_height_img.crop((0, 0, width, bbox[3]))
        return line_height_img

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
        # 兼容旧格式
        if (self.card_type in ['密谋卡', '场景卡'] and self.is_back) or self.card_type == '故事卡':
            text = re.sub(r'<relish>(.*?)</relish>', r'<flavor align="left" quote="true" flex="false">\1</flavor>',
                          text)
        elif self.card_type in ['密谋卡', '场景卡'] and not self.is_back:
            text = re.sub(r'<relish>(.*?)</relish>', r'<flavor align="left" padding="0"  flex="false">\1</flavor>',
                          text)
        self.rich_renderer.draw_complex_text(
            text,
            polygon_vertices=vertices,
            padding=padding,
            options=DrawOptions(
                font_name=default_font_name,
                font_size=default_size,
                font_color=color
            ),
            draw_debug_frame=draw_virtual_box
        )
        pass

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
        elif health == -2:
            self.draw_centered_text(
                position=(323, 970),
                text='*',
                font_name='star',
                font_size=64,
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
        elif horror == -2:
            self.draw_centered_text(
                position=(434, 970),
                text='*',
                font_name='star',
                font_size=64,
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

    @staticmethod
    def _get_text_dimensions(text, font):
        """
        获取文本尺寸

        :param text: 要测量的文本
        :param font: 字体对象
        :return: (宽度, 高度)元组
        """
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def set_number_value(self, position, text, font_size=1, color='#f8f1e4', stroke_color='#060001'):
        """画数值"""
        font = self.font_manager.get_font('Bolton', font_size)
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
            font = self.font_manager.get_font('simfang', font_size)
        if '-' in text or '一' in text or '无' in text:
            number = 'x'
            font = self.font_manager.get_font('arkham-icons', font_size)
        # 计算数字
        number_width, text_height = self._get_text_dimensions(number, font)
        investigator_width = 0
        investigator_font = None
        # 画调查员标
        if '<调查员>' in text:
            try:
                if int(number) > 0:
                    investigator_font = self.font_manager.get_font('arkham-icons', 24)
                    investigator_width, _ = self._get_text_dimensions('v', investigator_font)
            except:
                pass
        # 画中间
        x = position[0] - number_width // 2 - investigator_width // 2
        y = position[1] - text_height // 2
        if number == 'X':
            y -= 4
        if number == 'x' and self.card_type in ['场景卡', '密谋卡']:
            y -= 4
        self.draw.text((x, y), number, font=font, fill=color, stroke_width=2, stroke_fill=stroke_color)
        # 加入标记数据
        if number == 'x':
            number = '无'
        # 画调查员
        if investigator_font is not None:
            x = position[0] + number_width // 2 - investigator_width // 2 + 4
            self.draw.text((x, y + 3), 'v', font=investigator_font, fill=color, stroke_width=1,
                           stroke_fill=stroke_color)

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

    def set_encounter_icon(self, icon_name: str | Image.Image, size=None):
        """
        画遭遇组

        :param icon_name: 图标名称或PIL图像对象
        :param size: 图标大小，格式为(width, height)或单个数值(正方形)，None表示使用默认大小
        """
        if icon_name is None:
            return

        if isinstance(icon_name, Image.Image):
            im = icon_name
        else:
            im = self.image_manager.get_image(f'{icon_name}')

        # 定义每种卡牌类型的中心点坐标和默认大小
        icon_configs = {
            '地点卡': {'center': (370, 518), 'default_size': (60, 60)},
            '敌人卡': {'center': (369, 574), 'default_size': (60, 60)},
            '诡计卡': {'center': (372, 536), 'default_size': (60, 60)},
            '故事卡': {'center': (600, 98), 'default_size': (60, 60)},
            '冒险参考卡': {'center': (372, 152), 'default_size': (60, 60)},
            '密谋卡_正面': {'center': (742, 78), 'default_size': (60, 60)},
            '场景卡_正面': {'center': (282, 76), 'default_size': (60, 60)},
            '密谋卡_背面': {'center': (98, 140), 'default_size': (68, 68)},
            '场景卡_背面': {'center': (98, 140), 'default_size': (68, 68)},
            '密谋卡-大画': {'center': (106, 448), 'default_size': (72, 72)},
            '场景卡-大画': {'center': (106, 503), 'default_size': (82, 82)},
            '支援卡_中立': {'center': (672, 40), 'default_size': (60, 60)}
        }

        # 确定当前卡牌类型的配置键
        config_key = None
        if self.card_type == '地点卡':
            config_key = '地点卡'
        elif self.card_type == '敌人卡':
            config_key = '敌人卡'
        elif self.card_type == '诡计卡':
            config_key = '诡计卡'
            # 特殊处理弱点诡计卡的UI
            if self.card_class == '弱点':
                encounter_group_ui = self.image_manager.get_image('弱点-诡计卡-遭遇组')
                self._paste_by_center(encounter_group_ui, (346, 527), (70, 70))
        elif self.card_type == '故事卡':
            config_key = '故事卡'
        elif self.card_type == '冒险参考卡':
            config_key = '冒险参考卡'
        elif self.card_type == '密谋卡':
            config_key = '密谋卡_背面' if self.is_back else '密谋卡_正面'
        elif self.card_type == '场景卡':
            config_key = '场景卡_背面' if self.is_back else '场景卡_正面'
        elif self.card_type == '密谋卡-大画':
            config_key = '密谋卡-大画'
        elif self.card_type == '场景卡-大画':
            config_key = '场景卡-大画'
        elif self.card_type == '支援卡' and self.card_class == '中立':
            config_key = '支援卡_中立'
            # 特殊处理支援卡的UI
            encounter_group_ui = self.image_manager.get_image('支援卡-遭遇组')
            self._paste_by_center(encounter_group_ui, (671, 44), (88, 88))

        # 如果找到了配置，则粘贴图标
        if config_key and config_key in icon_configs:
            config = icon_configs[config_key]
            center = config['center']
            actual_size = size if size is not None else config['default_size']

            # 确保size格式正确
            if isinstance(actual_size, (int, float)):
                actual_size = (actual_size, actual_size)

            self._paste_by_center(im, center, actual_size)

    def _paste_by_center(self, image, center_point, size):
        """
        根据中心点坐标粘贴图片

        :param image: 要粘贴的图片
        :param center_point: 中心点坐标 (center_x, center_y)
        :param size: 图片大小 (width, height)
        """
        center_x, center_y = center_point
        width, height = size

        # 计算左上角坐标
        x = center_x - width // 2
        y = center_y - height // 2

        # 粘贴图片
        self.paste_image(image, (x, y, width, height), 'contain')

    @staticmethod
    def invert_rgba_image(img):
        """
        对RGBA图像进行取反色，保持透明度不变

        Args:
            img: PIL.Image对象，支持RGBA模式

        Returns:
            取反色后的PIL.Image对象
        """
        # 确保图像是RGBA模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 分离RGBA通道
        r, g, b, a = img.split()

        # 对RGB通道取反（255-原值）
        r = r.point(lambda x: 255 - x)
        g = g.point(lambda x: 255 - x)
        b = b.point(lambda x: 255 - x)
        # Alpha通道保持不变

        # 重新合并通道
        return Image.merge('RGBA', (r, g, b, a))

    def set_footer_information(self,
                               illustrator: str,
                               footer_copyright: str,
                               encounter_group_number: str,
                               footer_icon: Image.Image,
                               card_number: str):
        """
        写页脚信息
        :param illustrator: 插画信息
        :param footer_copyright: 版权信息
        :param encounter_group_number: 遭遇组序号
        :param footer_icon: 图标
        :param card_number: 卡牌序号
        :return:
        """
        if self.card_type in ['密谋卡', '场景卡'] and self.is_back:
            return
        if self.card_type == '调查员卡背':
            return
        left_text = ''
        center_text = ''
        encounter_text = ''
        right_text = ''
        footer_icon_copy = footer_icon

        if illustrator and illustrator != '':
            left_text = 'Illus. ' + illustrator
        if footer_copyright and footer_copyright != '':
            center_text = footer_copyright
        if encounter_group_number and encounter_group_number != '':
            encounter_text = encounter_group_number
        if card_number and card_number != '':
            right_text = card_number
        if self.card_type in ['故事卡', '冒险参考卡']:
            left_text = center_text
            center_text = ''
        # 通用位置点
        card_width, card_height = self.image.size
        pos_left = (40, card_height - 28)
        pos_center = (card_width // 2, card_height - 28)
        pos_icon = (card_width - 110, card_height - 34)
        pos_right = (card_width - 80, card_height - 28)
        pos_right_encounter_group_number = (card_width - 180, card_height - 28)
        font_color = (255, 255, 255)
        # 特殊卡牌位置点
        if self.card_type in ['密谋卡', '场景卡']:
            card_width = 1049 - 400
            offset_x = 400 if self.card_type == '密谋卡' else 0
            pos_left = (offset_x + 40, card_height - 28)
            pos_center = (offset_x + card_width // 2, card_height - 28)
            pos_icon = (offset_x + card_width - 110, card_height - 34)
            pos_right = (offset_x + card_width - 80, card_height - 28)
            pos_right_encounter_group_number = (offset_x + card_width - 180, card_height - 28)
            pass
        if self.card_type == '调查员卡':
            card_width = 1049 - 580
            offset_x = 580
            end_x = 28
            pos_left = (offset_x, card_height - 28)
            pos_center = (offset_x + card_width // 2, card_height - 28)
            pos_icon = (offset_x + card_width - 110 + end_x, card_height - 34)
            pos_right = (offset_x + card_width - 80 + end_x, card_height - 28)
            pos_right_encounter_group_number = (offset_x + card_width - 160 + end_x, card_height - 28)
            pass
        if self.card_type == '故事卡':
            card_width = 570
            offset_x = 80
            offset_y = -44
            pos_left = (offset_x + 40, offset_y + card_height - 28)
            pos_center = (offset_x + card_width // 2, offset_y + card_height - 28)
            pos_icon = (offset_x + card_width - 110, offset_y + card_height - 34)
            pos_right = (offset_x + card_width - 80, offset_y + card_height - 28)
            pos_right_encounter_group_number = (offset_x + card_width - 180, offset_y + card_height - 28)
            font_color = (0, 0, 0)
            footer_icon_copy = self.invert_rgba_image(footer_icon_copy)
            pass
        # 开始绘制
        if left_text:
            self.draw_left_text(
                position=(pos_left[0], pos_left[1]),
                text=left_text,
                font_name='ArnoPro-Bold',
                font_size=20,
                font_color=font_color
            )
        if center_text:
            self.draw_centered_text(
                position=(pos_center[0], pos_center[1] + 8),
                text=center_text,
                font_name='ArnoPro-Bold',
                font_size=20,
                font_color=font_color
            )
        if encounter_text:
            self.draw_centered_text(
                position=(pos_right_encounter_group_number[0], pos_right_encounter_group_number[1] + 9),
                text=encounter_text,
                font_name='ArnoPro-Bold',
                font_size=20,
                font_color=font_color
            )
        if footer_icon_copy:
            self.paste_image(
                footer_icon_copy,
                (pos_icon[0], pos_icon[1] + 3, 24, 24),
                'stretch'
            )
        if right_text:
            self.draw_left_text(
                position=(pos_right[0], pos_right[1]),
                text=right_text,
                font_name='ArnoPro-Bold',
                font_size=20,
                font_color=font_color
            )
