import base64
import io
import json
import mimetypes
import os
import sys
import tempfile  # 添加这个导入
import time
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional

from PIL import Image

from bin.tts_card_converter import TTSCardConverter

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

                self.font_manager = FontManager(fonts_path)
                self.image_manager = ImageManager(images_path)
                self.creator = CardCreator(
                    font_manager=self.font_manager,
                    image_manager=self.image_manager,
                )

            except Exception as e:
                print(f"初始化字体和图像管理器失败: {e}")
                self.font_manager = None
                self.image_manager = None
        else:
            self.font_manager = None
            self.image_manager = None

        self.config = self.get_config()

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
                return None

            abs_file_path = self._get_absolute_path(file_path)
            print(f"获取文件内容: {abs_file_path}")
            if not os.path.isfile(abs_file_path):
                return None

            with open(abs_file_path, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            print(f"读取文件内容失败: {e}")
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

    def generate_card_image(self, json_data: Dict[str, Any]):
        """
        生成卡图

        Args:
            json_data: 卡牌数据的JSON字典

        Returns:
            PIL.Image对象，如果生成失败返回None
        """
        if not CARD_GENERATION_AVAILABLE:
            print("卡牌生成功能不可用：缺少必要的模块")
            return None

        if not self.font_manager or not self.image_manager:
            print("字体或图像管理器未初始化")
            return None

        try:
            # 获取图片路径
            picture_path = json_data.get('picture_path', None)

            # 检查 picture_base64 字段
            picture_base64 = json_data.get('picture_base64', '')

            if picture_base64 and picture_base64.strip():
                # 如果有base64数据，转换为临时图片文件
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

            # 检测卡牌语言
            language = json_data.get('language', 'zh')
            self.font_manager.set_lang(language)

            # 调用process_card_json生成卡牌

            card = self.creator.create_card(
                json_data,
                picture_path=picture_path
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
            illustrator = json_data.get('illustrator', '')
            footer_copyright = self.config.get('footer_copyright', '')
            encounter_group_number = json_data.get('encounter_group_number', '')
            card_number = json_data.get('card_number', '')
            footer_icon_name = self.config.get('footer_icon_dir', '')
            footer_icon = None
            if footer_icon_name:
                footer_icon_path = self._get_absolute_path(footer_icon_name)
                if os.path.exists(footer_icon_path):
                    footer_icon = Image.open(footer_icon_path)

            card.set_footer_information(
                illustrator,
                footer_copyright,
                encounter_group_number,
                footer_icon,
                card_number
            )
            return card

        except Exception as e:
            # 打印异常栈
            traceback.print_exc()
            print(f"生成卡图失败: {e}")
            return None

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

    @staticmethod
    def _get_global_config_path() -> str:
        """获取全局配置文件路径"""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 打包后的临时目录
            return os.path.join(sys._MEIPASS, "global_config.json")
        return os.path.join(os.path.abspath("."), "global_config.json")

    def get_github_config(self) -> Dict[str, Any]:
        """获取GitHub配置"""
        global_config = self.get_global_config()
        return {
            "github_token": global_config.get("github_token", ""),
            "github_repo": global_config.get("github_repo", ""),
            "github_branch": global_config.get("github_branch", "main"),
            "github_folder": global_config.get("github_folder", "images")
        }

    def save_github_config(self, github_config: Dict[str, Any]) -> bool:
        """保存GitHub配置"""
        try:
            # 读取现有全局配置
            existing_global_config = self.get_global_config()

            # 更新GitHub相关配置
            github_keys = ["github_token", "github_repo", "github_branch", "github_folder"]
            for key in github_keys:
                if key in github_config:
                    existing_global_config[key] = github_config[key]

            # 保存全局配置
            return self.save_global_config(existing_global_config)
        except Exception as e:
            print(f"保存GitHub配置失败: {e}")
            return False

    @staticmethod
    def get_global_config() -> Dict[str, Any]:
        """获取全局配置（更新默认配置）"""
        try:
            global_config_path = WorkspaceManager._get_global_config_path()
            if os.path.exists(global_config_path):
                with open(global_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 返回默认全局配置（包含GitHub配置）
                return {
                    "ai_api_key": "",
                    "ai_endpoint": "https://api.deepseek.com/v1",
                    "ai_model": "deepseek-chat",
                    "github_token": "",
                    "github_repo": "",
                    "github_branch": "main",
                    "github_folder": "images",
                    "language": "zh"
                }
        except Exception as e:
            print(f"读取全局配置文件失败: {e}")
            return {
                "ai_api_key": "",
                "ai_endpoint": "https://api.deepseek.com/v1",
                "ai_model": "deepseek-chat",
                "github_token": "",
                "github_repo": "",
                "github_branch": "main",
                "github_folder": "images",
                "language": "zh"
            }

    @staticmethod
    def save_global_config(global_config: Dict[str, Any]) -> bool:
        """保存全局配置"""
        try:
            global_config_path = WorkspaceManager._get_global_config_path()
            with open(global_config_path, 'w', encoding='utf-8') as f:
                json.dump(global_config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存全局配置文件失败: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """获取配置项（合并全局配置和工作目录配置）"""
        try:
            # 读取工作目录配置
            workspace_config = {}
            config_path = os.path.join(self.workspace_path, 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    workspace_config = json.load(f)

            # 读取全局配置
            global_config = self.get_global_config()

            # 合并配置，全局配置的AI相关配置优先
            combined_config = workspace_config.copy()
            combined_config.update({
                "ai_api_key": global_config.get("ai_api_key", ""),
                "ai_endpoint": global_config.get("ai_endpoint", "https://api.deepseek.com/v1"),
                "ai_model": global_config.get("ai_model", "deepseek-chat"),
                "github_token": global_config.get("github_token", ""),
                "github_repo": global_config.get("github_repo", ""),
                "github_branch": global_config.get("github_branch", "main"),
                "github_folder": global_config.get("github_folder", "images"),
                "language": global_config.get("language", "zh")
            })

            return combined_config

        except Exception as e:
            print(f"读取配置文件失败: {e}")
            # 返回默认配置
            return {
                "ai_api_key": "",
                "ai_endpoint": "https://api.deepseek.com/v1",
                "ai_model": "deepseek-chat",
                "github_token": "",
                "github_repo": "",
                "github_branch": "main",
                "github_folder": "images",
                "language": "zh"
            }

    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置项（分别保存全局配置和工作目录配置）"""
        try:
            # AI相关配置项列表
            global_config_keys = [
                "ai_api_key",
                "ai_endpoint",
                "ai_model",
                "github_token",
                "github_repo",
                "github_branch",
                "github_folder",
                "language"
            ]

            # 分离全局配置和工作目录配置
            global_config = {}
            workspace_config = {}

            for key, value in config.items():
                if key in global_config_keys:
                    global_config[key] = value
                else:
                    workspace_config[key] = value

            # 保存全局配置
            if global_config:
                # 读取现有全局配置，然后更新
                existing_global_config = self.get_global_config()
                existing_global_config.update(global_config)

                if not self.save_global_config(existing_global_config):
                    return False

            # 保存工作目录配置
            if workspace_config:
                config_path = os.path.join(self.workspace_path, 'config.json')
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(workspace_config, f, ensure_ascii=False, indent=2)

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
        try:
            from PIL import Image, ImageDraw

            # 1. 读取牌库JSON文件
            deck_builder_path = os.path.join(self.workspace_path, 'DeckBuilder')
            if not os.path.exists(deck_builder_path):
                print("DeckBuilder目录不存在")
                return False

            deck_file_path = os.path.join(deck_builder_path, deck_name)
            if not os.path.exists(deck_file_path):
                print(f"牌库文件不存在: {deck_name}")
                return False

            with open(deck_file_path, 'r', encoding='utf-8') as f:
                deck_data = json.load(f)

            # 2. 获取底图尺寸
            width = deck_data.get('width', 1)
            height = deck_data.get('height', 1)

            # 单元大小
            card_width = 750
            card_height = 1050

            # 创建底图（黑色背景）
            canvas_width = width * card_width
            canvas_height = height * card_height

            front_image = Image.new('RGB', (canvas_width, canvas_height), (0, 0, 0))
            back_image = Image.new('RGB', (canvas_width, canvas_height), (0, 0, 0))

            # 3. 处理正面卡片
            front_cards = deck_data.get('frontCards', [])
            back_cards = deck_data.get('backCards', [])

            # 收集所有需要处理的位置
            positions_to_process = set()
            for card in front_cards:
                positions_to_process.add(card.get('index', 0))
            for card in back_cards:
                positions_to_process.add(card.get('index', 0))

            # 处理每个位置的卡片
            for position in positions_to_process:
                # 计算位置坐标（从左到右，从上到下）
                col = position % width
                row = position // width
                x = col * card_width
                y = row * card_height

                # 处理正面卡片
                front_card_image = self._get_card_image_for_position(front_cards, position)
                if front_card_image:
                    processed_front = self._process_card_image(front_card_image, True, card_width, card_height)
                    front_image.paste(processed_front, (x, y))

                # 处理背面卡片
                back_card_image = self._get_card_image_for_position(back_cards, position)
                if back_card_image:
                    processed_back = self._process_card_image(back_card_image, False, card_width, card_height)
                    back_image.paste(processed_back, (x, y))

            # 4. 保存图片
            deck_base_name = os.path.splitext(deck_name)[0]  # 去掉后缀

            front_filename = f"{deck_base_name}_front.{export_format.lower()}"
            back_filename = f"{deck_base_name}_back.{export_format.lower()}"

            front_path = os.path.join(deck_builder_path, front_filename)
            back_path = os.path.join(deck_builder_path, back_filename)

            save_kwargs = {}
            if export_format == 'JPG':
                save_kwargs['quality'] = quality
                save_kwargs['format'] = 'JPEG'
            else:
                save_kwargs['format'] = 'PNG'

            front_image.save(front_path, **save_kwargs)
            back_image.save(back_path, **save_kwargs)

            print(f"牌库图片已导出:")
            print(f"  正面: {self._get_relative_path(front_path)}")
            print(f"  背面: {self._get_relative_path(back_path)}")

            return True

        except Exception as e:
            print(f"导出牌库图片失败: {e}")
            return False

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
