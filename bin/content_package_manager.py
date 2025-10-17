import json
import os
import random
import uuid
from typing import Dict, List, Any, Optional


class ContentPackageManager:
    """内容包管理类，负责处理内容包的导出功能"""

    def __init__(self, content_package_data: Dict[str, Any], workspace_manager):
        """
        初始化内容包管理器

        Args:
            content_package_data: 内容包JSON对象
            workspace_manager: 工作空间管理器对象
        """
        self.content_package = content_package_data
        self.workspace_manager = workspace_manager
        self.logs = []  # 日志记录

        # 卡牌类型标签映射
        self.card_type_tags = {
            "调查员": ["Investigator", "PlayerCard"],
            "调查员背面": ["Investigator", "PlayerCard"],
            "定制卡": ["PlayerCard"],
            "技能卡": ["PlayerCard"],
            "事件卡": ["PlayerCard"],
            "支援卡": ["Asset", "PlayerCard"],
            "敌人卡": ["ScenarioCard"],
            "地点卡": ["Location", "ScenarioCard"],
            "密谋卡": ["ScenarioCard"],
            "密谋卡-大画": ["ScenarioCard"],
            "场景卡": ["ScenarioCard"],
            "场景卡-大画": ["ScenarioCard"],
            "故事卡": ["ScenarioCard"],
            "冒险参考卡": ["ScenarioCard"],
        }

    def _add_log(self, message: str) -> None:
        """添加日志信息"""
        self.logs.append(message)
        print(f"[ContentPackageManager] {message}")

    def _generate_guid(self) -> str:
        """生成随机GUID"""
        return ''.join(random.choices('0123456789abcdef', k=6))

    def _generate_custom_deck_id(self) -> str:
        """生成CustomDeck ID"""
        return str(random.randint(1000, 9999))

    def _read_template(self, template_name: str) -> Dict[str, Any]:
        """读取模板文件"""
        try:
            # 获取模板目录路径
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_path = os.path.join(current_dir, 'templates', template_name)

            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self._add_log(f"读取模板文件失败 {template_name}: {e}")
            return {}

    def _read_card_json(self, card_filename: str) -> Optional[Dict[str, Any]]:
        """读取卡牌JSON信息"""
        try:
            # 确保路径在工作空间内
            if not self.workspace_manager._is_path_in_workspace(card_filename):
                self._add_log(f"卡牌路径不在工作空间内: {card_filename}")
                return None

            card_path = self.workspace_manager._get_absolute_path(card_filename)

            if not os.path.exists(card_path):
                self._add_log(f"卡牌文件不存在: {card_filename}")
                return None

            with open(card_path, 'r', encoding='utf-8') as f:
                card_data = json.load(f)

            self._add_log(f"成功读取卡牌: {card_filename}")
            return card_data

        except Exception as e:
            self._add_log(f"读取卡牌JSON失败 {card_filename}: {e}")
            return None

    def _get_card_tags(self, card_type: str) -> List[str]:
        """根据卡牌类型获取标签"""
        return self.card_type_tags.get(card_type, ["PlayerCard"])

    def export_to_tts(self) -> Dict[str, Any]:
        """
        导出TTS物品

        Returns:
            dict: 包含盒子JSON和日志信息的字典
        """
        try:
            self._add_log("开始导出TTS物品...")

            # 1. 使用盒子模板创建最终导出文件对象
            box_template = self._read_template("Box.json")
            if not box_template:
                return {"success": False, "logs": self.logs, "error": "无法读取盒子模板"}

            # 2. 设置盒子信息
            meta_info = self.content_package.get("meta", {})
            box_name = meta_info.get("name", "未命名内容包")
            box_description = meta_info.get("description", "")

            # 设置盒子昵称和描述
            box_template["ObjectStates"][0]["Nickname"] = box_name
            box_template["ObjectStates"][0]["Description"] = f"{box_description} - 由阿卡姆印牌姬生成"

            self._add_log(f"设置盒子信息: {box_name}")

            # 3. 处理每张卡牌
            contained_objects = []
            cards = self.content_package.get("cards", [])

            self._add_log(f"找到 {len(cards)} 张卡牌")

            for i, card_info in enumerate(cards):
                try:
                    # 检查是否有front_url和back_url
                    front_url = card_info.get("front_url", "")
                    back_url = card_info.get("back_url", "")

                    # 支持本地文件路径（file:///开头）
                    if not front_url or not back_url:
                        self._add_log(f"跳过卡牌 {i+1}: 缺少图片URL（需要本地图片或云端图片）")
                        continue

                    # 读取卡牌JSON信息
                    card_filename = card_info.get("filename", "")
                    if not card_filename:
                        self._add_log(f"跳过卡牌 {i+1}: 缺少文件名")
                        continue

                    card_data = self._read_card_json(card_filename)
                    if not card_data:
                        self._add_log(f"跳过卡牌 {i+1}: 无法读取卡牌数据")
                        continue

                    # 创建卡牌对象
                    card_object = self._create_card_object(card_data, front_url, back_url, i+1)
                    if card_object:
                        contained_objects.append(card_object)

                        # 记录图片类型
                        image_type = "云端图片" if front_url.startswith('http') else "本地图片"
                        self._add_log(f"成功处理卡牌: {card_data.get('name', '未知卡牌')} ({image_type})")

                except Exception as e:
                    self._add_log(f"处理卡牌 {i+1} 时出错: {e}")
                    continue

            # 4. 将卡牌对象添加到盒子中
            box_template["ObjectStates"][0]["ContainedObjects"] = contained_objects

            self._add_log(f"成功处理 {len(contained_objects)} 张卡牌")

            self._add_log("TTS导出成功完成")
            return {
                "success": True,
                "box_json": box_template,
                "logs": self.logs.copy()  # 返回副本，避免外部修改
            }

        except Exception as e:
            self._add_log(f"导出TTS物品失败: {e}")
            return {
                "success": False,
                "logs": self.logs.copy(),  # 返回副本，避免外部修改
                "error": str(e)
            }

    def _create_card_object(self, card_data: Dict[str, Any], front_url: str, back_url: str,
                          card_index: int) -> Optional[Dict[str, Any]]:
        """
        创建卡牌对象

        Args:
            card_data: 卡牌JSON数据
            front_url: 正面图片URL
            back_url: 背面图片URL
            card_index: 卡牌索引

        Returns:
            dict: 卡牌对象，失败时返回None
        """
        try:
            # 判断卡牌类型
            card_type = card_data.get("type", "")
            is_investigator = card_type == "调查员"

            # 选择模板
            template_name = "Investigator.json" if is_investigator else "General.json"
            template = self._read_template(template_name)

            if not template:
                self._add_log(f"无法读取模板文件: {template_name}")
                return None

            # 生成GUID和CustomDeck ID
            guid = self._generate_guid()
            custom_deck_id = self._generate_custom_deck_id()
            card_id = int(f"{custom_deck_id}00")  # CardID设置为CustomDeck+00

            # 设置卡牌信息
            card_name = card_data.get("name", "未知卡牌")
            card_subtitle = card_data.get("subtitle", "")

            template["GUID"] = guid
            template["Nickname"] = card_name
            template["Description"] = card_subtitle
            template["CardID"] = card_id

            # 设置标签
            tags = self._get_card_tags(card_type)
            template["Tags"] = tags

            # 设置图片URL - 先移除默认的CustomDeck条目，然后添加新的
            template["CustomDeck"] = {}
            template["CustomDeck"][custom_deck_id] = {
                "FaceURL": front_url,
                "BackURL": back_url,
                "NumWidth": 1,
                "NumHeight": 1,
                "BackIsHidden": True,
                "UniqueBack": is_investigator,  # 调查员卡牌使用UniqueBack
                "Type": 0
            }

            # 设置调查员卡的特殊属性
            if is_investigator:
                template["SidewaysCard"] = True
                template["HideWhenFaceDown"] = False
            else:
                template["SidewaysCard"] = False
                template["HideWhenFaceDown"] = True

            # 读取原始卡牌对象中的LuaScript和GMNotes信息
            tts_script = card_data.get("tts_script", {})
            if tts_script:
                template["LuaScript"] = tts_script.get("LuaScript", "")
                template["GMNotes"] = tts_script.get("GMNotes", "")

            self._add_log(f"创建卡牌对象: {card_name} (ID: {card_id}, 类型: {card_type})")

            return template

        except Exception as e:
            self._add_log(f"创建卡牌对象失败: {e}")
            return None