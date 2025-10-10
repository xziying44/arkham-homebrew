import json
import re
from typing import Dict, Any, Tuple, Optional, List


class ArkhamDBConverter:
    """
    将 ArkhamDB 的 JSON 数据转换为符合前端 cardTypeConfigs.ts 规范的 card 数据对象。
    """

    # 类变量：存储遭遇组信息索引
    _encounter_group_index: Dict[str, str] = {}

    # 类变量：存储gmnotes索引数据
    _gmnotes_index: Dict[str, Any] = {}

    # 类变量：存储地点图标映射数据
    _location_icons_mapping: Dict[str, str] = {}

    # 类变量：存储完整数据库引用，用于查找linked_to_code
    _full_database: List[Dict[str, Any]] = []

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
        "story": "故事卡",
        "act": "场景卡",
        "agenda": "密谋卡",
        "scenario": "冒险参考卡"
        # ... 其他类型
    }

    TYPE_MAP_BACK = {
        "investigator": "调查员背面",
        "location": "地点卡",
        "act": "场景卡",
        "agenda": "密谋卡"
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
        r'\[per_investigator\]': '🕵️',
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

    # 遭遇组code到图标名称的映射
    ENCOUNTER_GROUP_MAP = {
        "torch": "the_gathering",
        "arkham": "midnight_masks",
        "cultists": "cult_of_umordoth",
        "tentacles": "the_devourer_below",
        "pentagram": "dark_cult",
        "bayou": "the_bayou",
        "rougarou": "curse_of_the_rougarou",
        "essex_county_express": "the_essex_county_express",
        "decay": "decay_and_filth",
        "stranger": "the_stranger",
        "flood": "the_flood_below",
        "vortex": "the_vortex_above",
        "traps": "deadly_traps",
        "expedition": "expedition",
        "ruins": "forgotten_ruins",
        "flux": "temporal_flux",
        "eztli": "the_doom_of_eztli",
        "wilds": "the_untamed_wilds",
        "venom": "yigs_venom",
        "the_city_of_archives": "city_of_archives",
        "the_eternal_slumber": "eternal_slumber",
        "the_nights_usurper": "nights_usurper",
        "ghouls_of_umôrdhoth": "ghouls_of_umrdhoth",
        "return_to_a_phantom_of_truth": "return_to_the_phantom_of_truth",
        "where_the_gods_dwell": "where_gods_dwell",
        "murder_at_the_excelsior_hotel": "excelsior",
        "blob_epic_multiplayer": "epic_multiplayer",
        "machinations_through_time_epic_multiplayer": "epic_multiplayer",
        "blob_single_group": "single_group",
        "machinations_through_time_single_group": "single_group",
        "migo_incursion": "migo",
        "return_to_heart_of_the_elders": "return_to_the_heart_of_the_elders",
        "return_to_pillars_of_judgment": "return_to_pillars_of_judgement",
        "return_to_the_city_of_archives": "return_to_city_of_archives",
        "the_pit_of_despair": "grotto_of_despair",
        "creatures_of_the_deep": "creatures_from_below",
        "flooded_caverns": "flooded_caves",
        "the_locals": "locals",
        "the_vanishing_of_elina_harper": "disappearance_of_elina_harper",
        "the_lair_of_dagon": "lair_of_dagon",
        "death_of_stars": "death_of_the_stars",
        "swarm_of_assimilation": "assimilating_swarm",
        "hexcraft": "witchwork",
        "unstable_realm": "spectral_realm",
        "chilling_mists": "cold_fog",
        "impending_evils": "threatening_evil",
        "seeping_nightmares": "sleeping_nightmares",
        "tekelili": "tekeli_li",
        "shades_of_suffering": "shades_of_sorrow",
        "relics_of_the_past": "rop",
        "blob_that_ate_everything_else": "blob_that_ate_everything_else",
        "migo_incursion_2": "migo_incursion_2",
        "the_midwinter_gala": "gala",
        "film_fatale": "film_fatale_encounter",
    }

    COPYRIGHT_DICT = {
        '01': {'name': '基础', 'year': 2016, 'font_text': '<font name="packicon_coreset">\ue91a</font>'},
        '02': {'name': '敦威治遗产', 'year': 2016, 'font_text': '<font name="packicon_dunwich">\uE947</font>'},
        '03': {'name': '卡尔克萨之路', 'year': 2017, 'font_text': '<font name="packicon_carcosa">\uE94C</font>'},
        '04': {'name': '失落的时代', 'year': 2017, 'font_text': '<font name="packicon_forgotten">\uE900</font>'},
        '05': {'name': '万象无终', 'year': 2018, 'font_text': '<font name="packicon_circle">\uE900</font>'},
        '06': {'name': '食梦者', 'year': 2019, 'font_text': '<font name="packicon_dreameaters">\uE900</font>'},
        '07': {'name': '印斯茅斯的阴谋', 'year': 2020, 'font_text': '<font name="packicon_innsmouth">A</font>'},
        '08': {'name': '暗与地球之界', 'year': 2021, 'font_text': '<font name="packicon_edge">\uE900</font>'},
        '09': {'name': '绯红密钥', 'year': 2022, 'font_text': '<font name="packicon_scarlet">\uE900</font>'},
        '10': {'name': '铁杉谷盛宴', 'year': 2024, 'font_text': '<font name="packicon_hemlock">\uE9B9</font>'},
        '50': {'name': '重返基础', 'year': 2017, 'font_text': '<font name="packicon_coreset">\uE90A</font>'},
        '51': {'name': '重返敦威治遗产', 'year': 2018, 'font_text': '<font name="packicon_dunwich">\uE91B</font>'},
        '52': {'name': '重返卡尔克萨之路', 'year': 2019, 'font_text': '<font name="packicon_carcosa">\uE903</font>'},
        '53': {'name': '重返失落的时代', 'year': 2020, 'font_text': '<font name="packicon_forgotten">\uE917</font>'},
        '54': {'name': '重返万象无终', 'year': 2021, 'font_text': '<font name="packicon_circle">\uE916</font>'},
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
        formatted_text = formatted_text.replace('（', '(')
        formatted_text = formatted_text.replace('）', ')')
        formatted_text = formatted_text.replace('?', '？')

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
        formatted_text = re.sub(r'<blockquote><i>(.*?)</i></blockquote>',
                                r'<flavor quote="true" padding="20" flavor align="left" flex="false">\1</flavor>',
                                formatted_text)
        # 1. 替换HTML粗体标签为【】
        formatted_text = re.sub(r'<b><i>(.*?)</i></b>', r'{\1}', formatted_text)
        formatted_text = re.sub(r'\[\[(.*?)]]', r'{\1}', formatted_text)
        formatted_text = re.sub(r'<b>(.*?)</b>', r'【\1】', formatted_text)
        formatted_text = re.sub(r'<p>(.*?)</p>', r'\1\n', formatted_text)

        # 2. 替换HTML斜体标签为[]（风味文本格式）
        formatted_text = re.sub(r'<i>(?:(?!</i>).)*?(?:FAQ|Erratum)(?:(?!</i>).)*?</i>', '', formatted_text,
                                flags=re.IGNORECASE)
        formatted_text = re.sub(r'<i>(.*?)</i>', r'[\1]', formatted_text)
        formatted_text = formatted_text.replace('\n<cite>', '<cite>')
        formatted_text = re.sub(r'<cite>(.*?)</cite>', r'<br>[-\1]', formatted_text)
        formatted_text = re.sub(r'\[([^]]+)]', r'<i>\1</i>', formatted_text)

        formatted_text = re.sub(r'\n- ', r"\n<点> ", formatted_text)
        formatted_text = re.sub(r'\n-', r"\n<点> ", formatted_text)

        formatted_text = re.sub(r'^- ', r"<点> ", formatted_text)
        formatted_text = re.sub(r'^-(?![0-9X])', r"<点> ", formatted_text)

        return formatted_text

    def _format_flavor_text(self, text: Optional[str]) -> str:
        """
        专门用于格式化风味文本的方法，对_format_text的包装，进行额外的特殊处理。
        :param text: 原始风味文本
        :return: 格式化后的风味文本
        """
        if not text:
            return ""

        # 先使用通用的文本格式化
        formatted_text = self._format_text(text)

        # 1. 删除所有换行
        formatted_text = formatted_text.replace('\n', '')

        # 2. 将<cite>XXXX</cite>内容转化为\n——XXXX
        def replace_cite_content(match):
            cite_content = match.group(1)
            return f'\n——{cite_content}'

        formatted_text = re.sub(r'<cite>(.*?)</cite>', replace_cite_content, formatted_text)

        return formatted_text

    def _convert_encounter_group_code(self, encounter_code: str) -> str:
        """
        转换遭遇组代码为对应的图标名称
        
        Args:
            encounter_code: 原始遭遇组代码
            
        Returns:
            转换后的图标名称，如果不在映射表中则返回原始代码
        """
        return self.ENCOUNTER_GROUP_MAP.get(encounter_code, encounter_code)

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
    # 遭遇组统计方法
    # -----------------------------------------------------

    @classmethod
    def calculate_encounter_group_statistics(cls, all_cards: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        计算所有卡牌的遭遇组统计信息
        
        Args:
            all_cards: 所有卡牌的列表
            
        Returns:
            遭遇组信息索引字典，key为card code，val为遭遇组信息
        """
        # 1. 首先找出所有有linked_card的卡牌对，避免重复计算
        linked_cards = set()
        for card in all_cards:
            linked_card = card.get('linked_card')
            if linked_card and isinstance(linked_card, dict):
                linked_card_code = linked_card.get('code')
                if linked_card_code:
                    # 将两个code都加入集合，表示它们是关联的
                    linked_cards.add(card.get('code'))
                    linked_cards.add(linked_card_code)

        # 2. 计算每个遭遇组的总数量，排除linked_card的重复计算
        encounter_group_totals = {}

        for card in all_cards:
            card_code = card.get('code')
            encounter_code = card.get('encounter_code')

            # 跳过linked_card中的副卡（只计算主卡）
            if card_code in linked_cards:
                # 检查是否是主卡（有linked_card字段的卡）
                if not card.get('linked_card'):
                    continue  # 跳过副卡

            if encounter_code and encounter_code.strip():  # 确保encounter_code存在且不为空
                quantity = card.get('quantity', 1)
                if encounter_code not in encounter_group_totals:
                    encounter_group_totals[encounter_code] = 0
                encounter_group_totals[encounter_code] += quantity

        # 3. 为每张卡生成遭遇组信息
        encounter_group_index = {}

        for card in all_cards:
            card_code = card.get('code')
            encounter_code = card.get('encounter_code')
            encounter_position = card.get('encounter_position')
            quantity = card.get('quantity', 1)

            # 只有encounter_code存在且不为空才能计算
            if encounter_code and encounter_code.strip() and card_code:
                total_count = encounter_group_totals.get(encounter_code, 0)

                if total_count > 0 and encounter_position is not None:
                    # 生成遭遇组信息
                    if quantity > 1:
                        # quantity大于1时显示范围信息：x-x/x
                        end_position = encounter_position + quantity - 1
                        group_info = f"{encounter_position}-{end_position}/{total_count}"
                    else:
                        # quantity为1时显示：x/x
                        group_info = f"{encounter_position}/{total_count}"

                    encounter_group_index[card_code] = group_info

        return encounter_group_index

    @classmethod
    def set_encounter_group_index(cls, encounter_group_index: Dict[str, str]):
        """
        设置遭遇组信息索引
        
        Args:
            encounter_group_index: 遭遇组信息索引字典
        """
        cls._encounter_group_index = encounter_group_index

    @classmethod
    def get_encounter_group_info(cls, card_code: str) -> Optional[str]:
        """
        获取指定卡牌的遭遇组信息
        
        Args:
            card_code: 卡牌代码
            
        Returns:
            遭遇组信息字符串，如果不存在则返回None
        """
        return cls._encounter_group_index.get(card_code)

    # -----------------------------------------------------
    # 地点图标映射方法
    # -----------------------------------------------------

    @classmethod
    def load_gmnotes_index(cls, gmnotes_file_path: str = "gmnotes_index.json"):
        """
        加载gmnotes_index.json文件
        
        Args:
            gmnotes_file_path: gmnotes_index.json文件路径
        """
        try:
            import os
            if os.path.exists(gmnotes_file_path):
                with open(gmnotes_file_path, 'r', encoding='utf-8') as f:
                    cls._gmnotes_index = json.load(f)
                print(f"成功加载gmnotes索引数据: {len(cls._gmnotes_index)} 条记录")
            else:
                print(f"警告: gmnotes索引文件不存在: {gmnotes_file_path}")
                cls._gmnotes_index = {}
        except Exception as e:
            print(f"加载gmnotes索引文件失败: {e}")
            cls._gmnotes_index = {}

    @classmethod
    def load_location_icons_mapping(cls, mapping_file_path: str = "location_icons_mapping.json"):
        """
        加载location_icons_mapping.json文件
        
        Args:
            mapping_file_path: location_icons_mapping.json文件路径
        """
        try:
            import os
            if os.path.exists(mapping_file_path):
                with open(mapping_file_path, 'r', encoding='utf-8') as f:
                    cls._location_icons_mapping = json.load(f)
                print(f"成功加载地点图标映射数据: {len(cls._location_icons_mapping)} 条映射")
            else:
                print(f"警告: 地点图标映射文件不存在: {mapping_file_path}")
                cls._location_icons_mapping = {}
        except Exception as e:
            print(f"加载地点图标映射文件失败: {e}")
            cls._location_icons_mapping = {}

    @classmethod
    def get_location_icon_mapping(cls, icon_code: str) -> Optional[str]:
        """
        获取图标代码对应的图标名称
        
        Args:
            icon_code: 图标代码
            
        Returns:
            图标名称，如果不存在或为空则返回None
        """
        icon_name = cls._location_icons_mapping.get(icon_code)
        if icon_name and icon_name.strip():  # 确保图标名称不为空
            return icon_name
        return None

    @classmethod
    def set_full_database(cls, full_database: List[Dict[str, Any]]):
        """
        设置完整数据库引用，用于查找linked_to_code
        
        Args:
            full_database: 完整的卡牌数据库列表
        """
        cls._full_database = full_database

    @classmethod
    def find_card_by_linked_to_code(cls, target_code: str) -> Optional[Dict[str, Any]]:
        """
        在完整数据库中查找linked_to_code指向指定代码的卡牌
        
        Args:
            target_code: 目标卡牌代码
            
        Returns:
            找到的卡牌数据，如果不存在则返回None
        """
        for card in cls._full_database:
            linked_to_code = card.get('linked_to_code')
            if linked_to_code == target_code:
                return card
        return None

    def _extract_location_icons_from_gmnotes(self, card_code: str, is_back: bool = False) -> tuple[dict[Any, Any], str]:
        """
        从gmnotes_index.json中提取地点图标信息

        Args:
            card_code: 卡牌代码
            is_back: 是否为背面

        Returns:
            包含location_icon和location_link的字典
        """
        direction = ''
        result = {}

        # 获取gmnotes数据
        gmnotes_data = self._gmnotes_index.get(card_code)
        if not gmnotes_data:
            return result, direction

        # 检查是否为地点类型
        if gmnotes_data.get("type") != "Location":
            return result, direction

        # 根据是否为背面选择对应的数据
        location_data = None
        if 'locationFront' in gmnotes_data and 'locationBack' not in gmnotes_data:
            location_data = gmnotes_data['locationFront']
            direction = 'front'
        elif 'locationFront' not in gmnotes_data and 'locationBack' in gmnotes_data:
            location_data = gmnotes_data['locationBack']
            direction = 'back'
        else:
            if is_back:
                location_data = gmnotes_data.get("locationFront")
                direction = 'front'
            else:
                location_data = gmnotes_data.get("locationBack")
                direction = 'back'

        if not location_data:
            return result, direction

        # 处理地点图标
        icons_str = location_data.get("icons", "")
        if icons_str:
            # 分割多个图标代码（用|分隔）
            icon_codes = [code.strip() for code in icons_str.split("|") if code.strip()]
            for icon_code in icon_codes:
                icon_name = self.get_location_icon_mapping(icon_code)
                if icon_name:
                    result["location_icon"] = icon_name
                    break  # 只取第一个有效图标

        # 处理连接图标
        connections_str = location_data.get("connections", "")
        if connections_str:
            # 分割多个连接图标代码（用|分隔）
            connection_codes = [code.strip() for code in connections_str.split("|") if code.strip()]
            connection_names = []
            for connection_code in connection_codes:
                connection_name = self.get_location_icon_mapping(connection_code)
                if connection_name:
                    connection_names.append(connection_name)

            if connection_names:
                result["location_link"] = connection_names

        return result, direction

    def _apply_special_card_handling(self, card_data: Dict[str, Any], is_back: bool = False) -> Dict[str, Any]:
        """
        对特定卡牌进行特殊处理的统一方法

        Args:
            card_data: 已转换的卡牌数据
            is_back: 是否为背面

        Returns:
            经过特殊处理的卡牌数据
        """
        card_code = self.data.get("code", "")

        # 特殊处理：code==01145 的背面设置 type 为"场景卡-大画"
        if card_code in ["01145", "02314", "04048", "04049", "04318","03322a","03323a"] and is_back:
            card_data["type"] = "场景卡-大画"
            card_data["footer_copyright"] = ""
            card_data["footer_icon_font"] = ""
            card_data["encounter_group_number"] = ""
            card_data["illustrator"] = ""
            card_data["card_number"] = ""
        if card_code in ['04121', '04122', '04210', '04214'] and not is_back:
            card_data["threshold"] = "-"

        if card_code == '04277':
            card_data["scenario_type"] = 1
            card_data["scenario_card"]['resource_name'] = '当前深度'

        if card_code in ['04125a', '04126a', '04127', '04128a', '04129', '04130a', '04131',
                         '04132', '03278', '03279a', '03280', '03282'] and 'serial_number' in card_data:
            if is_back:
                card_data["serial_number"] = card_data["serial_number"].replace('b', 'd')
            else:
                card_data["serial_number"] = card_data["serial_number"].replace('a', 'c')

        if card_code in ['04133a', '04134a', '04135', '04136', '04137a', '04138', '04139',
                         '04140'] and 'serial_number' in card_data:
            if is_back:
                card_data["serial_number"] = card_data["serial_number"].replace('b', 'f')
            else:
                card_data["serial_number"] = card_data["serial_number"].replace('a', 'e')

        if card_code == '02292':
            card_data["flavor"] = card_data["flavor"].replace(
                "这<i>【不可能】</i>在这儿！",
                '这<font name="江城斜宋体">不可能</font>在这儿！')
        if card_code in ['03062', '03318'] and is_back:
            card_data["flavor"] = card_data["flavor"].replace(
                "现在【真正的】晚宴终于可以开始了",
                '现在<font name="江城斜宋体">真正的</font>晚宴终于可以开始了')

        # 密谋调查员数
        if card_code in ['03121', '03122', '03123'] and not is_back:
            card_data['threshold'] = card_data["threshold"] + '<调查员>'

        if card_code in ['03278', '03279a', '03280', '03281'] and not is_back:
            card_data['mirror'] = True

        if card_code in ['03283', '03284'] and is_back:
            card_data["flavor"] = card_data["flavor"].split("<hr>")[0]

        # 可以在这里添加更多特殊处理逻辑
        # 例如：
        # if card_code == "xxxxx" and is_back:
        #     card_data["some_field"] = "some_value"

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

        # 添加遭遇组信息
        card_code = self.data.get('code')
        if card_code:
            encounter_group_info = self.get_encounter_group_info(card_code)
            if encounter_group_info:
                card_data['encounter_group_number'] = encounter_group_info
            else:
                card_data['encounter_group_number'] = ''

    def convert_customization(self) -> Optional[Dict[str, Any]]:
        """转化定制卡"""
        card_data = {}
        # 基础信息
        card_data["type"] = '定制卡'
        card_data["name"] = self.data.get("name", "")
        card_data["body"] = self._format_text(self.data.get("customization_text"))
        # 获取版权年份
        pack_code = self.data['code'][:2]
        pack_code_three = self.data['code'][:2]
        middle_text = ''
        if self.data['code'][:2] in self.COPYRIGHT_DICT:
            middle_text = f"© {self.COPYRIGHT_DICT[pack_code]['year']} FFG"
        elif pack_code_three in self.COPYRIGHT_DICT_THREE:
            middle_text = f"© {self.COPYRIGHT_DICT_THREE[pack_code_three]['year']} FFG"
        card_data['footer_copyright'] = middle_text
        return card_data

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
        elif type_code == "event":
            card_data = self._convert_event_front()
        elif type_code == "skill":
            card_data = self._convert_skill_front()
        elif type_code == "treachery":
            card_data = self._convert_treachery_front()
        elif type_code == "enemy":
            card_data = self._convert_enemy_front()
        elif type_code == "location":  # 新增地点卡处理
            card_data = self._convert_location_front()
        elif type_code == "act":  # 新增场景卡处理
            card_data = self._convert_act_front()
        elif type_code == "agenda":  # 新增密谋卡处理
            card_data = self._convert_agenda_front()
        elif type_code == "scenario":  # 新增冒险参考卡处理
            card_data = self._convert_scenario_front()
        elif type_code == "story":
            card_data = self._convert_story_front()
        else:
            print(f"警告：尚未实现对 '{type_code}' 类型的正面转换")
            return None
        card_data['type'] = card_type_name
        # 获取底标数据
        self.registered_base_mark_information(card_data)
        # 应用特殊卡牌处理
        card_data = self._apply_special_card_handling(card_data, is_back=False)
        return card_data

    def convert_back(self) -> Optional[Dict[str, Any]]:
        """
        转换卡牌背面数据。
        """
        type_code = self.data.get("type_code")
        card_type_name = self.TYPE_MAP_FRONT.get(type_code)
        if self.data.get('double_sided'):
            # 双面对象
            if type_code == "location":
                card_data = self._convert_location_back()
            elif type_code == "act":
                card_data = self._convert_act_back()
            elif type_code == "agenda":
                card_data = self._convert_agenda_back()
            elif type_code == "scenario":
                card_data = self._convert_scenario_back()
            elif type_code == "investigator":
                card_type_name = '调查员卡背'
                card_data = self._convert_investigator_back()
            else:
                return None
            card_data['type'] = card_type_name
            # 获取底标数据
            self.registered_base_mark_information(card_data)
            if type_code in ["location", "act", "agenda", "scenario"]:
                card_data['card_number'] = ''
                card_data['encounter_group_number'] = ''
            # 应用特殊卡牌处理
            card_data = self._apply_special_card_handling(card_data, is_back=True)
            return card_data
        if 'linked_card' in self.data:
            back_data = ArkhamDBConverter(self.data['linked_card'])
            return back_data.convert_front()

        # 查找连接面为自己的卡牌
        current_card_code = self.data.get('code')
        if current_card_code and self._full_database:
            linked_card = self.find_card_by_linked_to_code(current_card_code)
            if linked_card:
                print(
                    f"通过linked_to_code找到背面对象: {current_card_code} -> {linked_card.get('code')} ({linked_card.get('name')})")
                back_data = ArkhamDBConverter(linked_card)
                return back_data.convert_front()

        return None

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
        card_data["flavor"] = self._format_flavor_text(self.data.get("flavor"))

        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")

        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))

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
        card_data["flavor"] = self._format_flavor_text(self.data.get("flavor"))

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
        card_data["flavor"] = self._format_flavor_text(self.data.get("flavor"))
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))
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
        card_data["flavor"] = self._format_flavor_text(self.data.get("flavor"))
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))
        return card_data

    def _convert_treachery_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换诡计卡正面。
        """
        # 1. 获取所有玩家卡通用属性
        card_data = self._extract_common_player_card_properties()
        # 效果、风味文本和胜利点
        card_data["body"] = self._format_text(self.data.get("text"))
        card_data["flavor"] = self._format_flavor_text(self.data.get("flavor"))
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")

        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")
        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")
        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))
        return card_data

    def _format_compound_number(self, value_key: str, per_investigator_key: str, val: bool = True) -> Optional[str]:
        """
        格式化一个可能为 "X" 或 "每位调查员" 的数值。
        :param value_key: ArkhamDB JSON 中基础数值的键名 (e.g., 'health')
        :param per_investigator_key: ArkhamDB JSON 中 "每位调查员" 标记的键名 (e.g., 'health_per_investigator')
        :return: 格式化后的字符串 (e.g., '3', 'X', '2<调查员>')
        """
        if value_key not in self.data:
            return "-"
        value = self.data.get(value_key)
        if value is None:
            return "-"  # ArkhamDB 使用 null 来表示 '-'
        if value == -2:
            return 'X'
        value_str = str(value)
        if self.data.get(per_investigator_key, False) == val:
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
        card_data["flavor"] = self._format_flavor_text(self.data.get("flavor"))
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")

        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))
        return card_data

    def _convert_location_back(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转化地点卡背面
        """
        card_data = {}
        # 基础信息
        card_data["name"] = self.data.get("name", "")
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"
        if self.data.get("subname"):
            card_data["subtitle"] = self.data.get("subname")
        card_data["location_type"] = "未揭示"

        # 从gmnotes_index.json中获取地点图标信息
        card_code = self.data.get("code", "")
        location_icons, direction = self._extract_location_icons_from_gmnotes(card_code, is_back=True)
        card_data["Notes"] = direction

        # 设置地点图标
        if "location_icon" in location_icons:
            card_data["location_icon"] = location_icons["location_icon"]

        # 设置连接图标
        if "location_link" in location_icons:
            card_data["location_link"] = location_icons["location_link"]

        # 特性
        traits_str = self.data.get("traits", "")
        if traits_str:
            card_data["traits"] = [trait.strip() for trait in traits_str.replace('.', ' ').split() if trait.strip()]
        else:
            card_data["traits"] = []
        # 效果和风味文本
        card_data["body"] = self._format_text(self.data.get("back_text", ''))
        card_data["flavor"] = self._format_flavor_text(self.data.get("back_flavor", ''))
        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))
        return card_data

    def _convert_scenario_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换冒险参考卡正面。
        """
        card_data = {}

        # 基础信息
        card_data["name"] = self.data.get("name", "")
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"

        # 解析text中的副标题（优先尝试第一行，如果没有<b>标签则直接取第一行）
        text = self.data.get("text", "")
        subtitle_match = re.search(r'<b>(.*?)</b>', text)
        if subtitle_match:
            card_data["subtitle"] = subtitle_match.group(1).strip()
        else:
            # 如果没有<b>标签，尝试取第一行作为副标题
            lines = text.split('\n')
            if lines and lines[0].strip():
                first_line = lines[0].strip()
                # 如果第一行包含图标（如💀、👤等），则不作为副标题
                if not any(icon in first_line for icon in ['💀', '👤', '📜', '👹']):
                    card_data["subtitle"] = first_line
            elif self.data.get("subname"):
                card_data["subtitle"] = self.data.get("subname")

        # 设置默认类型为0（默认类型）
        card_data["scenario_type"] = 0

        # 解析text中的各种图标效果
        scenario_card_data = {}

        # 使用正则表达式提取各种图标效果
        # 匹配格式：💀 -X。X是你所在地点{食尸鬼}的数量。
        skull_match = re.search(r'💀\s*([^💀👤📜👹\n]*?)(?=\n|$|👤|📜|👹)', text)
        if skull_match:
            skull_text = skull_match.group(1).strip()
            # 删除图标文本中的冒号（如果存在）
            skull_text = re.sub(r'^：', '', skull_text)
            scenario_card_data["skull"] = self._format_text(skull_text)

        # 匹配👤效果
        cultist_match = re.search(r'👤\s*([^💀👤📜👹\n]*?)(?=\n|$|💀|📜|👹)', text)
        if cultist_match:
            cultist_text = cultist_match.group(1).strip()
            # 删除图标文本中的冒号（如果存在）
            cultist_text = re.sub(r'^：', '', cultist_text)
            scenario_card_data["cultist"] = self._format_text(cultist_text)

        # 匹配📜效果
        tablet_match = re.search(r'📜\s*([^💀👤📜👹\n]*?)(?=\n|$|💀|👤|👹)', text)
        if tablet_match:
            tablet_text = tablet_match.group(1).strip()
            # 删除图标文本中的冒号（如果存在）
            tablet_text = re.sub(r'^：', '', tablet_text)
            scenario_card_data["tablet"] = self._format_text(tablet_text)

        # 匹配👹效果
        elder_thing_match = re.search(r'👹\s*([^💀👤📜👹\n]*?)(?=\n|$|💀|👤|📜)', text)
        if elder_thing_match:
            elder_thing_text = elder_thing_match.group(1).strip()
            # 删除图标文本中的冒号（如果存在）
            elder_thing_text = re.sub(r'^：', '', elder_thing_text)
            scenario_card_data["elder_thing"] = self._format_text(elder_thing_text)

        # 将scenario_card数据包装到scenario_card字段中
        if scenario_card_data:
            card_data["scenario_card"] = scenario_card_data

        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))

        return card_data

    def _convert_scenario_back(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换冒险参考卡背面。
        """
        card_data = {}

        # 基础信息
        card_data["name"] = self.data.get("name", "")
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"

        # 解析back_text中的副标题（优先尝试第一行，如果没有<b>标签则直接取第一行）
        back_text = self.data.get("back_text", "")
        subtitle_match = re.search(r'<b>(.*?)</b>', back_text)
        if subtitle_match:
            card_data["subtitle"] = subtitle_match.group(1).strip()
        else:
            # 如果没有<b>标签，尝试取第一行作为副标题
            lines = back_text.split('\n')
            if lines and lines[0].strip():
                first_line = lines[0].strip()
                # 如果第一行包含图标（如💀、👤等），则不作为副标题
                if not any(icon in first_line for icon in ['💀', '👤', '📜', '👹']):
                    card_data["subtitle"] = first_line
            elif self.data.get("subname"):
                card_data["subtitle"] = self.data.get("subname")

        # 设置为背面
        card_data["is_back"] = True

        # 设置默认类型为0（默认类型）
        card_data["scenario_type"] = 0

        # 解析back_text中的各种图标效果
        scenario_card_data = {}

        # 使用正则表达式提取各种图标效果
        # 匹配格式：💀 -2。如果失败，在该次技能检定后，查找遭遇牌堆和弃牌堆，抽取一个{食尸鬼}敌人。混洗遭遇牌堆。
        skull_match = re.search(r'💀\s*([^💀👤📜👹\n]*?)(?=\n|$|👤|📜|👹)', back_text)
        if skull_match:
            skull_text = skull_match.group(1).strip()
            # 删除图标文本中的冒号（如果存在）
            skull_text = re.sub(r'^：', '', skull_text)
            scenario_card_data["skull"] = self._format_text(skull_text)

        # 匹配👤效果
        cultist_match = re.search(r'👤\s*([^💀👤📜👹\n]*?)(?=\n|$|💀|📜|👹)', back_text)
        if cultist_match:
            cultist_text = cultist_match.group(1).strip()
            # 删除图标文本中的冒号（如果存在）
            cultist_text = re.sub(r'^：', '', cultist_text)
            scenario_card_data["cultist"] = self._format_text(cultist_text)

        # 匹配📜效果
        tablet_match = re.search(r'📜\s*([^💀👤📜👹\n]*?)(?=\n|$|💀|👤|👹)', back_text)
        if tablet_match:
            tablet_text = tablet_match.group(1).strip()
            # 删除图标文本中的冒号（如果存在）
            tablet_text = re.sub(r'^：', '', tablet_text)
            scenario_card_data["tablet"] = self._format_text(tablet_text)

        # 匹配👹效果
        elder_thing_match = re.search(r'👹\s*([^💀👤📜👹\n]*?)(?=\n|$|💀|👤|📜)', back_text)
        if elder_thing_match:
            elder_thing_text = elder_thing_match.group(1).strip()
            # 删除图标文本中的冒号（如果存在）
            elder_thing_text = re.sub(r'^：', '', elder_thing_text)
            scenario_card_data["elder_thing"] = self._format_text(elder_thing_text)

        # 将scenario_card数据包装到scenario_card字段中
        if scenario_card_data:
            card_data["scenario_card"] = scenario_card_data

        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))

        return card_data

    def _convert_act_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换场景卡正面。
        """
        card_data = {}
        # 基础信息
        card_data["name"] = self.data.get("name", "")
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"
        if self.data.get("subname"):
            card_data["subtitle"] = self.data.get("subname")

        # 场景卡特有属性
        # 场景编号
        card_data["serial_number"] = str(self.data.get("stage")) + 'a'

        # 场景目标（线索值）
        card_data["threshold"] = self._format_compound_number("clues", "clues_fixed", False)

        # 阶段（stage）
        if self.data.get("stage") is not None:
            card_data["stage"] = self.data.get("stage")

        # 效果和风味文本
        card_data["body"] = self._format_text(self.data.get("text"))
        card_data["flavor"] = self._format_flavor_text(self.data.get("flavor"))

        # 胜利点
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")

        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))

        return card_data

    def _convert_act_back(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换场景卡背面。
        参考地点卡背面的处理方式
        """
        card_data = {}
        # 基础信息（使用背面的名称）
        card_data["is_back"] = True
        card_data["name"] = self.data.get("back_name", self.data.get("name", ""))
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"
        if self.data.get("subname"):
            card_data["subtitle"] = self.data.get("subname")

        # 场景卡特有属性
        # 场景编号
        card_data["serial_number"] = str(self.data.get("stage")) + 'b'

        # 背面效果和风味文本
        card_data["body"] = self._format_text(self.data.get("back_text", ""))
        card_data["flavor"] = self._format_flavor_text(self.data.get("back_flavor", ""))

        # 背面可能有胜利点
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")

        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))

        return card_data

    def _convert_story_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换故事卡正面。
        """
        card_data = {}
        # 基础信息
        card_data["name"] = self.data.get("name", "")
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"

        # 效果和风味文本
        card_data["body"] = self._format_text(self.data.get("text"))
        card_data["flavor"] = self._format_flavor_text(self.data.get("flavor"))

        # 胜利点
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")

        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))

        return card_data

    def _convert_agenda_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换密谋卡正面。
        """
        card_data = {}
        # 基础信息
        card_data["name"] = self.data.get("name", "")
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"
        if self.data.get("subname"):
            card_data["subtitle"] = self.data.get("subname")

        # 密谋卡特有属性
        # 密谋编号
        card_data["serial_number"] = str(self.data.get("stage")) + 'a'

        # 毁灭阈值（doom值）
        card_data["threshold"] = self._format_compound_number("doom", "doom_per_investigator")

        # 阶段（stage）
        if self.data.get("stage") is not None:
            card_data["stage"] = self.data.get("stage")

        # 效果和风味文本
        card_data["body"] = self._format_text(self.data.get("text"))
        card_data["flavor"] = self._format_flavor_text(self.data.get("flavor"))

        # 胜利点
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")

        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))

        return card_data

    def _convert_agenda_back(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换密谋卡背面。
        参考地点卡背面的处理方式
        """
        card_data = {}
        # 基础信息（使用背面的名称）
        card_data["is_back"] = True
        card_data["name"] = self.data.get("back_name", self.data.get("name", ""))
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"
        if self.data.get("subname"):
            card_data["subtitle"] = self.data.get("subname")

        # 密谋卡特有属性
        # 密谋编号
        card_data["serial_number"] = str(self.data.get("stage")) + 'b'

        # 背面效果和风味文本
        card_data["body"] = self._format_text(self.data.get("back_text", ""))
        card_data["flavor"] = self._format_flavor_text(self.data.get("back_flavor", ""))

        # 背面可能有胜利点
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")

        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))

        return card_data

    # 新增地点卡转换方法
    def _convert_location_front(self) -> Dict[str, Any]:
        """
        私有方法，专门用于转换地点卡正面。
        """
        card_data = {}
        # 基础信息
        card_data["name"] = self.data.get("name", "")
        if self.data.get("is_unique"):
            card_data["name"] = f"🏅{card_data['name']}"
        if self.data.get("subname"):
            card_data["subtitle"] = self.data.get("subname")
        # 地点类型（已揭示/未揭示）
        card_data["location_type"] = "已揭示"

        # 从gmnotes_index.json中获取地点图标信息
        card_code = self.data.get("code", "")
        location_icons, direction = self._extract_location_icons_from_gmnotes(card_code, is_back=False)
        card_data["Notes"] = direction

        # 设置地点图标
        if "location_icon" in location_icons:
            card_data["location_icon"] = location_icons["location_icon"]

        # 设置连接图标
        if "location_link" in location_icons:
            card_data["location_link"] = location_icons["location_link"]

        # 隐藏值和线索值
        card_data["shroud"] = self._format_compound_number("shroud", "shroud_per_investigator")
        card_data["clues"] = self._format_compound_number("clues", "clues_fixed", False)
        # 特性
        traits_str = self.data.get("traits", "")
        if traits_str:
            card_data["traits"] = [trait.strip() for trait in traits_str.replace('.', ' ').split() if trait.strip()]
        else:
            card_data["traits"] = []
        # 效果和风味文本
        card_data["body"] = self._format_text(self.data.get("text"))
        card_data["flavor"] = self._format_flavor_text(self.data.get("flavor"))
        # 胜利点
        if self.data.get("victory") is not None:
            card_data["victory"] = self.data.get("victory")
        if self.data.get("vengeance") is not None:
            card_data["vengeance"] = self.data.get("vengeance")
        # 遭遇组
        if self.data.get("encounter_code"):
            card_data["encounter_group"] = self._convert_encounter_group_code(self.data.get("encounter_code"))
        return card_data
