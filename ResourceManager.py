import hashlib
import json
import os
import sys
import shutil
from collections import deque
from dataclasses import dataclass
from typing import Optional, Dict, Tuple
import time
import threading

from PIL import Image, ImageFont

from bin.logger import logger_manager
from bin.config_directory_manager import config_dir_manager


# ============================================
# 常量定义（缓存上限可调）
# ============================================
FONT_CACHE_LIMIT = 30
TEXT_BOX_CACHE_LIMIT = 500_000
TEXT_BOX_CACHE_FILE = "text_box_cache.json"
TEXT_BOX_CACHE_FLUSH_THRESHOLD = 2000
TEXT_BOX_CACHE_FLUSH_INTERVAL = 60.0


# ============================================
# dataclass 定义
# ============================================
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
# 资源路径和文件名映射
# ============================================
def get_resource_path(relative_path):
    """获取资源文件的绝对路径，适用于开发环境、PyInstaller打包和Android打包"""

    # 1. 检查是否在 Android 环境
    if 'ANDROID_ARGUMENT' in os.environ:
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

            # 方式2: 尝试直接使用相对路径
            direct_path = os.path.join(os.path.abspath("."), relative_path)
            if os.path.exists(direct_path):
                return direct_path

            # 方式3: 检查当前工作目录
            cwd_path = os.path.join(os.getcwd(), relative_path)
            if os.path.exists(cwd_path):
                return cwd_path

            return resource_path

        except Exception as e:
            logger_manager.info(f"[Android] 获取资源路径失败: {e}")
            return os.path.join(os.path.abspath("."), relative_path)

    # 2. PyInstaller 打包环境
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    # 3. 开发环境
    return os.path.join(os.path.abspath("."), relative_path)


def load_filename_mapping() -> Dict[str, Dict[str, str]]:
    """
    加载文件名翻译映射
    返回格式: {
        "images": {"中文名.png": "english-name.png"},
        "fonts": {"中文名.ttf": "english-name.ttf"}
    }
    """
    mapping_file = get_resource_path('fonts/filename_translation_mapping.json')

    if os.path.exists(mapping_file):
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
                logger_manager.info(
                    f"[映射] 成功加载文件名映射: {len(mapping.get('images', {}))} 个图片, {len(mapping.get('fonts', {}))} 个字体")
                return mapping
        except Exception as e:
            logger_manager.info(f"[映射] 加载文件名映射失败: {e}")
    else:
        logger_manager.info(f"[映射] 映射文件不存在: {mapping_file}")

    return {"images": {}, "fonts": {}}


def create_reverse_mapping(forward_mapping: Dict[str, str]) -> Dict[str, str]:
    """
    创建反向映射：去除扩展名的中文键 -> 英文文件名
    例如: "UI-伤害" -> "UI-damage.png"
    """
    reverse = {}

    for chinese_filename, english_filename in forward_mapping.items():
        # 获取中文文件名（无扩展名）
        chinese_key = os.path.splitext(chinese_filename)[0]

        # 转换为小写作为键
        key = chinese_key.lower()

        # 映射到英文文件名
        reverse[key] = english_filename

        # 同时添加英文键映射（无扩展名）
        english_key = os.path.splitext(english_filename)[0].lower()
        reverse[english_key] = english_filename

    return reverse


# ============================================
# ImageManager
# ============================================
class ImageManager:
    """图像资源管理器，用于预加载和管理图片文件"""

    def __init__(self, image_folder='images'):
        """
        初始化图像管理器
        :param image_folder: 图片文件存放目录，默认为'images'
        """
        self.image_map = {}  # 懒加载缓存：英文键 -> Image（内存副本）
        self.name_mapping = {}  # 中文键 -> 英文文件名
        self.available_images = {}  # 可用图片路径：英文键 -> 完整文件路径
        self.image_folder_path = get_resource_path(image_folder)

        # 工作目录，默认为系统图片资源路径
        self.working_directory = self.image_folder_path

        logger_manager.info(f"[ImageManager] 初始化，图片目录: {image_folder}")
        logger_manager.info(f"[ImageManager] 工作目录: {self.working_directory}")

        # 加载文件名映射
        filename_mapping = load_filename_mapping()
        self.name_mapping = create_reverse_mapping(filename_mapping.get('images', {}))
        logger_manager.info(f"[ImageManager] 文件名映射数量: {len(self.name_mapping)}")

        # 扫描可用图片（懒加载，不打开文件）
        self.scan_available_images()

        logger_manager.info(f"[ImageManager] 初始化完成，发现 {len(self.available_images)} 个可用图片文件")

    def set_working_directory(self, directory_path):
        """
        设置工作目录
        :param directory_path: 工作目录路径
        """
        if os.path.isabs(directory_path):
            # 如果是绝对路径，直接使用
            self.working_directory = directory_path
        else:
            # 如果是相对路径，相对于当前工作目录
            self.working_directory = os.path.abspath(directory_path)

        logger_manager.info(f"[ImageManager] 工作目录已设置为: {self.working_directory}")

    def get_working_directory(self):
        """
        获取当前工作目录
        :return: 工作目录路径
        """
        return self.working_directory

    def scan_available_images(self):
        """
        扫描图片目录，建立文件名到路径的映射（不打开图片文件）
        用于懒加载机制的初始化
        """
        supported_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        logger_manager.info(f"[ImageManager] 扫描图片目录: {self.image_folder_path}")

        if not os.path.exists(self.image_folder_path):
            logger_manager.info(f"[ImageManager] 错误：图片目录不存在 - {self.image_folder_path}")
            return

        try:
            files = os.listdir(self.image_folder_path)
            logger_manager.info(f"[ImageManager] 目录中的文件数: {len(files)}")

            scanned_count = 0
            for filename in files:
                name, ext = os.path.splitext(filename)

                if ext.lower() not in supported_ext:
                    continue

                file_path = os.path.join(self.image_folder_path, filename)

                if not os.path.exists(file_path):
                    continue

                # 使用小写的英文文件名（无扩展名）作为键，存储完整路径
                key = name.lower()
                self.available_images[key] = file_path
                scanned_count += 1

                # 只打印前10个
                if scanned_count <= 10:
                    logger_manager.info(f"[ImageManager] #{scanned_count}: {filename} (key: {key})")

            logger_manager.info(f"[ImageManager] 成功扫描 {scanned_count} 个图片文件")

        except Exception as e:
            logger_manager.info(f"[ImageManager] 图片扫描失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def load_images(self, image_folder):
        """
        [已废弃] 原预加载方法，现已改为懒加载机制
        保留此方法仅为兼容性，实际不再使用
        """
        supported_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        image_folder_path = get_resource_path(image_folder)
        logger_manager.info(f"[ImageManager] 图片目录路径: {image_folder_path}")

        if not os.path.exists(image_folder_path):
            logger_manager.info(f"[ImageManager] 错误：图片目录不存在 - {image_folder_path}")
            return

        try:
            # 直接列出目录（文件名已经是英文）
            files = os.listdir(image_folder_path)
            logger_manager.info(f"[ImageManager] 目录中的文件数: {len(files)}")

            loaded_count = 0
            for filename in files:
                name, ext = os.path.splitext(filename)

                if ext.lower() not in supported_ext:
                    continue

                file_path = os.path.join(image_folder_path, filename)

                if not os.path.exists(file_path):
                    continue

                # 打开图片
                image = self.open(file_path)
                if image:
                    # 使用小写的英文文件名（无扩展名）作为键
                    key = name.lower()
                    self.image_map[key] = image
                    loaded_count += 1

                    # 只打印前10个
                    if loaded_count <= 10:
                        logger_manager.info(f"[ImageManager] #{loaded_count}: {filename} (key: {key})")

            logger_manager.info(f"[ImageManager] 成功加载 {loaded_count} 张图片")

        except Exception as e:
            logger_manager.info(f"[ImageManager] 图片加载失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def open(self, path, **kwargs):
        """
        打开指定图片文件并复制到内存
        :param path: 图片路径
        :param kwargs: 传递给Image.open的额外参数
        :return: PIL.Image对象（内存副本），如果找不到返回None
        """
        try:
            with Image.open(path, **kwargs) as img:
                # 转换模式并复制到内存
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                # 复制图片到内存，确保原文件可以安全关闭
                img_copy = img.copy()
            return img_copy
        except Exception as e:
            logger_manager.info(f"[ImageManager] 无法打开图片 {path}: {str(e)}")
            return None

    def get_image(self, image_name):
        """
        获取图片（支持中文键名和英文键名）
        使用懒加载机制：首次访问时加载并缓存
        :param image_name: 图片名称（可以是中文或英文，不带扩展名）
        :return: 图片对象（内存副本）
        """
        # 转换为小写
        key = image_name.lower()

        # 方式1: 从缓存中直接返回
        if key in self.image_map:
            return self.image_map[key]

        # 方式2: 查找文件路径并懒加载
        file_path = None

        # 2.1 直接查找英文键
        if key in self.available_images:
            file_path = self.available_images[key]
        # 2.2 通过中文键查找映射的英文文件名
        elif key in self.name_mapping:
            english_filename = self.name_mapping[key]
            english_key = os.path.splitext(english_filename)[0].lower()

            if english_key in self.available_images:
                file_path = self.available_images[english_key]

        # 找到路径，懒加载图片
        if file_path:
            img = self.open(file_path)
            if img:
                # 缓存到内存
                self.image_map[key] = img
                logger_manager.info(f"[ImageManager] 懒加载图片: {image_name} (key: {key})")
                return img

        # 找不到，打印调试信息
        logger_manager.info(f"[ImageManager] 找不到图片: {image_name} (key: {key})")
        logger_manager.info(f"[ImageManager] 可用的英文键示例: {list(self.available_images.keys())[:5]}")
        logger_manager.info(f"[ImageManager] 可用的中文键示例: {list(self.name_mapping.keys())[:5]}")

        return None

    def get_image_by_src(self, src_path):
        """
        根据源路径获取图片
        :param src_path: 图片源路径
                        - 以 "@" 开头：相对于工作目录的路径，如 "@export\\饥荒DIY\\杀人蜂群_advanced_a.png"
                        - 不以 "@" 开头：绝对路径
        :return: PIL.Image对象，如果文件不存在则返回20x20的灰色矩形
        """
        # 确定实际文件路径
        if src_path.startswith('@'):
            # 相对路径：去掉 @ 符号，拼接工作目录
            relative_path = src_path[1:]  # 去掉开头的 @

            # 按分隔符分割路径（兼容 Windows 的 \ 和 Unix 的 /）
            path_parts = relative_path.replace('\\', '/').split('/')
            # 过滤掉空字符串（如开头的分隔符会产生空字符串）
            path_parts = [part for part in path_parts if part]

            # 使用 os.path.join 确保使用正确的系统分隔符
            if path_parts:
                actual_path = os.path.join(self.working_directory, *path_parts)
            else:
                # 如果路径部分为空，直接使用工作目录（通常是无效路径）
                actual_path = self.working_directory
        else:
            # 绝对路径：同样按分隔符分割并重新组合
            path_parts = src_path.replace('\\', '/').split('/')
            path_parts = [part for part in path_parts if part]

            # 如果路径部分为空，使用原始路径（让后续逻辑处理）
            if not path_parts:
                actual_path = src_path
            # 对于绝对路径，需要保留根路径
            elif src_path.startswith('/'):
                # Unix 绝对路径
                actual_path = os.path.join('/', *path_parts)
            elif ':' in path_parts[0]:
                # Windows 绝对路径（如 C:\path）
                actual_path = os.path.join(*path_parts)
            else:
                actual_path = os.path.join(*path_parts)

        # 规范化路径（处理 .. 和 . 等）
        actual_path = os.path.normpath(actual_path)

        logger_manager.info(f"[ImageManager] 尝试加载图片: {actual_path}")

        # 尝试打开图片
        if os.path.exists(actual_path):
            try:
                with Image.open(actual_path) as img:
                    # 转换为 RGBA 模式以支持透明度
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGBA')
                    # 复制到内存，确保原文件可以安全关闭
                    img_copy = img.copy()
                logger_manager.info(f"[ImageManager] 成功加载图片: {actual_path}")
                return img_copy
            except Exception as e:
                logger_manager.info(f"[ImageManager] 打开图片失败 {actual_path}: {str(e)}")
        else:
            logger_manager.info(f"[ImageManager] 图片文件不存在: {actual_path}")

        # 文件不存在或打开失败，返回默认的灰色矩形
        return self._create_default_image()

    def _create_default_image(self, width=20, height=20, color=(128, 128, 128)):
        """
        创建默认的纯色矩形图片
        :param width: 图片宽度，默认20
        :param height: 图片高度，默认20
        :param color: RGB颜色元组，默认灰色(128, 128, 128)
        :return: PIL.Image对象
        """
        img = Image.new('RGB', (width, height), color)
        logger_manager.info(f"[ImageManager] 创建默认图片: {width}x{height}, 颜色: {color}")
        return img


# ============================================
# FontManager
# ============================================
class FontManager:
    """字体管理器，用于预加载和管理字体文件"""

    def __init__(self, font_folder='fonts', lang='zh'):
        """
        初始化字体管理器
        :param font_folder: 字体文件存放目录，默认为'fonts'
        :param lang: 默认语言
        """
        self.font_map = {}  # 英文键 -> 字体文件路径
        self.name_mapping = {}  # 中文键 -> 英文文件名
        self.font_folder = get_resource_path(font_folder)
        self.additional_font_folders = []  # 额外字体目录列表
        self.language_configs = {}
        self.lang = None
        self.silence = False  # 静默模式
        self.font_cache_limit = FONT_CACHE_LIMIT
        self._font_access_counts: Dict[Tuple[str, int], int] = {}
        self._font_cache: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}
        self.text_box_cache_limit = TEXT_BOX_CACHE_LIMIT
        self._text_box_cache_file = os.path.join(config_dir_manager.get_global_config_dir(), TEXT_BOX_CACHE_FILE)
        self._text_box_cache: Dict[str, Tuple[str, int, str, int, int]] = {}
        self._text_box_order = deque()
        self._text_box_dirty = 0
        self._text_box_last_flush = 0.0
        self._text_box_saving = False
        self._text_box_lock = threading.Lock()

        logger_manager.info(f"[FontManager] 初始化，字体目录: {self.font_folder}")

        # 加载文件名映射
        filename_mapping = load_filename_mapping()
        self.name_mapping = create_reverse_mapping(filename_mapping.get('fonts', {}))
        logger_manager.info(f"[FontManager] 字体名映射数量: {len(self.name_mapping)}")
        # 加载字体文件
        self._load_fonts()
        # 加载语言配置
        self._load_language_configs()
        # 设置默认语言
        self.set_lang(lang)
        # 加载文本盒缓存
        self._load_text_box_cache()

    def add_font_folder(self, folder: str):
        """添加额外的字体目录，并重新加载字体"""
        try:
            # 允许传入绝对路径或相对路径
            if not os.path.isabs(folder):
                folder_path = os.path.abspath(folder)
            else:
                folder_path = folder

            if folder_path not in self.additional_font_folders:
                self.additional_font_folders.append(folder_path)
                logger_manager.info(f"[FontManager] 附加字体目录: {folder_path}")

            # 重新加载字体（合并所有目录）
            self._load_fonts()
        except Exception as e:
            logger_manager.info(f"[FontManager] 附加字体目录失败: {folder}: {str(e)}")

    def _load_fonts(self):
        """加载所有支持的字体文件（主目录 + 额外目录）"""
        supported_ext = ['.ttf', '.otf', '.ttc']

        # 重新构建字体映射
        self.font_map = {}

        # 主目录 + 额外目录列表
        font_dirs = [self.font_folder] + self.additional_font_folders

        try:
            loaded_count = 0
            for folder in font_dirs:
                if not os.path.exists(folder) or not os.path.isdir(folder):
                    logger_manager.info(f"[FontManager] 字体目录不存在或不可用: {folder}")
                    continue

                files = os.listdir(folder)
                logger_manager.info(f"[FontManager] 扫描字体目录: {folder}, 文件数: {len(files)}")

                for filename in files:
                    name, ext = os.path.splitext(filename)

                    if ext.lower() not in supported_ext:
                        continue

                    font_path = os.path.join(folder, filename)

                    if not os.path.exists(font_path):
                        continue

                    # 使用小写的英文文件名（无扩展名）作为键
                    key = name.lower()
                    # 后扫描的目录可以覆盖之前的同名键
                    self.font_map[key] = font_path
                    loaded_count += 1

                    logger_manager.info(f"[FontManager] #{loaded_count}: {filename} (key: {key}) 来自 {folder}")

            logger_manager.info(f"[FontManager] 成功加载 {loaded_count} 个字体")
            if self.font_map:
                logger_manager.info(f"[FontManager] 字体键列表: {list(self.font_map.keys())}")

        except Exception as e:
            logger_manager.info(f"[FontManager] 字体加载失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def get_available_font_display_names(self):
        """获取当前已加载字体的显示名称列表

        优先使用文件名映射中的中文逻辑名；对未映射或用户自定义字体，
        使用实际文件名（不含扩展名）。
        """

        try:
            filename_mapping = load_filename_mapping()
            font_mapping = filename_mapping.get('fonts', {})

            english_to_display = {}
            for cn_filename, en_filename in font_mapping.items():
                cn_base = os.path.splitext(cn_filename)[0]
                en_base = os.path.splitext(en_filename)[0]
                english_to_display[en_base.lower()] = cn_base

            display_names = set()

            for font_path in self.font_map.values():
                base_name = os.path.splitext(os.path.basename(font_path))[0]
                key = base_name.lower()
                display_name = english_to_display.get(key, base_name)
                display_names.add(display_name)

            return sorted(display_names)
        except Exception as e:
            logger_manager.info(f"[FontManager] 获取可用字体显示名失败: {e}")
            fallback = set()
            for font_path in self.font_map.values():
                base_name = os.path.splitext(os.path.basename(font_path))[0]
                fallback.add(base_name)
            return sorted(fallback)

    def _load_language_configs(self, lang_config=None):
        """加载多语言配置

        优先使用用户配置目录下的 language_config.json，当不存在或不可用时
        回退到内置的 fonts/language_config.json，确保渲染始终有可用配置。
        """
        # 先清空现有配置，避免重复加载产生脏数据
        self.language_configs = {}

        # 默认与用户配置路径
        default_config_path = get_resource_path('fonts/language_config.json')
        user_config_path = config_dir_manager.get_language_config_file_path()

        # 未显式指定时，按“用户优先”的策略选择配置文件
        if lang_config is None:
            candidate_path = None

            # 1. 用户配置已存在，直接使用
            if os.path.exists(user_config_path):
                candidate_path = user_config_path
            # 2. 用户配置不存在但有默认模板，复制一份作为用户配置
            elif os.path.exists(default_config_path):
                try:
                    os.makedirs(os.path.dirname(user_config_path), exist_ok=True)
                    shutil.copy2(default_config_path, user_config_path)
                    logger_manager.info(
                        f"[FontManager] 已从默认模板创建用户语言配置: {user_config_path}")
                    candidate_path = user_config_path
                except Exception as e:
                    logger_manager.info(
                        f"[FontManager] 创建用户语言配置失败，将直接使用默认配置: {e}")
                    candidate_path = default_config_path
            # 3. 两者都不存在，只能使用空配置
            else:
                logger_manager.info("警告：未找到任何语言配置文件，将使用空配置")
                return

            lang_config = candidate_path

        # 根据类型加载配置
        if isinstance(lang_config, str):
            # 从 JSON 文件加载
            try:
                with open(lang_config, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._parse_config_data(config_data)
            except Exception as e:
                logger_manager.info(f"加载语言配置文件失败: {str(e)}")
        elif isinstance(lang_config, list):
            # 从列表加载
            self._parse_config_data(lang_config)

        # 若当前配置为空，尝试回退到默认配置，确保渲染可用
        if not self.language_configs and os.path.exists(default_config_path):
            try:
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._parse_config_data(config_data)
                    logger_manager.info("[FontManager] 用户语言配置不可用，已回退到默认配置")
            except Exception as e:
                logger_manager.info(f"加载默认语言配置文件失败: {str(e)}")

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
        """根据字体类型获取语言配置的字体信息"""
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
        return FontInfo(name=font_type)

    def get_font(self, font_name: str, size: int = 20) -> Optional[ImageFont.FreeTypeFont]:
        """
        获取指定字体和大小的字体对象
        :param font_name: 字体名称（可以是中文或英文）
        :param size: 字体大小
        :return: PIL.ImageFont对象，如果找不到返回None
        """
        font_key = (font_name.lower(), size)
        font_path = self.get_font_path(font_name)

        if font_path is None:
            return None

        self._font_access_counts[font_key] = self._font_access_counts.get(font_key, 0) + 1

        if font_key in self._font_cache:
            logger_manager.info(f"[FontManager] 缓存命中 {font_name} (大小: {size})")
            return self._font_cache[font_key]

        try:
            font_obj = ImageFont.truetype(font_path, size)
            self._maybe_cache_font(font_key, font_obj)
            return font_obj
        except Exception as e:
            if not self.silence:
                logger_manager.info(f"[FontManager] 无法加载字体 {font_name} (大小: {size}): {str(e)}")
            return None

    def _maybe_cache_font(self, font_key: Tuple[str, int], font_obj: ImageFont.FreeTypeFont):
        """记录访问后，将高频字体加入缓存并控制容量"""
        if self.font_cache_limit <= 0:
            return

        current_count = self._font_access_counts.get(font_key, 0)

        if font_key in self._font_cache:
            self._font_cache[font_key] = font_obj
            return

        if len(self._font_cache) < self.font_cache_limit:
            self._font_cache[font_key] = font_obj
            return

        # 找出当前缓存中的最低访问次数，只有达到前 N 才加入
        min_key = min(self._font_cache, key=lambda k: self._font_access_counts.get(k, 0))
        min_count = self._font_access_counts.get(min_key, 0)
        if current_count < min_count:
            return

        self._font_cache[font_key] = font_obj

        if len(self._font_cache) > self.font_cache_limit:
            sorted_keys = sorted(self._font_cache, key=lambda k: self._font_access_counts.get(k, 0))
            for candidate in sorted_keys:
                if len(self._font_cache) <= self.font_cache_limit:
                    break
                if candidate == font_key:
                    continue
                self._font_cache.pop(candidate, None)

            # 若仍超限（可能全部键相同计数），移除一个最低计数的键
            if len(self._font_cache) > self.font_cache_limit:
                extra = sorted(self._font_cache, key=lambda k: self._font_access_counts.get(k, 0))[0]
                if extra != font_key:
                    self._font_cache.pop(extra, None)

    def get_font_path(self, font_name: str) -> Optional[str]:
        """
        获取字体文件路径（支持中文键名和英文键名）
        :param font_name: 字体名称（可以是中文或英文）
        :return: 字体文件路径，如果找不到返回None
        """
        # 转换为小写
        key = font_name.lower()

        # 方式1: 直接查找英文键
        if key in self.font_map:
            return self.font_map[key]

        # 方式2: 通过中文键查找映射的英文文件名
        if key in self.name_mapping:
            english_filename = self.name_mapping[key]
            english_key = os.path.splitext(english_filename)[0].lower()

            if english_key in self.font_map:
                return self.font_map[english_key]

        # 找不到
        if not self.silence:
            logger_manager.info(f"[FontManager] 找不到字体: {font_name} (key: {key})")
            logger_manager.info(f"[FontManager] 可用的英文键: {list(self.font_map.keys())}")
            logger_manager.info(f"[FontManager] 可用的中文键: {list(self.name_mapping.keys())}")

        return None

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
        """
        if self.silence:
            return ''

        config = self.get_current_config()
        if not config:
            return text_key  # 如果没有配置，返回原始文本

        # 特殊字符处理
        if text_key == '：' or text_key == '。':
            if self.lang not in ['zh', 'zh-CHT']:
                if text_key == '：':
                    return ': '
                elif text_key == '。':
                    return '.'
            return text_key

        # 文本键映射
        text_key_mapping = {
            '技能': 'skill',
            '地点': 'location',
            '事件': 'event',
            '支援': 'asset',
            '诡计': 'treachery',
            '敌人': 'enemy',
            '弱点': 'weakness',
            '基础弱点': 'basic_weakness',
            '牌库卡牌张数': 'deck_size',
            '牌库构筑选项': 'deck_options',
            '牌库构筑需求': 'deck_requirements',
            '不计入卡牌张数': 'not_count',
            '密谋': 'agenda',
            '场景': 'act',
            '胜利点': 'victory',
            '升级项': 'upgrades',
            '剧情': 'story',
            '插画': 'Illus',
            '结局': 'resolution'
        }

        # 如果有映射，使用映射后的键
        mapped_key = text_key_mapping.get(text_key, text_key)

        return getattr(config.texts, mapped_key, text_key)

    def get_available_languages(self):
        """获取可用的语言列表"""
        return list(self.language_configs.keys())

    # ==================== 文本盒缓存 ====================
    def _build_text_box_key(self, font_name: str, font_size: int, text: str) -> str:
        """使用字体名+字号+文本构建哈希键，避免长文本占用空间"""
        base = f"{font_name}\u0001{font_size}\u0001{text}"
        return hashlib.md5(base.encode('utf-8')).hexdigest()

    def _store_text_box_cache_entry(self, key_hash: str, font_name: str, font_size: int,
                                    text: str, width: int, height: int):
        """存储文本盒缓存，维持容量并按阈值落盘"""
        entry = (font_name, int(font_size), text, int(width), int(height))
        with self._text_box_lock:
            if key_hash in self._text_box_cache:
                self._text_box_cache[key_hash] = entry
                self._text_box_order = deque(k for k in self._text_box_order if k != key_hash)
            else:
                self._text_box_cache[key_hash] = entry
            self._text_box_order.append(key_hash)
            self._text_box_dirty += 1

            while len(self._text_box_cache) > self.text_box_cache_limit and self._text_box_order:
                old_key = self._text_box_order.popleft()
                if old_key == key_hash and len(self._text_box_cache) <= self.text_box_cache_limit:
                    break
                self._text_box_cache.pop(old_key, None)

        self._maybe_flush_text_box_cache()

    def _load_text_box_cache(self):
        """从磁盘加载文本盒缓存"""
        try:
            if not os.path.exists(self._text_box_cache_file):
                return
            with open(self._text_box_cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            records = data.get("m", {})
            if not isinstance(records, dict):
                return
            for key_hash, value in records.items():
                if not isinstance(value, list) or len(value) < 5:
                    continue
                font_name, font_size, text, width, height = value[:5]
                self._text_box_cache[key_hash] = (
                    str(font_name),
                    int(font_size),
                    str(text),
                    int(width),
                    int(height)
                )
                self._text_box_order.append(key_hash)

            while len(self._text_box_cache) > self.text_box_cache_limit and self._text_box_order:
                old_key = self._text_box_order.popleft()
                self._text_box_cache.pop(old_key, None)
        except Exception as e:
            logger_manager.info(f"[FontManager] 加载文本盒缓存失败: {e}")

    def _save_text_box_cache(self, snapshot: Optional[Dict[str, Tuple[str, int, str, int, int]]] = None,
                             update_state: bool = True):
        """将文本盒缓存持久化为紧凑 JSON（单字母字段名，无缩进），可传入快照异步写入"""
        try:
            cache_data = snapshot if snapshot is not None else self._text_box_cache
            os.makedirs(os.path.dirname(self._text_box_cache_file), exist_ok=True)
            data = {
                "v": 1,
                "m": {k: [v[0], v[1], v[2], v[3], v[4]] for k, v in cache_data.items()}
            }
            with open(self._text_box_cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            if update_state:
                self._text_box_dirty = 0
                self._text_box_last_flush = time.time()
        except Exception as e:
            logger_manager.info(f"[FontManager] 保存文本盒缓存失败: {e}")
            # 失败不清零脏计数，便于下次继续尝试

    def _maybe_flush_text_box_cache(self, force: bool = False):
        """按阈值/时间节流写盘，采用异步写入避免阻塞渲染线程"""
        now = time.time()
        with self._text_box_lock:
            if not force:
                if self._text_box_dirty < TEXT_BOX_CACHE_FLUSH_THRESHOLD:
                    return
                if (now - self._text_box_last_flush) < TEXT_BOX_CACHE_FLUSH_INTERVAL:
                    return

            if self._text_box_saving:
                return

            snapshot = dict(self._text_box_cache)
            snapshot_dirty = self._text_box_dirty
            snapshot_time = self._text_box_last_flush
            self._text_box_saving = True

        def _save_async():
            try:
                self._save_text_box_cache(snapshot, update_state=False)
                with self._text_box_lock:
                    if self._text_box_dirty <= snapshot_dirty:
                        self._text_box_last_flush = time.time()
                    self._text_box_dirty = max(0, self._text_box_dirty - snapshot_dirty)
            finally:
                self._text_box_saving = False

        threading.Thread(target=_save_async, daemon=True).start()

    def get_text_box(self, text: str, font: ImageFont.FreeTypeFont,
                     font_name: Optional[str] = None) -> Tuple[int, int]:
        """
        获取文本 bbox 宽高，带缓存与持久化
        :param text: 文本内容
        :param font: 已加载的字体对象
        :param font_name: 字体名称（可选，用于稳定缓存键）
        :return: (宽度, 高度)
        """
        if font is None or text is None:
            return 0, 0

        resolved_font_name = font_name or (font.getname()[0] if hasattr(font, "getname") else "")
        font_size = getattr(font, "size", 0)
        key_hash = self._build_text_box_key(resolved_font_name, font_size, text)

        cached = self._text_box_cache.get(key_hash)
        if cached:
            return cached[3], cached[4]

        try:
            bbox = font.getbbox(text)
            width = int(bbox[2] - bbox[0])
            height = int(bbox[3] - bbox[1])
        except Exception as e:
            if not self.silence:
                logger_manager.info(f"[FontManager] 计算文本盒失败: {e}")
            return 0, 0

        self._store_text_box_cache_entry(key_hash, resolved_font_name, font_size, text, width, height)
        return width, height

    def flush_text_box_cache(self, force: bool = False):
        """外部可调用，主动刷新文本盒缓存到磁盘（异步写入）"""
        self._maybe_flush_text_box_cache(force=force)
