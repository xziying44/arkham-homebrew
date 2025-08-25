import json
import random
import re

from PIL import Image, ImageEnhance

from Card import Card, FontManager, ImageManager

se_icon = {
    '<rea>': '<反应>',
    '<act>️': '<启动>',
    '<fre>️': '<免费>',
    '<sku>️': '<骷髅>',
    '<cul>️': '<异教徒>',
    '<tab>️': '<石板>',
    '<mon>️': '<古神>',
    '<ten>️': '<触手>',
    '<eld>️': '<旧印>',
    '<com>️': '<拳>',
    '<int>️': '<书>',
    '<agi>️': '<脚>',
    '<wil>️': '<脑>',
    '<?>': '<?>',
    '<bul>': '<点>',
    '<cur>': '<诅咒>',
    '<ble>': '<祝福>',
    '️<per>': '<调查员>',
    '<rog>': '<流浪者>',
    '<sur>': '<生存者>',
    '<gua>️': '<守护者>',
    '<mys>': '<潜修者>',
    '<see>': '<探求者>'
}


def tidy_body_flavor2(body, flavor, flavor_type=0, align='center'):
    """整理正文和风味，正确处理flavor字段中的<lr>标签"""
    body = body.strip()
    tag_name = 'relish'
    if align == 'left':
        tag_name = "relish center='false'"

    if flavor:
        flavor = flavor.strip()

        if '<lr>' in flavor:
            # 分割字符串但保留分隔符
            parts = []
            remaining = flavor
            while '<lr>' in remaining:
                idx = remaining.index('<lr>')
                if idx > 0:
                    parts.append(remaining[:idx])
                parts.append('<lr>')
                remaining = remaining[idx + 4:]  # +4 是跳过'<lr>'
            if remaining:
                parts.append(remaining)

            # 构建结果
            result = []
            for part in parts:
                if part == '<lr>':
                    result.append('<lr>')
                elif part.strip():
                    result.append(f"<{tag_name}>{part.strip()}</relish>")

            flavor = ''.join(result)
        else:
            # 普通处理
            flavor = '\n'.join(
                f"<{tag_name}>{line.strip()}</relish>"
                for line in flavor.split('\n')
                if line.strip()
            )
        if flavor_type == 0:
            body += f'\n{flavor}'
        else:
            body = f'{flavor}\n{body}'

    return body


def tidy_body_flavor(data, flavor_type=0):
    """整理正文和风味，正确处理flavor字段中的<lr>标签"""
    body = data.get('body', '').strip()

    if 'flavor' in data and data['flavor']:
        flavor = data['flavor'].strip()

        if '<lr>' in flavor:
            # 分割字符串但保留分隔符
            parts = []
            remaining = flavor
            while '<lr>' in remaining:
                idx = remaining.index('<lr>')
                if idx > 0:
                    parts.append(remaining[:idx])
                parts.append('<lr>')
                remaining = remaining[idx + 4:]  # +4 是跳过'<lr>'
            if remaining:
                parts.append(remaining)

            # 构建结果
            result = []
            for part in parts:
                if part == '<lr>':
                    result.append('<lr>')
                elif part.strip():
                    result.append(f"<relish>{part.strip()}</relish>")

            flavor = ''.join(result)
        else:
            # 普通处理
            flavor = '\n'.join(
                f"<relish>{line.strip()}</relish>"
                for line in flavor.split('\n')
                if line.strip()
            )
        if flavor_type == 0:
            body += f'\n{flavor}'
        else:
            body = f'{flavor}\n{body}'

    return body


def integrate_traits_text(font_manager, traits):
    """整合特性文本"""
    if traits is None:
        return ''
    delimiter = '，'
    if font_manager.lang == 'en':
        delimiter = '. '

    return delimiter.join([font_manager.get_font_text(trait) for trait in traits])


def open_picture(card_json, path):
    """打开图片"""
    try:
        image = Image.open(path)
        if card_json.get('picture_enhanced', False):
            # 增加亮度
            enhancer = ImageEnhance.Brightness(image)
            bright_image = enhancer.enhance(1.7)  # 1.0是原图，>1.0增加亮度，<1.0降低亮度
            bright_image.point(lambda p: p * 1.5)
            return bright_image
        return image
    except Exception as e:
        print(f"Error opening image: {e}")
        return None


def create_location_card(card_json, picture_path=None, font_manager=None, image_manager=None, image_mode=0,
                         transparent_encounter=False, transparent_background=False):
    """制作地点卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    card = None
    # 创建Card对象
    card = Card(
        width=739,
        height=1049,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type='地点卡'
    )
    dp = open_picture(card_json, picture_path)
    is_enemy = False
    if data.get('enemy_health', '') != '':
        # 是否为敌人地点
        is_enemy = True
    if transparent_background is False:
        # 贴底图
        if picture_path is not None:
            if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
                image_mode = 1
            if image_mode == 1:
                # 铺满
                card.paste_image(dp, (0, 0, 739, 1049), 'cover')
            else:
                card.paste_image(dp, (0, 80, 739, 562), 'cover')
        if 'location_type' not in data or data['location_type'] not in ['未揭示', '已揭示']:
            raise ValueError('说明地点类型为未揭示或已揭示')
        # 贴牌框 是否有副标题
        is_enemy = False
        if data.get('enemy_health', '') != '':
            # 是否为敌人地点
            is_enemy = True
            if 'subtitle' in data and data['subtitle'] != '':
                card.paste_image(image_manager.get_image(f'{data["type"]}-{data["location_type"]}-敌人-副标题'), (0, 0),
                                 'contain')
            else:
                card.paste_image(image_manager.get_image(f'{data["type"]}-{data["location_type"]}-敌人'), (0, 0),
                                 'contain')
            pass
        else:
            if 'subtitle' in data and data['subtitle'] != '':
                card.paste_image(image_manager.get_image(
                    f'{data["type"]}-{data["location_type"]}-副标题{"-虚拟" if card_json.get("virtual", False) else ""}'),
                    (0, 0),
                    'contain')
            else:
                card.paste_image(image_manager.get_image(
                    f'{data["type"]}-{data["location_type"]}'
                    f'{"-半" if card_json.get("virtual", False) == "半" else ""}'
                    f'{"-虚拟" if card_json.get("virtual", False) else ""}'), (0, 0),
                    'contain')
    # 贴遭遇组
    if transparent_encounter:
        card.copy_circle_to_image(dp, (370, 518, 30), (370, 518, 30))
    # 写小字
    card.draw_centered_text(
        position=(370, 562),
        text=font_manager.get_font_text("地点"),
        font_name="小字",
        font_size=26,
        font_color=(0, 0, 0)
    )
    # 写标题
    card.draw_centered_text(
        position=(370, 32),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=48,
        font_color=(0, 0, 0)
    )
    # 写副标题
    if 'subtitle' in data and data['subtitle'] != '':
        card.draw_centered_text(
            position=(370, 88),
            text=data['subtitle'],
            font_name="副标题",
            font_size=32,
            font_color=(0, 0, 0)
        )
    # 写特性
    card.draw_centered_text(
        position=(370, 610) if not is_enemy else (370, 690),
        text=integrate_traits_text(font_manager, data.get('traits', [])),
        font_name="方正舒体",
        font_size=32,
        font_color=(0, 0, 0)
    )

    # 整合body和flavor
    body = tidy_body_flavor(data)
    # 写正文和风味
    card.draw_text(
        text=body,
        vertices=[
            (64, 620), (670, 620),
            (712, 675), (712, 900),
            (15, 900), (15, 675)
        ] if not is_enemy else [
            (64, 700), (670, 700),
            (712, 750), (712, 900),
            (15, 900), (15, 750)
        ],
        default_font_name='simfang',
        default_size=32,
        padding=18,
        draw_virtual_box=False
    )
    # 写隐藏值和线索值
    if data['location_type'] == '已揭示':
        shroud = data.get('shroud', '')
        clues = data.get('clues', '')
        card.set_number_value(
            position=(62, 557),
            text=shroud,
            font_size=52
        )
        card.set_number_value(
            position=(675, 557),
            text=clues,
            font_size=52,
            color=(0, 0, 0),
            stroke_color=(255, 255, 255)
        )
    if is_enemy:
        # 画生命值恐惧值
        health = 0
        horror = 0
        if 'enemy_damage' in data and isinstance(data['enemy_damage'], int):
            health = data['enemy_damage']
        if 'enemy_damage_horror' in data and isinstance(data['enemy_damage_horror'], int):
            horror = data['enemy_damage_horror']
        if health > 0 or horror > 0:
            card.set_health_and_horror(health, horror)
        # 画攻击生命躲避
        attack = data['attack'] if 'attack' in data else ''
        evade = data['evade'] if 'evade' in data else ''
        enemy_health = data['enemy_health'] if 'enemy_health' in data else ''
        card.set_number_value(
            position=(370, 132 + 480),
            text=enemy_health,
            font_size=52
        )
        card.set_number_value(
            position=(232, 132 + 480),
            text=attack,
            font_size=44
        )
        card.set_number_value(
            position=(508, 132 + 480),
            text=evade,
            font_size=44
        )
    # 写胜利点
    victory = data.get('victory', None)
    if victory is not None:
        card.draw_centered_text(
            position=(675, 907),
            text=f"胜利{data['victory']}。",
            font_name="思源黑体",
            font_size=28,
            font_color=(0, 0, 0)
        )
    # 画地点符号和连接符号
    if data.get('location_icon', '') != '':
        card.set_location_icon(0, data['location_icon'])
    if 'location_link' in data and isinstance(data['location_link'], list):
        for i in range(len(data['location_link'])):
            card.set_location_icon(i + 1, data['location_link'][i])
    return card


def create_treachery_card(card_json, picture_path=None, font_manager=None, image_manager=None, image_mode=0,
                          transparent_encounter=False, transparent_background=False):
    """诡计卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    card = None
    # 创建Card对象
    card = Card(
        width=739,
        height=1049,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type='诡计卡'
    )
    dp = open_picture(card_json, picture_path)
    if transparent_background is False:
        # 贴底图
        if picture_path is not None:
            if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
                image_mode = 1
            if image_mode == 1:
                # 铺满
                card.paste_image(dp, (0, 0, 739, 1049), 'cover')
            else:
                card.paste_image(dp, (0, 0, 739, 605), 'cover')

        # 贴牌框
        card.paste_image(image_manager.get_image(f'{data["type"]}'), (0, 0), 'contain')
    # 贴遭遇组
    if transparent_encounter:
        card.copy_circle_to_image(dp, (370, 534, 32), (370, 534, 32))
    # 写小字
    card.draw_centered_text(
        position=(370, 576),
        text=font_manager.get_font_text("诡计"),
        font_name="小字",
        font_size=24,
        font_color=(0, 0, 0)
    )
    # 写标题
    card.draw_centered_text(
        position=(370, 630),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=48,
        font_color=(0, 0, 0)
    )
    # 写特性
    card.draw_centered_text(
        position=(370, 690),
        text=integrate_traits_text(font_manager, data.get('traits', [])),
        font_name="方正舒体",
        font_size=32,
        font_color=(0, 0, 0)
    )
    # 整合body和flavor
    body = tidy_body_flavor(data)
    # 写正文和风味
    card.draw_text(
        text=body,
        vertices=[
            (38, 700), (704, 700),
            (704, 1010), (38, 1010)
        ],
        default_font_name='simfang',
        default_size=32,
        padding=18,
        draw_virtual_box=False
    )
    # 画胜利点
    victory = data.get('victory', None)
    if victory is not None:
        card.draw_centered_text(
            position=(378, 980),
            text=f"胜利{data['victory']}。",
            font_name="思源黑体",
            font_size=28,
            font_color=(0, 0, 0)
        )
    return card


def create_enemy_card(card_json, picture_path=None, font_manager=None, image_manager=None, image_mode=0,
                      transparent_encounter=False, transparent_background=False):
    """敌人卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    card = None
    # 创建Card对象
    card = Card(
        width=739,
        height=1049,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type='敌人卡'
    )
    dp = open_picture(card_json, picture_path)
    if transparent_background is False:
        # 贴底图
        if picture_path is not None:
            if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
                image_mode = 1
            if image_mode == 1:
                # 铺满
                card.paste_image(dp, (0, 0, 739, 1049), 'cover')
            else:
                card.paste_image(dp, (0, 456, 739, 593), 'cover')
        # 贴牌框
        if 'subtitle' in data and data['subtitle'] != '':
            card.paste_image(
                image_manager.get_image(f'{data["type"]}-副标题{"-虚拟" if card_json.get("virtual", False) else ""}'),
                (0, 0))
        else:
            card.paste_image(
                image_manager.get_image(f'{data["type"]}{"-虚拟" if card_json.get("virtual", False) else ""}'),
                (0, 0), 'contain')
    # 贴遭遇组
    if transparent_encounter:
        card.copy_circle_to_image(dp, (370, 570, 32), (370, 570, 32))

    # 写小字
    card.draw_centered_text(
        position=(364, 617),
        text=font_manager.get_font_text("敌人"),
        font_name="小字",
        font_size=24,
        font_color=(0, 0, 0)
    )
    # 写标题
    card.draw_centered_text(
        position=(370, 28),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=48,
        font_color=(0, 0, 0)
    )
    # 写副标题
    if 'subtitle' in data and data['subtitle'] != '':
        card.draw_centered_text(
            position=(370, 78),
            text=data['subtitle'],
            font_name="副标题",
            font_size=32,
            font_color=(0, 0, 0)
        )
    # 写特性
    card.draw_centered_text(
        position=(370, 218),
        text=integrate_traits_text(font_manager, data.get('traits', [])),
        font_name="方正舒体",
        font_size=32,
        font_color=(0, 0, 0)
    )
    # 整合body和flavor
    body = tidy_body_flavor(data)
    # 写胜利点数和正文
    if 'victory' in data and isinstance(data['victory'], int):
        card.draw_centered_text(
            position=(380, 512),
            text=f"胜利{data['victory']}。",
            font_name="思源黑体",
            font_size=28,
            font_color=(0, 0, 0)
        )
        card.draw_text(
            text=body,
            vertices=[
                (90, 230), (645, 230), (716, 270), (716, 450),
                (538, 510), (190, 510),
                (20, 450), (20, 270)

            ],
            default_font_name='simfang',
            default_size=32,
            padding=15,
            draw_virtual_box=False
        )
    else:
        card.draw_text(
            text=body,
            vertices=[
                (90, 230), (645, 230), (716, 270), (716, 450),
                (538, 540), (190, 540),
                (20, 450), (20, 270)
            ],
            default_font_name='simfang',
            default_size=32,
            padding=15,
            draw_virtual_box=False
        )
    # 画生命值恐惧值
    health = 0
    horror = 0
    if 'enemy_damage' in data and isinstance(data['enemy_damage'], int):
        health = data['enemy_damage']
    if 'enemy_damage_horror' in data and isinstance(data['enemy_damage_horror'], int):
        horror = data['enemy_damage_horror']
    if health > 0 or horror > 0:
        card.set_health_and_horror(health, horror)
    # 画攻击生命躲避
    attack = data['attack'] if 'attack' in data else ''
    evade = data['evade'] if 'evade' in data else ''
    enemy_health = data['enemy_health'] if 'enemy_health' in data else ''
    card.set_number_value(
        position=(370, 132),
        text=enemy_health,
        font_size=52
    )
    card.set_number_value(
        position=(232, 136),
        text=attack,
        font_size=44
    )
    card.set_number_value(
        position=(508, 136),
        text=evade,
        font_size=44
    )

    return card


def create_upgrade_card(card_json, picture_path=None, font_manager=None, image_manager=None):
    """制作升级卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    card = None
    # 创建Card对象
    card = Card(
        width=739,
        height=1049,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type='升级卡'
    )
    # 贴牌框
    card.paste_image(image_manager.get_image(f'升级卡'), (0, 0), 'contain')
    # 写标题
    card.draw_centered_text(
        position=(370, 94),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=52,
        font_color=(0, 0, 0)
    )
    # 写正文
    card.draw_text(
        text=data['body'],
        vertices=[
            (38, 186), (700, 186),
            (700, 1009), (38, 1009)
        ],
        default_font_name='simfang',
        default_size=32,
        padding=18,
        draw_virtual_box=False
    )
    return card


def create_weakness_back(card_json, picture_path=None, font_manager=None, image_manager=None, image_mode=0):
    """制作弱点卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'class' not in data or data['class'] not in ['弱点']:
        raise ValueError('职业类型错误')
    card = None
    # 创建Card对象
    card = Card(
        width=739,
        height=1049,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type=data['type'],
        card_class=data['class']
    )
    if data['type'] not in ['事件卡', '支援卡', '技能卡', '诡计卡', '敌人卡']:
        raise ValueError('卡牌类型错误')
    # 整合body和flavor
    body = tidy_body_flavor(data)
    if data['type'] == '事件卡':
        # 贴底图
        if picture_path is not None:
            dp = open_picture(card_json, picture_path)
            if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
                image_mode = 1
            if image_mode == 1:
                # 铺满
                card.paste_image(dp, (0, 0, 739, 1049), 'cover')
            else:
                card.paste_image(dp, (0, 0, 739, 580), 'cover')
        # 贴牌框
        card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(76, 130),
            text=font_manager.get_font_text("事件"),
            font_name="小字",
            font_size=24,
            font_color=(0, 0, 0)
        )
        # 写标题
        card.draw_centered_text(
            position=(370, 618),
            text=data['name'],
            font_name="汉仪小隶书简",
            font_size=48,
            font_color=(0, 0, 0)
        )
        # 写弱点类型
        card.draw_centered_text(
            position=(370, 670),
            text=data['weakness_type'],
            font_name="汉仪小隶书简",
            font_size=28,
            font_color=(0, 0, 0)
        )
        # 写特性
        card.draw_centered_text(
            position=(370, 715),
            text=integrate_traits_text(font_manager, data.get('traits', [])),
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )
        # 写费用
        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])
        # 写正文和风味
        card.draw_text(
            text=body,
            vertices=[
                (38, 726), (704, 726), (706, 757), (704, 817), (680, 887), (670, 952),
                (598, 980), (135, 980), (77, 949), (61, 907), (31, 793)
            ],
            default_font_name='simfang',
            default_size=32,
            padding=18,
            draw_virtual_box=False
        )
        pass
    elif data['type'] == '支援卡':
        # 贴底图
        if picture_path is not None:
            dp = open_picture(card_json, picture_path)
            if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
                image_mode = 1
            if image_mode == 1:
                # 铺满
                card.paste_image(dp, (0, 0, 739, 1049), 'cover')
            else:
                card.paste_image(dp, (0, 85, 739, 510), 'cover')
        # 贴牌框
        if 'subtitle' in data and data['subtitle'] != '':
            card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}-副标题'), (0, 0), 'contain')
        else:
            card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(76, 130),
            text=font_manager.get_font_text("支援"),
            font_name="小字",
            font_size=24,
            font_color=(0, 0, 0)
        )
        # 写标题
        card.draw_centered_text(
            position=(370, 48),
            text=data['name'],
            font_name="汉仪小隶书简",
            font_size=48,
            font_color=(0, 0, 0)
        )
        # 写副标题
        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text(
                position=(370, 101),
                text=data['subtitle'],
                font_name="副标题",
                font_size=32,
                font_color=(0, 0, 0)
            )
        # 写弱点类型
        card.draw_centered_text(
            position=(370, 605),
            text=data['weakness_type'],
            font_name="汉仪小隶书简",
            font_size=28,
            font_color=(0, 0, 0)
        )
        # 写特性
        card.draw_centered_text(
            position=(370, 649),
            text=integrate_traits_text(font_manager, data.get('traits', [])),
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )
        # 写费用
        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])
        # 写正文和风味
        card.draw_text(
            text=body,
            vertices=[
                (19, 662), (718, 662), (718, 910), (19, 910)
            ],
            default_font_name='simfang',
            default_size=32,
            padding=15,
            draw_virtual_box=False
        )
        # 画槽位
        if 'slots' in data and isinstance(data['slots'], str):
            card.add_slots(data['slots'])
        # 画生命值恐惧值
        health = 0
        horror = 0
        if 'health' in data and isinstance(data['health'], int):
            health = data['health']
        if 'horror' in data and isinstance(data['horror'], int):
            horror = data['horror']
        if health > 0 or horror > 0:
            card.set_health_and_horror(health, horror)
        pass
    elif data['type'] == '技能卡':
        # 贴底图
        if picture_path is not None:
            dp = open_picture(card_json, picture_path)
            if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
                image_mode = 1
            if image_mode == 1:
                # 铺满
                card.paste_image(dp, (0, 0, 739, 1049), 'cover')
            else:
                card.paste_image(dp, (0, 88, 739, 600), 'cover')
        # 贴牌框
        if 'subtitle' in data and data['subtitle'] != '':
            card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}-副标题'), (0, 0), 'contain')
        else:
            card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(76, 130),
            text=font_manager.get_font_text("技能"),
            font_name="小字",
            font_size=24,
            font_color=(0, 0, 0)
        )
        # 写标题
        card.draw_left_text(
            position=(140, 34),
            text=data['name'],
            font_name="汉仪小隶书简",
            font_size=48,
            font_color=(0, 0, 0)
        )
        # 写副标题
        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text(
                position=(378, 106),
                text=data['subtitle'],
                font_name="副标题",
                font_size=32,
                font_color=(0, 0, 0)
            )
        # 写弱点类型
        card.draw_centered_text(
            position=(368, 705),
            text=data['weakness_type'],
            font_name="汉仪小隶书简",
            font_size=28,
            font_color=(0, 0, 0)
        )
        # 写特性
        card.draw_centered_text(
            position=(368, 742),
            text=integrate_traits_text(font_manager, data.get('traits', [])),
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )
        # 写正文和风味
        card.draw_text(
            text=body,
            vertices=[
                (75, 754), (682, 754),
                (692, 770), (704, 838), (701, 914), (679, 986),
                (74, 986), (91, 920), (96, 844)
            ],
            default_font_name='simfang',
            default_size=32,
            padding=15,
            draw_virtual_box=False
        )
        # 画投入图标
        if 'submit_icon' in data and isinstance(data['submit_icon'], list):
            for icon in data['submit_icon']:
                card.add_submit_icon(icon)
        pass
    elif data['type'] == '诡计卡':
        # 贴底图
        if picture_path is not None:
            dp = open_picture(card_json, picture_path)
            if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
                image_mode = 1
            if image_mode == 1:
                # 铺满
                card.paste_image(dp, (0, 0, 739, 1049), 'cover')
            else:
                card.paste_image(dp, (0, 0, 739, 605), 'cover')
        # 贴牌框
        card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(370, 576),
            text=font_manager.get_font_text("诡计"),
            font_name="小字",
            font_size=24,
            font_color=(0, 0, 0)
        )
        # 写标题
        card.draw_centered_text(
            position=(370, 625),
            text=data['name'],
            font_name="汉仪小隶书简",
            font_size=48,
            font_color=(0, 0, 0)
        )
        # 写弱点类型
        card.draw_centered_text(
            position=(370, 678),
            text=data['weakness_type'],
            font_name="汉仪小隶书简",
            font_size=28,
            font_color=(0, 0, 0)
        )
        # 写特性
        card.draw_centered_text(
            position=(370, 715),
            text=integrate_traits_text(font_manager, data.get('traits', [])),
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )
        # 写正文和风味
        card.draw_text(
            text=body,
            vertices=[
                (38, 726), (704, 726),
                (704, 980), (38, 980)
            ],
            default_font_name='simfang',
            default_size=32,
            padding=18,
            draw_virtual_box=False
        )
        pass
    elif data['type'] == '敌人卡':
        # 贴底图
        if picture_path is not None:
            dp = open_picture(card_json, picture_path)
            if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
                image_mode = 1
            if image_mode == 1:
                # 铺满
                card.paste_image(dp, (0, 0, 739, 1049), 'cover')
            else:
                card.paste_image(dp, (0, 456, 739, 593), 'cover')
        # 贴牌框
        card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(370, 620),
            text=font_manager.get_font_text("敌人"),
            font_name="小字",
            font_size=24,
            font_color=(0, 0, 0)
        )
        # 写标题
        card.draw_centered_text(
            position=(370, 28),
            text=data['name'],
            font_name="汉仪小隶书简",
            font_size=48,
            font_color=(0, 0, 0)
        )
        # 写副标题
        card.draw_centered_text(
            position=(370, 78),
            text=data['weakness_type'],
            font_name="汉仪小隶书简",
            font_size=32,
            font_color=(0, 0, 0)
        )
        # 写特性
        card.draw_centered_text(
            position=(370, 218),
            text=integrate_traits_text(font_manager, data.get('traits', [])),
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )
        # 整合body和flavor
        body = tidy_body_flavor(data)
        # 写胜利点数和正文
        if 'victory' in data and isinstance(data['victory'], int):
            card.draw_centered_text(
                position=(380, 512),
                text=f"胜利{data['victory']}。",
                font_name="思源黑体",
                font_size=28,
                font_color=(0, 0, 0)
            )
            card.draw_text(
                text=body,
                vertices=[
                    (90, 230), (645, 230),
                    (699, 267), (727, 340), (688, 454),
                    (538, 504), (370, 504), (190, 504),
                    (47, 454), (5, 340), (32, 267)

                ],
                default_font_name='simfang',
                default_size=32,
                padding=15,
                draw_virtual_box=False
            )
        else:
            card.draw_text(
                text=body,
                vertices=[
                    (90, 230), (645, 230),
                    (699, 267), (727, 340), (688, 454),
                    (538, 540), (370, 540), (190, 540),
                    (47, 454), (5, 340), (32, 267)

                ],
                default_font_name='simfang',
                default_size=32,
                padding=15,
                draw_virtual_box=False
            )
        # 画生命值恐惧值
        health = 0
        horror = 0
        if 'enemy_damage' in data and isinstance(data['enemy_damage'], int):
            health = data['enemy_damage']
        if 'enemy_damage_horror' in data and isinstance(data['enemy_damage_horror'], int):
            horror = data['enemy_damage_horror']
        if health > 0 or horror > 0:
            card.set_health_and_horror(health, horror)

        # 画攻击生命躲避
        attack = data['attack'] if 'attack' in data else ''
        evade = data['evade'] if 'evade' in data else ''
        enemy_health = data['enemy_health'] if 'enemy_health' in data else ''
        card.set_number_value(
            position=(370, 132),
            text=enemy_health,
            font_size=52
        )
        card.set_number_value(
            position=(232, 136),
            text=attack,
            font_size=44
        )
        card.set_number_value(
            position=(508, 136),
            text=evade,
            font_size=44
        )
        pass
    if data['weakness_type'] == '基础弱点':
        card.set_basic_weakness_icon()

    return card


def create_investigators_card_back(card_json, picture_path=None, font_manager=None, image_manager=None, image_mode=0):
    """制作调查员卡背面"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'class' not in data or data['class'] not in ['守护者', '探求者', '流浪者', '潜修者', '生存者', '中立']:
        raise ValueError('职业类型错误')
    if 'card_back' not in data:
        data['card_back'] = {
            "size": 30,
            "option": [],
            "requirement": "",
            "other": data.get('body', ''),
            "story": ""
        }
    card_back = data['card_back']
    # 创建Card对象
    card = Card(
        width=1049,
        height=739,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type='调查员卡',
        card_class=data['class']
    )
    # 贴底图
    if picture_path is not None:
        dp = open_picture(card_json, picture_path)
        if image_mode == 1:
            # 检查是否高大于宽，如果是旋转90度
            if dp.size[0] < dp.size[1]:
                dp = dp.rotate(90, expand=True)
            # 铺满
            card.paste_image(dp, (0, 0, 1049, 739), 'cover')
        else:
            card.paste_image(dp, (0, 0, 373, 405), 'cover')

    # 贴牌框-UI
    card.paste_image(image_manager.get_image(f'调查员卡-{data["class"]}-卡背'), (0, 0), 'contain')

    # 写标题
    card.draw_centered_text(
        position=(750, 36),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=48,
        font_color=(0, 0, 0)
    )

    # 写副标题
    card.draw_centered_text(
        position=(750, 86),
        text=data['subtitle'],
        font_name="副标题",
        font_size=32,
        font_color=(0, 0, 0)
    )
    if card_json['body'] is not None and card_json['body'] != '':
        card_back['other'] = card_json['body']
    test_text = ""
    if 'size' in card_back and card_back['size'] > 0:
        test_text += f"【牌库卡牌张数】：{card_back['size']}。\n"
    if 'option' in card_back and len(card_back['option']) > 0:
        test_text += '【牌库构筑选项】：' + '，'.join(card_back['option']) + '。\n'
    if 'requirement' in card_back and card_back['requirement'] != '':
        test_text += f"【牌库构筑需求】(不计入卡牌张数)：{card_back['requirement']}。\n"
    if 'other' in card_back and card_back['other'] != '':
        test_text += card_back['other'] + '\n'
    if 'story' in card_back and card_back['story'] != '':
        test_text = tidy_body_flavor2(test_text, card_back['story'], align='left')
    vertices = [
        (385, 141), (1011, 141), (1011, 700), (36, 700),
        (36, 470), (170, 470), (182, 430), (358, 430)
    ]
    if data.get('class') == '守护者':
        vertices = [
            (385, 141), (1011, 141), (1011, 700), (36, 700),
            (36, 470), (220, 470), (220, 430), (366, 430)
        ]
    elif data.get('class') == '探求者':
        vertices = [
            (385, 141), (1011, 141), (1011, 700), (36, 700),
            (36, 470), (340, 470)
        ]
    elif data.get('class') == '生存者':
        vertices = [
            (385, 141), (1011, 141), (1011, 700), (36, 700),
            (36, 520), (114, 464), (340, 464)
        ]
    elif data.get('class') == '流浪者':
        vertices = [
            (385, 141), (1011, 141), (1011, 700), (36, 700),
            (36, 450), (350, 450)
        ]
    elif data.get('class') == '中立':
        vertices = [
            (420, 141), (1011, 141), (1011, 700), (36, 700),
            (36, 410), (380, 410)
        ]
    card.draw_text(
        test_text,
        vertices=vertices,
        default_font_name='simfang',
        default_size=32,
        padding=15,
        draw_virtual_box=False
    )

    return card


def create_investigators_card(card_json, picture_path=None, font_manager=None, image_manager=None, image_mode=0):
    """制作调查员卡正面"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'class' not in data or data['class'] not in ['守护者', '探求者', '流浪者', '潜修者', '生存者', '中立']:
        raise ValueError('职业类型错误')
    card = None
    # 创建Card对象
    card = Card(
        width=1049,
        height=739,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type='调查员卡',
        card_class=data['class']
    )
    # 贴牌框-底
    card.paste_image(image_manager.get_image(f'{data["type"]}-{data["class"]}-底图'), (0, 0), 'contain')
    # 贴底图
    if picture_path is not None:
        dp = open_picture(card_json, picture_path)
        if image_mode == 1:
            # 铺满
            card.paste_image(dp, (0, 0, 1049, 739), 'cover')
        else:
            card.paste_image(dp, (0, 75, 579, 664), 'cover', extension=470)
    # 贴牌框-UI
    card.paste_image(image_manager.get_image(f'{data["type"]}-{data["class"]}-UI'), (0, 0), 'contain')

    # 写标题
    card.draw_centered_text(
        position=(320, 38),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=48,
        font_color=(0, 0, 0)
    )

    # 写副标题
    card.draw_centered_text(
        position=(320, 90),
        text=data['subtitle'],
        font_name="副标题",
        font_size=32,
        font_color=(0, 0, 0)
    )
    # 写四维
    if 'attribute' in data and isinstance(data['attribute'], list):
        for i, attr in enumerate(data['attribute']):
            card.draw_centered_text(
                position=(600 + 120 * i, 57),
                text=str(attr),
                font_name="Bolton",
                font_size=48,
                font_color=(0, 0, 0)
            )
    # 写属性
    traits = ''
    if 'traits' in data and isinstance(data['traits'], list):
        traits = integrate_traits_text(font_manager, data['traits'])
    card.draw_centered_text(
        position=(810, 168),
        text=traits,
        font_name="方正舒体",
        font_size=32,
        font_color=(0, 0, 0)
    )
    # 整理body和风味
    body = tidy_body_flavor(data)
    card.draw_text(
        body,
        vertices=[
            (586, 178), (1026, 178), (1024, 600), (586, 600)
        ],
        default_font_name='simfang',
        default_size=32,
        padding=15,
        draw_virtual_box=False
    )
    # 画生命值恐惧值
    health = 0
    horror = 0
    if 'health' in data and isinstance(data['health'], int):
        health = data['health']
    if 'horror' in data and isinstance(data['horror'], int):
        horror = data['horror']
    if health > 0 or horror > 0:
        card.set_health_and_horror(health, horror)
    return card


def create_player_cards(card_json, picture_path=None, font_manager=None, image_manager=None, image_mode=0,
                        transparent_encounter=False):
    """制作玩家卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'type' not in data or data['type'] not in ['技能卡', '支援卡', '事件卡']:
        raise ValueError('卡牌类型错误')
    if 'class' not in data or data['class'] not in ['守护者', '探求者', '流浪者', '潜修者', '生存者', '中立', '多职阶',
                                                    '神话']:
        raise ValueError('职业类型错误')
    if data['class'] == '神话':
        data['class'] = '中立'
    if data['type'] == '技能卡' and data['class'] == '多职阶':
        raise ValueError('技能卡暂时不支持多职阶')
    card = None
    # 创建Card对象
    if data['type'] == '技能卡':
        card = Card(
            width=739,
            height=1049,
            font_manager=font_manager,
            image_manager=image_manager,
            card_type=data['type'],
            card_class=data['class']
        )
        # 贴底图
        if picture_path is not None:
            dp = open_picture(card_json, picture_path)
            if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
                image_mode = 1
            if image_mode == 1:
                # 铺满
                card.paste_image(dp, (0, 0, 739, 1049), 'cover')
            else:
                card.paste_image(dp, (0, 88, 739, 600), 'cover')
        # 贴牌框
        card.paste_image(image_manager.get_image(f'{data["type"]}-{data["class"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(73, 132),
            text=font_manager.get_font_text("技能"),
            font_name="小字",
            font_size=24,
            font_color=(0, 0, 0)
        )
        pass
    elif data['type'] == '事件卡':
        card = Card(
            width=739,
            height=1046,
            font_manager=font_manager,
            image_manager=image_manager,
            card_type=data['type'],
            card_class=data['class']
        )
        # 贴底图
        if picture_path is not None:
            dp = open_picture(card_json, picture_path)
            if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
                image_mode = 1
            if image_mode == 1:
                # 铺满
                card.paste_image(dp, (0, 0, 739, 1049), 'cover')
            else:
                card.paste_image(dp, (0, 0, 739, 589), 'cover')

        # 贴牌框
        card.paste_image(image_manager.get_image(f'{data["type"]}-{data["class"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(73, 130),
            text=font_manager.get_font_text("事件"),
            font_name="小字",
            font_size=24,
            font_color=(0, 0, 0)
        )
        pass
    elif data['type'] == '支援卡':
        card = Card(
            width=739,
            height=1049,
            font_manager=font_manager,
            image_manager=image_manager,
            card_type=data['type'],
            card_class=data['class']
        )
        # 贴底图
        if picture_path is not None:
            dp = open_picture(card_json, picture_path)
            if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
                image_mode = 1
            if image_mode == 1:
                # 铺满
                card.paste_image(dp, (0, 0, 739, 1049), 'cover')
            else:
                card.paste_image(dp, (0, 80, 739, 540), 'cover')
        # 贴牌框
        if 'subtitle' in data and data['subtitle'] != '':
            card.paste_image(image_manager.get_image(f'{data["type"]}-{data["class"]}-副标题'), (0, 0), 'contain',
                             (690, 50, 46) if transparent_encounter else None)
        else:
            card.paste_image(image_manager.get_image(f'{data["type"]}-{data["class"]}'), (0, 0), 'contain',
                             (690, 50, 46) if transparent_encounter else None)
        # 写小字
        card.draw_centered_text(
            position=(73, 130),
            text=font_manager.get_font_text("支援"),
            font_name="小字",
            font_size=24,
            font_color=(0, 0, 0)
        )
        pass
    # 检查错误
    if card is None:
        raise ValueError('卡牌类型错误')
    if 'name' not in data or data['name'] == '':
        raise ValueError('卡牌名称不能为空')
    if 'body' not in data or data['body'] == '':
        raise ValueError('正文内容不能为空')

    # 开始绘图
    # 画投入图标
    if 'submit_icon' in data and isinstance(data['submit_icon'], list):
        for icon in data['submit_icon']:
            card.add_submit_icon(icon)
    # 画等级
    if 'level' in data and isinstance(data['level'], int):
        card.set_card_level(data['level'])
    else:
        card.set_card_level(-1)
    traits = ''
    if 'traits' in data and isinstance(data['traits'], list):
        traits = integrate_traits_text(font_manager, data['traits'])
    # 整理body和风味
    body = tidy_body_flavor(data)
    # 按不同类型画位置
    if data['type'] == '技能卡':
        # 画名称
        card.draw_left_text(
            position=(140, 30),
            text=data['name'],
            font_name="汉仪小隶书简",
            font_size=48,
            font_color=(0, 0, 0)
        )
        # 画特性
        card.draw_centered_text(
            position=(368, 707),
            text=traits,
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )
        # 画正文和风味
        card.draw_text(
            text=body,
            vertices=[
                (75, 725), (682, 725), (692, 770), (704, 838), (701, 914),
                (679, 995), (74, 995),
                (91, 920), (96, 844)
            ],
            default_font_name='simfang',
            default_size=32,
            padding=15,
            draw_virtual_box=False
        )
        pass
    elif data['type'] == '事件卡':
        # 画名称
        offset = 0
        if data.get('class', '') == '潜修者':
            offset = -8
        elif data.get('class', '') == '守护者':
            offset = -3
        elif data.get('class', '') == '中立':
            offset = -5
        card.draw_centered_text(
            position=(370, 625 + offset),
            text=data['name'],
            font_name="汉仪小隶书简",
            font_size=48,
            font_color=(0, 0, 0)
        )
        # 画特性
        card.draw_centered_text(
            position=(368, 682),
            text=traits,
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )
        # 画正文和风味
        card.draw_text(
            text=body,
            vertices=[
                (43, 700), (694, 700), (706, 757), (704, 817), (680, 887), (670, 952),
                (598, 1000), (135, 1000),
                (77, 949), (61, 907), (31, 793)
            ],
            default_font_name='simfang',
            default_size=32,
            padding=15,
            draw_virtual_box=False
        )
        # 画价格
        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])
        # 画胜利点
        victory = data.get('victory', None)
        if victory is not None:
            card.draw_centered_text(
                position=(378, 960),
                text=f"胜利{data['victory']}。",
                font_name="思源黑体",
                font_size=28,
                font_color=(0, 0, 0)
            )
        pass
    elif data['type'] == '支援卡':
        # 画名称
        card.draw_centered_text(
            position=(375, 48),
            text=data['name'],
            font_name="汉仪小隶书简",
            font_size=48,
            font_color=(0, 0, 0)
        )
        # 画副标题
        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text(
                position=(375, 101),
                text=data['subtitle'],
                font_name="副标题",
                font_size=32,
                font_color=(0, 0, 0)
            )
        # 画特性
        card.draw_centered_text(
            position=(375, 649),
            text=traits,
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )
        # 画正文和风味
        card.draw_text(
            text=body,
            vertices=[
                (19, 662), (718, 662), (718, 925), (19, 925)
            ],
            default_font_name='simfang',
            default_size=32,
            padding=15,
            draw_virtual_box=False
        )
        # 画价格
        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])
        # 画槽位
        if 'slots' in data and isinstance(data['slots'], str):
            card.add_slots(data['slots'])
        if 'slots2' in data and isinstance(data['slots2'], str):
            card.add_slots(data['slots2'])

        # 画生命值恐惧值
        health = 0
        horror = 0
        if 'health' in data and isinstance(data['health'], int):
            health = data['health']
        if 'horror' in data and isinstance(data['horror'], int):
            horror = data['horror']
        if health > 0 or horror > 0:
            card.set_health_and_horror(health, horror)
        # 写胜利点
        victory = data.get('victory', None)
        if victory is not None:
            card.draw_centered_text(
                position=(675, 938) if 'slots' not in data else (379, 885),
                text=f"胜利{data['victory']}。",
                font_name="思源黑体",
                font_size=28,
                font_color=(0, 0, 0)
            )
        pass
    # 画多职介
    if data['class'] == '多职阶' and 'subclass' in data and isinstance(data['subclass'], list):
        card.set_subclass_icon(data['subclass'])
    return card


def create_large_picture(
        card_json,
        picture_path=None,
        font_manager=None,
        image_manager=None,
        transparent_encounter=False
):
    """制作大画卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'type' not in data or data['type'] not in ['场景卡-大画', '密谋卡-大画']:
        raise ValueError('卡牌类型错误')
    # 创建Card对象
    card = Card(
        width=1049,
        height=739,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type=data['type']
    )
    # 贴底图
    if picture_path is not None:
        dp = open_picture(card_json, picture_path)
        # 判断图片宽高，如果高大于宽，则需要将图片向左旋转90度
        if dp.size[1] > dp.size[0]:
            dp = dp.rotate(90, expand=True)
        # 铺满
        card.paste_image(dp, (0, 0, 1049, 739), 'cover')
    # 透明列表
    encounter_list = [
        (105, 499, 42)

    ]
    if data['type'] != '场景卡-大画':
        encounter_list = [
            (105, 459, 42),
            (953, 447, 52)
        ]
    # 贴牌框-UI
    card.paste_image(image_manager.get_image(f'{data["type"]}'), (0, 0), 'contain',
                     encounter_list if transparent_encounter else None)
    # 写标题
    card.draw_centered_text(
        position=(500, 513) if data['type'] == '场景卡-大画' else (500, 464),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=48,
        font_color=(0, 0, 0)
    )
    # 整理body和风味
    body = tidy_body_flavor(data)
    # 写正文
    card.draw_text(
        body,
        vertices=[
            (28, 556), (1016, 556),
            (1016, 686), (28, 686)
        ] if data['type'] == '场景卡-大画' else [
            (28, 512), (1016, 512),
            (1016, 686), (28, 686)
        ],
        default_font_name='simfang',
        default_size=32,
        padding=15,
        draw_virtual_box=False
    )
    # 写阈值
    if 'threshold' in data and data['type'] == '密谋卡-大画':
        card.set_number_value(
            position=(953, 447),
            text=data['threshold'],
            font_size=54
        )
    return card


def create_act_card(
        card_json,
        picture_path=None,
        font_manager=None,
        image_manager=None,
        image_mode=0,
        transparent_encounter=False
):
    """制作场景卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'type' not in data or data['type'] not in ['场景卡', '密谋卡']:
        raise ValueError('卡牌类型错误')
    # 创建Card对象
    card = Card(
        width=1049,
        height=739,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type=data['type']
    )
    dp = open_picture(card_json, picture_path)
    # 贴底图
    if picture_path is not None:
        if abs(dp.size[0] - card.image.size[0]) < 3 and abs(dp.size[1] - card.image.size[1]) < 3:
            image_mode = 1
        if image_mode == 1:
            # 判断图片宽高，如果高大于宽，则需要将图片向左旋转90度
            if dp.size[1] > dp.size[0]:
                dp = dp.rotate(90, expand=True)
            # 铺满
            card.paste_image(dp, (0, 0, 1049, 739), 'cover')
        else:
            card.paste_image(
                dp,
                (1049 - 626, 0, 626, 739) if data['type'] == '场景卡' else (0, 0, 626, 739)
                , 'cover'
            )
    # 透明列表
    encounter_list = [
        [(533, 628, 42), (528, 622, 42)],
        [(270, 74, 34), (288, 74, 34)]
    ]
    if data['type'] != '场景卡':
        encounter_list = [
            [(520, 636, 44), (500, 630, 44)],
            [(288 + 473, 76, 34), (288 + 473, 76, 34)]
        ]
    # 贴牌框-UI
    card.paste_image(image_manager.get_image(f'{data["type"]}'), (0, 0), 'contain')
    # 贴遭遇组
    if transparent_encounter:
        for item in encounter_list:
            card.copy_circle_to_image(dp, item[0], item[1])
    # 写序列号
    if data['type'] == '场景卡':
        card.draw_centered_text(
            position=(287, 25),
            text=f"场景{data.get('serial_number', '')}",
            font_name="小字",
            font_size=28,
            font_color=(0, 0, 0)
        )
    else:
        card.draw_centered_text(
            position=(758, 25),
            text=f"密谋{data.get('serial_number', '')}",
            font_name="小字",
            font_size=28,
            font_color=(0, 0, 0)
        )
    # 写标题
    card.draw_centered_text(
        position=(285, 150) if data['type'] == '场景卡' else (765, 150),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=48,
        font_color=(0, 0, 0)
    )
    vertices = [
        (10, 185), (560, 185),
        (560, 574), (470, 574), (470, 678),
        (10, 678)
    ]
    offset_x = -20
    if data['type'] != '场景卡':
        vertices = [
            (10 + 480 + offset_x, 185), (560 + 480 + offset_x, 185),
            (560 + 480 + offset_x, 678), (10 + 480 + 80 + offset_x, 678), (10 + 480 + 80 + offset_x, 574),
            (10 + 480 + offset_x, 574)
        ]
    # 写正文
    body = tidy_body_flavor(data, flavor_type=1)
    card.draw_text(
        body,
        vertices=vertices,
        default_font_name='simfang',
        default_size=32,
        padding=15,
        draw_virtual_box=False
    )
    # 写阈值
    if 'threshold' in data:
        card.set_number_value(
            position=(523, 618) if data['type'] == '场景卡' else (498, 624),
            text=data['threshold'],
            font_size=54
        )
    return card


def create_act_back_card(
        card_json,
        picture_path=None,
        font_manager=None,
        image_manager=None,
        transparent_encounter=False
):
    """制作场景卡背面"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'type' not in data or data['type'] not in ['场景卡', '密谋卡']:
        raise ValueError('卡牌类型错误')
    # 创建Card对象
    card = Card(
        width=1049,
        height=739,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type=data['type'],
        is_back=True
    )
    dp = open_picture(card_json, picture_path)
    # 贴底图
    if picture_path is not None and transparent_encounter:
        # 判断图片宽高，如果高大于宽，则需要将图片向左旋转90度
        if dp.size[1] > dp.size[0]:
            dp = dp.rotate(90, expand=True)
        # 铺满
        card.paste_image(dp, (0, 0, 1049, 739), 'cover')
    # 贴牌框-UI
    card.paste_image(image_manager.get_image(f'{data["type"]}-卡背'), (0, 0), 'contain')
    # 贴遭遇组
    if transparent_encounter:
        card.copy_circle_to_image(dp, (90, 144, 42), (97, 138, 42))
    # 写序列号
    small_words = '场景' if data['type'] == '场景卡' else '密谋'
    small_words += data.get('serial_number', '')
    card.draw_centered_text(
        position=(96, 68),
        text=small_words,
        font_name="小字",
        font_size=28,
        font_color=(0, 0, 0)
    )
    # 写标题
    title = Card(
        width=450,
        height=100,
        font_manager=font_manager,
        image_manager=image_manager,
    )
    title.draw_centered_text(
        position=(225, 50),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=48,
        font_color=(0, 0, 0)
    )
    title_img = title.image
    # 将表土向左旋转90度
    title_img = title_img.rotate(90, expand=True)
    card.paste_image(title_img, (40, 208), 'cover')
    # 写正文
    body = tidy_body_flavor(data, flavor_type=1)
    offset = -8
    card.draw_text(
        body,
        vertices=[
            (210 + offset, 67), (977 + offset, 67),
            (977 + offset, 672), (210 + offset, 672)
        ],
        default_font_name='simfang',
        default_size=32,
        padding=15,
        draw_virtual_box=False
    )

    # 画胜利点
    victory = data.get('victory', None)
    if victory is not None:
        card.draw_centered_text(
            position=(590, 680),
            text=f"胜利{data['victory']}。",
            font_name="思源黑体",
            font_size=28,
            font_color=(0, 0, 0)
        )
    return card


def create_story_card(
        card_json,
        picture_path=None,
        font_manager=None,
        image_manager=None,
        transparent_encounter=False,
        transparent_background=False
):
    """制作故事卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'type' not in data or data['type'] != '故事卡':
        raise ValueError('卡牌类型错误')
    # 创建Card对象
    card = Card(
        width=739,
        height=1049,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type=data['type'],
        is_back=True
    )
    dp = open_picture(card_json, picture_path)
    if transparent_background is False:
        # 贴底图
        if picture_path is not None:
            card.paste_image(dp, (0, 0, 739, 1049), 'cover')
        # 贴牌框-UI
        card.paste_image(image_manager.get_image(f'{data["type"]}'), (0, 0), 'contain')
    # 贴遭遇组
    if transparent_encounter:
        card.copy_circle_to_image(dp, (643, 92, 42), (600, 99, 42))
    # 写标题
    card.draw_centered_text(
        position=(313, 90),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=48,
        font_color=(0, 0, 0)
    )
    # 写小字
    card.draw_centered_text(
        position=(370, 1008),
        text='剧情',
        font_name="小字",
        font_size=30,
        font_color=(0, 0, 0)
    )
    # 写正文
    body = tidy_body_flavor(data)
    card.draw_text(
        body,
        vertices=[
            (50, 207), (685, 207),
            (685, 960), (50, 960)
        ],
        default_font_name='simfang',
        default_size=32,
        padding=15,
        draw_virtual_box=False
    )
    # 写胜利点
    victory = data.get('victory', None)
    if victory is not None:
        card.draw_centered_text(
            position=(386, 970),
            text=f"胜利{data['victory']}。",
            font_name="思源黑体",
            font_size=28,
            font_color=(0, 0, 0)
        )
    return card


def create_action_card(
        card_json,
        picture_path=None,
        font_manager=None,
        image_manager=None,
        transparent_encounter=False
):
    """制作行动卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'type' not in data or data['type'] != '行动卡':
        raise ValueError('卡牌类型错误')
    ui_name = f'{data["type"]}'
    vertices = [
        (56, 225), (685, 225),
        (685, 900), (56, 900)
    ]
    if data.get('action_type', 0) == 1:
        ui_name = f'{data["type"]}-中'
        vertices = [
            (56, 400), (685, 400),
            (685, 750), (56, 750)
        ]
    elif data.get('action_type', 0) == 2:
        ui_name = f'{data["type"]}-小'
        vertices = [
            (56, 470), (685, 470),
            (685, 670), (56, 670)
        ]
    # 创建Card对象
    card = Card(
        width=747,
        height=1043,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type=data['type'],
        is_back=True
    )
    # 贴底图
    if picture_path is not None:
        dp = open_picture(card_json, picture_path)
        card.paste_image(dp, (0, 0, 747, 1043), 'cover')
    # 贴牌框-UI
    card.paste_image(image_manager.get_image(ui_name), (0, 0), 'contain',
                     [(374, 180, 32)] if transparent_encounter else None)
    # 写标题
    card.draw_centered_text(
        position=(374, 85),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=48,
        font_color=(0, 0, 0)
    )
    # 写小字
    card.draw_centered_text(
        position=(372, 980),
        text='行动',
        font_name="小字",
        font_size=24,
        font_color=(0, 0, 0)
    )
    # 写正文
    body = tidy_body_flavor(data)
    card.draw_text(
        body,
        vertices,
        default_font_name='simfang',
        default_size=32,
        padding=15,
        draw_virtual_box=False
    )
    # 写胜利点
    victory = data.get('victory', None)
    if victory is not None:
        card.draw_centered_text(
            position=(386, 970),
            text=f"胜利{data['victory']}。",
            font_name="思源黑体",
            font_size=28,
            font_color=(0, 0, 0)
        )
    return card


def create_scenario_card(
        card_json,
        picture_path=None,
        font_manager=None,
        image_manager=None,
        transparent_encounter=False,
        transparent_background=False
):
    """生成冒险参考卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'type' not in data or data['type'] != '冒险参考卡':
        raise ValueError('卡牌类型错误')
    # 创建Card对象
    card = Card(
        width=739,
        height=1049,
        font_manager=font_manager,
        image_manager=image_manager,
        card_type=data['type'],
        is_back=True
    )
    dp = open_picture(card_json, picture_path)
    if transparent_background is False:
        # 贴底图
        if picture_path is not None:
            card.paste_image(dp, (0, 0, 739, 1049), 'cover')
        # 贴牌框-UI
        if data.get('scenario_type', 0) == 1:
            card.paste_image(image_manager.get_image(f'{data["type"]}-资源区'), (0, 0), 'contain')
        else:
            card.paste_image(image_manager.get_image(f'{data["type"]}'), (0, 0), 'contain')
    # 贴遭遇组
    if transparent_encounter:
        card.copy_circle_to_image(dp, (368, 144, 34), (368, 147, 34))
    # 写标题
    card.draw_centered_text(
        position=(369, 210),
        text=data['name'],
        font_name="汉仪小隶书简",
        font_size=48,
        font_color=(0, 0, 0),
        underline=True
    )
    if data.get('scenario_type', 0) == 2:
        # 辅助卡
        # 写正文
        body = tidy_body_flavor(data)
        card.draw_text(
            body,
            vertices=[
                (56, 250), (685, 250),
                (685, 920), (56, 920)
            ],
            default_font_name='simfang',
            default_size=32,
            padding=15,
            draw_virtual_box=False
        )
    else:
        # 写副标题
        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text(
                position=(369, 270),
                text=data['subtitle'],
                font_name="副标题",
                font_size=22,
                font_color=(0, 0, 0)
            )
        # 画正文
        scenario_card = data.get('scenario_card', {})
        card.draw_scenario_card(scenario_card, resource_name=scenario_card.get('resource_name', ''))
    return card


def sort_submit_icons(card_json):
    """
    对卡牌JSON中的submit_icon按指定顺序排序

    Args:
        card_json (dict): 卡牌JSON对象

    Returns:
        dict: 排序后的卡牌JSON对象
    """
    # 定义图标的优先级顺序
    icon_order = {
        "意志": 1,
        "智力": 2,
        "战力": 3,
        "敏捷": 4,
        "狂野": 5
    }

    # 复制原JSON对象以避免修改原对象
    result_json = card_json.copy()

    # 检查是否存在submit_icon字段
    if "submit_icon" in result_json and isinstance(result_json["submit_icon"], list):
        # 对submit_icon列表进行排序
        # 使用icon_order字典中的值作为排序键，如果图标不在字典中则放到最后
        result_json["submit_icon"] = sorted(
            result_json["submit_icon"],
            key=lambda x: icon_order.get(x, 999)
        )

    return result_json


def preprocessing_json(card_json):
    """预处理json信息"""

    card_json = sort_submit_icons(card_json)

    if 'body' not in card_json:
        card_json['body'] = ''

    if card_json.get('type', '') == '调查员':
        card_json['type'] = '调查员卡'
    if card_json.get('type', '') == '调查员背面':
        card_json['type'] = '调查员卡背'
    if card_json.get('type', '') == '定制卡':
        card_json['type'] = '升级卡'

    def replace_bracketed_content(match):
        content = match.group(1)  # 获取括号内的内容
        # 移除大括号
        content = content.replace('{', '').replace('}', '')
        # 分割成多行
        lines = content.split('\n')
        # 每行用<relish>标签包裹
        tagged_lines = [f'<relish>{line}</relish>' for line in lines if line.strip()]
        # 用换行符连接
        return '\n'.join(tagged_lines)

    if 'level' in card_json and card_json['level'] == '无':
        card_json['level'] = -1
    if 'body' in card_json and card_json['body'] != '':
        text = card_json['body']
        # 使用正则表达式匹配[XXX]格式的内容
        text = re.sub(r'<relish>(.*?)</relish>', replace_bracketed_content, text, flags=re.DOTALL)
        text = re.sub(r'\[([^]]+)]', replace_bracketed_content, text, flags=re.DOTALL)
        # 确保所有的<relish>都在行首，如果不是则加上换行
        text = re.sub(r'(?<!\n)<relish>', '\n<relish>', text)
        text = re.sub(r'<br>', '<lr>', text)
        card_json['body'] = text
    if card_json.get('class', '') == '弱点' and 'weakness_type' not in card_json:
        card_json['weakness_type'] = '弱点'

    if card_json.get('class', '') == '':
        # 如果没有class，则默认为中立
        card_json['class'] = '中立'

    text = json.dumps(card_json, ensure_ascii=False)
    # 将全角符号转换为半角符号
    text = text.replace('＜', '<').replace('＞', '>').replace('？', '?').replace('｛', '{').replace('｝', '}')

    # 替换se标签
    for se_item in se_icon:
        text = text.replace(se_item, se_icon[se_item])

    # 替换故事内容的换行
    if 'card_back' in card_json and 'story' in card_json['card_back']:
        story_text = card_json['card_back']['story']
        story_text = story_text.replace('\n', '<lr>')
        card_json['card_back']['story'] = story_text
    return json.loads(text)


def process_card_json(card_json, picture_path=None, font_manager=None, image_manager=None, image_mode=0,
                      transparent_encounter=False, transparent_background=False):
    """生成卡牌"""
    # 预处理
    card_json = preprocessing_json(card_json)
    if 'msg' in card_json and card_json['msg'] != '':
        raise ValueError(card_json['msg'])
    if 'type' not in card_json:
        raise ValueError('卡牌类型不能为空')
    if card_json['type'] == '调查员卡':
        return create_investigators_card(card_json, picture_path, font_manager, image_manager, image_mode=image_mode)
    elif card_json['type'] == '调查员卡背':
        return create_investigators_card_back(card_json, picture_path, font_manager, image_manager,
                                              image_mode=image_mode)
    elif card_json.get('class', '') == '弱点':
        return create_weakness_back(card_json, picture_path, font_manager, image_manager, image_mode=image_mode)
    elif card_json['type'] == '升级卡':
        return create_upgrade_card(card_json, picture_path, font_manager, image_manager)
    elif card_json['type'] == '故事卡':
        return create_story_card(card_json, picture_path, font_manager, image_manager,
                                 transparent_encounter=transparent_encounter,
                                 transparent_background=transparent_background)
    elif card_json['type'] == '行动卡':
        return create_action_card(card_json, picture_path, font_manager, image_manager,
                                  transparent_encounter=transparent_encounter)
    elif card_json['type'] == '冒险参考卡':
        return create_scenario_card(card_json, picture_path, font_manager, image_manager,
                                    transparent_encounter=transparent_encounter,
                                    transparent_background=transparent_background)
    elif card_json['type'] == '敌人卡':
        return create_enemy_card(card_json, picture_path, font_manager, image_manager, image_mode=image_mode,
                                 transparent_encounter=transparent_encounter,
                                 transparent_background=transparent_background)
    elif card_json['type'] == '诡计卡':
        return create_treachery_card(card_json, picture_path, font_manager, image_manager, image_mode=image_mode,
                                     transparent_encounter=transparent_encounter,
                                     transparent_background=transparent_background)
    elif card_json['type'] == '地点卡':
        return create_location_card(card_json, picture_path, font_manager, image_manager, image_mode=image_mode,
                                    transparent_encounter=transparent_encounter,
                                    transparent_background=transparent_background)
    elif card_json['type'] in ['场景卡-大画', '密谋卡-大画']:
        return create_large_picture(card_json, picture_path, font_manager, image_manager,
                                    transparent_encounter=transparent_encounter)
    elif card_json['type'] in ['场景卡', '密谋卡']:
        if card_json.get('is_back', False):
            return create_act_back_card(card_json, picture_path, font_manager, image_manager,
                                        transparent_encounter=transparent_encounter)
        return create_act_card(card_json, picture_path, font_manager, image_manager, image_mode=image_mode,
                               transparent_encounter=transparent_encounter)
    elif card_json['type'] in ['场景卡背', '密谋卡背']:
        card_json['is_back'] = True
        if card_json['type'] == '场景卡背':
            card_json['type'] = '场景卡'
        else:
            card_json['type'] = '密谋卡'
        return create_act_back_card(card_json, picture_path, font_manager, image_manager,
                                    transparent_encounter=transparent_encounter)
    else:
        if 'class' not in card_json:
            # 默认为中立
            card_json['class'] = '中立'
            # 默认无等级
            if 'level' not in card_json:
                card_json['level'] = -1
        return create_player_cards(card_json, picture_path, font_manager, image_manager, image_mode=image_mode,
                                   transparent_encounter=transparent_encounter)


if __name__ == '__main__':
    json_data = {
        "id": "",
        "created_at": "",
        "version": "1.0",
        "type": "调查员",
        "name": "🏅The Herta",
        "subtitle": "The Sorceress",
        "class": "探求者",
        "attribute": [
            3,
            6,
            1,
            1
        ],
        "health": 3,
        "horror": 12,
        "traits": [
            "Scholar",
            "Genius Society"
        ],
        "body":"",
        # "body": "You begin the game with 4 copies of Herta Puppet in play. When any amount of damage would be placed on you, place those damage on Herta Puppet (Online) instead.\n【Forced】 – When Herta Puppet (Online) is dealt damage: You take 1 direct horror.\n⚡Exhaust a copy of Herta Puppet at your location: You get +2 skill value during this test.\n⭐effect: +X. X is the number of Herta Puppet assets in play.",
        "language": "en",
        # "flavor": "“If they dared to write that, then I would call myself THE Herta.”"
        "flavor": ""
    }
    fm = FontManager('fonts')
    im = ImageManager('images')
    im.load_images('icons')

    fm.set_lang('en')
    card = process_card_json(json_data, picture_path=json_data.get('picture_path', None),
                             font_manager=fm,
                             image_manager=im,
                             image_mode=1,
                             transparent_encounter=False,
                             transparent_background=False)
    card.image.show()
