import json
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from ResourceManager import FontManager


class PDFVectorDrawer:
    """
    一个PDF矢量绘图器。
    它可以加载背景图片，并根据JSON数据在其上绘制矢量文字。
    JSON中的每个文本对象都可以有自己独立的字体和字号。
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
                # print(f"字体 '{font_name}' 从 '{font_path}' 注册成功。") # 可以取消注释来调试
            except Exception as e:
                print(f"警告: 无法注册字体 '{font_name}' 从路径 '{font_path}'. 错误: {e}")
                print("将使用默认字体代替。")
                return False
        return True

    def add_page(self, image_path, text_data, font_dir='fonts'):
        """
        向PDF添加一个新页面。

        Args:
            image_path (str): 背景图片的路径。
            text_data (list): 包含文本信息的JSON对象列表。
            font_dir (str): 存放字体文件的目录。
        """
        if not os.path.exists(image_path):
            print(f"错误: 背景图片 '{image_path}' 不存在。")
            return

        # 预注册此页面需要的所有字体
        unique_fonts = {item.get('font') for item in text_data if item.get('font')}
        for font_name in unique_fonts:
            font_path = self.font_manager.get_font_path(font_name)
            font_name = font_name.replace("-", "_")
            print(f"正在注册字体 '{font_name}' 从 '{font_path}'...")
            self._register_font(font_name, font_path)

        # 存储页面数据以供后续生成
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

        # 获取第一页的尺寸来初始化Canvas
        try:
            with Image.open(self.pages_data[0]['image_path']) as img:
                width, height = img.size
            c = canvas.Canvas(self.output_filename, pagesize=(width, height))
        except Exception as e:
            print(f"无法打开第一张图片以设置页面大小: {e}")
            return

        for i, page in enumerate(self.pages_data):
            print(f"正在绘制第 {i + 1}/{len(self.pages_data)} 页...")

            # 1. 设置当前页面的尺寸
            try:
                with Image.open(page['image_path']) as img:
                    width, height = img.size
                c.setPageSize((width, height))
            except Exception as e:
                print(f"警告: 无法加载页面 {i + 1} 的图片 '{page['image_path']}'。跳过此页面。错误: {e}")
                continue

            # 2. 绘制背景图片
            c.drawImage(page['image_path'], 0, 0, width=width, height=height)

            # 3. 绘制所有矢量文字
            for item in page['text_data']:
                text = item.get('text', '')
                x = item.get('x', 0)
                y = item.get('y', 0)
                font = item.get('font', 'Helvetica')
                font = font.replace("-", "_")
                color_hex = item.get('color', '#000000')
                # --- 主要修改点 ---
                # 从每个JSON对象中获取独立的font_size
                font_size = item.get('font_size', 12)  # 提供一个默认值以防万一

                # 设置字体和该字符的特定大小
                if font in self._registered_fonts:
                    c.setFont(font, font_size)  # <<< 使用 item 的 font_size
                else:
                    c.setFont('Helvetica', font_size)

                # 设置颜色
                c.setFillColor(colors.HexColor(color_hex))

                # 绘制文字
                # reportlab的坐标系原点(0,0)在左下角。
                # 假设JSON中的(x, y)是文字左上角的坐标。
                # 转换Y坐标: pdf_y = page_height - json_y - font_size
                pdf_y = height - y - font_size  # <<< 使用 item 的 font_size 进行定位
                c.drawString(x, pdf_y, text)

            # 完成当前页
            c.showPage()

        # 4. 保存文件
        c.save()
        print(f"PDF文件已成功保存到: {self.output_filename}")


if __name__ == '__main__':
    # --- 使用示例 ---

    # 1. 定义输入和输出文件
    JSON_FILE = 'text_information.json'
    # 请确保你有一个名为 background.png 的图片文件在同一个目录下
    BACKGROUND_IMAGE = 'background.png'
    OUTPUT_PDF = 'output_document_v2.pdf'
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
    # 添加一个页面，它会使用JSON中为每个字符指定的字号
    drawer.add_page(BACKGROUND_IMAGE, text_info)

    # 你可以继续添加更多页面
    # drawer.add_page('background_page2.png', other_text_info)

    # 5. 保存PDF
    drawer.save()
