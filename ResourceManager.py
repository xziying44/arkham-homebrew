import os
import os
import sys

from PIL import Image, ImageFont


def get_resource_path(relative_path):
    """获取资源文件的绝对路径，适用于开发环境和打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


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
        image_folder = get_resource_path(image_folder)
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


class FontManager:
    """字体管理器，用于预加载和管理字体文件"""

    def __init__(self, font_folder='fonts', lang='zh'):
        """
        初始化字体管理器

        :param font_folder: 字体文件存放目录，默认为'fonts'
        """

        self.font_map = {}
        self.font_folder = get_resource_path(font_folder)
        self._load_fonts()
        self.lang = None
        self.set_lang(lang)

    def set_lang(self, lang='zh'):
        if lang == self.lang:
            return
        if lang == 'en':
            self.lang = 'en'
            self.font_dict = {
                '思源黑体': 'NimbusRomNo9L-Med',
                '方正舒体': 'NimbusRomNo9L-MedIta',
                'simfang': 'ArnoPro-Regular',
                '汉仪小隶书简': 'Teutonic',
                '副标题': 'ArnoPro-Smbd',
                '小字': 'ArnoPro-Smbd'
            }
        else:
            self.lang = 'zh'
            self.font_dict = {
                '副标题': '汉仪小隶书简',
                '小字': '汉仪小隶书简',
            }

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

    def get_font(self, font_name, font_size):
        """
        获取字体对象
        :param font_name:
        :param font_size:
        :return:
        """
        font_path = self.get_font_path(font_name)
        # print(font_name,font_size)
        return ImageFont.truetype(font_path, font_size)

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
