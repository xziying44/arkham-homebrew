import json
import re

from Card import FontManager, ImageManager
from create_card import create_player_cards, create_weakness_back, create_enemy_card, create_treachery_card, \
    create_location_card, create_investigators_card, create_investigators_card_back


def build_submit_icon(json):
    """构建投入图标"""
    # 构建投入图标
    submit_icon = []
    if 'skill_willpower' in json:
        for i in range(json['skill_willpower']):
            submit_icon.append('意志')
    if 'skill_intellect' in json:
        for i in range(json['skill_intellect']):
            submit_icon.append('智力')
    if 'skill_combat' in json:
        for i in range(json['skill_combat']):
            submit_icon.append('战力')
    if 'skill_agility' in json:
        for i in range(json['skill_agility']):
            submit_icon.append('敏捷')
    if 'skill_wild' in json:
        for i in range(json['skill_wild']):
            submit_icon.append('狂野')
    return submit_icon


def batch_build_card(card_json, font_manager=None, image_manager=None, picture_path=None, encounter_count=-1,
                     is_back=False):
    """构建一张卡牌"""
    font_manager = font_manager
    image_manager = image_manager

    text = json.dumps(card_json, ensure_ascii=False)
    text = re.sub(r'守卫者', r"守护者", text)
    text = re.sub(r'求生者', r"生存者", text)

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

    text = re.sub(r'\[per_investigator]', r"<调查员>", text)
    text = re.sub(r'\[guardian]', r"<守护者>", text)
    text = re.sub(r'\[seeker]', r"<探求者>", text)
    text = re.sub(r'\[rogue]', r"<流浪者>", text)
    text = re.sub(r'\[mystic]', r"<潜修者>", text)
    text = re.sub(r'\[survivor]', r"<生存者>", text)

    card_json = json.loads(text)
    if 'text' in card_json and '[' in card_json['text']:
        # 报错
        raise ValueError('存在图标未处理 -> ' + text)
    if 'text' in card_json:
        card_json['text'] = re.sub(r'\n-', r"\n<点>", card_json['text'])
    if 'real_name' in card_json and card_json['name'] == card_json['real_name']:
        # 无中文
        return None
    print(card_json)
    # 解析成json输出
    build_json = {
        'type': '支援卡',
        'class': card_json['faction_name'],
        'name': ('<独特>' if card_json.get('is_unique', False) else '') + card_json['name'],
        'subtitle': card_json['subname'] if 'subname' in card_json else '',
        'cost': card_json['cost'] if 'cost' in card_json else -1,
        'slots': card_json['slot'] if 'slot' in card_json else '',
        'body': card_json['text'] if 'text' in card_json else '<hr>',
        'traits': [trait.strip() for trait in card_json['traits'].split('.')] if 'traits' in card_json else [],
        'level': card_json['xp'] if 'xp' in card_json else -1,
        'flavor': card_json['flavor'] if 'flavor' in card_json else '',
        'health': card_json['health'] if 'health' in card_json else 0,
        'horror': card_json['sanity'] if 'sanity' in card_json else 0,
        'victory': card_json['victory'] if 'victory' in card_json else -1,
        'submit_icon': build_submit_icon(card_json),
    }
    if card_json['type_name'] == '敌人':
        # 添加敌人相关
        print(f"正在导出敌人卡: {card_json}")
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
        print(f"正在导出弱点卡: {card_json['name']}")
        # 构建支援卡json
        build_json['type'] = f"{card_json['type_name']}卡"
        build_json['class'] = '弱点'
        build_json['weakness_type'] = card_json.get('subtype_name', '')
        print(build_json)
        # 构建图片
        card = create_weakness_back(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1
        )
    elif card_json['type_name'] == '支援':
        print(f"正在导出支援卡: {card_json['name']}")
        # 构建支援卡json
        build_json['type'] = '支援卡'
        # 判断是否为多职介
        if 'faction3_name' in card_json and card_json['faction3_name'] != '':
            build_json['class'] = '多职阶'
            build_json['subclass'] = [card_json['faction_name'], card_json['faction2_name'], card_json['faction3_name']]
        elif 'faction2_name' in card_json and card_json['faction2_name'] != '':
            build_json['class'] = '多职阶'
            build_json['subclass'] = [card_json['faction_name'], card_json['faction2_name']]
        # 判断是否多槽位
        if build_json['slots'] != '' and len(build_json['slots'].split('.')) > 1:
            temp = build_json['slots'].split('.')
            build_json['slots'] = temp[1].strip()
            build_json['slots2'] = temp[0].strip()

        if 'permanent' in card_json and card_json['permanent']:
            build_json['cost'] = -1
        # 构建图片
        print(build_json)
        card = create_player_cards(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1,
            transparent_encounter=True if 'encounter_code' in card_json else False
        )
    elif card_json['type_name'] == '事件':
        print(f"正在导出事件卡: {card_json['name']}")
        # 构建支援卡json
        build_json['type'] = '事件卡'
        # 判断是否为多职介
        if 'faction3_name' in card_json and card_json['faction3_name'] != '':
            build_json['class'] = '多职阶'
            build_json['subclass'] = [card_json['faction_name'], card_json['faction2_name'], card_json['faction3_name']]
        elif 'faction2_name' in card_json and card_json['faction2_name'] != '':
            build_json['class'] = '多职阶'
            build_json['subclass'] = [card_json['faction_name'], card_json['faction2_name']]
        if 'permanent' in card_json and card_json['permanent']:
            build_json['cost'] = -1
        print(build_json)
        # 构建图片
        card = create_player_cards(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1
        )
    elif card_json['type_name'] == '技能':
        print(f"正在导出技能卡: {card_json['name']}")
        # 构建支援卡json
        build_json['type'] = '技能卡'
        # 判断是否为多职介
        if 'faction2_name' in card_json and card_json['faction2_name'] != '':
            build_json['class'] = '多职阶'
            build_json['subclass'] = [card_json['faction_name'], card_json['faction2_name']]
        if 'permanent' in card_json and card_json['permanent']:
            build_json['cost'] = -1
        print(build_json)
        # 构建图片
        card = create_player_cards(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1
        )
    elif card_json['type_name'] == '敌人':
        print(f"正在导出敌人卡: {card_json['name']}")
        # 构建支援卡json
        build_json['type'] = '敌人卡'
        print(build_json)
        if is_back:
            return None
        # 构建图片
        card = create_enemy_card(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1,
            transparent_encounter=True
        )
    elif card_json['type_name'] == '诡计':
        print(f"正在导出诡计卡: {card_json['name']}")
        # 构建支援卡json
        build_json['type'] = '诡计卡'

        print(build_json)
        # 构建图片
        card = create_treachery_card(
            card_json=build_json,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            image_mode=1,
            transparent_encounter=True
        )
    elif card_json['type_name'] == '地点':
        # 构建地点卡json
        build_json['type'] = '地点卡'
        # 隐藏值线索
        build_json['shroud'] = f"{card_json.get('shroud', 0)}"
        build_json['clues'] = f"{card_json.get('clues', '')}{'' if card_json.get('clues_fixed', False) else '<调查员>'}"

        no_back = True
        for key in card_json.keys():
            if 'back_' in key and key != 'back_link':
                no_back = False
                break

        if no_back or is_back:
            print(f"正在导出地点卡已揭示面: {card_json['name']}")
            # 已揭示面
            build_json['location_type'] = '已揭示'
            build_json['body'] = card_json.get('text', '')
            build_json['name'] = card_json.get('name', '')
            build_json['flavor'] = card_json.get('flavor', '')
        else:
            print(f"正在导出地点卡未揭示面: {card_json['name']}")
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
            transparent_encounter=True
        )
    elif card_json['type_name'] == '调查员123 TODO':
        # 构建支援卡json
        build_json['type'] = '调查员卡'
        build_json['attribute'] = [card_json['skill_willpower'], card_json['skill_intellect'],
                                   card_json['skill_combat'], card_json['skill_agility']]
        # 构建图片
        if is_back:
            print(f"正在导出调查员卡背面: {card_json['name']}")
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
                picture_path=picture_path
            )
        else:
            # 构造正面
            print(f"正在导出调查员卡正面: {card_json['name']}")
            card = create_investigators_card(
                card_json=build_json,
                font_manager=font_manager,
                image_manager=image_manager,
                picture_path=picture_path
            )

    if card is not None:
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
            '10': {'name': '铁杉谷盛宴', 'year': 2023},
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
        if build_json['type'] != '敌人卡':
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
