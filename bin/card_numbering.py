"""
卡牌自动编号模块

负责为内容包中的卡牌自动分配编号，包括：
1. 卡牌分组（无遭遇组/各遭遇组）
2. 卡牌排序（遭遇组排序 + 类型排序）
3. 遭遇组编号计算
4. 卡牌序号计算
"""

import json
from typing import List, Dict, Any, Optional, Tuple


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


def get_card_type_priority(card_type: str) -> int:
    """
    获取卡牌类型的排序优先级

    Args:
        card_type: 卡牌类型

    Returns:
        int: 优先级数字，越小越靠前
    """
    return CARD_TYPE_ORDER.get(card_type, 999)  # 其他类型排在最后


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
    return sorted(cards, key=lambda card: get_card_type_priority(card.get('type', '')))


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
