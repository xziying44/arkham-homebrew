import json
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from enum import Enum, auto
# 假设 ResourceManager.py 和 FontManager 类存在且工作正常
from ResourceManager import FontManager


class RotationDirection(Enum):
    """旋转方向枚举"""
    NORMAL = auto()  # 不旋转
    LEFT = auto()  # 逆时针90度
    RIGHT = auto()  # 顺时针90度


class PDFVectorDrawer:
    """
    一个PDF矢量绘图器。
    它可以加载背景图片，并根据JSON数据在其上绘制矢量文字。
    JSON中的每个文本对象都可以有自己独立的字体、字号、颜色和边框。
    """

    def __init__(self, output_filename, font_manager: 'FontManager'):
        """
        初始化绘图器。

        Args:
            output_filename (str): 最终生成的PDF文件名。
        """
        if not output_filename.lower().endswith('.pdf'):
            raise ValueError("Output filename must end with .pdf")
        self.output_filename = output_filename
        self.font_manager = font_manager
        self.pages_data = []
        self._registered_fonts = set()
        print(f"PDF绘图器已初始化，准备输出到 {self.output_filename}")

    def _register_font(self, font_name, font_path):
        """
        私有方法，用于向reportlab注册字体。
        """
        if font_name not in self._registered_fonts:
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                self._registered_fonts.add(font_name)
            except Exception as e:
                print(f"警告: 无法注册字体 '{font_name}' 从路径 '{font_path}'. 错误: {e}")
                print("将使用默认字体代替。")
                return False
        return True

    def add_page(self, image_source, text_data, rotation=RotationDirection.NORMAL):
        """
        向PDF添加一个新页面。

        Args:
            image_source (str or PIL.Image.Image): 背景图片的路径或PIL图片对象。
            text_data (list): 包含文本信息的JSON对象列表。
            rotation (RotationDirection): 页面旋转方向，默认为不旋转。
        """
        # 处理图片源
        if isinstance(image_source, str):
            if not os.path.exists(image_source):
                print(f"错误: 背景图片 '{image_source}' 不存在。")
                return
            image_path = image_source
            pil_image = Image.open(image_source)
        elif isinstance(image_source, Image.Image):
            image_path = None  # 对于PIL对象，没有文件路径
            pil_image = image_source
        else:
            print(f"错误: 不支持的图片源类型 {type(image_source)}")
            return

        # 获取图片尺寸
        width, height = pil_image.size

        # 根据旋转方向调整页面尺寸
        if rotation == RotationDirection.LEFT or rotation == RotationDirection.RIGHT:
            # 旋转90度时交换宽高
            page_width, page_height = height, width
        else:
            page_width, page_height = width, height

        unique_fonts = {item.get('font') for item in text_data if item.get('font')}
        for font_name in unique_fonts:
            font_path = self.font_manager.get_font_path(font_name)
            if font_path:
                print(f"正在注册字体 '{font_name}' 从 '{font_path}'...")
                self._register_font(font_name, font_path)

        self.pages_data.append({
            'image_source': image_source,
            'text_data': text_data,
            'rotation': rotation,
            'width': width,
            'height': height,
            'page_width': page_width,
            'page_height': page_height
        })

        if isinstance(image_source, str):
            print(f"已添加新页面，使用背景图: {image_source}")
        else:
            print(f"已添加新页面，使用PIL图片对象，尺寸: {width}x{height}")

    def save(self):
        """
        生成并保存PDF文件。
        """
        if not self.pages_data:
            print("没有页面可以保存。请先调用 add_page() 方法。")
            return

        print("开始生成PDF...")

        try:
            # 使用第一页的尺寸创建画布
            first_page = self.pages_data[0]
            c = canvas.Canvas(self.output_filename,
                              pagesize=(first_page['page_width'], first_page['page_height']))
        except Exception as e:
            print(f"无法创建PDF画布: {e}")
            return

        for i, page in enumerate(self.pages_data):
            print(f"正在绘制第 {i + 1}/{len(self.pages_data)} 页...")

            # 设置页面尺寸
            c.setPageSize((page['page_width'], page['page_height']))

            # 应用旋转变换（先处理文字，然后旋转整个页面）
            if page['rotation'] == RotationDirection.LEFT:
                # 逆时针90度
                c.translate(0, page['page_height'])
                c.rotate(-90)
            elif page['rotation'] == RotationDirection.RIGHT:
                # 顺时针90度
                c.translate(page['page_width'], 0)
                c.rotate(90)

            # 绘制背景图片
            if isinstance(page['image_source'], str):
                # 从文件路径加载
                c.drawImage(page['image_source'], 0, 0,
                            width=page['width'], height=page['height'])
            else:
                # 保存PIL图片到临时文件并绘制
                try:
                    temp_path = f"temp_page_{i}.png"
                    page['image_source'].save(temp_path)
                    c.drawImage(temp_path, 0, 0,
                                width=page['width'], height=page['height'])
                    os.remove(temp_path)  # 删除临时文件
                except Exception as e:
                    print(f"警告: 无法处理PIL图片对象。跳过此页面。错误: {e}")
                    continue

            # 绘制文字
            for item in page['text_data']:
                text = item.get('text', '')
                x = item.get('x', 0)
                y = item.get('y', 0)
                font = item.get('font', 'Helvetica')
                font_size = item.get('font_size', 12)
                color_hex = item.get('color', '#000000')

                border_width = item.get('border_width', 0)
                border_color_hex = item.get('border_color', '#000000')

                # 计算Y坐标（PDF坐标系与图片坐标系不同）
                pdf_y = page['height'] - y - font_size * 0.9

                if border_width > 0:
                    c.saveState()

                    # 计算偏移量用于创建描边效果
                    offsets = []
                    for dx in range(-border_width, border_width + 1):
                        for dy in range(-border_width, border_width + 1):
                            if dx * dx + dy * dy <= border_width * border_width:  # 圆形描边
                                offsets.append((dx, dy))

                    # 设置字体
                    if font in self._registered_fonts:
                        c.setFont(font, font_size)
                    else:
                        c.setFont('Helvetica', font_size)

                    # 先绘制所有描边
                    c.setFillColor(colors.HexColor(border_color_hex))
                    for dx, dy in offsets:
                        if dx != 0 or dy != 0:  # 跳过中心点
                            c.drawString(x + dx, pdf_y + dy, text)

                    # 最后绘制主文字
                    c.setFillColor(colors.HexColor(color_hex))
                    c.drawString(x, pdf_y, text)

                    c.restoreState()

                else:
                    # 如果不需要边框，继续使用简单高效的 drawString 方法
                    if font in self._registered_fonts:
                        c.setFont(font, font_size)
                    else:
                        c.setFont('Helvetica', font_size)

                    c.setFillColor(colors.HexColor(color_hex))
                    c.drawString(x, pdf_y, text)

            c.showPage()

        c.save()
        print(f"PDF文件已成功保存到: {self.output_filename}")


if __name__ == '__main__':
    # --- 使用示例 ---

    # 1. 定义输入和输出文件
    JSON_FILE = 'text_information.json'
    BACKGROUND_IMAGE = 'background.png'
    OUTPUT_PDF = 'output_with_borders.pdf'
    # 假设 FontManager 可以找到你的字体
    font_manager = FontManager()

    # 2. 从JSON文件加载文本数据
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            text_info = json.load(f)
    except FileNotFoundError:
        print(f"错误: JSON文件 '{JSON_FILE}' 未找到。")
        exit()
    except json.JSONDecodeError:
        print(f"错误: JSON文件 '{JSON_FILE}' 格式不正确。")
        exit()

    # 3. 创建PDF绘图器实例
    drawer = PDFVectorDrawer(OUTPUT_PDF, font_manager)

    # 4. 添加页面 - 使用文件路径
    drawer.add_page(BACKGROUND_IMAGE, text_info, RotationDirection.NORMAL)

    # 5. 添加页面 - 使用PIL图片对象并旋转
    pil_image = Image.open(BACKGROUND_IMAGE)
    drawer.add_page(pil_image, text_info, RotationDirection.RIGHT)
    drawer.add_page(pil_image, text_info, RotationDirection.LEFT)

    # 6. 保存PDF
    drawer.save()
