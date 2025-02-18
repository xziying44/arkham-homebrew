import json
import random
import re

from PIL import Image

from Card import Card, FontManager, ImageManager

DEFAULT_CARD_JSON = {
    "SaveName": "",
    "Date": "",
    "VersionNumber": "",
    "GameMode": "",
    "GameType": "",
    "GameComplexity": "",
    "Tags": [],
    "Gravity": 0.5,
    "PlayArea": 0.5,
    "Table": "",
    "Sky": "",
    "Note": "",
    "TabStates": {},
    "LuaScript": "",
    "LuaScriptState": "",
    "XmlUI": "",
    "ObjectStates": [

    ]
}
DEFAULT_CARD_DEFAULT_JSON = {
    "GUID": "8fd879",
    "Name": "CardCustom",
    "Transform": {
        "posX": 19.1539841,
        "posY": 1.49510384,
        "posZ": 38.9961624,
        "rotX": -9.754563E-08,
        "rotY": 270.0,
        "rotZ": 2.057618E-07,
        "scaleX": 1.0,
        "scaleY": 1.0,
        "scaleZ": 1.0
    },
    "Nickname": "",
    "Description": "",
    "GMNotes": "",
    "AltLookAngle": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
    },
    "ColorDiffuse": {
        "r": 0.713235259,
        "g": 0.713235259,
        "b": 0.713235259
    },
    "Tags": [

    ],
    "LayoutGroupSortIndex": 0,
    "Value": 0,
    "Locked": False,
    "Grid": True,
    "Snap": True,
    "IgnoreFoW": False,
    "MeasureMovement": False,
    "DragSelectable": True,
    "Autoraise": True,
    "Sticky": True,
    "Tooltip": True,
    "GridProjection": False,
    "HideWhenFaceDown": True,
    "Hands": True,
    "CardID": 0,
    "SidewaysCard": False,
    "CustomDeck": {
    },
    "LuaScript": "",
    "LuaScriptState": "",
    "XmlUI": ""
}
DEFAULT_CARD_INVESTIGATOR_JSON = {
    "GUID": "89a2a6",
    "Name": "CardCustom",
    "Transform": {
        "posX": -37.8683434,
        "posY": 1.53360486,
        "posZ": 11.4118834,
        "rotX": 5.696528E-07,
        "rotY": 270.000153,
        "rotZ": -3.2847106E-07,
        "scaleX": 0.8291292,
        "scaleY": 1.0,
        "scaleZ": 0.8291292
    },
    "Nickname": "",
    "Description": "",
    "GMNotes": "",
    "AltLookAngle": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
    },
    "ColorDiffuse": {
        "r": 0.713235259,
        "g": 0.713235259,
        "b": 0.713235259
    },
    "LayoutGroupSortIndex": 0,
    "Value": 0,
    "Locked": False,
    "Grid": True,
    "Snap": True,
    "IgnoreFoW": False,
    "MeasureMovement": False,
    "DragSelectable": True,
    "Autoraise": True,
    "Sticky": True,
    "Tooltip": True,
    "GridProjection": False,
    "HideWhenFaceDown": True,
    "Hands": True,
    "CardID": 0,
    "SidewaysCard": False,
    "CustomDeck": {
    },
    "Tags": [

    ],
    "LuaScript": "",
    "LuaScriptState": "",
    "XmlUI": ""
}
DEFAULT_CARD_CUSTOM_DECK_JSON = {
    "FaceURL": "",
    "BackURL": "",
    "NumWidth": 1,
    "NumHeight": 1,
    "BackIsHidden": True,
    "UniqueBack": False,
    "Type": 0
}


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


def create_weakness_back(card_json, picture_path=None, font_manager=None, image_manager=None):
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
    if data['type'] not in ['事件卡', '支援卡', '技能卡', '诡计卡']:
        raise ValueError('卡牌类型错误')
    # 整合body和flavor
    body = data['body']
    if 'flavor' in data and data['flavor'] != '':
        body += "\n<hr>\n"
        flavor = data['flavor']
        flavor_list = flavor.split('\n')
        for i in range(len(flavor_list)):
            flavor_list[i] = f"<relish>{flavor_list[i]}</relish>"
        body += '\n'.join(flavor_list)
    if data['type'] == '事件卡':
        # 贴底图
        if picture_path is not None:
            dp = Image.open(picture_path)
            card.paste_image(dp, (0, 0, 739, 580), 'cover')
        # 贴牌框
        card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(76, 130),
            text="事件",
            font_name="汉仪小隶书简",
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
            text='，'.join(data['traits']),
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
            dp = Image.open(picture_path)
            card.paste_image(dp, (0, 85, 739, 510), 'cover')
        # 贴牌框
        if 'subtitle' in data and data['subtitle'] != '':
            card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}-副标题'), (0, 0), 'contain')
        else:
            card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(76, 130),
            text="支援",
            font_name="汉仪小隶书简",
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
                font_name="汉仪小隶书简",
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
            text='，'.join(data['traits']),
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
            dp = Image.open(picture_path)
            card.paste_image(dp, (0, 88, 739, 600), 'cover')
        # 贴牌框
        if 'subtitle' in data and data['subtitle'] != '':
            card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}-副标题'), (0, 0), 'contain')
        else:
            card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(76, 130),
            text="技能",
            font_name="汉仪小隶书简",
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
                font_name="汉仪小隶书简",
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
            text='，'.join(data['traits']),
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
            dp = Image.open(picture_path)
            card.paste_image(dp, (0, 0, 739, 605), 'cover')
        # 贴牌框
        card.paste_image(image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(370, 576),
            text="诡计",
            font_name="汉仪小隶书简",
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
            text='，'.join(data['traits']),
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
    if data['weakness_type'] == '基础弱点':
        card.set_basic_weakness_icon()

    return card


def create_investigators_card_back(card_json, picture_path=None, font_manager=None, image_manager=None):
    """制作调查员卡背面"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'class' not in data or data['class'] not in ['守护者', '探求者', '流浪者', '潜修者', '生存者', '中立']:
        raise ValueError('职业类型错误')
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
        dp = Image.open(picture_path)
        card.paste_image(dp, (0, 0, 373, 405), 'cover')

    # 贴牌框-UI
    card.paste_image(image_manager.get_image(f'{data["type"]}-{data["class"]}-卡背'), (0, 0), 'contain')

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
        position=(750, 88),
        text=data['subtitle'],
        font_name="汉仪小隶书简",
        font_size=32,
        font_color=(0, 0, 0)
    )
    test_text = ""
    if 'size' in card_back:
        test_text += f"【牌库卡牌张数】：{card_back['size']}。\n"
    if 'option' in card_back and len(card_back['option']) > 0:
        test_text += '【牌库构筑选项】：' + '，'.join(card_back['option']) + '。\n'
    if 'requirement' in card_back and card_back['requirement'] != '':
        test_text += f"【牌库构筑需求】(不计入卡牌张数)：{card_back['requirement']}\n"
    if 'other' in card_back and card_back['other'] != '':
        test_text += card_back['other'] + '\n'
    if 'story' in card_back and card_back['story'] != '':
        test_text += f"<hr><relish center='false'>{card_back['story']}</relish>"
    card.draw_text(
        test_text,
        vertices=[
            (385, 141), (1011, 141), (1011, 686), (36, 686),
            (36, 500), (308, 500), (308, 450), (358, 450)
        ],
        default_font_name='simfang',
        default_size=32,
        padding=15,
        draw_virtual_box=False
    )

    return card


def create_investigators_card(card_json, picture_path=None, font_manager=None, image_manager=None):
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
        dp = Image.open(picture_path)
        card.paste_image(dp, (0, 75, 579, 664), 'cover')
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
        font_name="汉仪小隶书简",
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
        traits = '，'.join(data['traits'])
    card.draw_centered_text(
        position=(810, 168),
        text=traits,
        font_name="方正舒体",
        font_size=32,
        font_color=(0, 0, 0)
    )
    # 整理body和风味
    body = data['body']
    if 'flavor' in data and data['flavor'] != '':
        # 按/n分割data['flavor']
        body += "\n<hr>\n"
        flavor = data['flavor']
        flavor_list = flavor.split('\n')
        for i in range(len(flavor_list)):
            flavor_list[i] = f"<relish>{flavor_list[i]}</relish>"
        body += '\n'.join(flavor_list)
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


def create_player_cards(card_json, picture_path=None, font_manager=None, image_manager=None):
    """制作玩家卡"""
    # 解析JSON字符串
    data = card_json
    if 'msg' in data and data['msg'] != '':
        raise ValueError(data['msg'])
    if 'type' not in data or data['type'] not in ['技能卡', '支援卡', '事件卡']:
        raise ValueError('卡牌类型错误')
    if 'class' not in data or data['class'] not in ['守护者', '探求者', '流浪者', '潜修者', '生存者', '中立', '多职阶']:
        raise ValueError('职业类型错误')
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
            dp = Image.open(picture_path)
            card.paste_image(dp, (0, 88, 739, 600), 'cover')
        # 贴牌框
        card.paste_image(image_manager.get_image(f'{data["type"]}-{data["class"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(73, 132),
            text="技能",
            font_name="汉仪小隶书简",
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
            dp = Image.open(picture_path)
            card.paste_image(dp, (0, 0, 739, 589), 'cover')
        # 贴牌框
        card.paste_image(image_manager.get_image(f'{data["type"]}-{data["class"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(73, 130),
            text="事件",
            font_name="汉仪小隶书简",
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
            dp = Image.open(picture_path)
            card.paste_image(dp, (0, 80, 739, 540), 'cover')
        # 贴牌框
        if 'subtitle' in data and data['subtitle'] != '':
            card.paste_image(image_manager.get_image(f'{data["type"]}-{data["class"]}-副标题'), (0, 0), 'contain')
        else:
            card.paste_image(image_manager.get_image(f'{data["type"]}-{data["class"]}'), (0, 0), 'contain')
        # 写小字
        card.draw_centered_text(
            position=(73, 130),
            text="支援",
            font_name="汉仪小隶书简",
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
    traits = ''
    if 'traits' in data and isinstance(data['traits'], list):
        traits = '，'.join(data['traits'])
    # 整理body和风味
    body = data['body']
    if 'flavor' in data and data['flavor'] != '':
        # 按/n分割data['flavor']
        body += "\n<hr>\n"
        flavor = data['flavor']
        flavor_list = flavor.split('\n')
        for i in range(len(flavor_list)):
            flavor_list[i] = f"<relish>{flavor_list[i]}</relish>"
        body += '\n'.join(flavor_list)
    # 按不同类型画位置
    if data['type'] == '技能卡':
        # 画名称
        card.draw_left_text(
            position=(140, 34),
            text=data['name'],
            font_name="汉仪小隶书简",
            font_size=48,
            font_color=(0, 0, 0)
        )
        # 画特性
        card.draw_centered_text(
            position=(368, 713),
            text=traits,
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )
        # 画正文和风味
        card.draw_text(
            text=body,
            vertices=[
                (75, 735), (682, 735), (692, 770), (704, 838), (701, 914), (679, 986),
                (74, 986), (91, 920), (96, 844)
            ],
            default_font_name='simfang',
            default_size=32,
            padding=15,
            draw_virtual_box=False
        )
        pass
    elif data['type'] == '事件卡':
        # 画名称
        card.draw_centered_text(
            position=(370, 618),
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
                (598, 980), (135, 980), (77, 949), (61, 907), (31, 793)
            ],
            default_font_name='simfang',
            default_size=32,
            padding=15,
            draw_virtual_box=False
        )
        # 画价格
        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])
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
                font_name="汉仪小隶书简",
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
                (19, 662), (718, 662), (718, 910), (19, 910)
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
    # 画多职介
    if data['class'] == '多职阶' and 'subclass' in data and isinstance(data['subclass'], list):
        card.set_subclass_icon(data['subclass'])
    return card


def process_card_json(card_json, picture_path=None, font_manager=None, image_manager=None):
    if 'type' not in card_json:
        raise ValueError('卡牌类型不能为空')
    if card_json['type'] == '调查员卡':
        if 'card_back' in card_json and len(card_json['card_back']['option']) > 0:
            return create_investigators_card_back(card_json, picture_path, font_manager, image_manager)
        else:
            return create_investigators_card(card_json, picture_path, font_manager, image_manager)
    elif card_json['class'] == '弱点':
        return create_weakness_back(card_json, picture_path, font_manager, image_manager)
    elif card_json['type'] == '升级卡':
        return create_upgrade_card(card_json, picture_path, font_manager, image_manager)
    else:
        return create_player_cards(card_json, picture_path, font_manager, image_manager)


card_type_transform = {
    '支援卡': 'Asset',
    '技能卡': 'Skill',
    '事件卡': 'Event',
    '诡计卡': 'Treachery',
    '调查员卡': 'Investigator',
}
card_class_transform = {
    '守护者': 'Guardian',
    '探求者': 'Seeker',
    '流浪者': 'Rogue',
    '潜修者': 'Mystic',
    '生存者': 'Survivor',
    '中立': 'Neutral'
}
# 资源 子弹 赏金 充能 证据 秘密 补给 贡品
card_token_transform = {
    '资源': 'Resource',
    '子弹': 'Ammo',
    '赏金': 'Bounty',
    '充能': 'Charge',
    '证据': 'Evidence',
    '秘密': 'Secret',
    '补给': 'Supply',
    '贡品': 'Offering'
}


def process_card_json_to_tts_json(card_json, front_image_url="", back_image_url=""):
    """生成TTS卡牌JSON"""
    print(card_json)
    if front_image_url == "":
        raise ValueError('正面图片URL不能为空')
    if back_image_url == "":
        raise ValueError('背面图片URL不能为空')
    # 生成卡牌元数据
    card_note = {
        'id': str(random.randint(100001, 999999))
    }
    if card_json['type'] in card_type_transform:
        card_note['type'] = card_type_transform[card_json['type']]
    if card_json['class'] in card_class_transform:
        card_note['class'] = card_class_transform[card_json['class']]
    # 支援卡的token
    if card_json['type'] == '支援卡':
        # 查找card_json['body']是否有 使用(X标记)的字样，取回字样这个词，X是数字，X也要取回
        match = re.search(r'使用[（(](\d+)([\u4e00-\u9fa5]+)[）)]', card_json['body'])
        if match:
            num, mark = match.groups()
            card_note['uses'] = [
                {
                    "count": int(num),
                    "type": card_token_transform[mark] if mark in card_token_transform else 'Resource',
                    "token": "resource"
                }
            ]
    # 调查员卡
    if card_json['type'] == '调查员卡':
        if len(card_json['attribute']) == 4:
            card_note['willpowerIcons'] = card_json['attribute'][0]
            card_note['intellectIcons'] = card_json['attribute'][1]
            card_note['combatIcons'] = card_json['attribute'][2]
            card_note['agilityIcons'] = card_json['attribute'][3]
        # 查找card_json['body']是否有<免费> <反应>
        if '<免费>' in card_json['body']:
            card_note['extraToken'] = 'FreeTrigger'
        elif '<反应>' in card_json['body']:
            card_note['extraToken'] = 'Reaction'
        pass

    temp_card = json.loads(json.dumps(DEFAULT_CARD_DEFAULT_JSON))
    if card_json['type'] == '调查员卡':
        temp_card = json.loads(json.dumps(DEFAULT_CARD_INVESTIGATOR_JSON))
    custom_deck = json.loads(json.dumps(DEFAULT_CARD_CUSTOM_DECK_JSON))
    custom_deck['FaceURL'] = front_image_url
    custom_deck['BackURL'] = back_image_url
    temp_card['Nickname'] = card_json['name']
    temp_card['GMNotes'] = json.dumps(card_note, indent=2)

    if card_json['type'] in ['技能卡', '支援卡', '事件卡', '调查员卡'] or card_json['class'] == '弱点':
        temp_card['Tags'].append('PlayerCard')
    if card_json['type'] == '支援卡':
        temp_card['Tags'].append('Asset')
    if card_json['type'] == '调查员卡':
        temp_card['Tags'].append('Investigator')
    # 在temp_card['CustomDeck']加一个对象，对象的key是一个随机数，value是temp_info
    card_id = str(random.randint(10000, 99999))
    temp_card['CustomDeck'] = {
        card_id: custom_deck
    }
    temp_card['CardID'] = int(card_id + '00')
    # 生成最终JSON
    tts_card_json = json.loads(json.dumps(DEFAULT_CARD_JSON))
    tts_card_json['ObjectStates'].append(temp_card)
    print(tts_card_json)
    return tts_card_json


if __name__ == '__main__':
    json_data = {
        "type": "升级卡",
        "class": "",
        "subclass": [],
        "name": "忍一手",
        "weakness_type": "",
        "subtitle": "",
        "attribute": [],
        "cost": 0,
        "submit_icon": [],
        "level": -1,
        "traits": [],
        "body": "□【升级选项】 测试升级正文测试升级正文测试升级正文\n□□□【升级选项】 测试升级正文测试升级正文测试升级正文\n□【升级选项】 测试升级正文测试升级正文测试升级正文",
        "flavor": "",
        "slots": "",
        "health": 0,
        "horror": 0,
        "card_back": {
            "size": 30,
            "option": [],
            "requirement": "",
            "other": "",
            "story": ""
        },
        "msg": ""
    }
    fm = FontManager('fonts')
    im = ImageManager('images')
    card = process_card_json(json_data, picture_path=r'C:\Users\xziyi\Desktop\java.png', font_manager=fm,
                             image_manager=im)
    card.image.save('output_card.png', quality=95)
