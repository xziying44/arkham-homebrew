import json
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# 假设 ResourceManager.py 和 FontManager 类存在且工作正常
from ResourceManager import FontManager


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

    def add_page(self, image_path, text_data):
        """
        向PDF添加一个新页面。

        Args:
            image_path (str): 背景图片的路径。
            text_data (list): 包含文本信息的JSON对象列表。
        """
        if not os.path.exists(image_path):
            print(f"错误: 背景图片 '{image_path}' 不存在。")
            return

        unique_fonts = {item.get('font') for item in text_data if item.get('font')}
        for font_name in unique_fonts:
            font_path = self.font_manager.get_font_path(font_name)
            if font_path:
                print(f"正在注册字体 '{font_name}' 从 '{font_path}'...")
                self._register_font(font_name, font_path)

        self.pages_data.append({
            'image_path': image_path,
            'text_data': text_data,
        })
        print(f"已添加新页面，使用背景图: {image_path}")

    def save(self):
        """
        生成并保存PDF文件。
        """
        if not self.pages_data:
            print("没有页面可以保存。请先调用 add_page() 方法。")
            return

        print("开始生成PDF...")

        try:
            with Image.open(self.pages_data[0]['image_path']) as img:
                width, height = img.size
            c = canvas.Canvas(self.output_filename, pagesize=(width, height))
        except Exception as e:
            print(f"无法打开第一张图片以设置页面大小: {e}")
            return

        for i, page in enumerate(self.pages_data):
            print(f"正在绘制第 {i + 1}/{len(self.pages_data)} 页...")

            try:
                with Image.open(page['image_path']) as img:
                    width, height = img.size
                c.setPageSize((width, height))
            except Exception as e:
                print(f"警告: 无法加载页面 {i + 1} 的图片 '{page['image_path']}'。跳过此页面。错误: {e}")
                continue

            c.drawImage(page['image_path'], 0, 0, width=width, height=height)

            for item in page['text_data']:
                text = item.get('text', '')
                x = item.get('x', 0)
                y = item.get('y', 0)
                font = item.get('font', 'Helvetica')
                font_size = item.get('font_size', 12)
                color_hex = item.get('color', '#000000')

                # --- 修正部分开始 ---

                border_width = item.get('border_width', 0)
                border_color_hex = item.get('border_color', '#000000')

                pdf_y = height - y - font_size * 0.9

                if border_width > 0:
                    # 使用 saveState 和 restoreState 来隔离对画布状态的修改
                    c.saveState()

                    # 1. 在画布(c)上设置线宽
                    c.setLineWidth(border_width)

                    # 2. 创建和设置文本对象
                    text_obj = c.beginText()
                    text_obj.setTextOrigin(x, pdf_y)

                    if font in self._registered_fonts:
                        text_obj.setFont(font, font_size)
                    else:
                        text_obj.setFont('Helvetica', font_size)

                    text_obj.setFillColor(colors.HexColor(color_hex))
                    text_obj.setStrokeColor(colors.HexColor(border_color_hex))
                    text_obj.setTextRenderMode(2)  # 2 = 填充并描边

                    text_obj.textLine(text)
                    c.drawText(text_obj)

                    # 3. 恢复画布状态，以免影响其他元素的绘制
                    c.restoreState()
                else:
                    # 如果不需要边框，继续使用简单高效的 drawString 方法
                    if font in self._registered_fonts:
                        c.setFont(font, font_size)
                    else:
                        c.setFont('Helvetica', font_size)

                    c.setFillColor(colors.HexColor(color_hex))
                    c.drawString(x, pdf_y, text)

                # --- 修正部分结束 ---

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

    # 4. 添加页面
    drawer.add_page(BACKGROUND_IMAGE, text_info)

    # 5. 保存PDF
    drawer.save()
