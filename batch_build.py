import json
import os
import random
import re

from Card import FontManager, ImageManager
from create_card import create_player_cards, create_weakness_back, create_enemy_card, create_treachery_card, \
    create_location_card, create_investigators_card, create_investigators_card_back

class_replace_dict = {
    'guardian': '守护者',
    'survivor': '生存者',
    'rogue': '流浪者',
    'seeker': '探求者',
    'mystic': '潜修者',
    'neutral': '中立',
    'mythos': '神话',
}

slot_replace_dict = {
    'Ally': '盟友',
    'Accessory': '饰品',
    'Hand': '手部',
    'Hand x2': '双手',
    'Body': '身体',
    'Arcane': '法术',
    'Arcane x2': '双法术',
    'Tarot': '塔罗'
}

type_code_dict = {
    'asset': '支援卡',
    'event': '事件卡',
    'skill': '技能卡',
    'enemy': '敌人卡',
    'treachery': '诡计卡',
    'location': '地点卡',
    'investigator': '调查员卡',
}


def build_submit_icon(json):
    """构建投入图标"""
    # 构建投入图标
    submit_icon = []
    if 'skill_willpower' in json and json['skill_willpower'] is not None:
        for i in range(json['skill_willpower']):
            submit_icon.append('意志')
    if 'skill_intellect' in json and json['skill_intellect'] is not None:
        for i in range(json['skill_intellect']):
            submit_icon.append('智力')
    if 'skill_combat' in json and json['skill_combat'] is not None:
        for i in range(json['skill_combat']):
            submit_icon.append('战力')
    if 'skill_agility' in json and json['skill_agility'] is not None:
        for i in range(json['skill_agility']):
            submit_icon.append('敏捷')
    if 'skill_wild' in json and json['skill_wild'] is not None:
        for i in range(json['skill_wild']):
            submit_icon.append('狂野')
    return submit_icon


def batch_build_card(card_json, font_manager=None, image_manager=None, picture_path=None, encounter_count=-1,
                     is_back=False):
    """构建一张卡牌"""
    font_manager = font_manager
    image_manager = image_manager

    if 'linked_card' in card_json and is_back:
        card_json = card_json['linked_card']

    text = json.dumps(card_json, ensure_ascii=False)

    text = re.sub(r'手部 x2', r"双手", text)
    text = re.sub(r'服装', r"身体", text)

    def replace_bold(match):
        content = match.group(1)
        if "设计" in content:
            return f""  # 如果包含“设计”，删除
        else:
            return f"【{content}】"  # 否则用【】包裹

    def replace_italic(match):
        content = match.group(1)
        if "FAQ" in content:
            return f""  # 如果包含“设计”，删除
        else:
            return f"{content}"

    text = re.sub(r'<b>(.*?)</b>', replace_bold, text)
    text = re.sub(r'<i>(.*?)</i>', replace_italic, text)
    text = re.sub(r'\[\[(.*?)]]', r"{\1}", text)
    text = re.sub(r'\[action]', r"<启动>", text)
    text = re.sub(r'\[Action]', r"<启动>", text)
    text = re.sub(r'\[reaction]', r"<反应>", text)
    text = re.sub(r'\[free]', r"<免费>", text)
    text = re.sub(r'\[fast]', r"<免费>", text)

    text = re.sub(r'\[combat]', r"<拳>", text)
    text = re.sub(r'\[intellect]', r"<书>", text)
    text = re.sub(r'\[willpower]', r"<脑>", text)
    text = re.sub(r'\[agility]', r"<脚>", text)
    text = re.sub(r'\[wild]', r"<?>", text)

    text = re.sub(r'\[skull]', r"<骷髅>", text)
    text = re.sub(r'\[cultist]', r"<异教徒>", text)
    text = re.sub(r'\[elder_thing]', r"<古神>", text)
    text = re.sub(r'\[tablet]', r"<石板>", text)
    text = re.sub(r'\[auto_fail]', r"<触手>", text)
    text = re.sub(r'\[elder_sign]', r"<旧印>", text)
    text = re.sub(r'\[bless]', r"<祝福>", text)
    text = re.sub(r'\[curse]', r"<诅咒>", text)
    text = re.sub(r'\[frost]', r"<雪花>", text)

    text = re.sub(r'\[per_investigator]', r"<调查员>", text)
    text = re.sub(r'\[guardian]', r"<守护者>", text)
    text = re.sub(r'\[seeker]', r"<探求者>", text)
    text = re.sub(r'\[rogue]', r"<流浪者>", text)
    text = re.sub(r'\[mystic]', r"<潜修者>", text)
    text = re.sub(r'\[survivor]', r"<生存者>", text)

    text = re.sub(r'</p><p>', r"\\n", text)
    text = re.sub(r'<p>', r"", text)
    text = re.sub(r'</p>', r"", text)

    text = re.sub(r'<span class=\\"icon-reaction\\" title=\\"Reaction\\">', r"<反应>", text)
    text = re.sub(r'</span>', r"", text)

    card_json = json.loads(text)
    if 'text' in card_json and '[' in card_json['text']:
        # 报错
        raise ValueError('存在图标未处理 -> ' + text)
    if 'text' in card_json:
        card_json['text'] = re.sub(r'\n-', r"\n<点>", card_json['text'])
    # 解析成json输出
    build_json = {
        'type': type_code_dict.get(card_json['type_code'], ''),
        'class': class_replace_dict.get(card_json['faction_code'].lower(), card_json['faction_name']),
        'name': ('<独特>' if card_json.get('is_unique', False) else '') + card_json['name'],
        'subtitle': card_json['subname'] if 'subname' in card_json else '',
        'cost': card_json['cost'] if 'cost' in card_json else -1,
        'slots': slot_replace_dict.get(card_json['real_slot'], '') if 'slot' in card_json else '',
        'body': card_json['text'] if 'text' in card_json else '<hr>',
        'traits': [trait.strip() for trait in card_json['traits'].split('.')] if card_json.get('traits', None) else [],
        'level': card_json['xp'] if 'xp' in card_json else -1,
        'flavor': card_json['flavor'] if 'flavor' in card_json else '',
        'health': card_json['health'] if 'health' in card_json else 0,
        'horror': card_json['sanity'] if 'sanity' in card_json else 0,
        'victory': card_json['victory'] if 'victory' in card_json else -1,
        'submit_icon': build_submit_icon(card_json),
    }
    # print(f"正在导出卡牌: {card_json['name']} -> {build_json}")
    if card_json['type_code'] == 'enemy':
        # 添加敌人相关
        build_json['enemy_health'] = str(card_json.get('health', '-'))
        if card_json.get('health_per_investigator', False):
            build_json['enemy_health'] += '<调查员>'
            pass
        build_json['attack'] = str(card_json.get('enemy_fight', '-'))
        build_json['evade'] = str(card_json.get('enemy_evade', '-'))
        build_json['enemy_damage'] = card_json['enemy_damage'] if 'enemy_damage' in card_json else 0
        build_json['enemy_damage_horror'] = card_json['enemy_horror'] if 'enemy_horror' in card_json else 0

    # 构造card
    card = None
    if 'subtype_code' in card_json and \
            (card_json['subtype_code'] == 'weakness' or card_json['subtype_code'] == 'basicweakness'):
        # 构建支援卡json
        # build_json['type'] = build_json['class']
        build_json['class'] = '弱点'
        build_json['weakness_type'] = card_json.get('subtype_name', '')
        # 构建图片
        card = create_weakness_back(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1
        )
    elif card_json['type_code'] == 'asset':
        # 构建支援卡json
        build_json['type'] = '支援卡'
        # 判断是否为多职介
        if 'faction3_name' in card_json and card_json['faction3_name'] != '':
            build_json['class'] = '多职阶'
            build_json['subclass'] = [
                class_replace_dict.get(card_json['faction_code']),
                class_replace_dict.get(card_json['faction2_code']),
                class_replace_dict.get(card_json['faction3_code'])
            ]
        elif 'faction2_name' in card_json and card_json['faction2_name'] != '':
            build_json['class'] = '多职阶'
            build_json['subclass'] = [
                class_replace_dict.get(card_json['faction_code']),
                class_replace_dict.get(card_json['faction2_code'])
            ]
        # 判断是否多槽位
        if (build_json['slots'] != '' and build_json['slots'] is not None) and len(build_json['slots'].split('.')) > 1:
            temp = build_json['slots'].split('.')
            build_json['slots'] = temp[1].strip()
            build_json['slots2'] = temp[0].strip()

        if 'permanent' in card_json and card_json['permanent']:
            build_json['cost'] = -1
        # 构建图片
        card = create_player_cards(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1,
            # transparent_encounter=True if 'encounter_code' in card_json else False
            transparent_encounter=False
        )
    elif card_json['type_code'] == 'event':
        # 构建支援卡json
        build_json['type'] = '事件卡'
        # 判断是否为多职介
        if 'faction3_name' in card_json and card_json['faction3_name'] != '':
            build_json['class'] = '多职阶'
            build_json['subclass'] = [
                class_replace_dict.get(card_json['faction_code']),
                class_replace_dict.get(card_json['faction2_code']),
                class_replace_dict.get(card_json['faction3_code'])
            ]
        elif 'faction2_name' in card_json and card_json['faction2_name'] != '':
            build_json['class'] = '多职阶'
            build_json['subclass'] = [
                class_replace_dict.get(card_json['faction_code']),
                class_replace_dict.get(card_json['faction2_code'])
            ]
        if 'permanent' in card_json and card_json['permanent']:
            build_json['cost'] = -1
        # print(f"正在导出事件卡: {card_json['name']} -> {build_json}")
        # 构建图片
        card = create_player_cards(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1
        )
    elif card_json['type_code'] == 'skill':
        # 构建支援卡json
        build_json['type'] = '技能卡'
        # 判断是否为多职介
        if 'faction2_name' in card_json and card_json['faction2_name'] != '':
            build_json['class'] = '多职阶'
            build_json['subclass'] = [
                class_replace_dict.get(card_json['faction_code']),
                class_replace_dict.get(card_json['faction2_code'])
            ]
        if 'permanent' in card_json and card_json['permanent']:
            build_json['cost'] = -1
        # 构建图片
        card = create_player_cards(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1
        )
    elif card_json['type_code'] == 'enemy':
        # 构建支援卡json
        build_json['type'] = '敌人卡'
        if is_back:
            return None
        # 构建图片
        card = create_enemy_card(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1,
            transparent_encounter=False
        )
    elif card_json['type_code'] == 'treachery':
        # 构建支援卡json
        build_json['type'] = '诡计卡'

        # 构建图片
        card = create_treachery_card(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1,
            transparent_encounter=False
        )
    elif card_json['type_code'] == 'location':
        # 构建地点卡json
        build_json['type'] = '地点卡'
        # 隐藏值线索
        build_json['shroud'] = f"{card_json.get('shroud', 0)}"
        build_json['clues'] = f"{card_json.get('clues', '')}{'' if card_json.get('clues_fixed', False) else '<调查员>'}"
        # 是否为生成训练数据环境
        if os.environ.get('CARD_TRAIN_DATA') == '1':
            # 随机生成链接图标
            # 绿菱、暗红漏斗、橙心、浅褐水滴、深紫星、深绿斜二、深蓝T、紫月、红十、红方、蓝三角、褐扭、青花、黄圆
            local_icons = [
                '绿菱', '暗红漏斗', '橙心', '浅褐水滴', '深紫星', '深绿斜二', '深蓝T', '紫月', '红十', '红方', '蓝三角',
                '褐扭', '青花', '黄圆', '粉桃', '粉心', '绿星', '橙圆', '红扭', '红斜二', '黄漏斗', '黄三角', '蓝菱',
                '蓝月', '绿T', '斜十字', '紫方'
            ]
            # 从local_icons中随机选择一个
            build_json['location_icon'] = build_json['location_icon'] = random.choice(local_icons)
            # 随机选择 1-6 个不重复的图标作为 location_link
            num_links = random.randint(4, 6)  # 随机决定要选多少个（4~6）
            build_json['location_link'] = random.sample(local_icons, num_links)

        no_back = True
        for key in card_json.keys():
            if 'back_' in key and key != 'back_link':
                no_back = False
                break

        if no_back or is_back:
            # print(f"正在导出地点卡已揭示面: {card_json['name']}")
            # 已揭示面
            build_json['location_type'] = '已揭示'
            build_json['body'] = card_json.get('text', '')
            build_json['name'] = card_json.get('name', '')
            build_json['flavor'] = card_json.get('flavor', '')
        else:
            # print(f"正在导出地点卡未揭示面: {card_json['name']}")
            # 未揭示面
            build_json['location_type'] = '未揭示'
            build_json['body'] = card_json.get('back_text', '')
            build_json['name'] = card_json.get('back_name', card_json.get('name'))
            build_json['flavor'] = card_json.get('back_flavor', '')
            build_json['victory'] = -1

        # 构建图片
        card = create_location_card(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1,
            transparent_encounter=False
        )
    elif card_json['type_code'] == 'investigator+++++':
        # 构建支援卡json
        build_json['type'] = '调查员卡'
        build_json['attribute'] = [card_json['skill_willpower'], card_json['skill_intellect'],
                                   card_json['skill_combat'], card_json['skill_agility']]
        if card_json['code'][:2] == '90':
            # 平行调查员
            build_json['investigators_type'] = '平行'
        # 构建图片
        if is_back:
            # print(f"正在导出调查员卡背面: {card_json['name']}")
            # 构造背面
            build_json['card_back'] = {
                "size": -1,
                "option": [],
                "requirement": "",
                "other": "",
                "story": ""
            }
            build_json['card_back']['other'] = card_json['back_text']
            build_json['card_back']['story'] = card_json['back_flavor']

            card = create_investigators_card_back(
                card_json=build_json,
                font_manager=font_manager,
                image_manager=image_manager,
                image_mode=1,
                picture_path=picture_path
            )
        else:
            # 构造正面
            # print(f"正在导出调查员卡正面: {card_json['name']}")
            card = create_investigators_card(
                card_json=build_json,
                font_manager=font_manager,
                image_manager=image_manager,
                image_mode=1,
                picture_path=picture_path
            )

    if card is not None:
        return card
        # 年份信息
        copyright_dict = {
            '01': {'name': '基础', 'year': 2016},
            '02': {'name': '敦威治遗产', 'year': 2016},
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
        copyright_dict_2 = {
            '601': {'name': '调查员包-守卫者', 'year': 2019},
            '602': {'name': '调查员包-探求者', 'year': 2019},
            '603': {'name': '调查员包-流浪者', 'year': 2019},
            '604': {'name': '调查员包-潜修者', 'year': 2020},
            '605': {'name': '调查员包-生存者', 'year': 2019},
        }
        if build_json['type'] != '敌人卡' and build_json['type'] != '调查员卡':
            # 写底部信息
            middle_text = ''
            pack_code = card_json['code'][:2]
            pack_icon = None
            if pack_code in copyright_dict:
                middle_text = f"© {copyright_dict[pack_code]['year']} FFG"
                pack_icon = copyright_dict[pack_code]['name']
            elif card_json['code'][:3] in copyright_dict_2:
                temp_code = card_json['code'][:3]
                middle_text = f"© {copyright_dict_2[temp_code]['year']} FFG"
                pack_icon = copyright_dict_2[temp_code]['name']

            card.set_bottom_information_by_text(
                illustrator=card_json['illustrator'] if 'illustrator' in card_json else '',
                position=card_json['position'] if 'position' in card_json else -1,
                middle_text=middle_text,
                pack_icon=pack_icon,
                encounter_count=encounter_count,
                encounter_position=card_json['encounter_position'] if 'encounter_position' in card_json else 1
            )
        return card
    print(f"找不到有效类型: {card_json['name']} -> {text}")
    return None


if __name__ == '__main__':
    pass
