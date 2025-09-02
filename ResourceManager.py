import json
import os
import sys
from dataclasses import dataclass
from typing import Optional

from PIL import Image, ImageFont


@dataclass
class FontInfo:
    """字体信息配置"""
    name: str  # 字体名称
    size_percent: float = 1.0  # 字体大小百分比
    vertical_offset: int = 0  # 垂直偏移量


@dataclass
class LanguageFonts:
    """语言字体配置"""
    title: FontInfo  # 标题字体
    subtitle: FontInfo  # 副标题字体
    card_type: FontInfo  # 卡牌类别字体
    trait: FontInfo  # 特征字体
    bold: FontInfo  # 粗体字体
    body: FontInfo  # 正文字体
    flavor: FontInfo  # 风味文本字体
    collection_info: FontInfo  # 收藏信息字体


@dataclass
class LanguageTexts:
    """语言文本配置"""
    skill: str = "技能"
    location: str = "地点"
    event: str = "事件"
    asset: str = "支援"
    treachery: str = "诡计"
    enemy: str = "敌人"
    weakness: str = "弱点"
    basic_weakness: str = "基础弱点"
    deck_size: str = "牌库卡牌张数"
    deck_options: str = "牌库构筑选项"
    deck_requirements: str = "牌库构筑需求"
    not_count: str = "不计入卡牌张数"


@dataclass
class LanguageConfig:
    """单一语言配置"""
    name: str  # 语言名称
    fonts: LanguageFonts  # 字体配置
    texts: LanguageTexts  # 文本配置


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
        :param lang: 默认语言
        """
        self.font_map = {}
        self.font_folder = get_resource_path(font_folder)
        self.language_configs = {}
        self.lang = None

        # 加载字体文件
        self._load_fonts()

        # 加载语言配置
        self._load_language_configs()

        # 设置默认语言
        self.set_lang(lang)

        self.silence = False  # 静默模式

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

    def _load_language_configs(self, lang_config=None):
        """加载多语言配置"""
        if lang_config is None:
            # 尝试加载默认配置文件
            default_config_path = get_resource_path('fonts/language_config.json')
            if os.path.exists(default_config_path):
                lang_config = default_config_path
            else:
                print("警告：未找到语言配置文件，将使用空配置")
                return

        if isinstance(lang_config, str):
            # 从JSON文件加载
            try:
                with open(get_resource_path(lang_config), 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._parse_config_data(config_data)
            except Exception as e:
                print(f"加载语言配置文件失败: {str(e)}")
        elif isinstance(lang_config, list):
            # 从列表加载
            self._parse_config_data(lang_config)

    def _parse_config_data(self, config_data):
        """解析配置数据"""
        for lang_data in config_data:
            try:
                # 解析字体配置
                fonts_data = lang_data['fonts']
                fonts = LanguageFonts(
                    title=FontInfo(**fonts_data['title']),
                    subtitle=FontInfo(**fonts_data['subtitle']),
                    card_type=FontInfo(**fonts_data['card_type']),
                    trait=FontInfo(**fonts_data['trait']),
                    bold=FontInfo(**fonts_data['bold']),
                    body=FontInfo(**fonts_data['body']),
                    flavor=FontInfo(**fonts_data['flavor']),
                    collection_info=FontInfo(**fonts_data['collection_info'])
                )

                # 解析文本配置
                texts_data = lang_data.get('texts', {})
                texts = LanguageTexts(**texts_data)

                # 创建语言配置
                lang_config = LanguageConfig(
                    name=lang_data['name'],
                    fonts=fonts,
                    texts=texts
                )

                # 使用语言代码作为键（从name中提取或使用完整name）
                lang_key = lang_data.get('code', lang_data['name'].lower())
                self.language_configs[lang_key] = lang_config

            except Exception as e:
                print(f"解析语言配置失败 {lang_data.get('name', 'unknown')}: {str(e)}")

    def set_lang(self, lang='zh'):
        """设置当前语言"""
        if lang == self.lang:
            return

        if lang in self.language_configs:
            self.lang = lang
        else:
            print(f"警告：未找到语言 '{lang}' 的配置，使用默认配置")
            # 如果没有找到指定语言，尝试使用第一个可用的语言配置
            if self.language_configs:
                self.lang = list(self.language_configs.keys())[0]
            else:
                self.lang = None

    def get_current_config(self) -> Optional[LanguageConfig]:
        """获取当前语言配置"""
        if self.lang and self.lang in self.language_configs:
            return self.language_configs[self.lang]
        return None

    def get_lang_font(self, font_type):
        current_config = self.get_current_config()
        if font_type == '标题字体':
            return current_config.fonts.title
        elif font_type == '副标题字体':
            return current_config.fonts.subtitle
        elif font_type == '卡牌类型字体':
            return current_config.fonts.card_type
        elif font_type == '特性字体':
            return current_config.fonts.trait
        elif font_type == '加粗字体':
            return current_config.fonts.bold
        elif font_type == '正文字体':
            return current_config.fonts.body
        elif font_type == '风味文本字体':
            return current_config.fonts.flavor
        elif font_type == '收藏信息字体':
            return current_config.fonts.collection_info
        return FontInfo(
            name=font_type
        )

    def get_font(self, font_name, font_size):
        """获取字体对象"""
        font_path = self.get_font_path(font_name)
        # print(font_name,font_size)
        return ImageFont.truetype(font_path, font_size)

    def get_font_path(self, font_name):
        """获取字体文件路径"""
        return self.font_map.get(font_name.lower())

    def get_font_offset(self, font_type):
        """
        获取字体垂直偏移量

        :param font_type: 字体类型
        :return: 垂直偏移量
        """
        config = self.get_current_config()
        if not config:
            return 0

        font_info = getattr(config.fonts, font_type, None)
        return font_info.vertical_offset if font_info else 0

    def get_font_text(self, text_key):
        """
        获取多语言文本

        :param text_key: 文本键名
        :return: 对应语言的文本
        skill: str = "技能"
        location: str = "地点"
        event: str = "事件"
        asset: str = "支援"
        treachery: str = "诡计"
        enemy: str = "敌人"
        weakness: str = "弱点"
        basic_weakness: str = "基础弱点"
        deck_size: str = "牌库卡牌张数"
        deck_options: str = "牌库构筑选项"
        deck_requirements: str = "牌库构筑需求"
        not_count: str = "不计入卡牌张数"
        """
        if self.silence:
            return ''
        config = self.get_current_config()
        if not config:
            return text_key  # 如果没有配置，返回原始文本
        # 特殊字符处理
        if text_key == '：' or text_key == '。':
            if self.lang != 'zh':
                if text_key == '：':
                    return ': '
                elif text_key == '。':
                    return '.'
            return text_key
        if text_key == '技能':
            text_key = 'skill'
        elif text_key == '地点':
            text_key = 'location'
        elif text_key == '事件':
            text_key = 'event'
        elif text_key == '支援':
            text_key = 'asset'
        elif text_key == '诡计':
            text_key = 'treachery'
        elif text_key == '敌人':
            text_key = 'enemy'
        elif text_key == '弱点':
            text_key = 'weakness'
        elif text_key == '基础弱点':
            text_key = 'basic_weakness'
        elif text_key == '牌库卡牌张数':
            text_key = 'deck_size'
        elif text_key == '牌库构筑选项':
            text_key = 'deck_options'
        elif text_key == '牌库构筑需求':
            text_key = 'deck_requirements'
        elif text_key == '不计入卡牌张数':
            text_key = 'not_count'
        return getattr(config.texts, text_key, text_key)

    def get_available_languages(self):
        """获取可用的语言列表"""
        return list(self.language_configs.keys())

    @staticmethod
    def create_default_config():
        """创建默认配置并保存为JSON文件"""
        default_config = [
            {
                "name": "简体中文",
                "code": "zh",
                "fonts": {
                    "title": {"name": "思源黑体", "size_percent": 1.0, "vertical_offset": 0},
                    "subtitle": {"name": "汉仪小隶书简", "size_percent": 1.0, "vertical_offset": 0},
                    "card_type": {"name": "思源黑体", "size_percent": 1.0, "vertical_offset": 0},
                    "trait": {"name": "思源黑体", "size_percent": 1.0, "vertical_offset": 0},
                    "bold": {"name": "思源黑体", "size_percent": 1.0, "vertical_offset": 0},
                    "body": {"name": "思源黑体", "size_percent": 1.0, "vertical_offset": 0},
                    "flavor": {"name": "方正舒体", "size_percent": 1.0, "vertical_offset": 0},
                    "collection_info": {"name": "汉仪小隶书简", "size_percent": 1.0, "vertical_offset": 0}
                },
                "texts": {
                    "skill": "技能",
                    "location": "地点",
                    "event": "事件",
                    "asset": "支援",
                    "treachery": "诡计",
                    "enemy": "敌人",
                    "weakness": "弱点",
                    "basic_weakness": "基础弱点",
                    "deck_size": "牌库卡牌张数",
                    "deck_options": "牌库构筑选项",
                    "deck_requirements": "牌库构筑需求",
                    "not_count": "不计入卡牌张数"
                }
            },
            {
                "name": "English",
                "code": "en",
                "fonts": {
                    "title": {"name": "NimbusRomNo9L-Med", "size_percent": 1.0, "vertical_offset": 0},
                    "subtitle": {"name": "ArnoPro-Smbd", "size_percent": 0.95, "vertical_offset": 3},
                    "card_type": {"name": "NimbusRomNo9L-Med", "size_percent": 1.0, "vertical_offset": 0},
                    "trait": {"name": "NimbusRomNo9L-Med", "size_percent": 1.0, "vertical_offset": 0},
                    "bold": {"name": "NimbusRomNo9L-Med", "size_percent": 1.0, "vertical_offset": 0},
                    "body": {"name": "ArnoPro-Regular", "size_percent": 1.0, "vertical_offset": 0},
                    "flavor": {"name": "NimbusRomNo9L-MedIta", "size_percent": 0.9, "vertical_offset": 9},
                    "collection_info": {"name": "Arkhamic", "size_percent": 0.95, "vertical_offset": 6}
                },
                "texts": {
                    "skill": "SKILL",
                    "location": "LOCATION",
                    "event": "EVENT",
                    "asset": "ASSET",
                    "treachery": "TREACHERY",
                    "enemy": "ENEMY",
                    "weakness": "WEAKNESS",
                    "basic_weakness": "BASIC WEAKNESS",
                    "deck_size": "Deck Size",
                    "deck_options": "Deck Options",
                    "deck_requirements": "Deck Requirements",
                    "not_count": "Does not count toward deck size"
                }
            }
        ]

        # 保存默认配置
        with open('language_config.json', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)

        print("默认语言配置文件已创建：language_config.json")
        return default_config
