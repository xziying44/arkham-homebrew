"""
卡牌自动编号模块

负责为内容包中的卡牌自动分配编号，包括：
1. 卡牌分组（无遭遇组/各遭遇组）
2. 卡牌排序（遭遇组排序 + 类型排序）
3. 遭遇组编号计算
4. 卡牌序号计算
"""

from typing import List, Dict, Any


# 卡牌类型排序优先级
CARD_TYPE_ORDER = {
    '调查员': 0,
    '支援卡': 1,
    '事件卡': 2,
    '技能卡': 3,
    '冒险参考卡': 4,
    '场景卡': 5,
    '密谋卡': 6,
    '地点卡': 7,
    '敌人卡': 8,
    '诡计卡': 9,
    '故事卡': 10,
}

PLAYER_CARD_TYPES = {
    '调查员',
    '调查员背面',
    '调查员小卡',
    '支援卡',
    '事件卡',
    '技能卡',
    '大画-支援卡',
    '大画-事件卡',
    '大画-技能卡',
    '定制卡',
}

PLAYER_CLASS_ORDER = {
    '守护者': 0,
    '探求者': 1,
    '潜修者': 2,
    '流浪者': 3,
    '生存者': 4,
    '多职阶': 10,
    '中立': 11,
    '弱点': 12,
}


def normalize_card_path(path: str) -> str:
    """统一卡牌相对路径格式，便于跨平台匹配。"""
    if not isinstance(path, str):
        return ''
    normalized = path.replace('\\', '/').strip()
    while normalized.startswith('./'):
        normalized = normalized[2:]
    return normalized


def normalize_card_type_for_sort(card_type: str) -> str:
    """将大画卡类型归一化为基础类型后再参与排序。"""
    if not isinstance(card_type, str):
        return ''
    if card_type.startswith('大画-'):
        return card_type[3:]
    return card_type


def get_card_type_priority(card_type: str) -> int:
    """
    获取卡牌类型的排序优先级

    Args:
        card_type: 卡牌类型

    Returns:
        int: 优先级数字，越小越靠前
    """
    normalized_type = normalize_card_type_for_sort(card_type)
    return CARD_TYPE_ORDER.get(normalized_type, 999)  # 其他类型排在最后


def is_player_card(card: Dict[str, Any]) -> bool:
    """判断是否为玩家卡。"""
    return card.get('type', '') in PLAYER_CARD_TYPES


def get_player_class_priority(card_class: str) -> int:
    """获取玩家卡职阶优先级。"""
    return PLAYER_CLASS_ORDER.get(card_class, 999)


def get_card_level_for_sort(card: Dict[str, Any]) -> int:
    """用于排序的等级值，未知或无等级统一排在最后。"""
    level = card.get('level', -1)
    if isinstance(level, bool):
        return 999
    if isinstance(level, int):
        return level if level >= 0 else 999
    if isinstance(level, str):
        try:
            parsed = int(level)
            return parsed if parsed >= 0 else 999
        except ValueError:
            return 999
    return 999


def extract_card_reference_values(card: Dict[str, Any]) -> List[str]:
    """提取可用于建立卡牌关联的稳定标识。"""
    values = []

    filename = normalize_card_path(card.get('filename', ''))
    if filename:
        values.append(filename)

    tts_config = card.get('tts_config') or {}
    if isinstance(tts_config, dict):
        script_id = tts_config.get('script_id')
        if isinstance(script_id, str) and script_id:
            values.append(script_id)

    for key in ('id', 'code'):
        value = card.get(key)
        if isinstance(value, str) and value:
            values.append(value)

    result = []
    seen = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def build_card_reference_map(cards: List[Dict[str, Any]]) -> Dict[str, str]:
    """建立各种稳定标识到文件名的映射。"""
    reference_map = {}

    for card in cards:
        filename = normalize_card_path(card.get('filename', ''))
        if not filename:
            continue
        for value in extract_card_reference_values(card):
            reference_map[value] = filename
            normalized_value = normalize_card_path(value)
            if normalized_value:
                reference_map[normalized_value] = filename

    return reference_map


def resolve_related_card_filename(reference: Any, reference_map: Dict[str, str]) -> str:
    """将路径或稳定标识解析为对应卡牌文件名。"""
    if not isinstance(reference, str) or not reference:
        return ''

    normalized_reference = normalize_card_path(reference)
    if normalized_reference in reference_map:
        return reference_map[normalized_reference]
    if reference in reference_map:
        return reference_map[reference]
    return ''


def build_player_card_relations(cards: List[Dict[str, Any]]) -> tuple[Dict[str, str], Dict[str, str], Dict[str, int]]:
    """构建签名卡和 Bonded 卡的父子关系。"""
    reference_map = build_card_reference_map(cards)
    signature_parent_map: Dict[str, str] = {}
    child_relation_map: Dict[str, str] = {}
    child_order_map: Dict[str, int] = {}

    for card in cards:
        filename = normalize_card_path(card.get('filename', ''))
        if not filename or card.get('type') != '调查员':
            continue

        tts_config = card.get('tts_config') or {}
        signatures = tts_config.get('signatures') if isinstance(tts_config, dict) else None
        if not isinstance(signatures, list):
            continue

        for index, item in enumerate(signatures):
            if not isinstance(item, dict):
                continue
            child_filename = resolve_related_card_filename(item.get('path'), reference_map)
            if not child_filename or child_filename == filename:
                continue
            signature_parent_map[child_filename] = filename
            child_relation_map[child_filename] = 'signature'
            child_order_map[child_filename] = index

    parent_map = dict(signature_parent_map)

    bonded_reference_keys = (
        'bonded_to',
        'bonded_parent',
        'bonded_parent_id',
        'bonded_parent_path',
    )
    for card in cards:
        child_filename = normalize_card_path(card.get('filename', ''))
        if not child_filename or child_filename in parent_map:
            continue

        for key in bonded_reference_keys:
            parent_reference = card.get(key)
            parent_filename = resolve_related_card_filename(parent_reference, reference_map)
            if parent_filename and parent_filename != child_filename:
                parent_map[child_filename] = parent_filename
                child_relation_map[child_filename] = 'bonded'
                child_order_map[child_filename] = 0
                break

    return parent_map, child_relation_map, child_order_map


def sort_non_player_cards(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """非玩家卡沿用既有类型排序，并补充稳定次序。"""
    return sorted(
        cards,
        key=lambda card: (
            get_card_type_priority(card.get('type', '')),
            str(card.get('name', '')),
            normalize_card_path(card.get('filename', '')),
        )
    )


def sort_player_cards(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """按玩家卡规则排序，并将签名卡 / Bonded 卡挂到父卡后面。"""
    if not cards:
        return []

    cards_by_filename = {
        normalize_card_path(card.get('filename', '')): card
        for card in cards
        if normalize_card_path(card.get('filename', ''))
    }
    parent_map, child_relation_map, child_order_map = build_player_card_relations(cards)
    children_map: Dict[str, List[str]] = {}
    for child_filename, parent_filename in parent_map.items():
        if parent_filename not in cards_by_filename or child_filename not in cards_by_filename:
            continue
        children_map.setdefault(parent_filename, []).append(child_filename)

    def root_sort_key(filename: str) -> tuple:
        card = cards_by_filename[filename]
        return (
            get_player_class_priority(card.get('class', '')),
            0 if card.get('type') == '调查员' else 1,
            get_card_level_for_sort(card),
            get_card_type_priority(card.get('type', '')),
            str(card.get('name', '')),
            filename,
        )

    def child_sort_key(filename: str) -> tuple:
        card = cards_by_filename[filename]
        relation = child_relation_map.get(filename, '')
        if relation == 'signature':
            return (
                0,
                get_card_type_priority(card.get('type', '')),
                get_card_level_for_sort(card),
                child_order_map.get(filename, 999),
                str(card.get('name', '')),
                filename,
            )

        return (
            1,
            get_card_level_for_sort(card),
            get_card_type_priority(card.get('type', '')),
            str(card.get('name', '')),
            filename,
        )

    def expand_children(parent_filename: str) -> List[str]:
        result = []
        direct_children = sorted(children_map.get(parent_filename, []), key=child_sort_key)
        for child_filename in direct_children:
            result.append(child_filename)
            result.extend(expand_children(child_filename))
        return result

    root_filenames = [
        filename
        for filename in cards_by_filename
        if filename not in parent_map
    ]
    sorted_root_filenames = sorted(root_filenames, key=root_sort_key)

    result = []
    for root_filename in sorted_root_filenames:
        result.append(cards_by_filename[root_filename])
        for child_filename in expand_children(root_filename):
            result.append(cards_by_filename[child_filename])

    return result


def group_cards_by_encounter(cards: List[Dict[str, Any]], encounter_sets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    将卡牌按遭遇组分组

    Args:
        cards: 卡牌列表，每张卡牌应包含 filename 和 encounter_group 等字段
        encounter_sets: 遭遇组列表，包含 name 和 order 字段

    Returns:
        Dict: {遭遇组名称: [卡牌列表]}，包含特殊键 '_no_encounter' 表示无遭遇组卡牌
    """
    groups = {'_no_encounter': []}

    # 初始化所有遭遇组
    for encounter_set in encounter_sets:
        groups[encounter_set['name']] = []

    # 分组卡牌
    for card in cards:
        encounter_group = card.get('encounter_group')
        if not encounter_group or encounter_group not in groups:
            groups['_no_encounter'].append(card)
        else:
            groups[encounter_group].append(card)

    return groups


def sort_cards_in_group(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    对一个组内的卡牌按类型排序

    Args:
        cards: 卡牌列表

    Returns:
        List: 排序后的卡牌列表
    """
    cards_by_filename = {
        normalize_card_path(card.get('filename', '')): card
        for card in cards
        if normalize_card_path(card.get('filename', ''))
    }
    parent_map, _, _ = build_player_card_relations(cards)
    attached_card_filenames = {
        child_filename
        for child_filename, parent_filename in parent_map.items()
        if parent_filename in cards_by_filename and is_player_card(cards_by_filename[parent_filename])
    }

    player_cards = [
        card for card in cards
        if is_player_card(card) or normalize_card_path(card.get('filename', '')) in attached_card_filenames
    ]
    non_player_cards = [
        card for card in cards
        if not is_player_card(card) and normalize_card_path(card.get('filename', '')) not in attached_card_filenames
    ]

    if not player_cards:
        return sort_non_player_cards(non_player_cards)

    return sort_player_cards(player_cards) + sort_non_player_cards(non_player_cards)


def sort_encounter_groups(encounter_sets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    对遭遇组按 order 字段排序

    Args:
        encounter_sets: 遭遇组列表

    Returns:
        List: 排序后的遭遇组列表
    """
    return sorted(encounter_sets, key=lambda es: es.get('order', 0))


def calculate_encounter_group_number(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    为一个遭遇组中的卡牌计算遭遇组编号

    Args:
        cards: 已排序的卡牌列表

    Returns:
        List: 添加了 encounter_group_number 字段的卡牌列表
    """
    # 计算总数量
    total_quantity = sum(card.get('quantity', 1) for card in cards)

    # 当前位置
    current_position = 0

    result = []
    for card in cards:
        quantity = card.get('quantity', 1)
        card_copy = card.copy()

        if quantity == 1:
            # 数量为1，只显示位置
            card_copy['encounter_group_number'] = f"{current_position + 1}/{total_quantity}"
        else:
            # 数量大于1，显示范围
            start = current_position + 1
            end = current_position + quantity
            card_copy['encounter_group_number'] = f"{start}-{end}/{total_quantity}"

        current_position += quantity
        result.append(card_copy)

    return result


def assign_card_numbers(cards: List[Dict[str, Any]], start_number: int = 1) -> List[Dict[str, Any]]:
    """
    为卡牌分配序号

    Args:
        cards: 卡牌列表
        start_number: 起始序号

    Returns:
        List: 添加了 card_number 字段的卡牌列表
    """
    result = []
    current_number = start_number

    for card in cards:
        card_copy = card.copy()
        card_copy['card_number'] = str(current_number)
        current_number += 1
        result.append(card_copy)

    return result


def generate_numbering_plan(
    cards_data: List[Dict[str, Any]],
    encounter_sets: List[Dict[str, Any]],
    no_encounter_position: str = 'before',  # 'before' 或 'after'
    start_number: int = 1,
    footer_copyright: str = '',
    footer_icon_path: str = ''
) -> List[Dict[str, Any]]:
    """
    生成卡牌编号方案

    Args:
        cards_data: 卡牌数据列表，包含完整卡牌信息
        encounter_sets: 遭遇组列表
        no_encounter_position: 无遭遇组卡牌的位置，'before' 或 'after'
        start_number: 起始序号
        footer_copyright: 底部版权信息
        footer_icon_path: 底标图标路径

    Returns:
        List: 编号方案列表，每项包含：
            - filename: 卡牌文件路径
            - name: 卡牌名称
            - type: 卡牌类型
            - class: 职阶
            - encounter_group: 遭遇组
            - encounter_group_number: 遭遇组编号
            - card_number: 卡牌序号
            - quantity: 卡牌数量
            - footer_copyright: 底部版权信息（如果提供）
            - footer_icon_path: 底标图标路径（如果提供）
    """
    cards_data = [
        card for card in cards_data
        if card.get('type') != '调查员小卡'
    ]

    # 1. 分组
    grouped_cards = group_cards_by_encounter(cards_data, encounter_sets)

    # 2. 对遭遇组排序
    sorted_encounter_sets = sort_encounter_groups(encounter_sets)

    # 3. 对每个组内的卡牌排序
    for group_name in grouped_cards:
        grouped_cards[group_name] = sort_cards_in_group(grouped_cards[group_name])

    # 4. 按照指定顺序合并所有卡牌
    all_sorted_cards = []

    # 无遭遇组卡牌
    no_encounter_cards = grouped_cards['_no_encounter']

    # 有遭遇组的卡牌
    encounter_cards = []
    for encounter_set in sorted_encounter_sets:
        encounter_name = encounter_set['name']
        if encounter_name in grouped_cards and grouped_cards[encounter_name]:
            # 计算遭遇组编号
            cards_with_encounter_num = calculate_encounter_group_number(grouped_cards[encounter_name])
            encounter_cards.extend(cards_with_encounter_num)

    # 根据位置合并
    if no_encounter_position == 'before':
        all_sorted_cards = no_encounter_cards + encounter_cards
    else:
        all_sorted_cards = encounter_cards + no_encounter_cards

    # 5. 分配卡牌序号
    all_sorted_cards = assign_card_numbers(all_sorted_cards, start_number)

    # 6. 生成返回数据（只包含必要字段）
    result = []
    for card in all_sorted_cards:
        plan_item = {
            'filename': card.get('filename', ''),
            'name': card.get('name', ''),
            'type': card.get('type', ''),
            'class': card.get('class', ''),
            'encounter_group': card.get('encounter_group', ''),
            'encounter_group_number': card.get('encounter_group_number', ''),
            'card_number': card.get('card_number', ''),
            'quantity': card.get('quantity', 1)
        }

        # 添加底部版权信息和底标图标（如果提供）
        if footer_copyright:
            plan_item['footer_copyright'] = footer_copyright
        if footer_icon_path:
            plan_item['footer_icon_path'] = footer_icon_path

        result.append(plan_item)

    return result


def apply_numbering_plan(
    cards_data: List[Dict[str, Any]],
    numbering_plan: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    应用编号方案到卡牌数据

    Args:
        cards_data: 原始卡牌数据列表
        numbering_plan: 编号方案列表

    Returns:
        List: 更新后的卡牌数据列表
    """
    # 创建文件名到编号方案的映射
    plan_map = {plan['filename']: plan for plan in numbering_plan}

    # 应用编号
    result = []
    for card in cards_data:
        card_copy = card.copy()
        filename = card.get('filename', '')

        if filename in plan_map:
            plan = plan_map[filename]
            card_copy['encounter_group_number'] = plan.get('encounter_group_number', '')
            card_copy['card_number'] = plan.get('card_number', '')

            # 应用底部版权信息和底标图标（如果在方案中存在）
            if 'footer_copyright' in plan:
                card_copy['footer_copyright'] = plan['footer_copyright']
            if 'footer_icon_path' in plan:
                card_copy['footer_icon_path'] = plan['footer_icon_path']

        result.append(card_copy)

    return result
