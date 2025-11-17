import json
import os
import random
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from bin.card2arkhamdb import Card2ArkhamDBConverter
from bin import card_numbering
from bin.pnp_exporter import PNPExporter
from bin.tts_script_generator import TtsScriptGenerator


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
        self.tts_generator = TtsScriptGenerator(workspace_manager=self.workspace_manager)

        # 卡牌类型标签映射
        self.card_type_tags = {
            "调查员": ["Investigator", "PlayerCard"],
            "调查员小卡": ["PlayerCard"],
            "调查员背面": ["Investigator", "PlayerCard"],
            "定制卡": ["PlayerCard"],
            "技能卡": ["PlayerCard"],
            "事件卡": ["PlayerCard"],
            "支援卡": ["Asset", "PlayerCard"],
            "敌人卡": ["ScenarioCard"],
            "诡计卡": ["ScenarioCard"],
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

    def _get_card_tags(self, card_type: str, card_class: str) -> List[str]:
        """根据卡牌类型获取标签"""
        if card_class == '弱点':
            return ["PlayerCard"]
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

    def _clean_name(self, name: str) -> str:
        """清理卡牌名称，移除特殊标记"""
        return name.replace("🏅", "").replace("<独特>", "").strip()

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
            card_class = card_data.get("class", "")
            is_investigator = card_type == "调查员"

            # 定义需要使用act.json模板的卡牌类型
            act_card_types = {"密谋卡", "密谋卡-大画", "场景卡", "场景卡-大画"}
            is_act_card = card_type in act_card_types
            # 选择模板
            if is_investigator:
                template_name = "Investigator.json"
            elif card_type == '调查员小卡':
                template_name = "InvestigatorMini.json"
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
            card_name = self._clean_name(card_data.get("name", ""))
            card_subtitle = card_data.get("subtitle", "")

            template["GUID"] = guid
            template["Nickname"] = card_name
            template["Description"] = card_subtitle
            template["CardID"] = card_id

            # 设置标签
            tags = self._get_card_tags(card_type, card_class)
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

            # 统一使用后端生成器实时生成 GMNotes 与 LuaScript（忽略旧的 tts_script 字段）
            try:
                result = self.tts_generator.generate(card_data)
                template["GMNotes"] = result.get("GMNotes", "")
                lua_script = result.get("LuaScript", "")
                if lua_script:
                    template["LuaScript"] = lua_script
            except Exception as gen_err:
                self._add_log(f"生成TTS脚本失败: {gen_err}")

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
            customization_text_map = {}  # 绑定卡脚本ID -> 定制卡正文

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

            # 第二遍扫描：收集定制卡绑定（所有卡牌可作为绑定目标）
            self._add_log("第二遍扫描：收集定制卡绑定 → customization_text 映射...")
            for card_meta in cards:
                card_filename = card_meta.get("filename", "")
                if not card_filename:
                    continue
                card_data = self._read_card_json(card_filename)
                if not card_data or card_data.get('type') != '定制卡':
                    continue
                try:
                    tcfg = (card_data or {}).get('tts_config') or {}
                    bind_path = ((tcfg.get('custom') or {}).get('bind') or {}).get('path')
                    if not isinstance(bind_path, str) or not bind_path:
                        # 未绑定的定制卡：按普通卡处理，不注入 customization_text
                        continue
                    if not self.workspace_manager._is_path_in_workspace(bind_path):
                        self._add_log(f"  跳过定制卡绑定：路径不在工作空间内 {bind_path}")
                        continue
                    base_json = self._read_card_json(bind_path)
                    if not base_json:
                        self._add_log(f"  跳过定制卡绑定：找不到绑定卡 {bind_path}")
                        continue
                    # 提取绑定卡脚本ID（与后端一致的规则）
                    base_id = self.tts_generator.extract_script_id_from_card_json(base_json)
                    if not base_id:
                        self._add_log(f"  跳过定制卡绑定：无法解析脚本ID {bind_path}")
                        continue
                    # 冲突策略：仅保留首个，后续告警
                    if base_id in customization_text_map:
                        self._add_log(f"⚠️ 警告：存在多个定制卡同时绑定 {base_id}，仅采用首个")
                        continue
                    body = (card_data or {}).get('body', '') or ''
                    customization_text_map[base_id] = body
                    self._add_log(f"  映射 customization_text：{base_id} ← 定制卡 [{card_data.get('name', '')}]")
                except Exception as e:
                    self._add_log(f"  处理定制卡绑定失败：{e}")

            # 转换卡牌
            converted_cards = []
            cards = self.content_package.get("cards", [])
            encounter_sets = self.content_package.get("encounter_sets", [])

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
                        encounter_sets=encounter_sets,
                        workspace_manager=self.workspace_manager,
                        signature_to_investigator=signature_to_investigator,
                        customization_text_map=customization_text_map
                    )
                    converted_card = converter.convert()
                    converted_cards.extend(converted_card)

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
        """从卡牌数据中提取GMNotes的ID（v2 优先，回退旧数据）"""
        try:
            tcfg = card_data.get('tts_config') or {}
            if isinstance(tcfg, dict) and str(tcfg.get('version', '')).lower() == 'v2':
                result = self.tts_generator.generate(card_data)
                gm = result.get('GMNotes', '')
                if gm:
                    import json
                    gmj = json.loads(gm)
                    return gmj.get('id', '')
        except Exception:
            pass
        # 旧数据回退
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
        """解析GMNotes为字典（v2 优先，回退旧数据）"""
        try:
            tcfg = card_data.get('tts_config') or {}
            if isinstance(tcfg, dict) and str(tcfg.get('version', '')).lower() == 'v2':
                result = self.tts_generator.generate(card_data)
                gm = result.get('GMNotes', '')
                if gm:
                    import json
                    return json.loads(gm)
        except Exception:
            pass
        # 旧数据回退
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

        arkhamdb_result = {
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
                "generator": "Arkham Card Maker v3.3"
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

        # 构建遭遇组数据
        encounter_sets = self.content_package.get("encounter_sets", [])
        arkhamdb_encounter_sets = []

        for encounter_set in encounter_sets:
            encounter_data = {
                "code": encounter_set.get("code"),
                "name": encounter_set.get("name")
            }

            # 如果存在icon_url，添加到数据中
            if encounter_set.get("icon_url"):
                encounter_data["icon_url"] = encounter_set["icon_url"]

            arkhamdb_encounter_sets.append(encounter_data)

        # 设置encounter_sets到两个位置（保持与原结构一致）
        arkhamdb_result["data"]["encounter_sets"] = arkhamdb_encounter_sets
        arkhamdb_result["encounter_sets"] = arkhamdb_encounter_sets

        return arkhamdb_result

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

    def get_encounter_groups_from_package(self) -> List[Dict[str, Any]]:
        """
        从内容包中获取所有遭遇组图片

        Returns:
            List[Dict]: 遭遇组列表，每个元素包含 name、base64 和 relative_path 字段
        """
        try:
            self._add_log("开始获取内容包中的遭遇组...")

            encounter_groups = {}  # 使用字典来去重，key为遭遇组名称
            encounter_groups_dir = self.workspace_manager.config.get('encounter_groups_dir', 'encounter_groups')

            # 遍历内容包中的所有卡牌
            cards = self.content_package.get("cards", [])
            self._add_log(f"扫描 {len(cards)} 张卡牌以查找遭遇组...")

            for i, card_info in enumerate(cards):
                try:
                    # 读取卡牌JSON数据
                    card_filename = card_info.get("filename", "")
                    if not card_filename:
                        continue

                    card_data = self._read_card_json(card_filename)
                    if not card_data:
                        continue

                    # 获取遭遇组名称
                    encounter_group = card_data.get("encounter_group", "")
                    if not encounter_group:
                        continue

                    # 如果这个遭遇组已经处理过，跳过
                    if encounter_group in encounter_groups:
                        continue

                    # 获取遭遇组图片的base64数据
                    encounter_group_base64 = self._get_encounter_group_base64(encounter_group)

                    # 添加到结果中
                    encounter_groups[encounter_group] = {
                        "name": encounter_group,
                        "base64": encounter_group_base64,
                        "relative_path": os.path.join(encounter_groups_dir, encounter_group + '.png')
                    }

                    self._add_log(f"找到遭遇组: {encounter_group}")

                except Exception as e:
                    self._add_log(f"处理卡牌 {i + 1} 时出错: {e}")
                    continue

            # 转换为列表
            result = list(encounter_groups.values())
            self._add_log(f"成功获取 {len(result)} 个遭遇组")

            return result

        except Exception as e:
            self._add_log(f"获取遭遇组失败: {e}")
            return []

    def _get_encounter_group_base64(self, encounter_group: str) -> str:
        """
        获取遭遇组图片的base64数据

        Args:
            encounter_group: 遭遇组名称

        Returns:
            str: base64图片数据，失败时返回空字符串
        """
        try:
            # 获取遭遇组图片路径（参考workspace_manager.py中的逻辑）
            encounter_groups_dir = self.workspace_manager.config.get('encounter_groups_dir', 'encounter_groups')
            encounter_group_picture_path = self.workspace_manager._get_absolute_path(
                os.path.join(encounter_groups_dir, encounter_group + '.png')
            )

            self._add_log(f"查找遭遇组图片: {encounter_group_picture_path}")

            # 检查文件是否存在
            if not os.path.exists(encounter_group_picture_path):
                self._add_log(f"遭遇组图片不存在: {encounter_group}")
                return ""

            # 读取图片并转换为base64
            image_data = self.workspace_manager.get_image_as_base64(
                os.path.join(encounter_groups_dir, encounter_group + '.png')
            )

            if image_data:
                self._add_log(f"成功读取遭遇组图片: {encounter_group}")
            else:
                self._add_log(f"读取遭遇组图片失败: {encounter_group}")

            return image_data or ""

        except Exception as e:
            self._add_log(f"获取遭遇组图片base64失败 {encounter_group}: {e}")
            return ""

    def generate_card_numbering_plan(
            self,
            no_encounter_position: str = 'before',
            start_number: int = 1,
            footer_copyright: str = '',
            footer_icon_path: str = ''
    ) -> Dict[str, Any]:
        """
        生成卡牌编号方案

        Args:
            no_encounter_position: 无遭遇组卡牌的位置，'before' 或 'after'
            start_number: 起始序号
            footer_copyright: 底部版权信息
            footer_icon_path: 底标图标路径

        Returns:
            Dict: {
                'success': bool,
                'numbering_plan': List[Dict] - 编号方案列表,
                'logs': List[str] - 日志信息
            }
        """
        try:
            self.logs = []
            self._add_log("开始生成卡牌编号方案...")

            # 获取卡牌列表
            cards = self.content_package.get('cards', [])
            if not cards:
                return {
                    'success': False,
                    'error': '内容包中没有卡牌',
                    'logs': self.logs
                }

            self._add_log(f"找到 {len(cards)} 张卡牌")

            # 读取所有卡牌数据
            cards_data = []
            for card_meta in cards:
                filename = card_meta.get('filename', '')
                if not filename:
                    continue

                card_data = self._read_card_json(filename)
                if card_data:
                    # 合并元数据
                    card_data['filename'] = filename
                    cards_data.append(card_data)

            self._add_log(f"成功读取 {len(cards_data)} 张卡牌数据")

            # 获取遭遇组列表
            encounter_sets = self.content_package.get('encounter_sets', [])
            self._add_log(f"找到 {len(encounter_sets)} 个遭遇组")

            # 生成编号方案
            numbering_plan = card_numbering.generate_numbering_plan(
                cards_data=cards_data,
                encounter_sets=encounter_sets,
                no_encounter_position=no_encounter_position,
                start_number=start_number,
                footer_copyright=footer_copyright,
                footer_icon_path=footer_icon_path
            )

            self._add_log(f"成功生成编号方案，共 {len(numbering_plan)} 张卡牌")

            return {
                'success': True,
                'numbering_plan': numbering_plan,
                'logs': self.logs
            }

        except Exception as e:
            self._add_log(f"生成编号方案失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'logs': self.logs
            }

    def apply_card_numbering(self, numbering_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        应用卡牌编号方案

        Args:
            numbering_plan: 编号方案列表

        Returns:
            Dict: {
                'success': bool,
                'updated_count': int - 更新的卡牌数量,
                'logs': List[str] - 日志信息
            }
        """
        try:
            self.logs = []
            self._add_log("开始应用卡牌编号方案...")

            # 创建文件名到编号方案的映射
            plan_map = {plan['filename']: plan for plan in numbering_plan}

            updated_count = 0

            # 遍历所有卡牌文件并应用编号
            for filename, plan in plan_map.items():
                try:
                    # 读取卡牌数据
                    card_data = self._read_card_json(filename)
                    if not card_data:
                        self._add_log(f"跳过: 无法读取卡牌 {filename}")
                        continue

                    # 应用编号
                    has_changes = False

                    if 'encounter_group_number' in plan and plan['encounter_group_number']:
                        card_data['encounter_group_number'] = plan['encounter_group_number']
                        has_changes = True

                    if 'card_number' in plan and plan['card_number']:
                        card_data['card_number'] = plan['card_number']
                        has_changes = True

                    # 应用底部版权信息和底标图标
                    if 'footer_copyright' in plan:
                        card_data['footer_copyright'] = plan['footer_copyright']
                        has_changes = True

                    if 'footer_icon_path' in plan:
                        card_data['footer_icon_path'] = plan['footer_icon_path']
                        has_changes = True

                    # 保存修改
                    if has_changes:
                        self.workspace_manager.save_file_content(
                            filename,
                            json.dumps(card_data, ensure_ascii=False, indent=2)
                        )
                        updated_count += 1
                        self._add_log(
                            f"更新成功: {filename} (编号: {plan.get('card_number')}, 遭遇组编号: {plan.get('encounter_group_number')})")

                except Exception as e:
                    self._add_log(f"更新失败: {filename} - {e}")
                    continue

            self._add_log(f"编号应用完成，共更新 {updated_count} 张卡牌")

            return {
                'success': True,
                'updated_count': updated_count,
                'logs': self.logs
            }

        except Exception as e:
            self._add_log(f"应用编号方案失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'logs': self.logs
            }

    def export_to_pnp(
            self,
            export_params: Dict[str, Any],
            output_filename: str,
            mode: str = 'single_card',
            paper_size: str = 'A4',
            task_id: Optional[str] = None,
            log_callback=None
    ) -> Dict[str, Any]:
        """
        导出内容包为PNP PDF

        Args:
            export_params: 导出参数(传递给ExportHelper)
            output_filename: 输出PDF文件名
            mode: 导出模式，'single_card' 或 'print_sheet'
            paper_size: 纸张规格(仅在print_sheet模式下使用)，默认'A4'
            task_id: 任务ID，用于实时日志更新
            log_callback: 日志回调函数，用于实时更新日志

        Returns:
            Dict: {
                'success': bool,
                'output_path': str - 输出文件路径,
                'cards_exported': int - 导出的卡牌数量,
                'logs': List[str] - 日志信息
            }
        """
        try:
            self.logs = []
            self._add_log("开始导出PNP PDF...")

            # 获取内容包的卡牌列表
            cards = self.content_package.get('cards', [])
            if not cards:
                return {
                    'success': False,
                    'error': '内容包中没有卡牌',
                    'logs': self.logs
                }

            self._add_log(f"找到 {len(cards)} 张卡牌")

            # 构建输出路径
            output_path = self.workspace_manager._get_absolute_path(
                os.path.join('ContentPackage', output_filename)
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 创建PNP导出器，传递日志回调
            pnp_exporter = PNPExporter(export_params, self.workspace_manager, task_id=task_id,
                                       log_callback=log_callback)

            # 执行导出
            result = pnp_exporter.export_pnp(
                cards=cards,
                output_path=output_path,
                mode=mode,
                paper_size=paper_size
            )

            # 合并日志
            self.logs.extend(result.get('logs', []))

            if result.get('success'):
                self._add_log(f"PNP PDF导出成功: {output_path}")
                return {
                    'success': True,
                    'output_path': output_path,
                    'cards_exported': result.get('cards_exported', 0),
                    'logs': self.logs
                }
            else:
                self._add_log(f"PNP PDF导出失败: {result.get('error', 'Unknown error')}")
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'logs': self.logs
                }

        except Exception as e:
            self._add_log(f"导出PNP PDF失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'logs': self.logs
            }


if __name__ == '__main__':
    from bin.workspace_manager import WorkspaceManager

    os.chdir("../")

    workspace_manager = WorkspaceManager(r'C:\Users\xziyi\Desktop\arkham-homebrew-projects\EdgeOfTheEarth')

    content_package_manager = ContentPackageManager(
        content_package_data=json.loads(workspace_manager.get_file_content("ContentPackage/本地测试遭遇卡.pack")),
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

    # 测试获取所有遭遇组
    print(content_package_manager.get_encounter_groups_from_package())
    print("=" * 50)
