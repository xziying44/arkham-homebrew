import json
import re
from typing import Dict, Any, Tuple, Optional, List


class ArkhamDBConverter:
    """
    将 ArkhamDB 的 JSON 数据转换为符合前端 cardTypeConfigs.ts 规范的 card 数据对象。
    """

    # 用于将 arkhamdb 的 faction_code/name 映射为目标格式的职阶名
    FACTION_MAP = {
        "guardian": "守卫者",
        "seeker": "探求者",
        "rogue": "流浪者",
        "mystic": "潜修者",
        "survivor": "生存者",
        "neutral": "中立",
        "mythos": "遭遇",  # Mythos cards aren't a class, but map to something
    }

    # 用于将 arkhamdb 的 type_code 映射为目标格式的卡牌类型
    # 注意：这需要根据你的 cardTypeConfigs.ts 进行完整映射
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

    # 用于格式化卡牌效果文本中的图标和标签
    TEXT_FORMAT_MAP = {
        # Actions
        r'\[action\]': '➡️',
        r'\[reaction\]': '⭕',
        r'\[free\]': '⚡',
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
        r'\[rogue\]': '🚶',  # 使用流浪者图标
        r'\[mystic\]': '🧘',  # 使用潜修者图标
        r'\[survivor\]': '🏕️',  # 使用生存者图标
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
        formatted_text = json.dumps(self.data, ensure_ascii=False)
        for pattern, replacement in self.TEXT_FORMAT_MAP.items():
            formatted_text = re.sub(pattern, replacement, formatted_text)

        formatted_text = re.sub(r'\[\[(.*?)]]', r'{\1}', formatted_text)

        self.data = json.loads(formatted_text)
        pass

    def _format_text(self, text: Optional[str]) -> str:
        """
        一个辅助方法，用于格式化文本，替换特殊标记和HTML标签。
        :param text: 原始文本
        :return: 格式化后的文本
        """
        if not text:
            return ""

        # 1. 替换HTML粗体标签为【】
        # formatted_text = re.sub(r'<b>(.*?)</b>', r'【\1】', text)
        formatted_text = text

        # 2. 替换HTML斜体标签为[]（风味文本格式）
        formatted_text = re.sub(r'<i>(.*?)</i>', r'[\1]', formatted_text)

        return formatted_text

    def convert_front(self) -> Optional[Dict[str, Any]]:
        """
        转换卡牌正面数据。
        根据 `type_code` 字段分发到不同的私有转换方法。
        :return: 一个元组，包含 (card_type, card_data)，如果无法转换则返回 (None, None)
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
        # --- 在这里为其他 type_code 添加 elif 分支 ---
        # elif type_code == "asset":
        #     card_data = self._convert_asset_front()
        # elif type_code == "event":
        #     card_data = self._convert_event_front()
        else:
            print(f"警告：尚未实现对 '{type_code}' 类型的正面转换")
            return None

        card_data['type'] = card_type_name

        return card_data

    def convert_back(self) -> Optional[Dict[str, Any]]:
        """
        转换卡牌背面数据。
        仅对 `double_sided` 为 true 的卡牌生效。
        :return: 一个元组，包含 (card_type, card_data)，如果无背面或无法转换则返回 (None, None)
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
        # --- 在这里为其他 type_code 添加 elif 分支 ---
        else:
            print(f"警告：尚未实现对 '{type_code}' 类型的背面转换")
            return None

        card_data['type'] = card_type_name
        return card_data

    # -----------------------------------------------------
    # 私有转换方法区域
    # -----------------------------------------------------

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

        # 属性 (attribute 字段是一个数组)
        card_data["attribute"] = [
            self.data.get("skill_willpower", 0),
            self.data.get("skill_intellect", 0),
            self.data.get("skill_combat", 0),
            self.data.get("skill_agility", 0),
        ]

        # 生命值和理智值
        card_data["health"] = self.data.get("health")
        card_data["horror"] = self.data.get("sanity")

        # 特性 (需要从 "A. B. C" 格式转为 ["A", "B", "C"])
        traits_str = self.data.get("traits", "")
        if traits_str:
            card_data["traits"] = [trait.strip() for trait in traits_str.replace('.', '').split()]
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

        # 背面也需要名称、副标题和职阶
        card_data["name"] = self.data.get("name", "")
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅 {card_data['name']}"
        card_data["subtitle"] = self.data.get("subname", "")
        card_data["class"] = self.FACTION_MAP.get(self.data.get("faction_code"))

        # card_back 是一个嵌套对象
        card_back_data = {}

        # 牌库构建需求与故事文本
        # ArkhamDB的结构化数据不好直接生成名字，我们从back_text中解析
        back_text = self.data.get("back_text", "")

        card_back_data["other"] = back_text
        card_back_data["story"] = self._format_text(self.data.get("back_flavor", ""))

        card_data["card_back"] = card_back_data

        return card_data
