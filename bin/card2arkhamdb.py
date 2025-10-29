"""
卡牌到ArkhamDB格式转换器
专注于卡牌数据格式转换，不处理文件IO和路径操作
"""

import re
from typing import Dict, Any, List, Optional

from card_cdapter import CardAdapter


class Card2ArkhamDBConverter:
    """
    将自定义卡牌数据转换为ArkhamDB格式的转换器
    只负责数据转换，不涉及文件读写
    """

    # 中文职阶映射到英文代码
    FACTION_CODE_MAP = {
        "守护者": "guardian",
        "探求者": "seeker",
        "流浪者": "rogue",
        "潜修者": "mystic",
        "生存者": "survivor",
        "中立": "neutral"
    }

    # 中文卡牌类型映射到英文代码
    TYPE_CODE_MAP = {
        "调查员": "investigator",
        "支援卡": "asset",
        "事件卡": "event",
        "技能卡": "skill",
        "诡计卡": "treachery",
        "敌人卡": "enemy",
        "地点卡": "location",
        "故事卡": "story",
        "场景卡": "act",
        "密谋卡": "agenda",
        "冒险参考卡": "scenario"
    }

    # 槽位中文映射到英文
    SLOT_CODE_MAP = {
        "盟友": "Ally",
        "身体": "Body",
        "饰品": "Accessory",
        "手部": "Hand",
        "双手": "Hand x2",
        "法术": "Arcane",
        "双法术": "Arcane x2",
        "塔罗": "Tarot"
    }

    # 技能图标映射
    SKILL_ICON_MAP = {
        "意志": "willpower",
        "智力": "intellect",
        "战力": "combat",
        "敏捷": "agility",
        "狂野": "wild"
    }

    # 默认卡背类型（不需要处理）
    DEFAULT_BACK_TYPES = {
        "玩家卡背",
        "遭遇卡背",
        "定制卡背",
        "敌库卡背"
    }

    def __init__(self, card_data: Dict[str, Any], card_meta: Dict[str, Any], pack_code: str,
                 workspace_manager, signature_to_investigator: Dict[str, str] = None) -> None:
        """
        初始化转换器
        Args:
            card_data: 卡牌原始数据（从.card文件读取）
            card_meta: 卡牌元数据（从内容包的cards数组中获取，包含图片URL、数量等）
            pack_code: 包代码
            workspace_manager: 工作空间管理器
            signature_to_investigator: 签名卡ID到调查员ID的映射字典
        """
        adapter = CardAdapter(card_data, workspace_manager.font_manager)
        self.card_data = adapter.convert(True)
        card_data_back = card_data.get('back', {})
        if card_data_back and isinstance(card_data_back, dict):
            adapter = CardAdapter(card_data_back, workspace_manager.font_manager)
            self.card_data['back'] = adapter.convert(True)
        self.card_meta = card_meta
        self.pack_code = pack_code
        self.workspace_manager = workspace_manager
        self.signature_to_investigator = signature_to_investigator or {}

    def convert(self) -> List[Dict[str, Any]]:
        """
        根据卡牌类型执行相应的转换

        Returns:
            ArkhamDB格式的卡牌数据列表（通常为1个，特殊双面卡为2个）

        Raises:
            ValueError: 不支持的卡牌类型
        """
        card_type = self.card_data.get("type", "")
        lang_code = self.card_data.get("language", "zh")
        self.workspace_manager.font_manager.set_lang(lang_code)

        converter_map = {
            "调查员": self._convert_investigator,
            "支援卡": self._convert_asset,
            "事件卡": self._convert_event,
            "技能卡": self._convert_skill,
            "敌人卡": self._convert_enemy,
            "地点卡": self._convert_location,
            "场景卡": self._convert_act_agenda,
            "场景卡-大画": self._convert_act_agenda,
            "密谋卡": self._convert_act_agenda,
            "密谋卡-大画": self._convert_act_agenda,
            "诡计卡": self._convert_treachery,
            "冒险参考卡": self._convert_scenario,
        }

        converter = converter_map.get(card_type)
        if not converter:
            raise ValueError(f"不支持的卡牌类型: {card_type}")

        # 转换主卡
        card_data = converter()

        # 对所有非调查员卡检查是否需要添加restrictions
        if card_type != "调查员":
            card_data = self._add_signature_restrictions(card_data)

        flags = self._get_special_flags()
        card_data = card_data | flags
        card_data = self._validate_card_data(card_data)

        # 检查是否需要生成背面独立对象
        back_card = self._check_and_convert_back()

        if back_card:
            # 有特殊背面，返回两个对象
            # 在正面卡中添加linked_card引用
            card_data = {k: v for k, v in card_data.items() if not k.startswith("back_")}
            card_data["double_sided"] = False
            card_data["back_link"] = back_card["code"]
            back_card['hidden'] = True
            return [card_data, back_card]
        else:
            # 默认情况，返回一个对象
            return [card_data]

    def _check_and_convert_back(self) -> Optional[Dict[str, Any]]:
        """
        检查背面是否需要生成独立对象

        Returns:
            背面卡牌数据，如果不需要独立对象则返回None
        """
        back = self.card_data.get("back")
        if not back or not isinstance(back, dict):
            return None

        back_type = back.get("type", "")
        front_type = self.card_data.get("type", "")

        # 如果是默认卡背类型，不需要处理
        if back_type in self.DEFAULT_BACK_TYPES:
            return None

        # 检查是否为预设的默认双面组合
        if self._is_default_double_sided(front_type, back_type):
            return None

        # 需要生成独立背面对象
        return self._convert_back_to_separate_card(back)

    def _is_default_double_sided(self, front_type: str, back_type: str) -> bool:
        """
        检查是否为预设的默认双面卡组合

        Args:
            front_type: 正面类型
            back_type: 背面类型

        Returns:
            是否为默认组合
        """
        # 调查员的默认情况
        if front_type == "调查员" and back_type == "调查员背面":
            return True

        # 地点卡的特殊处理
        if front_type == "地点卡" and back_type == "地点卡":
            # 检查背面是否为"未揭示"
            back = self.card_data.get("back", {})
            location_type = back.get("location_type", "")
            return location_type == "未揭示"

        # 场景卡密谋卡的特殊处理
        if front_type in ["场景卡", "密谋卡"]:
            if back_type == front_type:
                # 检查is_back标记
                back = self.card_data.get("back", {})
                is_back = back.get("is_back", False)
                return is_back
            elif back_type in ["密谋卡-大画", "场景卡-大画"]:
                return True
            return False

        # 冒险参考卡
        if front_type == "冒险参考卡" and back_type == "冒险参考卡":
            return True

        return False

    def _convert_back_to_separate_card(self, back_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        将背面数据转换为独立的卡牌对象

        Args:
            back_data: 背面原始数据

        Returns:
            转换后的背面卡牌对象
        """
        # 创建背面转换器
        back_converter = Card2ArkhamDBConverter(
            card_data={"back": {}, **back_data},  # 将back_data作为主数据
            card_meta=self.card_meta,
            pack_code=self.pack_code,
            workspace_manager=self.workspace_manager,
            signature_to_investigator=self.signature_to_investigator
        )

        # 获取正面的code
        front_code = self._extract_code_from_gmnotes()

        # 转换背面
        back_cards = back_converter.convert()
        back_card = back_cards[0] if back_cards else {}

        # 修改背面code，添加"b"后缀
        back_card["code"] = f"{front_code}b"

        # 交换图片URL：背面图片变为正面图片
        # 因为独立背面对象在视图上显示为正面
        if "back_image_url" in back_card:
            back_card["image_url"] = back_card.pop("back_image_url")

        if "back_thumbnail_url" in back_card:
            back_card["thumbnail_url"] = back_card.pop("back_thumbnail_url")

        # 移除背面相关的URL字段（独立对象不需要背面URL）
        back_card.pop("back_image_url", None)
        back_card.pop("back_thumbnail_url", None)

        return back_card

    # ==================== 基础辅助方法 ====================

    def _get_gmnotes(self) -> Dict[str, Any]:
        """获取TTS脚本中的GMNotes"""
        tts_script = self.card_data.get("tts_script", {})
        gm_notes = tts_script.get("GMNotes", "")
        try:
            import json
            return json.loads(gm_notes)
        except:
            return {}

    def _extract_code_from_gmnotes(self) -> str:
        """从TTS脚本的GMNotes中提取卡牌ID"""
        tts_script = self.card_data.get("tts_script", {})
        gm_notes = tts_script.get("GMNotes", "")

        if not gm_notes:
            return ""

        try:
            import json
            gm_data = json.loads(gm_notes)
            return gm_data.get("id", "")
        except:
            id_match = re.search(r'"id"\s*:\s*"([^"]+)"', gm_notes)
            return id_match.group(1) if id_match else ""

    def _extract_position(self) -> int:
        """从卡牌编号中提取位置数字"""
        card_number = self.card_data.get("card_number", "")
        if not card_number:
            return 1

        number_match = re.search(r'\d+', str(card_number))
        return int(number_match.group()) if number_match else 1

    def _get_quantity(self) -> int:
        """获取卡牌数量"""
        return self.card_data.get("quantity", 1)

    def _check_is_unique(self) -> bool:
        """检查卡牌是否为独特卡"""
        name = self.card_data.get("name", "")
        return "🏅" in name or "<独特>" in name or self.card_meta.get("unique", False)

    def _get_special_flags(self) -> Dict[str, bool]:
        """获取特殊标记"""
        return {
            "is_unique": self._check_is_unique(),
            "permanent": self.card_meta.get("permanent", False),
            "exceptional": self.card_meta.get("exceptional", False),
            "myriad": self.card_meta.get("myriad", False),
            "exile": self.card_meta.get("exile", False)
        }

    def _convert_faction_codes(self) -> List[str]:
        """转换职阶代码"""
        class_name = self.card_data.get("class", "")

        # 处理多职阶
        if class_name == "多职阶":
            subclass = self.card_data.get("subclass", [])
            if isinstance(subclass, str):
                subclass = [subclass]

            faction_codes = [
                self.FACTION_CODE_MAP.get(f, "neutral")
                for f in subclass if f
            ]
            return faction_codes if faction_codes else ["neutral"]

        # 处理弱点
        if class_name == "弱点":
            return ["neutral"]

        # 处理普通职阶
        return [self.FACTION_CODE_MAP.get(class_name, "neutral")]

    def _convert_text_format(self, text: str) -> str:
        """转换文本格式，将emoji转换为arkhamdb格式"""
        if not text:
            return ""

        emoji_map = {
            "🧠": "[willpower]",
            "📚": "[intellect]",
            "👊": "[combat]",
            "🦶": "[agility]",
            "❓": "[wild]",
            "💀": "[skull]",
            "👤": "[cultist]",
            "📜": "[tablet]",
            "👹": "[elder_thing]",
            "🐙": "[auto_fail]",
            "⭐": "[elder_sign]",
            "⭕": "[reaction]",
            "➡️": "[action]",
            "⚡": "[free]",
            "🌟": "[bless]",
            "🌑": "[curse]",
            "❄️": "[frost]",
            '🛡️': '[guardian]',
            '🔍': '[seeker]',
            '🚶': '[rogue]',
            '🧘': '[mystic]',
            '🏕️': '[survivor]',
            '🕵️': '[per_investigator]',
            '🔵': '-',
            '<nbsp>': ' ',
        }

        result = text
        for emoji, code in emoji_map.items():
            result = result.replace(emoji, code)

        # 处理粗体标记
        result = re.sub(r'【([^】]+)】', r'<b>\1</b>', result)

        # 处理特性标记
        result = re.sub(r'\{([^}]+)\}', r'[[\1]]', result)

        # 处理调查员标记
        result = re.sub(r'<调查员>', r'[per_investigator]', result)

        return result

    def _get_image_urls(self) -> Dict[str, str]:
        """获取图片URL"""
        urls = {}

        front_url = self.card_meta.get("original_front_url", self.card_meta.get("front_url", ""))
        back_url = self.card_meta.get("original_back_url", self.card_meta.get("back_url", ""))
        front_thumbnail_url = self.card_meta.get("front_thumbnail_url", "")
        back_thumbnail_url = self.card_meta.get("back_thumbnail_url", "")

        # 只设置非空且不是默认卡背的URL
        if front_url and not self._is_default_card_back(front_url):
            urls["image_url"] = front_url

        if back_url and not self._is_default_card_back(back_url):
            urls["back_image_url"] = back_url

        if front_thumbnail_url:
            urls["thumbnail_url"] = front_thumbnail_url

        if back_thumbnail_url:
            urls["back_thumbnail_url"] = back_thumbnail_url

        return urls

    def _is_default_card_back(self, url: str) -> bool:
        """检查是否为默认卡背"""
        return url.endswith(
            "https://steamusercontent-a.akamaihd.net/ugc/2342503777940352139/A2D42E7E5C43D045D72CE5CFC907E4F886C8C690/") or \
            url.endswith(
                "https://steamusercontent-a.akamaihd.net/ugc/2342503777940351785/F64D8EFB75A9E15446D24343DA0A6EEF5B3E43DB/")

    def _parse_skill_icons(self) -> Dict[str, int]:
        """解析技能图标"""
        skill_icons = self.card_data.get("submit_icon", [])
        skill_counts = {skill: 0 for skill in self.SKILL_ICON_MAP.values()}

        for icon in skill_icons:
            skill_key = self.SKILL_ICON_MAP.get(icon)
            if skill_key:
                skill_counts[skill_key] += 1

        return {f"skill_{k}": v for k, v in skill_counts.items() if v > 0}

    def _get_traits(self) -> Optional[str]:
        """获取特性字符串"""
        traits = self.card_data.get("traits", [])
        return ". ".join(traits) + "." if traits else None

    def _clean_name(self, name: str) -> str:
        """清理卡牌名称，移除特殊标记"""
        return name.replace("🏅", "").replace("<独特>", "").strip()

    def _is_signature_card(self, card_id: str) -> bool:
        """检查卡牌是否为签名卡"""
        return card_id in self.signature_to_investigator

    # ==================== 各类型卡牌转换方法 ====================

    def _convert_investigator(self) -> Dict[str, Any]:
        """转换调查员卡"""
        flags = self._get_special_flags()
        faction_codes = self._convert_faction_codes()

        data = {
            "code": self._extract_code_from_gmnotes(),
            "position": self._extract_position(),
            "quantity": 1,  # 调查员卡固定为1
            "name": self._clean_name(self.card_data.get("name", "")),
            "subname": self.card_data.get("subtitle", ""),
            "type_code": "investigator",
            "faction_code": faction_codes[0],
            "skill_willpower": self.card_data.get("attribute", [0, 0, 0, 0])[0],
            "skill_intellect": self.card_data.get("attribute", [0, 0, 0, 0])[1],
            "skill_combat": self.card_data.get("attribute", [0, 0, 0, 0])[2],
            "skill_agility": self.card_data.get("attribute", [0, 0, 0, 0])[3],
            "health": self.card_data.get("health", 0),
            "sanity": self.card_data.get("sanity", self.card_data.get("horror", 0)),
            "text": self._convert_text_format(self.card_data.get("body", "")),
            "flavor": self._convert_text_format(self.card_data.get("flavor", "")),
            "deck_limit": 1,
            "double_sided": True,
            "is_unique": flags["is_unique"],
            "illustrator": self.card_data.get("illustrator", ""),
            "pack_code": self.pack_code
        }

        # 背面数据
        card_size = 30
        card_back = self.card_data.get("back", {})
        if card_back and card_back.get('type', '') in ['调查员背面', '调查员卡背']:
            back_data = self.card_data.get("back", {}).get("card_back", {})
            data["back_name"] = self._clean_name(self.card_data.get("name", ""))
            data["back_subname"] = self.card_data.get("subtitle", "")
            data["back_text"] = self._convert_text_format(
                self.workspace_manager.creator.build_investigators_card_back_test(back_data)
            )
            data["back_flavor"] = self._convert_text_format(back_data.get("story", ""))
            card_size = back_data.get("size", card_size)

        # 组牌选项
        data["deck_options"] = self._convert_deck_options()
        deck_requirements = f'size:{card_size}'
        card_signatures = self._get_gmnotes().get('signatures', [])
        if len(card_signatures) > 0:
            card_signatures = card_signatures[0]
            for sig_id in card_signatures.keys():
                deck_requirements += f', card:{sig_id}'
        deck_requirements += ', random:subtype:basicweakness'
        data["deck_requirements"] = deck_requirements

        # 图片
        data.update(self._get_image_urls())

        return data

    def _add_signature_restrictions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        为签名卡添加restrictions字段

        Args:
            data: 已转换的卡牌数据

        Returns:
            添加了restrictions的卡牌数据
        """
        card_id = data.get("code", "")

        # 检查这张卡是否是某个调查员的签名卡
        if card_id in self.signature_to_investigator:
            investigator_id = self.signature_to_investigator[card_id]
            data["restrictions"] = f"investigator:{investigator_id}"

        return data

    def _convert_deck_options(self) -> List[Dict[str, Any]]:
        """转换组牌选项"""
        deck_options = self.card_data.get("deck_options", [])
        return deck_options

    def _convert_cost(self) -> Optional[int]:
        """
        转换费用值，将Card格式转换为ArkhamDB格式

        Card格式:
            -1: 无费用（-）
            -2: X费用
            ≥0: 具体数值

        ArkhamDB格式:
            null: 无费用（-）
            -2: X费用
            -3: *费用
            -4: ?费用
            ≥0: 具体数值
        """
        cost = self.card_data.get("cost")

        # 如果cost不存在或为None，返回None
        if cost is None:
            return None

        # 转换逻辑
        if cost == -1:
            # 无费用用null表示
            return None
        elif cost == -2:
            # X费用保持-2
            return -2
        elif cost >= 0:
            # 具体数值保持不变
            return cost
        else:
            # 其他负数（如果有-3、-4等）保持原值
            # 这是为了未来支持*费用(-3)和?费用(-4)
            return cost

    def _convert_asset(self) -> Dict[str, Any]:
        """转换支援卡"""
        flags = self._get_special_flags()
        faction_codes = self._convert_faction_codes()

        # 判断是否为签名卡以设置正确的deck_limit
        card_id = self._extract_code_from_gmnotes()
        is_signature = self._is_signature_card(card_id)

        data = {
            "code": card_id,
            "position": self._extract_position(),
            "quantity": self._get_quantity(),
            "name": self._clean_name(self.card_data.get("name", "")),
            "subname": self.card_data.get("subtitle", ""),
            "type_code": "asset",
            "faction_code": faction_codes[0],
            "text": self._convert_text_format(self.card_data.get("body", "")),
            "flavor": self._convert_text_format(self.card_data.get("flavor", "")),
            "deck_limit": self._get_quantity() if is_signature else (1 if flags["is_unique"] else 2),
            "is_unique": flags["is_unique"],
            "illustrator": self.card_data.get("illustrator", ""),
            "pack_code": self.pack_code
        }
        # 添加费用字段（如果有）
        cost = self._convert_cost()
        if cost is not None:
            data["cost"] = cost

        # 处理多职介
        if len(faction_codes) > 1:
            data.update({f"faction{i + 2}_code": code for i, code in enumerate(faction_codes[1:])})

        # 技能图标
        data.update(self._parse_skill_icons())

        # 属性
        if (health := self.card_data.get("health", -1)) != -1:
            data["health"] = health
        if (horror := self.card_data.get("horror", -1)) != -1:
            data["sanity"] = horror

        # 槽位
        if slot := self._convert_slots():
            data["slot"] = slot

        # 特性
        if traits := self._get_traits():
            data["traits"] = traits

        # 等级
        if (level := self.card_data.get("level", -1)) >= 0:
            data["xp"] = level

        # 图片
        data.update(self._get_image_urls())

        return data

    def _convert_slots(self) -> Optional[str]:
        """转换槽位信息"""
        slot = self.card_data.get("slots")
        slot2 = self.card_data.get("slots2")

        if not slot:
            return None

        slot_code = self.SLOT_CODE_MAP.get(slot, slot)

        if slot2:
            slot2_code = self.SLOT_CODE_MAP.get(slot2, slot2)
            return f"{slot2_code}.{slot_code}"

        return slot_code

    def _convert_event(self) -> Dict[str, Any]:
        """转换事件卡"""
        flags = self._get_special_flags()
        faction_codes = self._convert_faction_codes()

        # 判断是否为签名卡以设置正确的deck_limit
        card_id = self._extract_code_from_gmnotes()
        is_signature = self._is_signature_card(card_id)

        data = {
            "code": card_id,
            "position": self._extract_position(),
            "quantity": self._get_quantity(),
            "name": self._clean_name(self.card_data.get("name", "")),
            "type_code": "event",
            "faction_code": faction_codes[0],
            "text": self._convert_text_format(self.card_data.get("body", "")),
            "flavor": self._convert_text_format(self.card_data.get("flavor", "")),
            "deck_limit": self._get_quantity() if is_signature else (1 if flags["is_unique"] else 2),
            "is_unique": flags["is_unique"],
            "illustrator": self.card_data.get("illustrator", ""),
            "pack_code": self.pack_code
        }

        # 添加费用字段（如果有）
        cost = self._convert_cost()
        if cost is not None:
            data["cost"] = cost

        # 处理多职介
        if len(faction_codes) > 1:
            data.update({f"faction{i + 2}_code": code for i, code in enumerate(faction_codes[1:])})

        # 技能图标
        data.update(self._parse_skill_icons())

        # 特性
        if traits := self._get_traits():
            data["traits"] = traits

        # 等级
        if (level := self.card_data.get("level", -1)) >= 0:
            data["xp"] = level

        # 图片
        data.update(self._get_image_urls())

        return data

    def _convert_skill(self) -> Dict[str, Any]:
        """转换技能卡"""
        flags = self._get_special_flags()
        faction_codes = self._convert_faction_codes()

        # 判断是否为签名卡以设置正确的deck_limit
        card_id = self._extract_code_from_gmnotes()
        is_signature = self._is_signature_card(card_id)

        data = {
            "code": card_id,
            "position": self._extract_position(),
            "quantity": self._get_quantity(),
            "name": self._clean_name(self.card_data.get("name", "")),
            "type_code": "skill",
            "faction_code": faction_codes[0],
            "text": self._convert_text_format(self.card_data.get("body", "")),
            "flavor": self._convert_text_format(self.card_data.get("flavor", "")),
            "deck_limit": self._get_quantity() if is_signature else (1 if flags["is_unique"] else 2),
            "is_unique": flags["is_unique"],
            "illustrator": self.card_data.get("illustrator", ""),
            "pack_code": self.pack_code
        }
        # 处理多职介
        if len(faction_codes) > 1:
            data.update({f"faction{i + 2}_code": code for i, code in enumerate(faction_codes[1:])})

        # 技能图标
        data.update(self._parse_skill_icons())

        # 特性
        if traits := self._get_traits():
            data["traits"] = traits

        # 等级
        if (level := self.card_data.get("level", -1)) >= 0:
            data["xp"] = level

        # 图片
        data.update(self._get_image_urls())

        return data

    def _convert_enemy(self) -> Dict[str, Any]:
        """转换敌人卡"""
        flags = self._get_special_flags()

        data = {
            "code": self._extract_code_from_gmnotes(),
            "position": self._extract_position(),
            "quantity": self._get_quantity(),
            "name": self._clean_name(self.card_data.get("name", "")),
            "subname": self.card_data.get("subtitle", ""),
            "type_code": "enemy",
            "text": self._convert_text_format(self.card_data.get("body", "")),
            "flavor": self._convert_text_format(self.card_data.get("flavor", "")),
            "deck_limit": 1,
            "is_unique": flags["is_unique"],
            "illustrator": self.card_data.get("illustrator", ""),
            "pack_code": self.pack_code
        }

        # 敌人类型
        if self.card_data.get("class", "") == "弱点":
            data['faction_code'] = 'neutral'
        else:
            data['faction_code'] = 'mythos'

        # 敌人属性
        if fight := self._parse_enemy_stat(self.card_data.get("attack", "")):
            data.update(fight)

        if health := self._parse_enemy_stat(self.card_data.get("enemy_health", ""), "health"):
            data.update(health)

        if evade := self._parse_enemy_stat(self.card_data.get("evade", ""), "enemy_evade"):
            data.update(evade)

        # 伤害
        if (damage := self.card_data.get("enemy_damage", 0)) > 0:
            data["enemy_damage"] = damage

        if (horror := self.card_data.get("enemy_damage_horror", 0)) > 0:
            data["enemy_horror"] = horror

        # 特性
        if traits := self._get_traits():
            data["traits"] = traits

        # 图片
        data.update(self._get_image_urls())

        return data

    def _parse_enemy_stat(self, value: str, key: str = "enemy_fight") -> Dict[str, Any]:
        """解析敌人属性值（支持<调查员>标记）"""
        if not value:
            return {}

        result = {}
        match = re.search(r'(\d+)(?:<调查员>)?', value)
        if match:
            result[key] = int(match.group(1))
            if "<调查员>" in value:
                per_inv_key = key.replace("enemy_", "") + "_per_investigator"
                result[per_inv_key] = True

        return result

    def _convert_location(self) -> Dict[str, Any]:
        """转换地点卡"""
        flags = self._get_special_flags()

        data = {
            "code": self._extract_code_from_gmnotes(),
            "position": self._extract_position(),
            "quantity": self._get_quantity(),
            "name": self._clean_name(self.card_data.get("name", "")),
            "subname": self.card_data.get("subtitle", ""),
            "type_code": "location",
            "faction_code": "mythos",
            "text": self._convert_text_format(self.card_data.get("body", "")),
            "flavor": self._convert_text_format(self.card_data.get("flavor", "")),
            "deck_limit": 1,
            "is_unique": flags["is_unique"],
            "illustrator": self.card_data.get("illustrator", ""),
            "pack_code": self.pack_code
        }

        # 地点属性
        if shroud := self._parse_location_value(self.card_data.get("shroud", "")):
            data["shroud"] = shroud

        if clues := self._parse_location_value(self.card_data.get("clues", "")):
            data["clues"] = clues
            data["clues_fixed"] = True

        # 特性
        if traits := self._get_traits():
            data["traits"] = traits

        # 双面卡
        if "back" in self.card_data:
            data["double_sided"] = True
            back = self.card_data["back"]
            data["back_name"] = back.get("name", data["name"])
            data["back_text"] = self._convert_text_format(back.get("body", ""))
            data["back_flavor"] = self._convert_text_format(back.get("flavor", ""))

        # 图片
        data.update(self._get_image_urls())

        return data

    def _parse_location_value(self, value: str) -> Optional[int]:
        """解析地点属性值（支持-和X）"""
        if not value or value == "-":
            return None
        if value == "X":
            return -2

        match = re.search(r'(\d+)', value)
        return int(match.group(1)) if match else None

    def _convert_act_agenda(self) -> Dict[str, Any]:
        """转换场景卡/密谋卡"""
        card_type = self.card_data.get("type", "")
        flags = self._get_special_flags()

        is_act = "场景" in card_type
        type_code = "act" if is_act else "agenda"

        data = {
            "code": self._extract_code_from_gmnotes(),
            "position": self._extract_position(),
            "quantity": self._get_quantity(),
            "name": self._clean_name(self.card_data.get("name", "")),
            "subname": self.card_data.get("subtitle", ""),
            "type_code": type_code,
            "faction_code": "mythos",
            "text": self._convert_text_format(self.card_data.get("body", "")),
            "flavor": self._convert_text_format(self.card_data.get("flavor", "")),
            "deck_limit": 1,
            "is_unique": flags["is_unique"],
            "illustrator": self.card_data.get("illustrator", ""),
            "pack_code": self.pack_code,
            "double_sided": True,
            "stage": 1
        }

        # 阈值
        threshold = self.card_data.get("threshold", "")
        if threshold:
            if is_act:
                if clues := self._parse_location_value(threshold):
                    data["clues"] = clues
            else:
                if doom := self._parse_location_value(threshold):
                    data["doom"] = doom

        # 背面数据
        if "back" in self.card_data:
            back = self.card_data["back"]
            data["back_name"] = back.get("name", data["name"])
            data["back_text"] = self._convert_text_format(back.get("body", ""))
            data["back_flavor"] = self._convert_text_format(back.get("flavor", ""))

        # 图片
        data.update(self._get_image_urls())

        return data

    def _convert_treachery(self) -> Dict[str, Any]:
        """转换诡计卡"""
        flags = self._get_special_flags()

        data = {
            "code": self._extract_code_from_gmnotes(),
            "position": self._extract_position(),
            "quantity": self._get_quantity(),
            "name": self._clean_name(self.card_data.get("name", "")),
            "type_code": "treachery",
            "faction_code": "mythos",
            "text": self._convert_text_format(self.card_data.get("body", "")),
            "flavor": self._convert_text_format(self.card_data.get("flavor", "")),
            "deck_limit": 1,
            "is_unique": flags["is_unique"],
            "illustrator": self.card_data.get("illustrator", ""),
            "pack_code": self.pack_code
        }

        # 特性
        if traits := self._get_traits():
            data["traits"] = traits

        # 图片
        data.update(self._get_image_urls())

        return data

    def _convert_scenario(self) -> Dict[str, Any]:
        """转换冒险参考卡"""
        flags = self._get_special_flags()

        data = {
            "code": self._extract_code_from_gmnotes(),
            "position": self._extract_position(),
            "quantity": 1,  # 冒险参考卡固定为1
            "name": self._clean_name(self.card_data.get("name", "")),
            "type_code": "scenario",
            "type_name": "剧本",
            "faction_code": "mythos",
            "text": self._build_scenario_text(),
            "deck_limit": 1,
            "is_unique": flags["is_unique"],
            "illustrator": self.card_data.get("illustrator", ""),
            "pack_code": self.pack_code,
            "double_sided": True
        }

        # 遭遇位置
        encounter_position = self.card_data.get("encounter_group_number", "")
        if encounter_position:
            # 解析 "1/21" 格式
            match = re.search(r'(\d+)/(\d+)', encounter_position)
            if match:
                data["encounter_position"] = int(match.group(1))

        # 背面数据
        if "back" in self.card_data:
            back = self.card_data["back"]
            data["back_text"] = self._build_scenario_text(back)

        # 图片
        data.update(self._get_image_urls())

        return data

    def _build_scenario_text(self, card_data: Dict[str, Any] = None) -> str:
        """构建冒险参考卡的文本内容"""
        if card_data is None:
            card_data = self.card_data

        # 获取难度标签（如 "Easy / Standard" 或 "Hard / Expert"）
        subtitle = card_data.get("subtitle", "")

        # 获取scenario_card中的混沌标记效果
        scenario_card = card_data.get("scenario_card", {})

        text_parts = []

        # 添加难度标签
        if subtitle:
            text_parts.append(subtitle)

        # 混沌标记顺序
        token_order = ["skull", "cultist", "tablet", "elder_thing"]

        # 处理每个混沌标记
        for token_key in token_order:
            if token_key in scenario_card and scenario_card[token_key]:
                effect = scenario_card[token_key]
                # 转换标记名称为显示格式
                token_display = f"[{token_key}]"
                # 转换文本格式
                effect_text = self._convert_text_format(effect)
                text_parts.append(f"{token_display}：{effect_text}")

        return "\n".join(text_parts)

    def _format_encounter_name(self, encounter_code: str) -> str:
        """从遭遇组代码格式化显示名称"""
        # 将下划线替换为空格，首字母大写
        words = encounter_code.replace("_", " ").split()
        return " ".join(word.capitalize() for word in words)

    def _validate_card_data(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证卡牌数据的完整性，确保符合ArkhamDB格式要求

        Args:
            card_data: 待验证的卡牌数据

        Returns:
            验证后的卡牌数据
        """
        import uuid

        # 必要字段及其默认值
        required_defaults = {
            "code": f"CARD{str(uuid.uuid4())[:8].upper()}",
            "position": 1,
            "quantity": 1,
            "name": "Unknown Card",
            "type_code": "skill",
            "faction_code": "neutral",
            "pack_code": self.pack_code,
            "deck_limit": 2
        }

        for field, default in required_defaults.items():
            if field not in card_data or not card_data[field]:
                card_data[field] = default

        # 弱点标记
        if self.card_data.get("class") == "弱点":
            card_data['faction_code'] = 'neutral'
            if self.card_data.get("weakness_type") == '基础弱点':
                card_data["subtype_code"] = "basicweakness"
            else:
                card_data["subtype_code"] = "weakness"

        return card_data
