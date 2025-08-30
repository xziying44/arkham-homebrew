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

    def __init__(self, arkhamdb_json: Dict[str, Any]):
        """
        构造函数
        :param arkhamdb_json: 从 ArkhamDB API 获取的单张卡牌的 JSON 数据（已转为 Python 字典）
        """
        if not arkhamdb_json or not isinstance(arkhamdb_json, dict):
            raise ValueError("输入的 arkhamdb_json 必须是一个非空字典")
        self.data = arkhamdb_json
        self._format_global()

    def _format_global(self):
        """预处理整个JSON数据，替换所有文本中的图标代码。"""
        formatted_text = json.dumps(self.data, ensure_ascii=False)
        for pattern, replacement in self.TEXT_FORMAT_MAP.items():
            formatted_text = re.sub(pattern, replacement, formatted_text)

        # 转换 [[Trait]] 为 {Trait}
        formatted_text = re.sub(r'\[\[(.*?)]]', r'{\1}', formatted_text)

        self.data = json.loads(formatted_text)

    def _format_text(self, text: Optional[str]) -> str:
        """
        一个辅助方法，用于格式化文本，替换特殊标记和HTML标签。
        :param text: 原始文本
        :return: 格式化后的文本
        """
        if not text:
            return ""

        # 1. 替换HTML粗体标签为【】
        formatted_text = re.sub(r'<b>(.*?)</b>', r'【\1】', text)

        # 2. 替换HTML斜体标签为[]（风味文本格式）
        formatted_text = re.sub(r'<i>(.*?)</i>', r'[\1]', formatted_text)

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
            card_data["name"] = f"🏅 {card_data['name']}"
        if self.data.get("subname"):
            card_data["subtitle"] = self.data.get("subname")

        # 职阶 (处理弱点和多职阶)
        if self.data.get("subtype_code") == 'weakness':
            card_data["class"] = '弱点'
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

        return card_data

    # -----------------------------------------------------
    # 公共转换方法
    # -----------------------------------------------------

    def convert_front(self) -> Optional[Dict[str, Any]]:
        """
        转换卡牌正面数据。
        """
        type_code = self.data.get("type_code")
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
        # elif type_code == "event":
        #     card_data = self._convert_event_front()  # 未来可在此处添加
        # elif type_code == "skill":
        #     card_data = self._convert_skill_front()  # 未来可在此处添加
        else:
            print(f"警告：尚未实现对 '{type_code}' 类型的正面转换")
            return None

        card_data['type'] = card_type_name
        return card_data

    def convert_back(self) -> Optional[Dict[str, Any]]:
        """
        转换卡牌背面数据。
        """
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
            card_data["name"] = f"🏅 {card_data['name']}"
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
            card_data["name"] = f"🏅 {card_data['name']}"
        card_data["subtitle"] = self.data.get("subname", "")
        card_data["class"] = self.FACTION_MAP.get(self.data.get("faction_code"))

        # 牌库构建需求与故事文本
        card_back_data = {}
        back_text = self.data.get("back_text", "")
        card_back_data["other"] = self._format_text(back_text)
        card_back_data["story"] = self._format_text(self.data.get("back_flavor", ""))
        card_data["card_back"] = card_back_data

        return card_data
