import json
import re
from typing import Dict, Any, Tuple, Optional, List


class ArkhamDBConverter:
    """
    将 ArkhamDB 的 JSON 数据转换为符合前端 cardTypeConfigs.ts 规范的 card 数据对象。
    """

    # 用于将 arkhamdb 的 faction_code/name 映射为目标格式的职阶名
    FACTION_MAP = {
        "guardian": "守护者",
        "seeker": "探求者",
        "rogue": "流浪者",
        "mystic": "潜修者",
        "survivor": "生存者",
        "neutral": "中立",
        "mythos": "遭遇",
    }

    # 用于将 arkhamdb 的 type_code 映射为目标格式的卡牌类型
    TYPE_MAP_FRONT = {
        "investigator": "调查员",
        "asset": "支援卡",
        "event": "事件卡",
        "skill": "技能卡",
        "treachery": "诡计卡",
        "enemy": "敌人卡",
        "location": "地点卡",
        "story": "故事卡"
        # ... 其他类型
    }

    TYPE_MAP_BACK = {
        "investigator": "调查员背面",
        # ... 其他双面卡牌的背面类型
    }

    # 用于槽位映射
    SLOT_MAP = {
        "Ally": "盟友",
        "Body": "身体",
        "Accessory": "饰品",
        "Hand": "手部",
        "Hand x2": "双手",
        "Arcane": "法术",
        "Arcane x2": "双法术",
        "Tarot": "塔罗",
    }

    # 用于格式化卡牌效果文本中的图标和标签
    TEXT_FORMAT_MAP = {
        # Actions
        r'\[action\]': '➡️',
        r'\[reaction\]': '⭕',
        r'\[free\]': '⚡',
        r'\[fast\]': '⚡',
        # Stats
        r'\[willpower\]': '🧠',
        r'\[intellect\]': '📚',
        r'\[combat\]': '👊',
        r'\[agility\]': '🦶',
        r'\[wild\]': '❓',
        # Tokens
        r'\[skull\]': '💀',
        r'\[cultist\]': '👤',
        r'\[tablet\]': '📜',
        r'\[elder_thing\]': '👹',
        r'\[auto_fail\]': '🐙',
        r'\[elder_sign\]': '⭐',
        # Modifiers
        r'\[bless\]': '🌟',
        r'\[curse\]': '🌑',
        # Other
        r'\[guardian\]': '🛡️',
        r'\[seeker\]': '🔍',
        r'\[rogue\]': '🚶',
        r'\[mystic\]': '🧘',
        r'\[survivor\]': '🏕️',
    }

    # span图标映射
    SPAN_ICON_MAP = {
        "icon-reaction": "⭕",
        "icon-action": "➡️",
        "icon-free": "⚡",
        "icon-fast": "⚡",
        "icon-willpower": "🧠",
        "icon-intellect": "📚",
        "icon-combat": "👊",
        "icon-agility": "🦶",
        "icon-wild": "❓",
        "icon-skull": "💀",
        "icon-cultist": "👤",
        "icon-tablet": "📜",
        "icon-elder_thing": "👹",
        "icon-auto_fail": "🐙",
        "icon-elder_sign": "⭐",
        "icon-bless": "🌟",
        "icon-curse": "🌑",
        "icon-guardian": "🛡️",
        "icon-seeker": "🔍",
        "icon-rogue": "🚶",
        "icon-mystic": "🧘",
        "icon-survivor": "🏕️",
    }

    COPYRIGHT_DICT = {
        '01': {'name': '基础', 'year': 2016, 'font_text': '<font name="packicon_coreset">\ue91a</font>'},
        '02': {'name': '敦威治遗产', 'year': 2016, 'font_text': '<font name="dunwich">\uE947</font>'},
        '03': {'name': '卡尔克萨之路', 'year': 2017},
        '04': {'name': '失落的时代', 'year': 2017},
        '05': {'name': '万象无终', 'year': 2018},
        '06': {'name': '食梦者', 'year': 2019},
        '07': {'name': '印斯茅斯的阴谋', 'year': 2020},
        '08': {'name': '暗与地球之界', 'year': 2021},
        '09': {'name': '绯红密钥', 'year': 2022},
        '10': {'name': '铁杉谷盛宴', 'year': 2024},
        '50': {'name': '重返基础', 'year': 2017},
        '51': {'name': '重返敦威治遗产', 'year': 2018},
        '52': {'name': '重返卡尔克萨之路', 'year': 2019},
        '53': {'name': '重返失落的时代', 'year': 2020},
        '54': {'name': '重返万象无终', 'year': 2021},
    }

    COPYRIGHT_DICT_THREE = {
        '601': {'name': '调查员包-守卫者', 'year': 2019},
        '602': {'name': '调查员包-探求者', 'year': 2019},
        '603': {'name': '调查员包-流浪者', 'year': 2019},
        '604': {'name': '调查员包-潜修者', 'year': 2020},
        '605': {'name': '调查员包-生存者', 'year': 2019},
    }

    def __init__(self, arkhamdb_json: Dict[str, Any]):
        """
        构造函数
        :param arkhamdb_json: 从 ArkhamDB API 获取的单张卡牌的 JSON 数据（已转为 Python 字典）
        """
        if not arkhamdb_json or not isinstance(arkhamdb_json, dict):
            raise ValueError("输入的 arkhamdb_json 必须是一个非空字典")
        self.data = arkhamdb_json
        # 将所有null字段删除
        self.data = {k: v for k, v in self.data.items() if v is not None}
        self._format_global()

    def _format_global(self):
        """预处理整个JSON数据，替换所有文本中的图标代码。"""
        formatted_text = json.dumps(self.data, ensure_ascii=False)
        for pattern, replacement in self.TEXT_FORMAT_MAP.items():
            formatted_text = re.sub(pattern, replacement, formatted_text)

        # 转换 [[Trait]] 为 {Trait}
        formatted_text = re.sub(r'\[\[(.*?)]]', r'{\1}', formatted_text)
        formatted_text = formatted_text.replace('‧', '·')

        self.data = json.loads(formatted_text)

    def _format_text(self, text: Optional[str]) -> str:
        """
        一个辅助方法，用于格式化文本，替换特殊标记和HTML标签。
        :param text: 原始文本
        :return: 格式化后的文本
        """
        if not text:
            return ""

        # 1. 处理span图标标签
        def replace_span_icon(match):
            class_attr = match.group(1)
            # 提取class属性中的图标类名
            class_match = re.search(r'class="([^"]*)"', class_attr)
            if class_match:
                classes = class_match.group(1).split()
                for cls in classes:
                    if cls in self.SPAN_ICON_MAP:
                        return self.SPAN_ICON_MAP[cls]
            return ""  # 如果找不到对应图标，返回空字符串

        formatted_text = re.sub(r'<span([^>]*)></span>', replace_span_icon, text)
        # 1. 替换HTML粗体标签为【】
        formatted_text = re.sub(r'<b><i>(.*?)</i></b>', r'{\1}', formatted_text)
        formatted_text = re.sub(r'\[\[(.*?)]]', r'{\1}', formatted_text)
        formatted_text = re.sub(r'<b>(.*?)</b>', r'【\1】', formatted_text)
        formatted_text = re.sub(r'<p>(.*?)</p>', r'\1\n', formatted_text)

        # 2. 替换HTML斜体标签为[]（风味文本格式）
        formatted_text = re.sub(r'<i>.*?(?:FAQ|Erratum).*?</i>', '', formatted_text, flags=re.IGNORECASE)
        formatted_text = re.sub(r'<i>(.*?)</i>', r'[\1]', formatted_text)
        formatted_text = formatted_text.replace('\n<cite>', '<cite>')
        formatted_text = re.sub(r'<cite>(.*?)</cite>', r'<br>[-\1]', formatted_text)
        formatted_text = re.sub(r'\[([^]]+)]', r'<i>\1</i>', formatted_text)

        formatted_text = re.sub(r'\n- ', r"\n<点> ", formatted_text)
        formatted_text = re.sub(r'\n-', r"\n<点> ", formatted_text)

        return formatted_text

    def _extract_common_player_card_properties(self) -> Dict[str, Any]:
        """
        提取所有玩家卡（支援、事件、技能）通用的属性。
        包括：名称、副标题、职阶（处理多职阶）、等级、费用、投入图标、特性。
        """
        card_data = {}

        # 标题、副标题
        card_data["name"] = self.data.get("name", "")
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"
        if self.data.get("subname"):
            card_data["subtitle"] = self.data.get("subname")

        # 职阶 (处理弱点和多职阶)
        if self.data.get("subtype_code") == 'weakness':
            card_data["class"] = '弱点'
        elif self.data.get("subtype_code") == 'basicweakness':
            card_data["class"] = '弱点'
            card_data["weakness_type"] = '基础弱点'
        else:
            faction_codes = ["faction_code", "faction2_code", "faction3_code"]
            factions = [
                self.FACTION_MAP.get(self.data[code])
                for code in faction_codes if self.data.get(code)
            ]

            if len(factions) > 1:
                card_data["class"] = "多职阶"
                card_data["subclass"] = factions
            elif len(factions) == 1:
                card_data["class"] = factions[0]
            else:
                card_data["class"] = "中立"

        # 等级
        level = self.data.get("xp")
        card_data["level"] = level if level is not None else -1

        # 费用
        if 'cost' in self.data:
            cost = self.data.get('cost')
            card_data['cost'] = -2 if cost is None else cost  # -2 for X Cost
        else:
            card_data['cost'] = -1  # -1 for No Cost (e.g., Skills)

        # 投入图标
        icons = []
        for _ in range(self.data.get("skill_willpower", 0)):
            icons.append("意志")
        for _ in range(self.data.get("skill_intellect", 0)):
            icons.append("智力")
        for _ in range(self.data.get("skill_combat", 0)):
            icons.append("战力")
        for _ in range(self.data.get("skill_agility", 0)):
            icons.append("敏捷")
        for _ in range(self.data.get("skill_wild", 0)):
            icons.append("狂野")
        card_data["submit_icon"] = icons

        # 特性
        traits_str = self.data.get("traits", "")
        if traits_str:
            card_data["traits"] = [trait.strip() for trait in traits_str.replace('.', ' ').split() if trait.strip()]
        else:
            card_data["traits"] = []

        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["is_encounter"] = True

        return card_data

    # -----------------------------------------------------
    # 公共转换方法
    # -----------------------------------------------------

    def registered_base_mark_information(self, card_data: Optional[Dict[str, Any]]):
        """注册底标信息"""
        type_code = self.data.get("type_code")
        if type_code in ['investigator', 'enemy']:
            return
        card_data['illustrator'] = self.data.get("illustrator", '')
        card_data['card_number'] = str(self.data.get("position", ''))

        # 获取版权年份
        pack_code = self.data['code'][:2]
        pack_code_three = self.data['code'][:2]
        middle_text = ''
        footer_icon_font = ''
        if self.data['code'][:2] in self.COPYRIGHT_DICT:
            middle_text = f"© {self.COPYRIGHT_DICT[pack_code]['year']} FFG"
            footer_icon_font = self.COPYRIGHT_DICT[pack_code]['font_text']
        elif pack_code_three in self.COPYRIGHT_DICT_THREE:
            middle_text = f"© {self.COPYRIGHT_DICT_THREE[pack_code_three]['year']} FFG"
            footer_icon_font = self.COPYRIGHT_DICT_THREE[pack_code_three]['font_text']
        card_data['footer_copyright'] = middle_text
        card_data['footer_icon_font'] = footer_icon_font

    def convert_front(self) -> Optional[Dict[str, Any]]:
        """
        转换卡牌正面数据。
        """
        type_code = self.data.get("type_code")
        if self.data.get('real_name') == self.data.get('name'):
            return None
        if not type_code:
            return None
        card_type_name = self.TYPE_MAP_FRONT.get(type_code)
        if not card_type_name:
            print(f"警告：未知的正面卡牌类型代码 '{type_code}'")
            return None
        if type_code == "investigator":
            card_data = self._convert_investigator_front()
        elif type_code == "asset":
            card_data = self._convert_asset_front()
        elif type_code == "event":
            card_data = self._convert_event_front()
        elif type_code == "skill":
            card_data = self._convert_skill_front()
        elif type_code == "treachery":
            card_data = self._convert_treachery_front()
        elif type_code == "enemy":
            card_data = self._convert_enemy_front()
        else:
            print(f"警告：尚未实现对 '{type_code}' 类型的正面转换")
            return None
        card_data['type'] = card_type_name
        # 获取底标数据
        self.registered_base_mark_information(card_data)
        return card_data

    def convert_back(self) -> Optional[Dict[str, Any]]:
        """
        转换卡牌背面数据。
        """
        if 'linked_card' in self.data:
            back_data = ArkhamDBConverter(self.data['linked_card'])
            return back_data.convert_front()
        if not self.data.get("double_sided"):
            return None

        type_code = self.data.get("type_code")
        if not type_code:
            return None

        card_type_name = self.TYPE_MAP_BACK.get(type_code)
        if not card_type_name:
            print(f"警告：未知的背面卡牌类型代码 '{type_code}'")
            return None

        if type_code == "investigator":
            card_data = self._convert_investigator_back()
        else:
            print(f"警告：尚未实现对 '{type_code}' 类型的背面转换")
            return None

        card_data['type'] = card_type_name
        return card_data

    # -----------------------------------------------------
    # 私有转换方法区域
    # -----------------------------------------------------

    def _convert_asset_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换支援卡正面。
        """
        # 1. 获取所有玩家卡通用属性
        card_data = self._extract_common_player_card_properties()

        # 2. 添加支援卡特有的属性
        # 生命值和理智值
        health = self.data.get("health")
        card_data["health"] = health if health is not None else -1
        sanity = self.data.get("sanity")
        card_data["horror"] = sanity if sanity is not None else -1

        # 槽位
        slot_str = self.data.get("real_slot", "")
        card_data["slots"] = None
        card_data["slots2"] = None
        if slot_str:
            if slot_str in self.SLOT_MAP:
                # 处理单槽位或特殊槽位 (如 "Hand x2")
                card_data["slots"] = self.SLOT_MAP.get(slot_str)
            else:
                # 处理复合槽位 (如 "Hand. Arcane")
                slot_parts = [p.strip() for p in slot_str.split('.')]
                if len(slot_parts) == 1:
                    card_data["slots"] = self.SLOT_MAP.get(slot_parts[0])
                if len(slot_parts) == 2:
                    card_data["slots"] = self.SLOT_MAP.get(slot_parts[1])
                    card_data["slots2"] = self.SLOT_MAP.get(slot_parts[0])

        # 效果、风味文本、胜利点和遭遇组
        card_data["body"] = self._format_text(self.data.get("text"))
        card_data["flavor"] = self._format_text(self.data.get("flavor"))

        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")

        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self.data.get("encounter_name")

        return card_data

    def _convert_investigator_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换调查员正面。
        """
        card_data = {}

        # 基础信息
        card_data["name"] = self.data.get("name", "")
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"
        card_data["subtitle"] = self.data.get("subname", "")
        card_data["class"] = self.FACTION_MAP.get(self.data.get("faction_code"))

        # 属性
        card_data["attribute"] = [
            self.data.get("skill_willpower", 0),
            self.data.get("skill_intellect", 0),
            self.data.get("skill_combat", 0),
            self.data.get("skill_agility", 0),
        ]

        # 生命值和理智值
        card_data["health"] = self.data.get("health")
        card_data["horror"] = self.data.get("sanity")

        # 特性
        traits_str = self.data.get("traits", "")
        if traits_str:
            card_data["traits"] = [trait.strip() for trait in traits_str.replace('.', ' ').split() if trait.strip()]
        else:
            card_data["traits"] = []

        # 卡牌效果和风味文本
        card_data["body"] = self._format_text(self.data.get("text"))
        card_data["flavor"] = self._format_text(self.data.get("flavor"))

        return card_data

    def _convert_investigator_back(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换调查员背面。
        """
        card_data = {}

        # 背面基础信息
        card_data["name"] = self.data.get("name", "")
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"
        card_data["subtitle"] = self.data.get("subname", "")
        card_data["class"] = self.FACTION_MAP.get(self.data.get("faction_code"))

        # 牌库构建需求与故事文本
        card_back_data = {}
        back_text = self.data.get("back_text", "")
        card_back_data["other"] = self._format_text(back_text)
        card_back_data["story"] = self._format_text(self.data.get("back_flavor", ""))
        card_data["card_back"] = card_back_data

        return card_data

    def _convert_event_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换事件卡正面。
        """
        # 1. 获取所有玩家卡通用属性
        card_data = self._extract_common_player_card_properties()
        # 2. 添加事件卡特有的属性
        # 效果、风味文本、胜利点和遭遇组
        card_data["body"] = self._format_text(self.data.get("text"))
        card_data["flavor"] = self._format_text(self.data.get("flavor"))
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self.data.get("encounter_name")
        return card_data

    def _convert_skill_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换技能卡正面。
        """
        # 1. 获取所有玩家卡通用属性
        card_data = self._extract_common_player_card_properties()
        # 2. 添加技能卡特有的属性
        # 效果、风味文本、胜利点和遭遇组
        card_data["body"] = self._format_text(self.data.get("text"))
        card_data["flavor"] = self._format_text(self.data.get("flavor"))
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self.data.get("encounter_name")
        return card_data

    def _convert_treachery_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换诡计卡正面。
        """
        # 1. 获取所有玩家卡通用属性
        card_data = self._extract_common_player_card_properties()
        # 效果、风味文本和胜利点
        card_data["body"] = self._format_text(self.data.get("text"))
        card_data["flavor"] = self._format_text(self.data.get("flavor"))
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        return card_data

    def _format_compound_number(self, value_key: str, per_investigator_key: str) -> Optional[str]:
        """
        格式化一个可能为 "X" 或 "每位调查员" 的数值。
        :param value_key: ArkhamDB JSON 中基础数值的键名 (e.g., 'health')
        :param per_investigator_key: ArkhamDB JSON 中 "每位调查员" 标记的键名 (e.g., 'health_per_investigator')
        :return: 格式化后的字符串 (e.g., '3', 'X', '2<调查员>')
        """
        if value_key not in self.data:
            return None
        value = self.data.get(value_key)
        if value is None:
            return "X"  # ArkhamDB 使用 null 来表示 'X'
        value_str = str(value)
        if self.data.get(per_investigator_key, False):
            return f"{value_str}<调查员>"
        return value_str

    def _convert_enemy_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换敌人卡正面。
        """
        # 1. 获取所有玩家卡通用属性
        card_data = self._extract_common_player_card_properties()
        # 敌人数值 (攻击、生命、躲避)
        # 注意: ArkhamDB JSON 通常只对 health 有 per_investigator 标记
        card_data["attack"] = self._format_compound_number("enemy_fight", "fight_per_investigator")
        card_data["enemy_health"] = self._format_compound_number("health", "health_per_investigator")
        card_data["evade"] = self._format_compound_number("enemy_evade", "evade_per_investigator")
        # 伤害和恐惧
        if self.data.get("enemy_damage") is not None:
            card_data["enemy_damage"] = self.data.get("enemy_damage")
        if self.data.get("enemy_horror") is not None:
            # 前端 key 是 'enemy_damage_horror'
            card_data["enemy_damage_horror"] = self.data.get("enemy_horror")
        # 特性
        traits_str = self.data.get("traits", "")
        if traits_str:
            card_data["traits"] = [trait.strip() for trait in traits_str.replace('.', ' ').split() if trait.strip()]
        else:
            card_data["traits"] = []
        # 效果、风味文本和胜利点
        card_data["body"] = self._format_text(self.data.get("text"))
        card_data["flavor"] = self._format_text(self.data.get("flavor"))
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        return card_data
