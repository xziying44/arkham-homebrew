import json
import os
import random
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from bin.card2arkhamdb import Card2ArkhamDBConverter


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

            return card_data

        except Exception as e:
            self._add_log(f"读取卡牌JSON失败 {card_filename}: {e}")
            return None

    def _get_card_tags(self, card_type: str) -> List[str]:
        """根据卡牌类型获取标签"""
        return self.card_type_tags.get(card_type, ["PlayerCard"])

    # ==================== TTS导出功能 ====================

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

            # 设置盒子封面
            if meta_info.get('banner_box_url', ''):
                box_template["ObjectStates"][0]["CustomMesh"]["DiffuseURL"] = meta_info.get('banner_box_url', '')

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
                        self._add_log(f"跳过卡牌 {i + 1}: 缺少图片URL（需要本地图片或云端图片）")
                        continue

                    # 读取卡牌JSON信息
                    card_filename = card_info.get("filename", "")
                    if not card_filename:
                        self._add_log(f"跳过卡牌 {i + 1}: 缺少文件名")
                        continue

                    card_data = self._read_card_json(card_filename)
                    if not card_data:
                        self._add_log(f"跳过卡牌 {i + 1}: 无法读取卡牌数据")
                        continue

                    # 创建卡牌对象
                    card_object = self._create_card_object(card_data, front_url, back_url, i + 1)
                    if card_object:
                        contained_objects.append(card_object)

                        # 记录图片类型
                        image_type = "云端图片" if front_url.startswith('http') else "本地图片"
                        self._add_log(f"成功处理卡牌: {card_data.get('name', '未知卡牌')} ({image_type})")

                except Exception as e:
                    self._add_log(f"处理卡牌 {i + 1} 时出错: {e}")
                    continue

            # 4. 将卡牌对象添加到盒子中
            box_template["ObjectStates"][0]["ContainedObjects"] = contained_objects

            self._add_log(f"成功处理 {len(contained_objects)} 张卡牌")

            self._add_log("TTS导出成功完成")
            return {
                "success": True,
                "box_json": box_template,
                "logs": self.logs.copy()
            }

        except Exception as e:
            self._add_log(f"导出TTS物品失败: {e}")
            return {
                "success": False,
                "logs": self.logs.copy(),
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

            # 定义需要使用act.json模板的卡牌类型
            act_card_types = {"密谋卡", "密谋卡-大画", "场景卡", "场景卡-大画"}
            is_act_card = card_type in act_card_types
            # 选择模板
            if is_investigator:
                template_name = "Investigator.json"
            elif is_act_card:
                template_name = "Act.json"
            else:
                template_name = "General.json"
            print(card_type + ' - ' + template_name)

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
                "UniqueBack": is_investigator,
                "Type": 0
            }

            # 读取原始卡牌对象中的LuaScript和GMNotes信息
            tts_script = card_data.get("tts_script", {})
            if tts_script:
                template["LuaScript"] = tts_script.get("LuaScript", "")
                template["GMNotes"] = tts_script.get("GMNotes", "")

            return template

        except Exception as e:
            self._add_log(f"创建卡牌对象失败: {e}")
            return None

    # ==================== ArkhamDB导出功能 ====================

    def export_to_arkhamdb(self, output_path: str = None) -> Dict[str, Any]:
        """
        导出为ArkhamDB格式
        Args:
            output_path: 输出文件路径，如果不指定则自动生成
        Returns:
            dict: 包含导出结果和日志信息的字典
        """
        try:
            self._add_log("开始导出ArkhamDB格式...")
            # 生成包代码
            pack_code = self._get_pack_code()
            self._add_log(f"包代码: {pack_code}")
            signature_to_investigator = {}  # 签名卡ID -> 调查员ID的映射

            cards = self.content_package.get("cards", [])
            self._add_log(f"第一遍扫描：查找调查员的签名卡...")

            for card_meta in cards:
                card_filename = card_meta.get("filename", "")
                if not card_filename:
                    continue

                card_data = self._read_card_json(card_filename)
                if not card_data:
                    continue

                # 只处理调查员卡
                if card_data.get("type") == "调查员":
                    try:
                        investigator_id = self._extract_gmnotes_id(card_data)
                        gm_notes = self._parse_gmnotes(card_data)
                        signatures = gm_notes.get('signatures', [])

                        if signatures and len(signatures) > 0:
                            signature_dict = signatures[0]  # 取第一个签名卡组
                            for sig_id in signature_dict.keys():
                                signature_to_investigator[sig_id] = investigator_id
                                self._add_log(f"  找到签名卡映射: {sig_id} -> {investigator_id}")
                    except Exception as e:
                        self._add_log(f"  处理调查员签名卡时出错: {e}")

            self._add_log(f"签名卡映射完成，共找到 {len(signature_to_investigator)} 张签名卡")

            # 转换卡牌
            converted_cards = []
            cards = self.content_package.get("cards", [])

            self._add_log(f"开始处理 {len(cards)} 张卡牌...")

            for i, card_meta in enumerate(cards):
                try:
                    # 读取卡牌原始数据
                    card_filename = card_meta.get("filename", "")
                    if not card_filename:
                        self._add_log(f"✗ 跳过卡牌 {i + 1}: 缺少文件名")
                        continue

                    card_data = self._read_card_json(card_filename)
                    if not card_data:
                        self._add_log(f"✗ 跳过卡牌 {i + 1}: 无法读取卡牌数据")
                        continue

                    # 使用Card2ArkhamDBConverter转换卡牌
                    converter = Card2ArkhamDBConverter(
                        card_data=card_data,
                        card_meta=card_meta,
                        pack_code=pack_code,
                        workspace_manager=self.workspace_manager,
                        signature_to_investigator=signature_to_investigator
                    )
                    converted_card = converter.convert()
                    converted_cards.append(converted_card)

                    # 记录成功信息
                    card_name = card_data.get("name", "未知卡牌")
                    image_info = self._get_image_info(card_meta)
                    self._add_log(f"✓ 成功转换卡牌: {card_name} {image_info}")

                except Exception as e:
                    self._add_log(f"✗ 转换卡牌 {i + 1} 失败: {e}")
                    continue

            # 构建ArkhamDB格式数据
            arkhamdb_data = self._build_arkhamdb_data(pack_code, converted_cards)

            # 保存文件
            if not output_path:
                output_path = self._generate_output_path()

            self._save_arkhamdb_file(arkhamdb_data, output_path)

            self._add_log(f"成功导出ArkhamDB格式文件: {output_path}")
            self._add_log(f"总共转换了 {len(converted_cards)} 张卡牌")

            return {
                "success": True,
                "arkhamdb_data": arkhamdb_data,
                "output_path": output_path,
                "logs": self.logs.copy()
            }

        except Exception as e:
            error_msg = f"导出ArkhamDB格式失败: {e}"
            self._add_log(error_msg)
            return {
                "success": False,
                "logs": self.logs.copy(),
                "error": error_msg
            }

    def _extract_gmnotes_id(self, card_data: Dict[str, Any]) -> str:
        """从卡牌数据中提取GMNotes的ID"""
        tts_script = card_data.get("tts_script", {})
        gm_notes = tts_script.get("GMNotes", "")

        if not gm_notes:
            return ""

        try:
            import json
            gm_data = json.loads(gm_notes)
            return gm_data.get("id", "")
        except:
            import re
            id_match = re.search(r'"id"\s*:\s*"([^"]+)"', gm_notes)
            return id_match.group(1) if id_match else ""

    def _parse_gmnotes(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析GMNotes为字典"""
        tts_script = card_data.get("tts_script", {})
        gm_notes = tts_script.get("GMNotes", "")

        if not gm_notes:
            return {}

        try:
            import json
            return json.loads(gm_notes)
        except:
            return {}

    def _get_pack_code(self) -> str:
        """获取或生成包代码"""
        pack_code = self.content_package.get("meta", {}).get("code", "")
        if not pack_code:
            pack_code = str(uuid.uuid4())[:8]
        return pack_code

    def _get_image_info(self, card_meta: Dict[str, Any]) -> str:
        """获取图片信息字符串"""
        front_url = card_meta.get("front_url", "")
        back_url = card_meta.get("back_url", "")

        info = []
        if front_url:
            info.append(f"正面:{'本地' if front_url.startswith('file://') else '云端'}")
        if back_url:
            info.append(f"背面:{'本地' if back_url.startswith('file://') else '云端'}")

        return f"(图片: {', '.join(info)})" if info else "(无图片)"

    def _build_arkhamdb_data(self, pack_code: str, cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建ArkhamDB格式数据"""
        meta_info = self.content_package.get("meta", {})

        return {
            "meta": {
                "code": pack_code,
                "name": meta_info.get("name", "Unknown"),
                "description": meta_info.get("description", ""),
                "author": meta_info.get("author", "Unknown"),
                "language": meta_info.get("language", "zh"),
                "external_link": meta_info.get("external_link", ""),
                "banner_url": meta_info.get("banner_url", ""),
                "types": meta_info.get("types", []),
                "status": meta_info.get("status", "final"),
                "date_updated": datetime.now().isoformat() + 'Z',
                "generator": "Arkham Card Maker 3.0 beta"
            },
            "data": {
                "cards": cards,
                "encounter_sets": [],
                "packs": [{
                    "code": pack_code,
                    "name": meta_info.get("name", "Unknown"),
                    "date_release": datetime.now().strftime('%Y-%m-%d'),
                    **({"icon_url": meta_info["icon_url"]} if meta_info.get("icon_url") else {}),
                }]
            }
        }

    def _generate_output_path(self) -> str:
        """生成输出文件路径"""
        pack_name = self.content_package.get("meta", {}).get("name", "Unknown")
        safe_name = "".join(c for c in pack_name if c.isalnum() or c in (' ', '-', '_')).strip()
        return self.workspace_manager._get_absolute_path(f"ContentPackage/{safe_name}_arkhambuild.json")

    def _save_arkhamdb_file(self, data: Dict[str, Any], output_path: str) -> None:
        """保存ArkhamDB格式文件"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    from bin.workspace_manager import WorkspaceManager

    os.chdir("../")

    workspace_manager = WorkspaceManager(r'D:\汉化文件夹\测试工作空间v2')

    content_package_manager = ContentPackageManager(
        content_package_data=json.loads(workspace_manager.get_file_content("ContentPackage/Test Pack.pack")),
        workspace_manager=workspace_manager,
    )

    # 测试TTS导出
    print("=" * 50)
    print("测试TTS导出:")
    tts_result = content_package_manager.export_to_tts()
    if tts_result["success"]:
        print("TTS导出成功！")
    else:
        print("TTS导出失败！")
    print("=" * 50)

    # 测试ArkhamDB导出
    print("\n" + "=" * 50)
    print("测试ArkhamDB导出:")
    arkhamdb_result = content_package_manager.export_to_arkhamdb()
    if arkhamdb_result["success"]:
        print("ArkhamDB导出成功！")
        print(f"输出文件: {arkhamdb_result['output_path']}")
        print(f"导出卡牌数量: {len(arkhamdb_result['arkhamdb_data']['data']['cards'])}")
    else:
        print("ArkhamDB导出失败！")
        print(f"错误: {arkhamdb_result.get('error')}")
    print("=" * 50)
