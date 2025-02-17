from PIL import Image

from Card import Card, FontManager, ImageManager


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


if __name__ == '__main__':
    json = {
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
    card = process_card_json(json, picture_path=r'C:\Users\xziyi\Desktop\java.png', font_manager=fm,
                               image_manager=im)
    card.image.save('output_card.png', quality=95)
