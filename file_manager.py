import os
import json
import sys
import time
import base64
import tempfile  # 添加这个导入
import mimetypes
from typing import List, Dict, Any, Optional
from pathlib import Path

from PIL import Image

# 导入卡牌生成相关模块
try:
    from create_card import process_card_json, FontManager, ImageManager

    CARD_GENERATION_AVAILABLE = True
except ImportError:
    CARD_GENERATION_AVAILABLE = False
    print("警告: 无法导入卡牌生成模块，卡牌生成功能将不可用")


class QuickStart:
    """快速开始类，负责目录选择和最近记录管理"""

    def __init__(self, config_file: str = "recent_directories.json"):
        self.config_file = config_file
        self.max_records = 20

    def _load_recent_records(self) -> List[Dict[str, Any]]:
        """加载最近打开的目录记录"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载最近记录失败: {e}")
        return []

    def _save_recent_records(self, records: List[Dict[str, Any]]):
        """保存最近打开的目录记录"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存最近记录失败: {e}")

    def add_recent_directory(self, directory_path: str) -> bool:
        """添加最近打开的目录"""
        try:
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return False

            records = self._load_recent_records()

            # 检查是否已存在，如果存在则移除旧记录
            records = [r for r in records if r.get('path') != directory_path]

            # 添加新记录到开头
            new_record = {
                'path': directory_path,
                'name': os.path.basename(directory_path) or directory_path,
                'timestamp': int(time.time()),
                'formatted_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            }

            records.insert(0, new_record)

            # 保持最多20条记录
            if len(records) > self.max_records:
                records = records[:self.max_records]

            self._save_recent_records(records)
            return True

        except Exception as e:
            print(f"添加最近目录失败: {e}")
            return False

    def get_recent_directories(self) -> List[Dict[str, Any]]:
        """获取最近打开的目录列表"""
        records = self._load_recent_records()

        # 验证目录是否仍然存在，移除不存在的记录
        valid_records = []
        for record in records:
            if os.path.exists(record.get('path', '')):
                valid_records.append(record)

        # 如果有无效记录被移除，保存更新后的列表
        if len(valid_records) != len(records):
            self._save_recent_records(valid_records)

        return valid_records

    def remove_recent_directory(self, directory_path: str) -> bool:
        """移除指定的最近目录记录"""
        try:
            records = self._load_recent_records()
            original_length = len(records)
            records = [r for r in records if r.get('path') != directory_path]

            if len(records) != original_length:
                self._save_recent_records(records)
                return True
            return False
        except Exception as e:
            print(f"移除最近目录失败: {e}")
            return False

    def clear_recent_directories(self) -> bool:
        """清空所有最近目录记录"""
        try:
            self._save_recent_records([])
            return True
        except Exception as e:
            print(f"清空最近目录失败: {e}")
            return False


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
            except Exception as e:
                print(f"初始化字体和图像管理器失败: {e}")
                self.font_manager = None
                self.image_manager = None
        else:
            self.font_manager = None
            self.image_manager = None

        self.config = self.get_config()

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
                item_key = f"{item_path}_{int(time.time() * 1000000)}"  # 使用路径+时间戳生成唯一key

                if os.path.isdir(item_path):
                    # 处理目录，递归获取子项并排序
                    children = self._build_tree_recursive(item_path, include_hidden)
                    children = self._sort_items(children)  # 对子项进行排序

                    items.append({
                        'label': item,
                        'key': item_key,
                        'type': 'directory',
                        'path': item_path,
                        'children': children
                    })

                elif os.path.isfile(item_path):
                    # 处理文件
                    items.append({
                        'label': item,
                        'key': item_key,
                        'type': self._get_file_type(item),
                        'path': item_path
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
                'path': self.workspace_path,
                'children': children
            }

        except Exception as e:
            print(f"获取文件树失败: {e}")
            return {
                'label': 'Error',
                'key': 'error',
                'type': 'error',
                'path': self.workspace_path,
                'children': []
            }

    def create_directory(self, dir_name: str, parent_path: Optional[str] = None) -> bool:
        """创建目录"""
        try:
            if parent_path:
                # 确保parent_path在工作目录内
                abs_parent = os.path.abspath(parent_path)
                if not abs_parent.startswith(self.workspace_path):
                    return False
                target_path = os.path.join(abs_parent, dir_name)
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
                abs_parent = os.path.abspath(parent_path)
                if not abs_parent.startswith(self.workspace_path):
                    return False
                target_path = os.path.join(abs_parent, file_name)
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
            abs_old_path = os.path.abspath(old_path)
            if not abs_old_path.startswith(self.workspace_path):
                return False

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
            abs_item_path = os.path.abspath(item_path)
            if not abs_item_path.startswith(self.workspace_path):
                return False

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
            abs_file_path = os.path.abspath(file_path)
            if not abs_file_path.startswith(self.workspace_path):
                return None

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
            image_path: 图片文件路径

        Returns:
            str: base64格式的图片数据（包含data URL前缀），失败时返回None
        """
        try:
            # 确保路径在工作目录内
            abs_image_path = os.path.abspath(image_path)
            if not abs_image_path.startswith(self.workspace_path):
                return None

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
            file_path: 文件路径

        Returns:
            dict: 文件信息，包含type、size、modified等
        """
        try:
            # 确保路径在工作目录内
            abs_file_path = os.path.abspath(file_path)
            if not abs_file_path.startswith(self.workspace_path):
                return None

            if not os.path.exists(abs_file_path):
                return None

            stat_info = os.stat(abs_file_path)
            file_type = self._get_file_type(abs_file_path)

            return {
                'path': abs_file_path,
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
            abs_file_path = os.path.abspath(file_path)
            if not abs_file_path.startswith(self.workspace_path):
                return False

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

        temp_image_path = None  # 用于跟踪临时文件

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

                    # 创建临时文件
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        temp_file.write(image_data)
                        temp_image_path = temp_file.name
                        picture_path = temp_image_path

                    print(f"已将base64图片数据保存到临时文件: {temp_image_path}")

                except Exception as e:
                    print(f"解码base64图片数据失败: {e}")
                    return None

            # 如果picture_path是相对路径，尝试在工作目录中查找
            elif picture_path and not os.path.isabs(picture_path):
                full_picture_path = os.path.join(self.workspace_path, picture_path)
                if os.path.exists(full_picture_path):
                    picture_path = full_picture_path

            # 调用process_card_json生成卡牌
            card = process_card_json(
                json_data,
                picture_path=picture_path,
                font_manager=self.font_manager,
                image_manager=self.image_manager
            )

            # 检测是否有遭遇组
            encounter_group = json_data.get('encounter_group', None)
            encounter_groups_dir = self.config.get('encounter_groups_dir', None)
            if encounter_group and encounter_groups_dir:
                # 获取遭遇组图片路径
                encounter_group_picture_path = os.path.join(self.workspace_path, encounter_groups_dir,
                                                            encounter_group + '.png')
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
            footer_icon_path = os.path.join(self.workspace_path, footer_icon_name)
            footer_icon = None
            if footer_icon_name:
                footer_icon = Image.open(footer_icon_path)
            card.set_footer_information(
                illustrator,
                footer_copyright,
                encounter_group_number,
                footer_icon,
                card_number
            )
            return card.image

        except Exception as e:
            print(f"生成卡图失败: {e}")
            return None

        finally:
            # 清理临时文件
            if temp_image_path and os.path.exists(temp_image_path):
                try:
                    os.unlink(temp_image_path)
                    print(f"已删除临时文件: {temp_image_path}")
                except Exception as e:
                    print(f"删除临时文件失败: {e}")

    def save_card_image(self, json_data: Dict[str, Any], filename: str, parent_path: Optional[str] = None) -> bool:
        """
        保存卡图到文件

        Args:
            json_data: 卡牌数据的JSON字典
            filename: 保存的文件名（包含扩展名）
            parent_path: 保存的父目录路径，如果为None则保存到工作目录

        Returns:
            bool: 保存是否成功
        """
        try:
            # 生成卡图
            card_image = self.generate_card_image(json_data)
            if card_image is None:
                return False

            # 确定保存路径
            if parent_path:
                # 确保parent_path在工作目录内
                abs_parent = os.path.abspath(parent_path)
                if not abs_parent.startswith(self.workspace_path):
                    return False
                save_path = os.path.join(abs_parent, filename)
            else:
                save_path = os.path.join(self.workspace_path, filename)

            # 确保父目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # 保存图片
            card_image.save(save_path)

            print(f"卡图已保存到: {save_path}")
            return True

        except Exception as e:
            print(f"保存卡图失败: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """获取配置项"""
        try:
            config_path = os.path.join(self.workspace_path, 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 返回默认配置
                return {}
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return {}

    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置项"""
        try:
            config_path = os.path.join(self.workspace_path, 'config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.config = config
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
            encounter_path = os.path.join(self.workspace_path, encounter_dir)

            if not os.path.exists(encounter_path):
                print(f"遭遇组目录不存在: {encounter_path}")
                return []

            if not os.path.isdir(encounter_path):
                print(f"指定路径不是目录: {encounter_path}")
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
