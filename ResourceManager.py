import json
import os
import sys
from dataclasses import dataclass
from typing import Optional

from PIL import Image, ImageFont

from bin.logger import logger_manager


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
    story: str = "剧情"
    treachery: str = "诡计"
    enemy: str = "敌人"
    weakness: str = "弱点"
    basic_weakness: str = "基础弱点"
    deck_size: str = "牌库卡牌张数"
    deck_options: str = "牌库构筑选项"
    deck_requirements: str = "牌库构筑需求"
    not_count: str = "不计入卡牌张数"
    agenda: str = "密谋"
    act: str = "场景"
    resolution: str = "结局"
    upgrades: str = "升级项"
    victory: str = "胜利<X>。"
    Illus: str = "Illus."
    # 卡牌关键词
    prey: str = "猎物"
    spawn: str = "生成"
    forced: str = "强制"
    haunted: str = "闹鬼"
    objective: str = "目标"
    patrol: str = "巡逻"
    revelation: str = "显现"


@dataclass
class LanguageConfig:
    """单一语言配置"""
    name: str  # 语言名称
    fonts: LanguageFonts  # 字体配置
    texts: LanguageTexts  # 文本配置


# ============================================
# 文件系统扫描和编码修复
# ============================================
def scan_directory_properly(directory):
    """
    正确扫描目录，处理 Android 编码问题
    返回: [(显示名称, 实际文件路径), ...]
    """
    files_info = []

    try:
        # 使用字节模式扫描
        dir_bytes = os.fsencode(directory)

        for entry_bytes in os.listdir(dir_bytes):
            try:
                # 方式1: 使用 os.fsdecode（优先）
                display_name = os.fsdecode(entry_bytes)
                file_path = os.path.join(directory, display_name)

                # 检查文件是否真实存在
                if os.path.exists(file_path):
                    files_info.append((display_name, file_path))
                    continue

            except Exception as e:
                pass

            # 方式2: 如果方式1失败，尝试强制UTF-8解码
            try:
                display_name = entry_bytes.decode('utf-8')
                file_path = os.path.join(directory, display_name)

                if os.path.exists(file_path):
                    files_info.append((display_name, file_path))
                    continue

            except Exception as e:
                pass

            # 方式3: 使用字节路径
            try:
                # 直接使用字节构建路径
                file_path_bytes = os.path.join(dir_bytes, entry_bytes)
                file_path = os.fsdecode(file_path_bytes)

                # 尝试解码显示名称
                try:
                    display_name = entry_bytes.decode('utf-8')
                except:
                    display_name = entry_bytes.decode('utf-8', errors='replace')

                if os.path.exists(file_path):
                    files_info.append((display_name, file_path))
                    continue

            except Exception as e:
                pass

            # 如果所有方法都失败，打印警告
            logger_manager.info(f"[扫描] 无法处理文件: {entry_bytes}")

    except Exception as e:
        logger_manager.info(f"[扫描] 扫描目录失败: {directory}")
        logger_manager.info(f"[扫描] 错误: {e}")
        import traceback
        traceback.logger_manager.info_exc()

    return files_info


# ============================================
# 原有函数保持不变
# ============================================
def get_resource_path(relative_path):
    """获取资源文件的绝对路径，适用于开发环境、PyInstaller打包和Android打包"""

    # 1. 检查是否在 Android 环境
    if 'ANDROID_ARGUMENT' in os.environ:
        # Android 环境：使用应用的私有目录
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            # 获取应用的私有文件目录
            files_dir = activity.getFilesDir().getAbsolutePath()

            # 资源文件在 app 目录下
            resource_path = os.path.join(files_dir, 'app', relative_path)

            # 检查文件是否存在
            if os.path.exists(resource_path):
                return resource_path

            # 方式2: 尝试直接使用相对路径（某些情况下有效）
            direct_path = os.path.join(os.path.abspath("."), relative_path)
            if os.path.exists(direct_path):
                return direct_path

            # 方式3: 检查当前工作目录
            cwd_path = os.path.join(os.getcwd(), relative_path)
            if os.path.exists(cwd_path):
                return cwd_path

            # 返回第一个尝试的路径（即使不存在）
            return resource_path

        except Exception as e:
            logger_manager.info(f"[Android] 获取资源路径失败: {e}")
            # 回退到相对路径
            return os.path.join(os.path.abspath("."), relative_path)

    # 2. PyInstaller 打包环境
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    # 3. 开发环境
    return os.path.join(os.path.abspath("."), relative_path)


class ImageManager:
    """图像资源管理器，用于预加载和管理图片文件"""

    def __init__(self, image_folder='images'):
        """
        初始化图像管理器
        :param image_folder: 图片文件存放目录，默认为'images'
        """
        self.image_map = {}
        logger_manager.info(f"[ImageManager] 初始化，图片目录: {image_folder}")
        self.load_images(image_folder)
        logger_manager.info(f"[ImageManager] 加载完成，共加载 {len(self.image_map)} 张图片")
        if self.image_map:
            # 显示前5个键（用于调试）
            keys_sample = list(self.image_map.keys())[:5]
            logger_manager.info(f"[ImageManager] 图片键示例: {keys_sample}")

    def load_images(self, image_folder):
        """加载图片目录下所有支持的图像文件"""
        supported_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        image_folder_path = get_resource_path(image_folder)
        logger_manager.info(f"[ImageManager] 图片目录路径: {image_folder_path}")
        logger_manager.info(f"[ImageManager] 目录是否存在: {os.path.exists(image_folder_path)}")

        try:
            if not os.path.exists(image_folder_path):
                logger_manager.info(f"[ImageManager] 错误：图片目录不存在 - {image_folder_path}")
                return

            if not os.path.isdir(image_folder_path):
                logger_manager.info(f"[ImageManager] 错误：路径不是目录 - {image_folder_path}")
                return

            # ✅ 使用新的扫描函数
            files_info = scan_directory_properly(image_folder_path)
            logger_manager.info(f"[ImageManager] 扫描到 {len(files_info)} 个文件")

            loaded_count = 0
            for display_name, file_path in files_info:
                name, ext = os.path.splitext(display_name)

                if ext.lower() not in supported_ext:
                    continue

                # 检查文件是否真实存在（应该已经确认过了）
                if not os.path.exists(file_path):
                    logger_manager.info(f"[ImageManager] 警告：文件不存在 - {file_path}")
                    continue

                # 打开图片
                image = self.open(file_path)
                if image:
                    # 使用显示名称（去除扩展名）作为键
                    key = name.lower()
                    self.image_map[key] = image
                    loaded_count += 1

                    # 只打印前10个文件的详细信息
                    if loaded_count <= 10:
                        logger_manager.info(f"[ImageManager] #{loaded_count}: {display_name} -> key: {key}")
                else:
                    logger_manager.info(f"[ImageManager] 加载失败: {display_name}")

            logger_manager.info(f"[ImageManager] 成功加载 {loaded_count} 张图片")

        except Exception as e:
            logger_manager.info(f"[ImageManager] 图片加载失败: {str(e)}")
            import traceback
            traceback.logger_manager.info_exc()

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
            logger_manager.info(f"无法打开图片 {path}: {str(e)}")
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
            logger_manager.info(f"字体加载失败: {str(e)}")

    def _load_language_configs(self, lang_config=None):
        """加载多语言配置"""
        if lang_config is None:
            # 尝试加载默认配置文件
            default_config_path = get_resource_path('fonts/language_config.json')
            if os.path.exists(default_config_path):
                lang_config = default_config_path
            else:
                logger_manager.info("警告：未找到语言配置文件，将使用空配置")
                return

        if isinstance(lang_config, str):
            # 从JSON文件加载
            try:
                with open(get_resource_path(lang_config), 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._parse_config_data(config_data)
            except Exception as e:
                logger_manager.info(f"加载语言配置文件失败: {str(e)}")
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
                logger_manager.info(f"解析语言配置失败 {lang_data.get('name', 'unknown')}: {str(e)}")

    def set_lang(self, lang='zh'):
        """设置当前语言"""
        if lang == self.lang:
            return

        if lang in self.language_configs:
            self.lang = lang
        else:
            logger_manager.info(f"警告：未找到语言 '{lang}' 的配置，使用默认配置")
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
        # logger_manager.info(font_name,font_size)
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
        elif text_key == '密谋':
            text_key = 'agenda'
        elif text_key == '场景':
            text_key = 'act'
        elif text_key == '胜利点':
            text_key = 'victory'
        elif text_key == '升级项':
            text_key = 'upgrades'
        elif text_key == '剧情':
            text_key = 'story'
        elif text_key == '插画':
            text_key = 'Illus'
        elif text_key == '结局':
            text_key = 'resolution'
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

        logger_manager.info("默认语言配置文件已创建：language_config.json")
        return default_config
