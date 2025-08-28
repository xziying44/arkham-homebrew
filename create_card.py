import json
import random
import re
from typing import Union, Optional
from PIL import Image, ImageEnhance
from Card import Card, FontManager, ImageManager


class CardCreator:
    """卡牌创建器类"""

    def __init__(self, font_manager: FontManager, image_manager: ImageManager,
                 image_mode: int = 0, transparent_encounter: bool = False,
                 transparent_background: bool = False):
        """
        初始化卡牌创建器

        Args:
            font_manager: 字体管理器
            image_manager: 图片管理器
            image_mode: 图片模式
            transparent_encounter: 透明遭遇组
            transparent_background: 透明背景
        """
        self.font_manager = font_manager
        self.image_manager = image_manager
        self.image_mode = image_mode
        self.transparent_encounter = transparent_encounter
        self.transparent_background = transparent_background

    def _open_picture(self, card_json: dict, picture_path: Union[str, Image.Image, None]) -> Optional[Image.Image]:
        """打开图片 - 支持路径和PIL图片对象"""
        if picture_path is None:
            return None

        try:
            # 如果传入的是PIL Image对象，直接使用
            if isinstance(picture_path, Image.Image):
                image = picture_path.copy()
            else:
                # 如果传入的是路径，则打开图片
                image = Image.open(picture_path)

            if card_json.get('picture_enhanced', False):
                # 增加亮度
                enhancer = ImageEnhance.Brightness(image)
                bright_image = enhancer.enhance(1.7)
                bright_image.point(lambda p: p * 1.5)
                return bright_image
            return image
        except Exception as e:
            print(f"Error opening image: {e}")
            return None

    def _paste_background_image(self, card: Card, picture_path: Union[str, Image.Image, None],
                                card_data: dict, dp: Optional[Image.Image] = None) -> None:
        """
        统一贴底图方法

        Args:
            card: 卡牌对象
            picture_path: 图片路径或PIL图片对象
            card_data: 卡牌数据
            dp: 已打开的图片对象(可选)
        """
        if picture_path is None:
            return

        if dp is None:
            dp = self._open_picture(card_data, picture_path)
            if dp is None:
                return

        card_type = card_data.get('type', '')

        # 透明遭遇组的特殊处理
        if self.transparent_encounter:
            if dp.size[1] > dp.size[0]:
                dp = dp.rotate(90, expand=True)
            card.paste_image(dp, (0, 0, card.width, card.height), 'cover')
            return

        # 常规贴底图逻辑
        image_mode = self.image_mode
        picture_layout = card_data.get('picture_layout', {})
        if picture_layout.get('mode', 'auto') == 'custom':
            image_mode = 3

        # 如果图片尺寸与卡牌尺寸几乎一致，使用覆盖模式
        if dp and abs(dp.size[0] - card.width) < 3 and abs(dp.size[1] - card.height) < 3:
            image_mode = 1

        if image_mode == 1:
            # 全覆盖模式
            if card_type in ['调查员卡', '调查员卡背'] and dp.size[0] < dp.size[1]:
                dp = dp.rotate(90, expand=True)
            elif card_type in ['场景卡', '密谋卡', '场景卡-大画', '密谋卡-大画'] and dp.size[1] > dp.size[0]:
                dp = dp.rotate(90, expand=True)

            card.paste_image(dp, (0, 0, card.width, card.height), 'cover')
        elif image_mode == 3:
            # 自定义模式
            paste_area = self._get_paste_area(card_type, card_data)
            if card_type in ['调查员卡']:
                paste_area = (0, 0, 1049, 739)
            card.paste_image_with_transform(dp, paste_area, picture_layout)
        else:
            # 部分覆盖模式 - 根据卡牌类型确定粘贴区域
            paste_area = self._get_paste_area(card_type, card_data)
            card.paste_image(dp, paste_area, 'cover')

    def _get_paste_area(self, card_type: str, card_data: dict) -> tuple:
        """
        获取不同卡牌类型的粘贴区域

        Args:
            card_type: 卡牌类型
            card_data: 卡牌数据

        Returns:
            tuple: (x, y, width, height) 粘贴区域
        """
        # 卡牌粘贴区域配置
        paste_areas = {
            # 竖向卡牌 (739x1049)
            '地点卡': (0, 80, 739, 562),
            '敌人卡': (0, 456, 739, 593),
            '诡计卡': (0, 0, 739, 605),
            '技能卡': (0, 88, 739, 600),
            '事件卡': (0, 0, 739, 589),
            '支援卡': (0, 80, 739, 540),
            '故事卡': (0, 0, 739, 1049),  # 全覆盖
            '行动卡': (0, 0, 747, 1043),  # 全覆盖
            '冒险参考卡': (0, 0, 739, 1049),  # 全覆盖

            # 横向卡牌 (1049x739)
            '调查员卡': (0, 75, 579, 664),
            '调查员卡背': (0, 0, 373, 405),
            '场景卡-大画': (0, 0, 1049, 739),  # 全覆盖
            '密谋卡-大画': (0, 0, 1049, 739),  # 全覆盖
        }

        # 场景卡和密谋卡的特殊处理
        if card_type == '场景卡':
            return (1049 - 626, 0, 626, 739)
        elif card_type == '密谋卡':
            return (0, 0, 626, 739)

        return paste_areas.get(card_type, (0, 0, 739, 1049))  # 默认全覆盖

    def _tidy_body_flavor(self, body: str, flavor: str, flavor_type: int = 0,
                          align: str = 'center', quote: bool = False) -> str:
        """整理正文和风味，正确处理flavor字段中的<lr>标签"""
        body = body.strip()
        tag_name = 'flavor'
        if align == 'left':
            tag_name = 'flavor align="left" flex="false" padding="0"'
        if quote:
            tag_name += ' quote="true" padding="20"'

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
                    remaining = remaining[idx + 4:]
                if remaining:
                    parts.append(remaining)

                # 构建结果
                result = []
                for part in parts:
                    if part == '<lr>':
                        result.append('<lr>')
                    elif part.strip():
                        result.append(f"<{tag_name}>{part.strip()}</flavor>")

                flavor = ''.join(result)
            else:
                # 普通处理
                flavor = '\n'.join(
                    f"<{tag_name}>{line.strip()}</flavor>"
                    for line in flavor.split('\n')
                    if line.strip()
                )
            if flavor_type == 0:
                body += f'\n{flavor}'
            else:
                body = f'{flavor}\n{body}'

        return body

    def _integrate_traits_text(self, traits: list) -> str:
        """整合特性文本"""
        if traits is None:
            return ''
        delimiter = '，'
        if self.font_manager.lang == 'en':
            delimiter = '. '

        result = delimiter.join([self.font_manager.get_font_text(trait) for trait in traits])
        if self.font_manager.lang == 'en' and result != '':
            result += '.'
        return result

    def _sort_submit_icons(self, card_json: dict) -> dict:
        """对卡牌JSON中的submit_icon按指定顺序排序"""
        icon_order = {
            "意志": 1,
            "智力": 2,
            "战力": 3,
            "敏捷": 4,
            "狂野": 5
        }

        result_json = card_json.copy()

        if "submit_icon" in result_json and isinstance(result_json["submit_icon"], list):
            result_json["submit_icon"] = sorted(
                result_json["submit_icon"],
                key=lambda x: icon_order.get(x, 999)
            )

        return result_json

    def _preprocessing_json(self, card_json: dict) -> dict:
        """预处理json信息"""
        card_json['name'] = card_json.get('name', '')
        card_json['name'] = card_json.get('name', '')
        card_json['body'] = card_json.get('body', '')
        card_json['flavor'] = card_json.get('flavor', '')
        card_json['subtitle'] = card_json.get('subtitle', '')

        card_json = self._sort_submit_icons(card_json)

        if 'subclass' in card_json:
            subclass = card_json.get('subclass', [])
            # 清除subclass里的null
            subclass = [item for item in subclass if item is not None]
            card_json['subclass'] = subclass
        if 'body' not in card_json:
            card_json['body'] = ''

        if card_json.get('type', '') == '调查员':
            card_json['type'] = '调查员卡'
        if card_json.get('type', '') == '调查员背面':
            card_json['type'] = '调查员卡背'
        if card_json.get('type', '') == '定制卡':
            card_json['type'] = '升级卡'

        def replace_bracketed_content(match):
            content = match.group(1)
            tag_name = 'flavor'
            if card_json.get('type', '') in ['密谋卡', '场景卡'] and card_json.get('is_back', False):
                tag_name += ' align="left" flex="false" quote="true" padding="20"'
            elif card_json.get('type', '') in ['密谋卡-大画', '场景卡-大画']:
                tag_name += ' align="left" flex="false" padding="0"'
            elif card_json.get('type', '') in ['故事卡']:
                tag_name += ' align="left" flex="false" quote="true" padding="20"'
            return f'<{tag_name}>{content}</flavor>'

        if 'level' in card_json and card_json['level'] == '无':
            card_json['level'] = -1
        if card_json['body'] != '':
            text = card_json['body']
            text = re.sub(r'\[([^]]+)]', replace_bracketed_content, text, flags=re.DOTALL)
            text = text.replace('】。', '】<font name="思源黑体">\uff61</font>')
            text = text.replace('。】', '】<font name="思源黑体">\uff61</font>')

            card_json['body'] = text
        if card_json.get('class', '') == '弱点' and 'weakness_type' not in card_json:
            card_json['weakness_type'] = '弱点'

        if card_json.get('class', '') == '':
            card_json['class'] = '中立'

        text = json.dumps(card_json, ensure_ascii=False)
        text = text.replace('＜', '<').replace('＞', '>').replace('？', '?').replace('｛', '{').replace('｝', '}')

        if 'card_back' in card_json and 'story' in card_json['card_back']:
            story_text = card_json['card_back']['story']
            story_text = story_text.replace('\n', '<lr>')
            card_json['card_back']['story'] = story_text

        return json.loads(text)

    def create_location_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作地点卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])

        card = Card(
            width=739,
            height=1049,
            font_manager=self.font_manager,
            image_manager=self.image_manager,
            card_type='地点卡'
        )

        dp = self._open_picture(card_json, picture_path)
        is_enemy = bool(data.get('enemy_health', ''))

        if not self.transparent_background:
            # 贴底图
            self._paste_background_image(card, picture_path, data, dp)

            if 'location_type' not in data or data['location_type'] not in ['未揭示', '已揭示']:
                data['location_type'] = '已揭示'

            if is_enemy:
                if 'subtitle' in data and data['subtitle'] != '':
                    card.paste_image(
                        self.image_manager.get_image(f'{data["type"]}-{data["location_type"]}-敌人-副标题'), (0, 0),
                        'contain')
                else:
                    card.paste_image(self.image_manager.get_image(f'{data["type"]}-{data["location_type"]}-敌人'),
                                     (0, 0), 'contain')
            else:
                if 'subtitle' in data and data['subtitle'] != '':
                    card.paste_image(self.image_manager.get_image(
                        f'{data["type"]}-{data["location_type"]}-副标题{"-虚拟" if card_json.get("virtual", False) else ""}'),
                        (0, 0), 'contain')
                else:
                    card.paste_image(self.image_manager.get_image(
                        f'{data["type"]}-{data["location_type"]}'
                        f'{"-半" if card_json.get("virtual", False) == "半" else ""}'
                        f'{"-虚拟" if card_json.get("virtual", False) else ""}'), (0, 0), 'contain')

        if self.transparent_encounter and dp:
            card.copy_circle_to_image(dp, (370, 518, 30), (370, 518, 30))

        # 写小字
        card.draw_centered_text(
            position=(370, 562),
            text=self.font_manager.get_font_text("地点"),
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
            text=self._integrate_traits_text(data.get('traits', [])),
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )

        # 整合body和flavor
        body = self._tidy_body_flavor(data['body'], data['flavor'])

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
            card.set_number_value(position=(62, 557), text=shroud, font_size=52)
            card.set_number_value(
                position=(675, 557), text=clues, font_size=52,
                color=(0, 0, 0), stroke_color=(255, 255, 255)
            )

        if is_enemy:
            # 画生命值恐惧值
            health = data.get('enemy_damage', 0) if isinstance(data.get('enemy_damage'), int) else 0
            horror = data.get('enemy_damage_horror', 0) if isinstance(data.get('enemy_damage_horror'), int) else 0
            if health > 0 or horror > 0:
                card.set_health_and_horror(health, horror)

            # 画攻击生命躲避
            attack = data.get('attack', '')
            evade = data.get('evade', '')
            enemy_health = data.get('enemy_health', '')
            card.set_number_value(position=(370, 132 + 480), text=enemy_health, font_size=52)
            card.set_number_value(position=(232, 132 + 480), text=attack, font_size=44)
            card.set_number_value(position=(508, 132 + 480), text=evade, font_size=44)

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
            for i, link in enumerate(data['location_link']):
                card.set_location_icon(i + 1, link)

        return card

    def create_treachery_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """诡计卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])

        card = Card(
            width=739,
            height=1049,
            font_manager=self.font_manager,
            image_manager=self.image_manager,
            card_type='诡计卡'
        )

        dp = self._open_picture(card_json, picture_path)

        if not self.transparent_background:
            # 贴底图
            self._paste_background_image(card, picture_path, data, dp)
            # 贴牌框
            card.paste_image(self.image_manager.get_image(f'{data["type"]}'), (0, 0), 'contain')

        # 贴遭遇组
        if self.transparent_encounter and dp:
            card.copy_circle_to_image(dp, (370, 534, 32), (370, 534, 32))

        # 写小字
        card.draw_centered_text(
            position=(370, 576),
            text=self.font_manager.get_font_text("诡计"),
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
            text=self._integrate_traits_text(data.get('traits', [])),
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )

        # 整合body和flavor
        body = self._tidy_body_flavor(data['body'], data['flavor'])

        # 写正文和风味
        card.draw_text(
            text=body,
            vertices=[(38, 700), (704, 700), (704, 1010), (38, 1010)],
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

    def create_enemy_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """敌人卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])

        card = Card(
            width=739,
            height=1049,
            font_manager=self.font_manager,
            image_manager=self.image_manager,
            card_type='敌人卡'
        )

        dp = self._open_picture(card_json, picture_path)

        if not self.transparent_background:
            # 贴底图
            self._paste_background_image(card, picture_path, data, dp)

            # 贴牌框
            if 'subtitle' in data and data['subtitle'] != '':
                card.paste_image(
                    self.image_manager.get_image(
                        f'{data["type"]}-副标题{"-虚拟" if card_json.get("virtual", False) else ""}'),
                    (0, 0))
            else:
                card.paste_image(
                    self.image_manager.get_image(f'{data["type"]}{"-虚拟" if card_json.get("virtual", False) else ""}'),
                    (0, 0), 'contain')

        # 贴遭遇组
        if self.transparent_encounter and dp:
            card.copy_circle_to_image(dp, (370, 570, 32), (370, 570, 32))

        # 写小字
        card.draw_centered_text(
            position=(364, 617),
            text=self.font_manager.get_font_text("敌人"),
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
            text=self._integrate_traits_text(data.get('traits', [])),
            font_name="方正舒体",
            font_size=32,
            font_color=(0, 0, 0)
        )

        # 整合body和flavor
        body = self._tidy_body_flavor(data['body'], data['flavor'])

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
                    (538, 510), (190, 510), (20, 450), (20, 270)
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
                    (538, 540), (190, 540), (20, 450), (20, 270)
                ],
                default_font_name='simfang',
                default_size=32,
                padding=15,
                draw_virtual_box=False
            )

        # 画生命值恐惧值
        health = data.get('enemy_damage', 0) if isinstance(data.get('enemy_damage'), int) else 0
        horror = data.get('enemy_damage_horror', 0) if isinstance(data.get('enemy_damage_horror'), int) else 0
        if health > 0 or horror > 0:
            card.set_health_and_horror(health, horror)

        # 画攻击生命躲避
        attack = data.get('attack', '')
        evade = data.get('evade', '')
        enemy_health = data.get('enemy_health', '')
        card.set_number_value(position=(370, 132), text=enemy_health, font_size=52)
        card.set_number_value(position=(232, 136), text=attack, font_size=44)
        card.set_number_value(position=(508, 136), text=evade, font_size=44)

        return card

    def create_upgrade_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作升级卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])

        card = Card(
            width=739,
            height=1049,
            font_manager=self.font_manager,
            image_manager=self.image_manager,
            card_type='升级卡'
        )

        # 贴牌框
        card.paste_image(self.image_manager.get_image('升级卡'), (0, 0), 'contain')

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
            vertices=[(38, 186), (700, 186), (700, 1009), (38, 1009)],
            default_font_name='simfang',
            default_size=32,
            padding=18,
            draw_virtual_box=False
        )

        return card

    def create_weakness_back(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作弱点卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])
        if 'class' not in data or data['class'] not in ['弱点']:
            raise ValueError('职业类型错误')

        card = Card(
            width=739,
            height=1049,
            font_manager=self.font_manager,
            image_manager=self.image_manager,
            card_type=data['type'],
            card_class=data['class']
        )

        if data['type'] not in ['事件卡', '支援卡', '技能卡', '诡计卡', '敌人卡']:
            raise ValueError('卡牌类型错误')

        # 整合body和flavor
        body = self._tidy_body_flavor(data['body'], data['flavor'])
        dp = self._open_picture(card_json, picture_path)

        if data['type'] == '事件卡':
            self._create_weakness_event_card(card, data, body, dp)
        elif data['type'] == '支援卡':
            self._create_weakness_support_card(card, data, body, dp)
        elif data['type'] == '技能卡':
            self._create_weakness_skill_card(card, data, body, dp)
        elif data['type'] == '诡计卡':
            self._create_weakness_treachery_card(card, data, body, dp)
        elif data['type'] == '敌人卡':
            self._create_weakness_enemy_card(card, data, body, dp)

        if data['weakness_type'] == '基础弱点':
            card.set_basic_weakness_icon()

        return card

    def _create_weakness_event_card(self, card, data, body, dp):
        """创建弱点事件卡"""
        if dp:
            # 贴底图
            self._paste_background_image(card, None, data, dp)

        card.paste_image(self.image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        card.draw_centered_text((76, 130), self.font_manager.get_font_text("事件"), "小字", 22, (0, 0, 0))
        card.draw_centered_text((370, 618), data['name'], "汉仪小隶书简", 48, (0, 0, 0))
        card.draw_centered_text((370, 668), self.font_manager.get_font_text(data['weakness_type']), "小字", 28,
                                (0, 0, 0))
        card.draw_centered_text((370, 705), self._integrate_traits_text(data.get('traits', [])), "方正舒体", 32,
                                (0, 0, 0))

        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])

        card.draw_text(
            body,
            vertices=[(38, 720), (704, 720), (706, 757), (704, 817), (680, 887), (670, 952),
                      (598, 980), (135, 980), (77, 949), (61, 907), (31, 793)],
            default_font_name='simfang', default_size=32, padding=18, draw_virtual_box=False
        )

    def _create_weakness_support_card(self, card, data, body, dp):
        """创建弱点支援卡"""
        if dp:
            # 贴底图
            self._paste_background_image(card, None, data, dp)

        if 'subtitle' in data and data['subtitle'] != '':
            card.paste_image(self.image_manager.get_image(f'{data["class"]}-{data["type"]}-副标题'), (0, 0), 'contain')
        else:
            card.paste_image(self.image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')

        card.draw_centered_text((76, 130), self.font_manager.get_font_text("支援"), "小字", 22, (0, 0, 0))
        card.draw_centered_text((370, 48), data['name'], "汉仪小隶书简", 48, (0, 0, 0))

        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text((370, 98), data['subtitle'], "副标题", 31, (0, 0, 0))

        card.draw_centered_text((370, 605), self.font_manager.get_font_text(data['weakness_type']), "小字", 28,
                                (0, 0, 0))
        card.draw_centered_text((370, 635), self._integrate_traits_text(data.get('traits', [])), "方正舒体", 32,
                                (0, 0, 0))

        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])

        card.draw_text(body, vertices=[(19, 660), (718, 660), (718, 910), (19, 910)],
                       default_font_name='simfang', default_size=32, padding=15, draw_virtual_box=False)

        if 'slots' in data and isinstance(data['slots'], str):
            card.add_slots(data['slots'])

        health = data.get('health', -1) if isinstance(data.get('health'), int) else -1
        horror = data.get('horror', -1) if isinstance(data.get('horror'), int) else -1
        if health != -1 or horror != -1:
            card.set_health_and_horror(health, horror)

    def _create_weakness_skill_card(self, card, data, body, dp):
        """创建弱点技能卡"""
        if dp:
            # 贴底图
            self._paste_background_image(card, None, data, dp)

        if 'subtitle' in data and data['subtitle'] != '':
            card.paste_image(self.image_manager.get_image(f'{data["class"]}-{data["type"]}-副标题'), (0, 0), 'contain')
        else:
            card.paste_image(self.image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')

        card.draw_centered_text((76, 132), self.font_manager.get_font_text("技能"), "小字", 22, (0, 0, 0))
        card.draw_left_text((140, 34), data['name'], "汉仪小隶书简", 48, (0, 0, 0))

        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text((378, 106), data['subtitle'], "副标题", 32, (0, 0, 0))

        card.draw_centered_text((368, 705), self.font_manager.get_font_text(data['weakness_type']), "小字", 28,
                                (0, 0, 0))
        card.draw_centered_text((368, 742), self._integrate_traits_text(data.get('traits', [])), "方正舒体", 30,
                                (0, 0, 0))

        offset = 16
        card.draw_text(
            body,
            vertices=[(75, 758), (682 + offset, 758), (692 + offset, 770), (704 + offset, 838), (701 + offset, 914),
                      (679 + offset, 989),
                      (74, 989), (91, 920), (96, 844)],
            default_font_name='simfang', default_size=32, padding=15, draw_virtual_box=False
        )

        if 'submit_icon' in data and isinstance(data['submit_icon'], list):
            for icon in data['submit_icon']:
                card.add_submit_icon(icon)

    def _create_weakness_treachery_card(self, card, data, body, dp):
        """创建弱点诡计卡"""
        if dp:
            # 贴底图
            self._paste_background_image(card, None, data, dp)

        card.paste_image(self.image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        card.draw_centered_text((370, 576), self.font_manager.get_font_text("诡计"), "小字", 24, (0, 0, 0))
        card.draw_centered_text((370, 625), data['name'], "汉仪小隶书简", 48, (0, 0, 0))
        card.draw_centered_text((370, 678), data['weakness_type'], "汉仪小隶书简", 28, (0, 0, 0))
        card.draw_centered_text((370, 715), self._integrate_traits_text(data.get('traits', [])), "方正舒体", 32,
                                (0, 0, 0))

        card.draw_text(body, vertices=[(38, 726), (704, 726), (704, 980), (38, 980)],
                       default_font_name='simfang', default_size=32, padding=18, draw_virtual_box=False)

    def _create_weakness_enemy_card(self, card, data, body, dp):
        """创建弱点敌人卡"""
        if dp:
            # 贴底图
            self._paste_background_image(card, None, data, dp)

        card.paste_image(self.image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        card.draw_centered_text((370, 620), self.font_manager.get_font_text("敌人"), "小字", 24, (0, 0, 0))
        card.draw_centered_text((370, 28), data['name'], "汉仪小隶书简", 48, (0, 0, 0))
        card.draw_centered_text((370, 78), data['weakness_type'], "汉仪小隶书简", 32, (0, 0, 0))
        card.draw_centered_text((370, 218), self._integrate_traits_text(data.get('traits', [])), "方正舒体", 32,
                                (0, 0, 0))

        if 'victory' in data and isinstance(data['victory'], int):
            card.draw_centered_text((380, 512), f"胜利{data['victory']}。", "思源黑体", 28, (0, 0, 0))
            vertices = [(90, 230), (645, 230), (699, 267), (727, 340), (688, 454),
                        (538, 504), (370, 504), (190, 504), (47, 454), (5, 340), (32, 267)]
        else:
            vertices = [(90, 230), (645, 230), (699, 267), (727, 340), (688, 454),
                        (538, 540), (370, 540), (190, 540), (47, 454), (5, 340), (32, 267)]

        card.draw_text(body, vertices=vertices, default_font_name='simfang', default_size=32, padding=15,
                       draw_virtual_box=False)

        health = data.get('enemy_damage', 0) if isinstance(data.get('enemy_damage'), int) else 0
        horror = data.get('enemy_damage_horror', 0) if isinstance(data.get('enemy_damage_horror'), int) else 0
        if health > 0 or horror > 0:
            card.set_health_and_horror(health, horror)

        attack = data.get('attack', '')
        evade = data.get('evade', '')
        enemy_health = data.get('enemy_health', '')
        card.set_number_value((370, 132), enemy_health, 52)
        card.set_number_value((232, 136), attack, 44)
        card.set_number_value((508, 136), evade, 44)

    def create_investigators_card_back(self, card_json: dict,
                                       picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作调查员卡背面"""
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
        card = Card(
            width=1049, height=739,
            font_manager=self.font_manager,
            image_manager=self.image_manager,
            card_type='调查员卡',
            card_class=data['class']
        )

        dp = self._open_picture(card_json, picture_path)

        # 贴底图
        if not self.transparent_background:
            self._paste_background_image(card, picture_path, data, dp)

        card.paste_image(self.image_manager.get_image(f'调查员卡-{data["class"]}-卡背'), (0, 0), 'contain')
        card.draw_centered_text((750, 36), data['name'], "汉仪小隶书简", 48, (0, 0, 0))
        card.draw_centered_text((750, 86), data['subtitle'], "副标题", 32, (0, 0, 0))

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
            test_text = self._tidy_body_flavor(test_text, card_back['story'], align='left')

        # 根据职业设置不同的文本区域
        vertices_map = {
            '守护者': [(385, 141), (1011, 141), (1011, 700), (36, 700), (36, 470), (220, 470), (220, 430), (366, 430)],
            '探求者': [(385, 141), (1011, 141), (1011, 700), (36, 700), (36, 470), (340, 470)],
            '生存者': [(385, 141), (1011, 141), (1011, 700), (36, 700), (36, 520), (114, 464), (340, 464)],
            '流浪者': [(385, 141), (1011, 141), (1011, 700), (36, 700), (36, 450), (350, 450)],
            '中立': [(420, 141), (1011, 141), (1011, 700), (36, 700), (36, 410), (380, 410)],
            '潜修者': [(385, 141), (1011, 141), (1011, 700), (36, 700), (36, 470), (170, 470), (182, 430), (358, 430)]
        }
        vertices = vertices_map.get(data['class'], vertices_map['潜修者'])

        card.draw_text(test_text, vertices=vertices, default_font_name='simfang', default_size=32,
                       padding=15, draw_virtual_box=False)

        return card

    def create_investigators_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作调查员卡正面"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])
        if 'class' not in data or data['class'] not in ['守护者', '探求者', '流浪者', '潜修者', '生存者', '中立']:
            raise ValueError('职业类型错误')

        card = Card(
            width=1049, height=739,
            font_manager=self.font_manager,
            image_manager=self.image_manager,
            card_type='调查员卡',
            card_class=data['class']
        )

        dp = self._open_picture(card_json, picture_path)

        card.paste_image(self.image_manager.get_image(f'{data["type"]}-{data["class"]}-底图'), (0, 0), 'contain')

        # 贴底图
        if not self.transparent_background:
            self._paste_background_image(card, picture_path, data, dp)

        card.paste_image(self.image_manager.get_image(f'{data["type"]}-{data["class"]}-UI'), (0, 0), 'contain')
        card.draw_centered_text((320, 36), data['name'], "汉仪小隶书简", 48, (0, 0, 0))
        card.draw_centered_text((320, 88), data['subtitle'], "副标题", 32, (0, 0, 0))

        # 写四维
        if 'attribute' in data and isinstance(data['attribute'], list):
            for i, attr in enumerate(data['attribute']):
                card.draw_centered_text((600 + 120 * i, 57), str(attr), "Bolton", 48, (0, 0, 0))

        traits = self._integrate_traits_text(data.get('traits', []))
        card.draw_centered_text((810, 160), traits, "方正舒体", 29, (0, 0, 0))

        body = self._tidy_body_flavor(data['body'], data['flavor'])
        card.draw_text(body, vertices=[(596, 178), (1016, 178),
                                       (1016, 600), (596, 600)],
                       default_font_name='simfang', default_size=32, padding=10, draw_virtual_box=False)

        health = data.get('health', 0) if isinstance(data.get('health'), int) else 0
        horror = data.get('horror', 0) if isinstance(data.get('horror'), int) else 0
        card.set_health_and_horror(health, horror)

        return card

    def create_player_cards(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作玩家卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])
        if 'type' not in data or data['type'] not in ['技能卡', '支援卡', '事件卡']:
            raise ValueError('卡牌类型错误')
        if 'class' not in data or data['class'] not in ['守护者', '探求者', '流浪者', '潜修者', '生存者', '中立',
                                                        '多职阶', '神话']:
            raise ValueError('职业类型错误')

        if data['class'] == '神话':
            data['class'] = '中立'
        if data['type'] == '技能卡' and data['class'] == '多职阶':
            raise ValueError('技能卡暂时不支持多职阶')

        card = self._create_player_card_base(data, picture_path)
        self._setup_player_card_content(card, data)

        return card

    def _create_player_card_base(self, data, picture_path):
        """创建玩家卡基础结构"""
        if data['type'] == '技能卡':
            card = Card(739, 1049, self.font_manager, self.image_manager, data['type'], data['class'])
            self._setup_skill_card_base(card, data, picture_path)
        elif data['type'] == '事件卡':
            card = Card(739, 1046, self.font_manager, self.image_manager, data['type'], data['class'])
            self._setup_event_card_base(card, data, picture_path)
        elif data['type'] == '支援卡':
            card = Card(739, 1049, self.font_manager, self.image_manager, data['type'], data['class'])
            self._setup_support_card_base(card, data, picture_path)

        return card

    def _setup_skill_card_base(self, card, data, picture_path):
        """设置技能卡基础"""
        dp = self._open_picture(data, picture_path)

        if not self.transparent_background:
            # 贴底图
            self._paste_background_image(card, picture_path, data, dp)

        card.paste_image(self.image_manager.get_image(f'{data["type"]}-{data["class"]}'), (0, 0), 'contain')
        card.draw_centered_text((73, 134), self.font_manager.get_font_text("技能"), "小字", 22, (0, 0, 0))

    def _setup_event_card_base(self, card, data, picture_path):
        """设置事件卡基础"""
        dp = self._open_picture(data, picture_path)

        if not self.transparent_background:
            # 贴底图
            self._paste_background_image(card, picture_path, data, dp)

        card.paste_image(self.image_manager.get_image(f'{data["type"]}-{data["class"]}'), (0, 0), 'contain')
        card.draw_centered_text((73, 134), self.font_manager.get_font_text("事件"), "小字", 22, (0, 0, 0))

    def _setup_support_card_base(self, card, data, picture_path):
        """设置支援卡基础"""
        dp = self._open_picture(data, picture_path)

        if not self.transparent_background:
            # 贴底图
            self._paste_background_image(card, picture_path, data, dp)

        frame_name = f'{data["type"]}-{data["class"]}'
        if 'subtitle' in data and data['subtitle'] != '':
            frame_name += '-副标题'

        transparency_list = [(690, 50, 46)] if self.transparent_encounter else None
        card.paste_image(self.image_manager.get_image(frame_name), (0, 0), 'contain', transparency_list)
        card.draw_centered_text((73, 134), self.font_manager.get_font_text("支援"), "小字", 22, (0, 0, 0))

    def _setup_player_card_content(self, card, data):
        """设置玩家卡内容"""

        # 画投入图标
        if 'submit_icon' in data and isinstance(data['submit_icon'], list):
            for icon in data['submit_icon']:
                card.add_submit_icon(icon)

        # 画等级
        level = data.get('level', -1)
        if isinstance(level, int):
            card.set_card_level(level)
        else:
            card.set_card_level(-1)

        traits = self._integrate_traits_text(data.get('traits', []))
        body = self._tidy_body_flavor(data['body'], data['flavor'])

        if data['type'] == '技能卡':
            self._setup_skill_card_content(card, data, traits, body)
        elif data['type'] == '事件卡':
            self._setup_event_card_content(card, data, traits, body)
        elif data['type'] == '支援卡':
            self._setup_support_card_content(card, data, traits, body)

        # 画多职介
        if data['class'] == '多职阶' and 'subclass' in data and isinstance(data['subclass'], list):
            card.set_subclass_icon(data['subclass'])

    def _setup_skill_card_content(self, card, data, traits, body):
        """设置技能卡内容"""
        card.draw_left_text((140, 30), data['name'], "汉仪小隶书简", 48, (0, 0, 0))
        card.draw_centered_text((368, 707), traits, "方正舒体", 32, (0, 0, 0))
        card.draw_text(
            body,
            vertices=[(75, 725), (682, 725), (692, 770), (704, 838), (701, 914), (679, 995),
                      (74, 995), (91, 920), (96, 844)],
            default_font_name='simfang', default_size=32, padding=15, draw_virtual_box=False
        )

    def _setup_event_card_content(self, card, data, traits, body):
        """设置事件卡内容"""
        offset = {'潜修者': -8, '守护者': -1, '生存者': -1, '中立': -5}.get(data.get('class', ''), 0)
        card.draw_centered_text((370, 621 + offset), data['name'], "汉仪小隶书简", 48, (0, 0, 0))
        card.draw_centered_text((368, 675), traits, "方正舒体", 32, (0, 0, 0))
        card.draw_text(
            body,
            vertices=[(45, 690), (694, 690), (706, 757), (704, 817), (680, 887), (670, 952),
                      (598, 992), (135, 992), (77, 949), (61, 907), (31, 793)],
            default_font_name='simfang', default_size=32, padding=18, draw_virtual_box=False
        )

        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])

        victory = data.get('victory', None)
        if victory is not None:
            card.draw_centered_text((378, 960), f"胜利{data['victory']}。", "思源黑体", 28, (0, 0, 0))

    def _setup_support_card_content(self, card, data, traits, body):
        """设置支援卡内容"""

        subclass = data.get('subclass', [])
        name_offset = 0
        if len(subclass) == 3:
            name_offset = -80
        elif len(subclass) == 2:
            name_offset = -40

        card.draw_centered_text((375 + name_offset, 46), data['name'], "汉仪小隶书简", 48, (0, 0, 0))

        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text((375, 98), data['subtitle'], "副标题", 31, (0, 0, 0))

        card.draw_centered_text((375, 643), traits, "方正舒体", 32, (0, 0, 0))
        card.draw_text(body, vertices=[(19, 662), (718, 662), (718, 925), (19, 925)],
                       default_font_name='simfang', default_size=32, padding=15, draw_virtual_box=False)

        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])

        if 'slots' in data and isinstance(data['slots'], str):
            card.add_slots(data['slots'])
        if 'slots2' in data and isinstance(data['slots2'], str):
            card.add_slots(data['slots2'])

        health = data.get('health', -1) if isinstance(data.get('health'), int) else -1
        horror = data.get('horror', -1) if isinstance(data.get('horror'), int) else -1
        if health != -1 or horror != -1:
            card.set_health_and_horror(health, horror)

        victory = data.get('victory', None)
        if victory is not None:
            pos = (675, 938) if 'slots' not in data else (379, 885)
            card.draw_centered_text(pos, f"胜利{data['victory']}。", "思源黑体", 28, (0, 0, 0))

    def create_large_picture(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作大画卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])
        if 'type' not in data or data['type'] not in ['场景卡-大画', '密谋卡-大画']:
            raise ValueError('卡牌类型错误')

        card = Card(1049, 739, self.font_manager, self.image_manager, data['type'])
        dp = self._open_picture(card_json, picture_path)

        # 贴底图
        if not self.transparent_background:
            self._paste_background_image(card, picture_path, data, dp)

        # 透明列表
        encounter_list = [(105, 499, 42)] if data['type'] == '场景卡-大画' else [(105, 459, 42), (953, 447, 52)]

        card.paste_image(self.image_manager.get_image(f'{data["type"]}'), (0, 0), 'contain',
                         encounter_list if self.transparent_encounter else None)

        title_y = 513 if data['type'] == '场景卡-大画' else 464
        card.draw_centered_text((500, title_y), data['name'], "汉仪小隶书简", 48, (0, 0, 0))

        body = self._tidy_body_flavor(data['body'], data['flavor'])
        text_y = 556 if data['type'] == '场景卡-大画' else 512
        card.draw_text(body, vertices=[(28, text_y), (1016, text_y), (1016, 686), (28, 686)],
                       default_font_name='simfang', default_size=32, padding=15, draw_virtual_box=False)

        # 写阈值
        if 'threshold' in data and data['type'] == '密谋卡-大画':
            card.set_number_value((953, 447), data['threshold'], 54)

        return card

    def create_act_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作场景卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])
        if 'type' not in data or data['type'] not in ['场景卡', '密谋卡']:
            raise ValueError('卡牌类型错误')

        card = Card(1049, 739, self.font_manager, self.image_manager, data['type'])
        dp = self._open_picture(card_json, picture_path)

        # 贴底图
        if not self.transparent_background:
            self._paste_background_image(card, picture_path, data, dp)

        # 透明列表
        encounter_list = [[(533, 628, 42), (528, 622, 42)], [(270, 74, 34), (288, 74, 34)]]
        if data['type'] != '场景卡':
            encounter_list = [[(520, 636, 44), (500, 630, 44)], [(288 + 473, 76, 34), (288 + 473, 76, 34)]]

        card.paste_image(self.image_manager.get_image(f'{data["type"]}'), (0, 0), 'contain')

        # 贴遭遇组
        if self.transparent_encounter and dp:
            for item in encounter_list:
                card.copy_circle_to_image(dp, item[0], item[1])

        # 写序列号
        if data['type'] == '场景卡':
            card.draw_centered_text((287, 25), f"场景{data.get('serial_number', '')}", "小字", 28, (0, 0, 0))
        else:
            card.draw_centered_text((758, 25), f"密谋{data.get('serial_number', '')}", "小字", 28, (0, 0, 0))

        # 写标题
        title_x = 285 if data['type'] == '场景卡' else 765
        card.draw_centered_text((title_x, 150), data['name'], "汉仪小隶书简", 48, (0, 0, 0))

        vertices = [(10, 185), (560, 185), (560, 574), (470, 574), (470, 678), (10, 678)]
        offset_x = -20
        if data['type'] != '场景卡':
            vertices = [
                (10 + 480 + offset_x, 185), (560 + 480 + offset_x, 185),
                (560 + 480 + offset_x, 678), (10 + 480 + 80 + offset_x, 678),
                (10 + 480 + 80 + offset_x, 574), (10 + 480 + offset_x, 574)
            ]

        # 写正文
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_type=1, align='left')
        card.draw_text(body, vertices=vertices, default_font_name='simfang', default_size=32,
                       padding=15, draw_virtual_box=False)

        # 写阈值
        if 'threshold' in data:
            threshold_pos = (523, 618) if data['type'] == '场景卡' else (498, 624)
            card.set_number_value(threshold_pos, data['threshold'], 54)

        return card

    def create_act_back_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作场景卡背面"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])
        if 'type' not in data or data['type'] not in ['场景卡', '密谋卡']:
            raise ValueError('卡牌类型错误')

        card = Card(1049, 739, self.font_manager, self.image_manager, data['type'], is_back=True)
        dp = self._open_picture(card_json, picture_path)

        # 贴底图
        if self.transparent_encounter and dp:
            self._paste_background_image(card, picture_path, data, dp)

        card.paste_image(self.image_manager.get_image(f'{data["type"]}-卡背'), (0, 0), 'contain')

        # 贴遭遇组
        if self.transparent_encounter and dp:
            card.copy_circle_to_image(dp, (90, 144, 42), (97, 138, 42))

        # 写序列号
        small_words = '场景' if data['type'] == '场景卡' else '密谋'
        small_words += data.get('serial_number', '')
        card.draw_centered_text((96, 68), small_words, "小字", 28, (0, 0, 0))

        # 写标题
        title = Card(450, 100, self.font_manager, self.image_manager)
        title.draw_centered_text((225, 50), data['name'], "汉仪小隶书简", 48, (0, 0, 0))
        title_img = title.image.rotate(90, expand=True)
        card.paste_image(title_img, (40, 208), 'cover')

        # 写正文
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_type=1, align='left', quote=True)
        offset = -8
        card.draw_text(
            body,
            vertices=[(210 + offset, 67), (977 + offset, 67), (977 + offset, 672), (210 + offset, 672)],
            default_font_name='simfang', default_size=32, padding=15, draw_virtual_box=False
        )

        # 画胜利点
        victory = data.get('victory', None)
        if victory is not None:
            card.draw_centered_text((590, 680), f"胜利{data['victory']}。", "思源黑体", 28, (0, 0, 0))

        return card

    def create_story_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作故事卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])
        if 'type' not in data or data['type'] != '故事卡':
            raise ValueError('卡牌类型错误')

        card = Card(739, 1049, self.font_manager, self.image_manager, data['type'], is_back=True)
        dp = self._open_picture(card_json, picture_path)

        if not self.transparent_background:
            # 贴底图
            self._paste_background_image(card, picture_path, data, dp)
            card.paste_image(self.image_manager.get_image(f'{data["type"]}'), (0, 0), 'contain')

        # 贴遭遇组
        if self.transparent_encounter and dp:
            card.copy_circle_to_image(dp, (643, 92, 42), (600, 99, 42))

        card.draw_centered_text((313, 90), data['name'], "汉仪小隶书简", 48, (0, 0, 0))
        card.draw_centered_text((370, 1008), '剧情', "小字", 30, (0, 0, 0))

        body = self._tidy_body_flavor(data['body'], data['flavor'])
        card.draw_text(body, vertices=[(50, 207), (685, 207), (685, 960), (50, 960)],
                       default_font_name='simfang', default_size=32, padding=15, draw_virtual_box=False)

        victory = data.get('victory', None)
        if victory is not None:
            card.draw_centered_text((386, 970), f"胜利{data['victory']}。", "思源黑体", 28, (0, 0, 0))

        return card

    def create_action_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作行动卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])
        if 'type' not in data or data['type'] != '行动卡':
            raise ValueError('卡牌类型错误')

        ui_name = f'{data["type"]}'
        vertices = [(56, 225), (685, 225), (685, 900), (56, 900)]

        if data.get('action_type', 0) == 1:
            ui_name = f'{data["type"]}-中'
            vertices = [(56, 400), (685, 400), (685, 750), (56, 750)]
        elif data.get('action_type', 0) == 2:
            ui_name = f'{data["type"]}-小'
            vertices = [(56, 470), (685, 470), (685, 670), (56, 670)]

        card = Card(747, 1043, self.font_manager, self.image_manager, data['type'], is_back=True)
        dp = self._open_picture(card_json, picture_path)

        # 贴底图
        if not self.transparent_background:
            self._paste_background_image(card, picture_path, data, dp)

        transparency_list = [(374, 180, 32)] if self.transparent_encounter else None
        card.paste_image(self.image_manager.get_image(ui_name), (0, 0), 'contain', transparency_list)

        card.draw_centered_text((374, 85), data['name'], "汉仪小隶书简", 48, (0, 0, 0))
        card.draw_centered_text((372, 980), '行动', "小字", 24, (0, 0, 0))

        body = self._tidy_body_flavor(data['body'], data['flavor'])
        card.draw_text(body, vertices, default_font_name='simfang', default_size=32,
                       padding=15, draw_virtual_box=False)

        victory = data.get('victory', None)
        if victory is not None:
            card.draw_centered_text((386, 970), f"胜利{data['victory']}。", "思源黑体", 28, (0, 0, 0))

        return card

    def create_scenario_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """生成冒险参考卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])
        if 'type' not in data or data['type'] != '冒险参考卡':
            raise ValueError('卡牌类型错误')

        card = Card(739, 1049, self.font_manager, self.image_manager, data['type'], is_back=True)
        dp = self._open_picture(card_json, picture_path)

        if not self.transparent_background:
            # 贴底图
            self._paste_background_image(card, picture_path, data, dp)

            if data.get('scenario_type', 0) == 1:
                card.paste_image(self.image_manager.get_image(f'{data["type"]}-资源区'), (0, 0), 'contain')
            else:
                card.paste_image(self.image_manager.get_image(f'{data["type"]}'), (0, 0), 'contain')

        # 贴遭遇组
        if self.transparent_encounter and dp:
            card.copy_circle_to_image(dp, (368, 144, 34), (368, 147, 34))

        card.draw_centered_text((369, 210), data['name'], "汉仪小隶书简", 48, (0, 0, 0), underline=True)

        if data.get('scenario_type', 0) == 2:
            # 辅助卡
            body = self._tidy_body_flavor(data['body'], data['flavor'])
            card.draw_text(body, vertices=[(56, 250), (685, 250), (685, 920), (56, 920)],
                           default_font_name='simfang', default_size=32, padding=15, draw_virtual_box=False)
        else:
            # 写副标题
            if 'subtitle' in data and data['subtitle'] != '':
                card.draw_centered_text((369, 270), data['subtitle'], "副标题", 22, (0, 0, 0))

            # 画正文
            scenario_card = data.get('scenario_card', {})
            card.draw_scenario_card(scenario_card, resource_name=scenario_card.get('resource_name', ''))

        return card

    def create_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """
        入口函数 - 根据卡牌类型创建对应的卡牌

        Args:
            card_json: 卡牌JSON数据
            picture_path: 图片路径或PIL图片对象

        Returns:
            Card: 创建的卡牌对象
        """
        # 预处理
        card_json = self._preprocessing_json(card_json)

        if 'msg' in card_json and card_json['msg'] != '':
            raise ValueError(card_json['msg'])
        if 'type' not in card_json:
            raise ValueError('卡牌类型不能为空')

        card_type = card_json['type']

        # 根据卡牌类型调用对应的创建方法
        if card_type == '调查员卡':
            return self.create_investigators_card(card_json, picture_path)
        elif card_type == '调查员卡背':
            return self.create_investigators_card_back(card_json, picture_path)
        elif card_json.get('class', '') == '弱点':
            return self.create_weakness_back(card_json, picture_path)
        elif card_type == '升级卡':
            return self.create_upgrade_card(card_json, picture_path)
        elif card_type == '故事卡':
            return self.create_story_card(card_json, picture_path)
        elif card_type == '行动卡':
            return self.create_action_card(card_json, picture_path)
        elif card_type == '冒险参考卡':
            return self.create_scenario_card(card_json, picture_path)
        elif card_type == '敌人卡':
            return self.create_enemy_card(card_json, picture_path)
        elif card_type == '诡计卡':
            return self.create_treachery_card(card_json, picture_path)
        elif card_type == '地点卡':
            return self.create_location_card(card_json, picture_path)
        elif card_type in ['场景卡-大画', '密谋卡-大画']:
            return self.create_large_picture(card_json, picture_path)
        elif card_type in ['场景卡', '密谋卡']:
            if card_json.get('is_back', False):
                return self.create_act_back_card(card_json, picture_path)
            return self.create_act_card(card_json, picture_path)
        elif card_type in ['场景卡背', '密谋卡背']:
            card_json['is_back'] = True
            if card_type == '场景卡背':
                card_json['type'] = '场景卡'
            else:
                card_json['type'] = '密谋卡'
            return self.create_act_back_card(card_json, picture_path)
        else:
            if 'class' not in card_json:
                card_json['class'] = '中立'
                if 'level' not in card_json:
                    card_json['level'] = -1
            return self.create_player_cards(card_json, picture_path)


# 使用示例
if __name__ == '__main__':
    json_data = {
        "type": "故事卡",
        "name": "矿工",
        "id": 330,
        "created_at": "",
        "version": "1.0",
        "language": "zh",
        "victory": 1,
        "body": "\n<relish>当通讯器连接到脑缸时，你只听到尖叫声。“啊啊啊！我在坠落！我在坠落！”也许脱离肉体对脆弱的人类心智来说太过难以承受。</relish>\n<hr>\n【如果太空漂流在胜利区：】\n<relish>你温柔地让他们相信他们不再漂浮在太空中——他们终于安息了。不知何故，那个声音感到宽慰并叹了口气。当你询问绑架他们的邪教徒时，他们告诉你所有记得的事情。</relish>\n将该卡牌加入胜利区。\n<hr>\n【否则：】\n<relish>你试图安抚他们并询问关于邪教徒的事，但他们从未停止尖叫。</relish>\n受到1点恐惧并将该卡牌洗回扫描牌库。",
        "subtitle": "",
        "traits": [],
        "picture_path": "D:\\BaiduSyncdisk\\PycharmProjects\\arkham_translate\\translation_space\\暗物质\\factory\\000330-raw.jpg",
        "class": "中立"
    }

    # 创建字体和图片管理器
    fm = FontManager('fonts')
    im = ImageManager('images')
    im.load_images('icons')

    # 创建卡牌创建器
    creator = CardCreator(
        font_manager=fm,
        image_manager=im,
        image_mode=1,
        transparent_encounter=False,
        transparent_background=False
    )

    # 创建卡牌 - 支持PIL图片对象
    # picture = Image.open("path/to/image.jpg")  # 也可以传入PIL图片对象
    # fm.set_lang('en')
    # card = creator.create_card(json_data, picture_path=None)
    # card.image.show()

    fm.set_lang('zh')
    card = creator.create_card(json_data, picture_path=None)
    card.image.show()
