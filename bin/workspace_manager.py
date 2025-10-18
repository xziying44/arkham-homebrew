import base64
import io
import json
import mimetypes
import os
import sys
import threading
import time
import traceback
from typing import List, Dict, Any, Optional, Union

from PIL import Image

from Card import Card
from bin.deck_exporter import DeckExporter
from bin.logger import logger_manager
from bin.tts_card_converter import TTSCardConverter
from bin.content_package_manager import ContentPackageManager

# 导入卡牌生成相关模块
try:
    from ResourceManager import FontManager, ImageManager
    from create_card import CardCreator

    CARD_GENERATION_AVAILABLE = True
except ImportError:
    CARD_GENERATION_AVAILABLE = False
    print("警告: 无法导入卡牌生成模块，卡牌生成功能将不可用")


class WorkspaceManager:
    """工作空间管理类，负责文件和目录操作"""

    # 系统配置字段定义 - 这些字段会保存到全局配置文件中
    SYSTEM_CONFIG_FIELDS = [
        "github_token",  # GitHub访问令牌
        "github_repo",  # GitHub仓库名
        "github_branch",  # GitHub分支名
        "github_folder",  # GitHub文件夹
        "language",  # 界面语言
        "first_visit_completed",  # 首次访问是否完成
        # Cloudinary图床配置
        "cloud_name",  # Cloudinary云名称
        "api_key",  # Cloudinary API密钥
        "api_secret",  # Cloudinary API密钥
        "folder",  # Cloudinary自定义上传目录
        # ImgBB图床配置
        "imgbb_api_key",  # ImgBB API密钥
        "imgbb_expiration",  # ImgBB图片过期时间
        # 可以在这里添加更多系统级配置字段
    ]

    # 工作空间配置字段定义 - 这些字段会保存到工作空间的config.json中
    WORKSPACE_CONFIG_FIELDS = [
        "encounter_groups_dir",  # 遭遇组目录
        "footer_copyright",  # 页脚版权信息
        "footer_icon_dir",  # 页脚图标目录
        # 可以在这里添加更多工作空间级配置字段
    ]

    def __init__(self, workspace_path: str):
        if not os.path.exists(workspace_path):
            raise ValueError(f"工作目录不存在: {workspace_path}")
        if not os.path.isdir(workspace_path):
            raise ValueError(f"指定路径不是目录: {workspace_path}")

        self.workspace_path = os.path.abspath(workspace_path)

        # 初始化卡牌生成相关管理器
        if CARD_GENERATION_AVAILABLE:
            try:
                fonts_path = os.path.join(self.workspace_path, 'fonts')
                images_path = os.path.join(self.workspace_path, 'images')

                # 如果fonts和images目录不存在，尝试查找或使用默认路径
                if not os.path.exists(fonts_path):
                    fonts_path = 'fonts'  # 使用相对路径
                if not os.path.exists(images_path):
                    images_path = 'images'  # 使用相对路径

                app_mode = os.environ.get('APP_MODE', 'normal')

                self.font_manager = FontManager(fonts_path)
                self.image_manager = ImageManager(images_path)
                self.creator = CardCreator(
                    font_manager=self.font_manager,
                    image_manager=self.image_manager,
                    image_mode=0 if app_mode == 'normal' else 1
                )

            except Exception as e:
                print(f"初始化字体和图像管理器失败: {e}")
                self.font_manager = None
                self.image_manager = None
        else:
            self.font_manager = None
            self.image_manager = None

        self.config = self.get_config()
        # 初始化牌库导出器
        self.deck_exporter = DeckExporter(self)

        self._export_helper = None
        self._export_params_hash = None
        self.card_lock = threading.Lock()

    def _get_relative_path(self, absolute_path: str) -> str:
        """将绝对路径转换为相对于工作目录的相对路径"""
        try:
            return os.path.relpath(absolute_path, self.workspace_path)
        except Exception:
            return absolute_path

    def _get_absolute_path(self, relative_path: str) -> str:
        """将相对路径转换为绝对路径"""
        if os.path.isabs(relative_path):
            return relative_path
        return os.path.join(self.workspace_path, relative_path)

    def _is_path_in_workspace(self, path: str) -> bool:
        """检查路径是否在工作目录内"""
        abs_path = self._get_absolute_path(path)
        return abs_path.startswith(self.workspace_path)

    def _get_file_type(self, file_path: str) -> str:
        """根据文件扩展名确定文件类型"""
        ext = os.path.splitext(file_path)[1].lower()

        type_mapping = {
            '.card': 'card',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.gif': 'image',
            '.svg': 'image',
            '.bmp': 'image',
            '.webp': 'image',
            '.tiff': 'image',
            '.ico': 'image',
            '.json': 'config',
            '.xml': 'data',
            '.css': 'style',
            '.txt': 'text',
            '.md': 'text',
            '.yml': 'config',
            '.yaml': 'config',
        }

        return type_mapping.get(ext, 'file')

    def _is_image_file(self, file_path: str) -> bool:
        """检查是否是图片文件"""
        return self._get_file_type(file_path) == 'image'

    def _get_type_priority(self, item_type: str) -> int:
        """获取类型优先级，数字越小优先级越高"""
        type_priorities = {
            'directory': 0,  # 目录最优先
            'card': 1,
            'image': 2,
            'config': 3,
            'text': 4,
            'style': 5,
            'data': 6,
            'file': 7,  # 其他文件类型最低优先级
        }
        return type_priorities.get(item_type, 99)

    def _sort_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对文件和目录进行排序：先按类型，再按名称"""

        def sort_key(item):
            # 第一排序键：类型优先级
            type_priority = self._get_type_priority(item.get('type', 'file'))
            # 第二排序键：文件名（不区分大小写）
            name = item.get('label', '').lower()
            return (type_priority, name)

        return sorted(items, key=sort_key)

    def _build_tree_recursive(self, path: str, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """递归构建目录树"""
        items = []

        try:
            for item in os.listdir(path):
                if not include_hidden and item.startswith('.'):
                    continue

                item_path = os.path.join(path, item)
                # 获取相对于工作目录的相对路径
                relative_path = self._get_relative_path(item_path)
                item_key = f"{relative_path}_{int(time.time() * 1000000)}"  # 使用相对路径+时间戳生成唯一key

                if os.path.isdir(item_path):
                    # 处理目录，递归获取子项并排序
                    children = self._build_tree_recursive(item_path, include_hidden)
                    children = self._sort_items(children)  # 对子项进行排序

                    items.append({
                        'label': item,
                        'key': item_key,
                        'type': 'directory',
                        'path': relative_path,  # 使用相对路径
                        'children': children
                    })

                elif os.path.isfile(item_path):
                    # 处理文件
                    items.append({
                        'label': item,
                        'key': item_key,
                        'type': self._get_file_type(item),
                        'path': relative_path  # 使用相对路径
                    })

        except PermissionError:
            # 如果没有权限访问目录，跳过
            pass
        except Exception as e:
            print(f"构建目录树失败 {path}: {e}")

        # 对当前级别的项目进行排序
        return self._sort_items(items)

    def get_file_tree(self, include_hidden: bool = False) -> Dict[str, Any]:
        """获取工作目录的文件树结构"""
        try:
            workspace_name = os.path.basename(self.workspace_path) or self.workspace_path
            children = self._build_tree_recursive(self.workspace_path, include_hidden)

            # 返回工作空间根节点
            return {
                'label': workspace_name,
                'key': f"workspace_{int(time.time() * 1000000)}",
                'type': 'workspace',
                'path': '.',  # 工作目录使用相对路径 '.'
                'children': children
            }

        except Exception as e:
            print(f"获取文件树失败: {e}")
            return {
                'label': 'Error',
                'key': 'error',
                'type': 'error',
                'path': '.',
                'children': []
            }

    def create_directory(self, dir_name: str, parent_path: Optional[str] = None) -> bool:
        """创建目录"""
        try:
            if parent_path:
                # 确保parent_path在工作目录内
                if not self._is_path_in_workspace(parent_path):
                    return False
                target_path = self._get_absolute_path(os.path.join(parent_path, dir_name))
            else:
                target_path = os.path.join(self.workspace_path, dir_name)

            os.makedirs(target_path, exist_ok=True)
            return True

        except Exception as e:
            print(f"创建目录失败: {e}")
            return False

    def create_file(self, file_name: str, content: str = "", parent_path: Optional[str] = None) -> bool:
        """创建文件"""
        try:
            if parent_path:
                # 确保parent_path在工作目录内
                if not self._is_path_in_workspace(parent_path):
                    return False
                target_path = self._get_absolute_path(os.path.join(parent_path, file_name))
            else:
                target_path = os.path.join(self.workspace_path, file_name)

            # 确保父目录存在
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        except Exception as e:
            print(f"创建文件失败: {e}")
            return False

    def rename_item(self, old_path: str, new_name: str) -> bool:
        """重命名文件或目录"""
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(old_path):
                return False

            abs_old_path = self._get_absolute_path(old_path)
            if not os.path.exists(abs_old_path):
                return False

            parent_dir = os.path.dirname(abs_old_path)
            new_path = os.path.join(parent_dir, new_name)

            if os.path.exists(new_path):
                return False  # 目标名称已存在

            os.rename(abs_old_path, new_path)
            return True

        except Exception as e:
            print(f"重命名失败: {e}")
            return False

    def delete_item(self, item_path: str) -> bool:
        """删除文件或目录"""
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(item_path):
                return False

            abs_item_path = self._get_absolute_path(item_path)
            if not os.path.exists(abs_item_path):
                return False

            if os.path.isfile(abs_item_path):
                os.remove(abs_item_path)
            elif os.path.isdir(abs_item_path):
                import shutil
                shutil.rmtree(abs_item_path)

            return True

        except Exception as e:
            print(f"删除失败: {e}")
            return False

    def get_file_content(self, file_path: str) -> Optional[str]:
        """获取文本文件内容"""
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(file_path):
                print(f"❌ 路径不在工作目录内: {file_path}")
                return None

            abs_file_path = self._get_absolute_path(file_path)
            print(f"📄 获取文件内容: {abs_file_path}")
            print(f"   - 文件是否存在: {os.path.exists(abs_file_path)}")
            print(f"   - 是否为文件: {os.path.isfile(abs_file_path)}")

            if not os.path.isfile(abs_file_path):
                print(f"❌ 文件不存在或不是文件")
                return None

            # 尝试以不同编码读取文件
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
            last_error = None

            for encoding in encodings:
                try:
                    with open(abs_file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    print(f"✅ 使用 {encoding} 编码成功读取文件")
                    return content
                except UnicodeDecodeError as e:
                    last_error = e
                    print(f"⚠️  使用 {encoding} 编码失败: {str(e)[:50]}")
                    continue

            print(f"❌ 所有编码尝试失败，最后错误: {last_error}")
            return None

        except Exception as e:
            print(f"❌ 读取文件内容失败: {e}")
            traceback.print_exc()
            return None

    def get_image_as_base64(self, image_path: str) -> Optional[str]:
        """
        获取图片文件并转换为base64格式

        Args:
            image_path: 图片文件相对路径

        Returns:
            str: base64格式的图片数据（包含data URL前缀），失败时返回None
        """
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(image_path):
                return None

            abs_image_path = self._get_absolute_path(image_path)
            if not os.path.isfile(abs_image_path):
                return None

            # 检查是否是图片文件
            if not self._is_image_file(abs_image_path):
                return None

            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(abs_image_path)
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/png'  # 默认MIME类型

            # 读取图片文件的二进制数据
            with open(abs_image_path, 'rb') as f:
                image_data = f.read()

            # 转换为base64
            base64_data = base64.b64encode(image_data).decode('utf-8')

            # 返回完整的data URL
            return f"data:{mime_type};base64,{base64_data}"

        except Exception as e:
            print(f"读取图片文件失败: {e}")
            return None

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息

        Args:
            file_path: 文件相对路径

        Returns:
            dict: 文件信息，包含type、size、modified等
        """
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(file_path):
                return None

            abs_file_path = self._get_absolute_path(file_path)
            if not os.path.exists(abs_file_path):
                return None

            stat_info = os.stat(abs_file_path)
            file_type = self._get_file_type(abs_file_path)

            return {
                'path': file_path,  # 返回相对路径
                'type': file_type,
                'is_file': os.path.isfile(abs_file_path),
                'is_directory': os.path.isdir(abs_file_path),
                'is_image': self._is_image_file(abs_file_path),
                'size': stat_info.st_size,
                'modified': stat_info.st_mtime,
                'modified_formatted': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat_info.st_mtime))
            }

        except Exception as e:
            print(f"获取文件信息失败: {e}")
            return None

    def save_file_content(self, file_path: str, content: str) -> bool:
        """保存文件内容"""
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(file_path):
                return False

            abs_file_path = self._get_absolute_path(file_path)

            # 确保父目录存在
            os.makedirs(os.path.dirname(abs_file_path), exist_ok=True)

            with open(abs_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        except Exception as e:
            print(f"保存文件内容失败: {e}")
            return False

    def get_card_base64(self, json_data: Dict[str, Any]) -> Union[str, Image.Image, None]:
        """
        获取卡牌的base64图片数据

        Args:
            json_data: 卡牌数据的JSON字典

        Returns:
            str: base64格式的图片数据（包含data URL前缀），失败时返回None
        """
        # 获取图片路径
        picture_path = json_data.get('picture_path', None)

        # 检查 picture_base64 字段
        picture_base64 = json_data.get('picture_base64', '')

        if picture_base64 and picture_base64.strip():
            try:
                # 解码base64数据
                if picture_base64.startswith('data:image/'):
                    # 去掉data URL前缀
                    base64_data = picture_base64.split(',', 1)[1]
                else:
                    base64_data = picture_base64

                image_data = base64.b64decode(base64_data)
                # 2. 将二进制数据读入一个内存中的字节流对象
                image_stream = io.BytesIO(image_data)
                # 3. 使用 PIL 的 Image.open() 从字节流中打开图片
                picture_path = Image.open(image_stream)
            except Exception as e:
                print(f"解码base64图片数据失败: {e}")
                return None
        # 如果picture_path是相对路径，转换为绝对路径
        elif picture_path and not os.path.isabs(picture_path):
            full_picture_path = self._get_absolute_path(picture_path)
            if os.path.exists(full_picture_path):
                picture_path = full_picture_path
        return picture_path

    def generate_card_image(self, json_data: Dict[str, Any], silence=False):
        """
        生成卡图

        Args:
            json_data: 卡牌数据的JSON字典

        Returns:
            Card对象，如果生成失败返回None
        """
        if not CARD_GENERATION_AVAILABLE:
            print("卡牌生成功能不可用：缺少必要的模块")
            return None

        if not self.font_manager or not self.image_manager:
            print("字体或图像管理器未初始化")
            return None

        try:
            # 检查是否为卡背类型
            card_type = json_data.get('type', '')
            cardback_filename = None
            if card_type == '玩家卡背':
                # 生成玩家卡背
                cardback_filename = 'cardback/player-back.jpg'
            elif card_type == '遭遇卡背':
                # 生成遭遇卡背
                cardback_filename = 'cardback/encounter-back.jpg'
            if cardback_filename:
                cardback_path = os.path.join('.', cardback_filename)
                # 如果是PyInstaller打包的程序
                if hasattr(sys, '_MEIPASS'):
                    cardback_path = os.path.join(sys._MEIPASS, cardback_filename)

                if os.path.exists(cardback_path):
                    # 创建Card对象并设置图片
                    cardback_pil = Image.open(cardback_path)
                    card = Card(cardback_pil.width, cardback_pil.height, image=cardback_pil)
                    card.image = cardback_pil
                    return card
                else:
                    print(f"遭遇卡背图片不存在: {cardback_path}")
                    return None

            # 检测卡牌语言
            language = json_data.get('language', 'zh')
            self.font_manager.set_lang(language)

            with self.card_lock:
                # 调用process_card_json生成卡牌
                if silence:
                    card = self.creator.create_card_bottom_map(
                        json_data,
                        picture_path=self.get_card_base64(json_data)
                    )
                else:
                    card = self.creator.create_card(
                        json_data,
                        picture_path=self.get_card_base64(json_data)
                    )

            # 检测是否有遭遇组
            encounter_group = json_data.get('encounter_group', None)
            encounter_groups_dir = self.config.get('encounter_groups_dir', None)
            if encounter_group and encounter_groups_dir:
                # 获取遭遇组图片路径
                encounter_group_picture_path = self._get_absolute_path(
                    os.path.join(encounter_groups_dir, encounter_group + '.png')
                )
                print(f"获取遭遇组图片路径: {encounter_group_picture_path}")
                # 检查路径是否存在
                if os.path.exists(encounter_group_picture_path):
                    card.set_encounter_icon(Image.open(encounter_group_picture_path))

            # 画页脚
            if not silence:
                illustrator = json_data.get('illustrator', '')
                footer_copyright = json_data.get('footer_copyright', '')
                if (footer_copyright and footer_copyright == '') or not footer_copyright:
                    footer_copyright = self.config.get('footer_copyright', '')

                encounter_group_number = json_data.get('encounter_group_number', '')
                card_number = json_data.get('card_number', '')
                footer_icon_name = self.config.get('footer_icon_dir', '')
                footer_icon_font = json_data.get('footer_icon_font', '')
                if footer_icon_font == '':
                    footer_icon = None
                    if footer_icon_name:
                        footer_icon_path = self._get_absolute_path(footer_icon_name)
                        if os.path.exists(footer_icon_path):
                            footer_icon = Image.open(footer_icon_path)

                    card.set_footer_information(
                        illustrator,
                        footer_copyright,
                        encounter_group_number,
                        card_number,
                        footer_icon=footer_icon
                    )
                else:
                    card.set_footer_information(
                        illustrator,
                        footer_copyright,
                        encounter_group_number,
                        card_number,
                        footer_icon_font=footer_icon_font
                    )
            return card

        except Exception as e:
            # 打印异常栈
            logger_manager.exception(e)
            print(f"生成卡图失败: {e}")
            return None

    def generate_double_sided_card_image(self, json_data: Dict[str, Any], silence: bool = False):
        """
        生成双面卡图

        Args:
            json_data: 卡牌数据的JSON字典
            silence: 是否静默模式

        Returns:
            dict: 包含正面和背面卡牌的字典，格式为 {'front': card, 'back': card}
        """
        try:
            # 生成正面卡牌
            front_card = self.generate_card_image(json_data, silence)
            if front_card is None:
                print("生成正面卡牌失败")
                return None

            # 获取背面数据
            back_data = json_data.get('back', {})
            if not back_data:
                print("双面卡牌缺少背面数据")
                return {
                    'front': front_card,
                    'back': None
                }

            # 为背面数据复制一些必要字段（从正面继承）
            back_json_data = back_data.copy()
            # 继承正面的语言设置
            back_json_data['language'] = json_data.get('language', 'zh')
            # 继承其他必要字段
            if 'version' not in back_json_data:
                back_json_data['version'] = json_data.get('version', '2.0')

            # 生成背面卡牌
            back_card = self.generate_card_image(back_json_data, silence)
            if back_card is None:
                print("生成背面卡牌失败")
                return {
                    'front': front_card,
                    'back': None
                }

            return {
                'front': front_card,
                'back': back_card
            }

        except Exception as e:
            print(f"生成双面卡图失败: {e}")
            traceback.print_exc()
            return None

    def resolve_reference_card(self, json_data: Dict[str, Any], allow_reference: bool = True) -> Dict[str, Any]:
        """
        解析引用卡牌

        Args:
            json_data: 卡牌数据的JSON字典
            allow_reference: 是否允许解析引用（防止无限引用）

        Returns:
            dict: 解析后的卡牌数据
        """
        try:
            card_type = json_data.get('type', '')

            # 检查是否为引用类型
            if card_type == '引用卡牌' and allow_reference:
                reference_path = json_data.get('reference_path', '')
                reference_side = json_data.get('reference_side', 'front')

                if not reference_path:
                    print("引用卡牌缺少引用地址")
                    return json_data

                # 确保路径在工作目录内
                if not self._is_path_in_workspace(reference_path):
                    print(f"引用路径不在工作目录内: {reference_path}")
                    return json_data

                # 读取引用的卡牌文件
                abs_reference_path = self._get_absolute_path(reference_path)
                if not os.path.exists(abs_reference_path):
                    print(f"引用的卡牌文件不存在: {reference_path}")
                    return json_data

                with open(abs_reference_path, 'r', encoding='utf-8') as f:
                    referenced_card_data = json.load(f)

                # 检查引用目标卡牌的版本
                referenced_version = referenced_card_data.get('version', '')

                if referenced_version == '2.0':
                    # 版本2.0，需要区分正面和反面
                    if reference_side == 'back':
                        # 使用背面数据
                        if 'back' in referenced_card_data:
                            # 复制背面数据，但保持当前卡牌的一些基本属性
                            result_data = referenced_card_data['back'].copy()
                            result_data['language'] = json_data.get('language',
                                                                    referenced_card_data.get('language', 'zh'))
                            result_data['version'] = referenced_version
                            return result_data
                        else:
                            print("引用的卡牌没有背面数据")
                            return json_data
                    else:
                        # 使用正面数据（默认）
                        result_data = referenced_card_data.copy()
                        # 移除背面数据，因为我们只需要正面
                        if 'back' in result_data:
                            del result_data['back']
                        return result_data
                else:
                    # 非2.0版本，直接使用整个数据
                    return referenced_card_data
            else:
                # 非引用类型或不允许引用，直接返回原数据
                return json_data

        except Exception as e:
            print(f"解析引用卡牌失败: {e}")
            return json_data

    def save_card_image(self, json_data: Dict[str, Any], filename: str, parent_path: Optional[str] = None) -> bool:
        """
        保存卡图到文件

        Args:
            json_data: 卡牌数据的JSON字典
            filename: 保存的文件名（包含扩展名）
            parent_path: 保存的父目录相对路径，如果为None则保存到工作目录

        Returns:
            bool: 保存是否成功
        """
        try:
            # 生成卡图
            card_image = self.generate_card_image(json_data).image
            if card_image is None:
                return False

            # 确定保存路径
            if parent_path:
                # 确保parent_path在工作目录内
                if not self._is_path_in_workspace(parent_path):
                    return False
                save_path = self._get_absolute_path(os.path.join(parent_path, filename))
            else:
                save_path = os.path.join(self.workspace_path, filename)

            # 确保父目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # 保存图片
            card_image.save(save_path)

            print(f"卡图已保存到: {self._get_relative_path(save_path)}")
            return True

        except Exception as e:
            print(f"保存卡图失败: {e}")
            return False

    def save_card_image_enhanced(self, json_data: Dict[str, Any], filename: str,
                               parent_path: Optional[str] = None, export_format: str = 'JPG',
                               quality: int = 95, rotate_landscape: bool = False) -> List[str]:
        """
        保存卡图到文件（增强版：支持双面卡牌、格式选择、质量设置和横向图片旋转）

        Args:
            json_data: 卡牌数据的JSON字典
            filename: 保存的文件名（不包含扩展名）
            parent_path: 保存的父目录相对路径，如果为None则保存到工作目录
            export_format: 导出格式（PNG或JPG），默认JPG
            quality: 图片质量（1-100），仅对JPG有效，默认95
            rotate_landscape: 是否旋转横向图片（宽大于高），默认False

        Returns:
            List[str]: 保存成功的文件路径列表（相对路径），失败时返回空列表
        """
        saved_files = []

        try:
            # 检查版本号判断是否为双面卡牌
            version = json_data.get('version', '')

            if version == '2.0':
                # 双面卡牌处理
                print("检测到双面卡牌，开始保存正面和背面")
                double_sided_result = self.generate_double_sided_card_image(json_data)

                if double_sided_result is None:
                    print("生成双面卡图失败")
                    return saved_files

                front_card = double_sided_result.get('front')
                back_card = double_sided_result.get('back')

                # 保存正面图片
                if front_card and front_card.image:
                    front_filename = f"{filename}_front.{export_format.lower()}"
                    front_path = self._save_single_image(
                        front_card.image, front_filename, parent_path, export_format, quality, rotate_landscape
                    )
                    if front_path:
                        saved_files.append(front_path)

                # 保存背面图片（如果存在）
                if back_card and back_card.image:
                    back_filename = f"{filename}_back.{export_format.lower()}"
                    back_path = self._save_single_image(
                        back_card.image, back_filename, parent_path, export_format, quality, rotate_landscape
                    )
                    if back_path:
                        saved_files.append(back_path)

                print(f"双面卡牌保存完成，共保存 {len(saved_files)} 个文件")
            else:
                # 单面卡牌处理
                print("检测到单面卡牌，开始保存")
                card = self.generate_card_image(json_data)

                if card is None or card.image is None:
                    print("生成卡图失败")
                    return saved_files

                # 保存单面图片
                final_filename = f"{filename}.{export_format.lower()}"
                save_path = self._save_single_image(
                    card.image, final_filename, parent_path, export_format, quality, rotate_landscape
                )
                if save_path:
                    saved_files.append(save_path)

                print("单面卡牌保存完成")

            return saved_files

        except Exception as e:
            print(f"保存卡图失败: {e}")
            traceback.print_exc()
            return saved_files

    def _save_single_image(self, image: Image.Image, filename: str, parent_path: Optional[str],
                          export_format: str, quality: int, rotate_landscape: bool = False) -> Optional[str]:
        """
        保存单张图片到文件

        Args:
            image: PIL图片对象
            filename: 文件名（包含扩展名）
            parent_path: 父目录相对路径
            export_format: 导出格式
            quality: 图片质量
            rotate_landscape: 是否旋转横向图片（宽大于高）

        Returns:
            str: 保存成功的文件相对路径，失败时返回None
        """
        try:
            # 处理横向图片旋转
            if rotate_landscape:
                width, height = image.size
                if width > height:
                    # 横向图片顺时针旋转90度
                    image = image.rotate(-90, expand=True)
                    print(f"横向图片已旋转90度，原尺寸: {width}x{height}，新尺寸: {image.size}")

            # 确定保存路径
            if parent_path:
                # 确保parent_path在工作目录内
                if not self._is_path_in_workspace(parent_path):
                    return None
                save_path = self._get_absolute_path(os.path.join(parent_path, filename))
            else:
                save_path = os.path.join(self.workspace_path, filename)

            # 确保父目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # 根据格式保存图片
            if export_format == 'JPG':
                # JPG格式需要转换为RGB模式
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(save_path, format='JPEG', quality=quality, optimize=True)
            else:
                # PNG格式保持透明通道
                image.save(save_path, format='PNG', optimize=True)

            print(f"图片已保存到: {self._get_relative_path(save_path)}")
            return self._get_relative_path(save_path)

        except Exception as e:
            print(f"保存图片失败: {e}")
            return None

    @staticmethod
    def _get_global_config_path() -> str:
        """获取全局配置文件路径"""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 打包后的临时目录
            return os.path.join(sys._MEIPASS, "global_config.json")
        return os.path.join(os.path.abspath("."), "global_config.json")

    def _get_default_global_config(self) -> Dict[str, Any]:
        """获取默认全局配置"""
        config = {}
        for field in self.SYSTEM_CONFIG_FIELDS:
            if field == "github_branch":
                config[field] = "main"
            elif field == "github_folder":
                config[field] = "images"
            elif field == "language":
                config[field] = "zh"
            elif field == "first_visit_completed":
                config[field] = False
            elif field == "folder":
                config[field] = "AH_LCG"  # Cloudinary默认文件夹
            elif field == "imgbb_expiration":
                config[field] = 0  # ImgBB默认永不过期
            else:
                config[field] = ""
        return config

    def _get_default_workspace_config(self) -> Dict[str, Any]:
        """获取默认工作空间配置"""
        config = {}
        for field in self.WORKSPACE_CONFIG_FIELDS:
            if field == "encounter_groups_dir":
                config[field] = "encounter_groups"
            else:
                config[field] = ""
        return config

    def _load_config_file(self, file_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"加载配置文件失败 {file_path}: {e}")
            return {}

    def _save_config_file(self, file_path: str, config: Dict[str, Any]) -> bool:
        """保存配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败 {file_path}: {e}")
            return False

    def _filter_config_by_fields(self, config: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """根据字段列表过滤配置"""
        return {key: value for key, value in config.items() if key in fields}

    def get_global_config(self) -> Dict[str, Any]:
        """获取全局配置"""
        try:
            global_config_path = self._get_global_config_path()
            loaded_config = self._load_config_file(global_config_path)

            # 合并默认配置和加载的配置
            default_config = self._get_default_global_config()
            default_config.update(loaded_config)

            return default_config
        except Exception as e:
            print(f"获取全局配置失败: {e}")
            return self._get_default_global_config()

    def save_global_config(self, global_config: Dict[str, Any]) -> bool:
        """保存全局配置"""
        try:
            # 只保存系统配置字段
            filtered_config = self._filter_config_by_fields(global_config, self.SYSTEM_CONFIG_FIELDS)

            global_config_path = self._get_global_config_path()
            return self._save_config_file(global_config_path, filtered_config)
        except Exception as e:
            print(f"保存全局配置失败: {e}")
            return False

    def get_workspace_config(self) -> Dict[str, Any]:
        """获取工作空间配置"""
        try:
            config_path = os.path.join(self.workspace_path, 'config.json')
            loaded_config = self._load_config_file(config_path)

            # 合并默认配置和加载的配置
            default_config = self._get_default_workspace_config()
            default_config.update(loaded_config)

            return default_config
        except Exception as e:
            print(f"获取工作空间配置失败: {e}")
            return self._get_default_workspace_config()

    def save_workspace_config(self, workspace_config: Dict[str, Any]) -> bool:
        """保存工作空间配置"""
        try:
            # 只保存工作空间配置字段
            filtered_config = self._filter_config_by_fields(workspace_config, self.WORKSPACE_CONFIG_FIELDS)

            config_path = os.path.join(self.workspace_path, 'config.json')
            return self._save_config_file(config_path, filtered_config)
        except Exception as e:
            print(f"保存工作空间配置失败: {e}")
            return False

    def get_github_config(self) -> Dict[str, Any]:
        """获取GitHub配置"""
        global_config = self.get_global_config()
        github_fields = ["github_token", "github_repo", "github_branch", "github_folder"]
        return self._filter_config_by_fields(global_config, github_fields)

    def save_github_config(self, github_config: Dict[str, Any]) -> bool:
        """保存GitHub配置"""
        try:
            # 读取现有全局配置
            existing_global_config = self.get_global_config()

            # 更新GitHub相关配置
            github_fields = ["github_token", "github_repo", "github_branch", "github_folder"]
            for key in github_fields:
                if key in github_config:
                    existing_global_config[key] = github_config[key]

            # 保存全局配置
            return self.save_global_config(existing_global_config)
        except Exception as e:
            print(f"保存GitHub配置失败: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """获取配置项（合并全局配置和工作目录配置）"""
        try:
            # 获取全局配置和工作空间配置
            global_config = self.get_global_config()
            workspace_config = self.get_workspace_config()

            # 合并配置，工作空间配置优先
            combined_config = global_config.copy()
            combined_config.update(workspace_config)

            return combined_config

        except Exception as e:
            print(f"读取配置文件失败: {e}")
            # 返回默认配置
            default_config = self._get_default_global_config()
            default_config.update(self._get_default_workspace_config())
            return default_config

    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置项（分别保存全局配置和工作目录配置）"""
        try:
            # 分离系统配置和工作空间配置
            global_config = self._filter_config_by_fields(config, self.SYSTEM_CONFIG_FIELDS)
            workspace_config = self._filter_config_by_fields(config, self.WORKSPACE_CONFIG_FIELDS)

            # 保存全局配置
            if global_config:
                # 读取现有全局配置，然后更新
                existing_global_config = self.get_global_config()
                existing_global_config.update(global_config)

                if not self.save_global_config(existing_global_config):
                    return False

            # 保存工作空间配置
            if workspace_config:
                # 读取现有工作空间配置，然后更新
                existing_workspace_config = self.get_workspace_config()
                existing_workspace_config.update(workspace_config)

                if not self.save_workspace_config(existing_workspace_config):
                    return False

            # 更新内存中的配置
            self.config = self.get_config()
            return True

        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get_encounter_groups(self) -> List[str]:
        """获取遭遇组列表"""
        try:
            # 获取配置
            config = self.config
            encounter_dir = config.get('encounter_groups_dir', '')

            if not encounter_dir:
                print("配置中未设置遭遇组目录")
                return []

            # 构建遭遇组目录的绝对路径
            encounter_path = self._get_absolute_path(encounter_dir)

            if not os.path.exists(encounter_path):
                print(f"遭遇组目录不存在: {encounter_dir}")
                return []

            if not os.path.isdir(encounter_path):
                print(f"指定路径不是目录: {encounter_dir}")
                return []

            # 搜索所有png图片文件
            encounter_groups = []
            for file in os.listdir(encounter_path):
                if file.lower().endswith('.png'):
                    # 去掉扩展名
                    name = os.path.splitext(file)[0]
                    encounter_groups.append(name)

            # 按名称排序
            encounter_groups.sort()
            return encounter_groups

        except Exception as e:
            print(f"获取遭遇组列表失败: {e}")
            return []

    def export_deck_image(self, deck_name: str, export_format: str = 'PNG', quality: int = 95) -> bool:
        """
        导出牌库图片

        Args:
            deck_name: 牌库名称（DeckBuilder文件夹中的文件名）
            export_format: 导出格式（JPG或PNG）
            quality: 图片质量百分比（1-100）

        Returns:
            bool: 导出是否成功
        """
        return self.deck_exporter.export_deck_image(deck_name, export_format, quality)

    def export_deck_pdf(self, deck_name: str, pdf_filename: Optional[str] = None) -> bool:
        """导出牌库PDF"""
        return self.deck_exporter.export_deck_pdf(deck_name, pdf_filename)

    def _get_card_image_for_position(self, cards: List[Dict], position: int) -> Optional[Image.Image]:
        """获取指定位置的卡片图片"""
        for card in cards:
            if card.get('index') == position:
                return self._load_card_image(card)
        return None

    def _load_card_image(self, card_data: Dict) -> Optional[Image.Image]:
        """根据卡片数据加载图片"""
        try:
            from PIL import Image

            card_type = card_data.get('type')
            card_path = card_data.get('path')

            if card_type == 'image':
                # 直接读取图片文件（相对工作目录路径）
                image_path = self._get_absolute_path(card_path)
                if os.path.exists(image_path):
                    return Image.open(image_path)

            elif card_type == 'cardback':
                # 固定的卡牌背面，从程序目录读取
                if card_path == 'player':
                    cardback_filename = 'cardback/player-back.jpg'
                elif card_path == 'encounter':
                    cardback_filename = 'cardback/encounter-back.jpg'
                else:
                    return None

                # 从程序目录读取
                cardback_path = os.path.join('.', cardback_filename)

                # 如果是PyInstaller打包的程序
                if hasattr(sys, '_MEIPASS'):
                    cardback_path = os.path.join(sys._MEIPASS, cardback_filename)

                print(f"正在读取卡牌背面图片: {cardback_path} {os.path.exists(cardback_path)}")
                if os.path.exists(cardback_path):
                    return Image.open(cardback_path)

            elif card_type == 'card':
                # 卡牌对象，需要读取卡牌JSON并生成图片
                card_json_path = self._get_absolute_path(card_path)
                if os.path.exists(card_json_path):
                    with open(card_json_path, 'r', encoding='utf-8') as f:
                        card_json_data = json.load(f)
                    return self.generate_card_image(card_json_data).image

            return None

        except Exception as e:
            print(f"加载卡片图片失败: {e}")
            return None

    def _process_card_image(self, image: Image.Image, is_front: bool, target_width: int,
                            target_height: int) -> Image.Image:
        """处理卡片图片（检测方向、旋转、拉伸）"""
        try:
            # 检测图片是横向还是纵向
            img_width, img_height = image.size
            is_landscape = img_width > img_height

            if is_landscape:
                # 横向图片需要旋转
                if is_front:
                    # 正面顺时针旋转90度
                    image = image.rotate(-90, expand=True)
                else:
                    # 背面逆时针旋转90度
                    image = image.rotate(90, expand=True)

            # 拉伸到目标尺寸
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

            return image

        except Exception as e:
            print(f"处理卡片图片失败: {e}")
            return image

    def open_directory_in_explorer(self, directory_path: str, bring_to_front: bool = True) -> bool:
        """
        在系统资源管理器中打开指定目录

        Args:
            directory_path: 相对于工作目录的目录路径
            bring_to_front: 是否将打开的窗口置顶

        Returns:
            bool: 是否成功打开
        """
        try:
            import subprocess
            import platform

            # 确保路径在工作目录内
            if not self._is_path_in_workspace(directory_path):
                print(f"路径不在工作目录内: {directory_path}")
                return False

            # 获取绝对路径
            abs_directory_path = self._get_absolute_path(directory_path)

            # 检查目录是否存在
            if not os.path.exists(abs_directory_path):
                print(f"目录不存在: {abs_directory_path}")
                return False

            if not os.path.isdir(abs_directory_path):
                print(f"指定路径不是目录: {abs_directory_path}")
                return False

            # 检查是否为Windows系统
            system = platform.system()
            if system != "Windows":
                print(f"不支持的操作系统: {system}")
                return False

            # Windows系统打开目录
            if bring_to_front:
                self._open_directory_windows_with_focus(abs_directory_path)
            else:
                # 简单打开
                os.startfile(abs_directory_path)

            print(f"已在资源管理器中打开目录: {self._get_relative_path(abs_directory_path)}")
            return True

        except Exception as e:
            print(f"打开目录失败: {e}")
            return False

    def _open_directory_windows_with_focus(self, abs_directory_path: str):
        """Windows系统打开目录并置顶"""
        try:
            import subprocess
            import time

            # 打开资源管理器
            subprocess.Popen(['explorer', abs_directory_path])

            # 等待一小段时间让窗口打开
            time.sleep(0.5)

            try:
                # 尝试使用Windows API将资源管理器窗口置顶
                import win32gui
                import win32con

                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        class_name = win32gui.GetClassName(hwnd)

                        # 查找资源管理器窗口
                        if (class_name == "CabinetWClass" or class_name == "ExploreWClass"):
                            # 检查窗口标题是否包含目录名
                            folder_name = os.path.basename(abs_directory_path)
                            if folder_name in window_title or abs_directory_path in window_title:
                                windows.append(hwnd)
                    return True

                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)

                # 将找到的窗口置顶
                for hwnd in windows:
                    win32gui.SetWindowPos(
                        hwnd,
                        win32con.HWND_TOPMOST,
                        0, 0, 0, 0,
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                    )
                    # 取消置顶状态，只是激活到前台
                    win32gui.SetWindowPos(
                        hwnd,
                        win32con.HWND_NOTOPMOST,
                        0, 0, 0, 0,
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                    )
                    win32gui.SetForegroundWindow(hwnd)
                    break

            except ImportError:
                # 如果没有安装pywin32，使用备用方案
                print("提示: 安装 pywin32 可获得更好的窗口置顶效果")
                print("安装命令: pip install pywin32")

        except Exception as e:
            print(f"Windows打开目录失败: {e}")
            # 回退到简单打开
            os.startfile(abs_directory_path)

    def _get_tts_save_directory(self) -> Optional[str]:
        """获取TTS保存目录，不存在则创建"""
        try:
            # 获取我的文档路径
            import os
            user_home = os.path.expanduser("~")
            documents_path = os.path.join(user_home, "Documents")

            # 如果Documents目录不存在，尝试中文版本
            if not os.path.exists(documents_path):
                documents_path = os.path.join(user_home, "文档")

            if not os.path.exists(documents_path):
                print("无法找到我的文档目录")
                return None

            # 构建完整路径
            tts_path = os.path.join(
                documents_path,
                "My Games",
                "Tabletop Simulator",
                "Saves",
                "Saved Objects",
                "阿卡姆姬制作"
            )

            # 创建目录（如果不存在）
            os.makedirs(tts_path, exist_ok=True)

            print(f"TTS保存目录: {tts_path}")
            return tts_path

        except Exception as e:
            print(f"创建TTS保存目录失败: {e}")
            return None

    def _generate_tts_cover(self, deck_config: Dict[str, Any]) -> Optional[Image.Image]:
        """生成TTS物品封面图片（256x256，等比缩放，透明背景）"""
        try:
            from PIL import Image

            # 获取前面卡片列表
            front_cards = deck_config.get("frontCards", [])

            if not front_cards:
                print("牌库中没有正面卡片")
                return None

            # 寻找第一个有效的对象作为封面
            for card_data in front_cards:
                try:
                    card_type = card_data.get('type')
                    card_path = card_data.get('path')

                    source_image = None

                    if card_type == 'card':
                        # 读取卡牌JSON并生成图片
                        card_json_path = self._get_absolute_path(card_path)
                        if os.path.exists(card_json_path):
                            with open(card_json_path, 'r', encoding='utf-8') as f:
                                card_json_data = json.load(f)

                            # 生成卡图
                            source_image = self.generate_card_image(card_json_data).image

                    elif card_type == 'image':
                        # 直接读取图片文件
                        image_path = self._get_absolute_path(card_path)
                        if os.path.exists(image_path):
                            source_image = Image.open(image_path)

                    elif card_type == 'cardback':
                        # 使用卡背图片
                        cardback_filename = None
                        if card_path == 'player':
                            cardback_filename = 'cardback/player-back.jpg'
                        elif card_path == 'encounter':
                            cardback_filename = 'cardback/encounter-back.jpg'

                        if cardback_filename:
                            cardback_path = os.path.join('.', cardback_filename)

                            # 如果是PyInstaller打包的程序
                            if hasattr(sys, '_MEIPASS'):
                                cardback_path = os.path.join(sys._MEIPASS, cardback_filename)

                            if os.path.exists(cardback_path):
                                source_image = Image.open(cardback_path)

                    # 如果成功获取到源图片，进行等比缩放处理
                    if source_image:
                        # 创建透明背景的256x256画布
                        cover_image = Image.new('RGBA', (256, 256), (0, 0, 0, 0))

                        # 计算等比缩放尺寸
                        source_width, source_height = source_image.size
                        aspect_ratio = source_width / source_height

                        if aspect_ratio > 1:  # 宽图
                            scaled_width = 256
                            scaled_height = int(256 / aspect_ratio)
                        else:  # 高图或正方形
                            scaled_width = int(256 * aspect_ratio)
                            scaled_height = 256

                        # 等比缩放源图片
                        scaled_image = source_image.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)

                        # 计算居中位置
                        x = (256 - scaled_width) // 2
                        y = (256 - scaled_height) // 2

                        # 如果源图片有alpha通道，直接粘贴；否则转换为RGBA
                        if scaled_image.mode != 'RGBA':
                            scaled_image = scaled_image.convert('RGBA')

                        # 将缩放后的图片粘贴到透明背景上
                        cover_image.paste(scaled_image, (x, y), scaled_image)

                        return cover_image

                except Exception as e:
                    print(f"处理封面卡片时出错 {card_data.get('path', 'unknown')}: {e}")
                    continue

            # 如果没有找到有效的卡片，创建一个默认透明封面
            print("未找到有效的封面卡片，创建默认封面")
            default_cover = Image.new('RGBA', (256, 256), (50, 50, 50, 128))  # 半透明灰色
            return default_cover

        except Exception as e:
            print(f"生成TTS封面失败: {e}")
            return None

    def _get_next_file_number(self, base_name: str, save_dir: str) -> int:
        """获取下一个可用的文件编号"""
        try:
            max_number = 0

            # 扫描目录中已存在的文件
            if os.path.exists(save_dir):
                for filename in os.listdir(save_dir):
                    # 匹配格式：base_name_数字.扩展名
                    if filename.startswith(f"{base_name}_") and (
                            filename.endswith('.json') or filename.endswith('.png')):
                        try:
                            # 提取数字部分
                            name_part = filename[len(base_name) + 1:]  # 去掉前缀和下划线
                            number_part = name_part.split('.')[0]  # 去掉扩展名

                            if number_part.isdigit():
                                number = int(number_part)
                                max_number = max(max_number, number)
                        except (ValueError, IndexError):
                            continue

            return max_number + 1

        except Exception as e:
            print(f"获取文件编号失败: {e}")
            return 1

    def export_deck_to_tts(self, deck_name: str, face_url: str, back_url: str) -> bool:
        """
        导出TTS物品

        Args:
            deck_name: 牌库名称（DeckBuilder文件夹中的文件名）
            face_url: 正面图片URL
            back_url: 背面图片URL

        Returns:
            bool: 导出是否成功
        """
        try:
            from PIL import Image

            # 1. 检查牌库文件是否存在
            deck_builder_path = os.path.join(self.workspace_path, 'DeckBuilder')
            if not os.path.exists(deck_builder_path):
                print("DeckBuilder目录不存在")
                return False

            deck_file_path = os.path.join(deck_builder_path, deck_name)
            if not os.path.exists(deck_file_path):
                print(f"牌库文件不存在: {deck_name}")
                return False

            # 2. 读取牌库配置
            with open(deck_file_path, 'r', encoding='utf-8') as f:
                deck_config = json.load(f)

            # 3. 创建TTS转换器并转换
            converter = TTSCardConverter(self.workspace_path)
            tts_json = converter.convert_deck_to_tts(deck_config, face_url, back_url)

            # 4. 生成封面图片（256x256，等比缩放，透明背景）
            cover_image = self._generate_tts_cover(deck_config)
            if cover_image is None:
                print("无法生成封面图片")
                return False

            # 5. 确定保存路径
            save_dir = self._get_tts_save_directory()
            if not save_dir:
                return False

            # 6. 生成文件名（去掉原文件扩展名）
            base_name = os.path.splitext(deck_name)[0]

            # 获取下一个可用的编号
            file_number = self._get_next_file_number(base_name, save_dir)

            json_filename = f"{base_name}_{file_number:03d}.json"  # 使用3位数字，例如001, 002, 003
            cover_filename = f"{base_name}_{file_number:03d}.png"

            json_path = os.path.join(save_dir, json_filename)
            cover_path = os.path.join(save_dir, cover_filename)

            # 7. 保存JSON文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(tts_json, f, indent=2, ensure_ascii=False)

            # 8. 保存封面图片
            cover_image.save(cover_path, 'PNG')

            print(f"TTS物品已导出:")
            print(f"  JSON: {json_path}")
            print(f"  封面: {cover_path}")

            return True

        except Exception as e:
            print(f"导出TTS物品失败: {e}")
            return False

    def export_card_with_params(self, card_path: str, export_filename: str, export_params: Dict[str, Any],
                                params_hash: str) -> bool:
        """
        使用指定的导出参数导出卡牌

        Args:
            card_path: 卡牌文件相对路径
            export_filename: 导出文件名（不包含扩展名）
            export_params: 导出参数
            params_hash: 参数哈希值，用于缓存判断

        Returns:
            bool: 导出是否成功
        """
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(card_path):
                print(f"卡牌路径不在工作目录内: {card_path}")
                return False

            # 检查导出目录是否存在，不存在则创建
            export_dir = os.path.join(self.workspace_path, 'export')
            os.makedirs(export_dir, exist_ok=True)

            # 获取导出格式
            export_format = export_params.get('format', 'PNG').upper()
            if export_format not in ['PNG', 'JPG']:
                print(f"不支持的导出格式: {export_format}")
                return False

            # 构建完整的导出文件名
            export_filepath = os.path.join(export_dir, f"{export_filename}.{export_format.lower()}")

            # 确保导出文件的父目录存在，一层一层创建直到目标目录存在
            export_parent_dir = os.path.dirname(export_filepath)
            os.makedirs(export_parent_dir, exist_ok=True)

            # 检查是否需要重新生成（通过参数哈希判断）
            export_helper = getattr(self, '_export_helper', None)
            current_hash = getattr(self, '_export_params_hash', None)

            if export_helper is None or current_hash != params_hash:
                from ExportHelper import ExportHelper
                # 创建新的ExportHelper实例
                export_helper = ExportHelper(export_params, self)
                self._export_helper = export_helper
                self._export_params_hash = params_hash
                print("创建新的ExportHelper实例")

            # 导出卡牌
            card_image = export_helper.export_card(card_path)
            if card_image is None:
                print("导出卡牌失败")
                return False

            # 保存图片
            dpi_info = (export_helper.dpi, export_helper.dpi)
            if export_format == 'JPG':
                quality = export_params.get('quality', 95)
                # 转为RGB
                card_image = card_image.convert('RGB')
                card_image.save(export_filepath, format='JPEG', quality=quality, dpi=dpi_info)
            else:
                card_image.save(export_filepath, format='PNG', dpi=dpi_info)

            print(f"卡牌已导出到: {export_filepath}")
            return True

        except Exception as e:
            print(f"导出卡牌失败: {e}")
            traceback.print_exc()
            return False

    def export_content_package_to_tts(self, package_relative_path: str) -> Dict[str, Any]:
        """
        导出内容包到TTS物品

        Args:
            package_relative_path: 内容包文件的相对路径

        Returns:
            dict: 包含成功状态和日志信息的字典
        """
        try:
            # 确保路径在工作空间内
            if not self._is_path_in_workspace(package_relative_path):
                return {
                    "success": False,
                    "logs": [f"内容包路径不在工作空间内: {package_relative_path}"],
                    "error": "路径安全检查失败"
                }

            # 读取内容包文件
            package_path = self._get_absolute_path(package_relative_path)
            if not os.path.exists(package_path):
                return {
                    "success": False,
                    "logs": [f"内容包文件不存在: {package_relative_path}"],
                    "error": "文件不存在"
                }

            with open(package_path, 'r', encoding='utf-8') as f:
                content_package_data = json.load(f)

            # 创建内容包管理器并导出
            manager = ContentPackageManager(content_package_data, self)
            result = manager.export_to_tts()

            if not result.get("success"):
                return result

            # 保存到TTS保存目录（Windows系统）
            if os.name == 'nt':  # Windows系统
                try:
                    tts_save_dir = self._get_tts_save_directory()
                    if tts_save_dir:
                        # 生成文件名
                        package_dir = os.path.dirname(package_relative_path)
                        package_name = os.path.splitext(os.path.basename(package_relative_path))[0]
                        tts_filename = f"{package_name}_tts.json"
                        tts_path = os.path.join(tts_save_dir, tts_filename)

                        # 保存JSON文件
                        with open(tts_path, 'w', encoding='utf-8') as f:
                            json.dump(result["box_json"], f, indent=2, ensure_ascii=False)

                        result["logs"].append(f"TTS物品已保存到: {tts_path}")
                        result["tts_path"] = tts_path
                except Exception as e:
                    result["logs"].append(f"保存到TTS目录失败（不影响导出）: {e}")

            # 保存到内容包目录
            try:
                package_dir = os.path.dirname(package_relative_path)
                package_name = os.path.splitext(os.path.basename(package_relative_path))[0]
                local_filename = f"{package_name}_tts.json"
                local_path = self._get_absolute_path(os.path.join(package_dir, local_filename))

                # 确保目录存在
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                # 保存JSON文件
                with open(local_path, 'w', encoding='utf-8') as f:
                    json.dump(result["box_json"], f, indent=2, ensure_ascii=False)

                result["logs"].append(f"TTS物品已保存到内容包目录: {os.path.join(package_dir, local_filename)}")
                result["local_path"] = os.path.join(package_dir, local_filename)

            except Exception as e:
                result["logs"].append(f"保存到内容包目录失败: {e}")
                result["success"] = False

            return result

        except Exception as e:
            error_msg = f"导出内容包到TTS失败: {e}"
            print(error_msg)
            return {
                "success": False,
                "logs": [error_msg],
                "error": str(e)
            }
