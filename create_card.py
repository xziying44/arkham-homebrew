import cProfile
import json
import pstats
import re
from typing import Union, Optional

from PIL import Image, ImageEnhance
from ResourceManager import FontManager, ImageManager
from Card import Card
from card_cdapter import CardAdapter

# 缩略图裁剪区域定义（从 images.ts 转换而来）
THUMBNAIL_REGIONS = {
    "investigator": {"x": 3, "y": 47, "width": 220, "height": 220},
    "investigator_back": {"x": 2, "y": 1, "width": 151, "height": 151},
    "asset": {"x": 64, "y": 50, "width": 174, "height": 174},
    "event": {"x": 65, "y": 26, "width": 174, "height": 174},
    "skill": {"x": 49, "y": 43, "width": 217, "height": 217},
    "enemy": {"x": 78, "y": 266, "width": 143, "height": 143},
    "enemy_swap": {"x": 74, "y": 2, "width": 152, "height": 152},
    "location": {"x": 85, "y": 55, "width": 132, "height": 132},
    "enemy_location": {"x": 77, "y": 204, "width": 166, "height": 166},
    "treachery": {"x": 67, "y": 2, "width": 166, "height": 166},
    "scenario": {"x": 9, "y": 7, "width": 283, "height": 283},
    "story": {"x": 7, "y": 3, "width": 288, "height": 288},
    "key": {"x": 70, "y": 41, "width": 162, "height": 162},
    "act": {"x": 258, "y": 67, "width": 164, "height": 164},
    "agenda": {"x": 0, "y": 67, "width": 164, "height": 164},
    "agenda_back": {"x": 3, "y": 12, "width": 64, "height": 64},
    "full": {"x": 128, "y": 1, "width": 164, "height": 164},
}

# 中文卡牌类型到英文类型的映射
CARD_TYPE_MAP = {
    "调查员": "investigator",
    "调查员卡": "investigator",
    "调查员卡背": "investigator_back",
    "调查员背面": "investigator_back",
    "支援卡": "asset",
    "事件卡": "event",
    "技能卡": "skill",
    "敌人卡": "enemy",
    "地点卡": "location",
    "诡计卡": "treachery",
    "冒险参考卡": "scenario",
    "故事卡": "story",
    "场景卡": "act",
    "密谋卡": "agenda",
}


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

    def _get_text_boundary_offset(self, card_data: dict, boundary_type: str = 'body') -> Optional[dict]:
        """
        从卡牌数据中提取文本边界偏移配置

        Args:
            card_data: 卡牌数据字典
            boundary_type: 边界类型 'body' 或 'flavor'

        Returns:
            边界偏移字典 {'top': int, 'bottom': int, 'left': int, 'right': int} 或 None
        """
        text_boundary = card_data.get('text_boundary')
        if not text_boundary:
            return None

        boundary = text_boundary.get(boundary_type)
        if not boundary:
            return None

        # 只返回有非零值的边界设置
        result = {}
        for key in ['top', 'bottom', 'left', 'right']:
            value = boundary.get(key)
            if value is not None and value != 0:
                result[key] = value

        return result if result else None

    def _get_flavor_padding(self, card_data: dict) -> int:
        """
        从卡牌数据中提取风味文本padding值

        Args:
            card_data: 卡牌数据字典

        Returns:
            padding值（默认20）
        """
        text_boundary = card_data.get('text_boundary')
        if not text_boundary:
            return 20

        flavor = text_boundary.get('flavor')
        if not flavor:
            return 20

        padding = flavor.get('padding', 20)
        return int(padding) if padding is not None else 0

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
        if picture_path is None and dp is None:
            return

        if dp is None:
            dp = self._open_picture(card_data, picture_path)
            if dp is None:
                return

        card_type = card_data.get('type', '')

        # 透明遭遇组的特殊处理
        # if self.transparent_encounter:
        #     if dp.size[1] > dp.size[0]:
        #         dp = dp.rotate(90, expand=True)
        #     card.paste_image(dp, (0, 0, card.width, card.height), 'cover')
        #     return

        # 常规贴底图逻辑
        image_mode = self.image_mode
        picture_layout = card_data.get('picture_layout', {})
        if picture_layout.get('mode', 'auto') == 'custom':
            image_mode = 3

        # 如果图片尺寸与卡牌尺寸几乎一致，使用覆盖模式
        if dp and abs(dp.size[0] - card.width) < 3 and abs(dp.size[1] - card.height) < 3:
            image_mode = 1

        print('image_mode', image_mode)

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
        if card_data.get('special_type') == 1:
            # 大画卡
            return (0, 0, 739, 1049)
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
                          align: str = 'center', quote: bool = False, flavor_padding: int = 0) -> str:
        """整理正文和风味，正确处理flavor字段中的<lr>标签"""
        body = body.strip()
        tag_name = 'flavor'
        if align == 'left':
            tag_name = f'flavor align="left" flex="false" padding="0"'
        else:
            tag_name = f'flavor padding="{flavor_padding}"'
        if quote:
            tag_name += ' quote="true"'

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

        body = body.replace('·', '﹒')
        return body

    def _integrate_traits_text(self, traits: list) -> str:
        """整合特性文本"""
        if traits is None:
            return ''
        delimiter = '，'
        if self.font_manager.lang not in ['zh', 'zh-CHT']:
            delimiter = '. '

        result = delimiter.join([self.font_manager.get_font_text(trait) for trait in traits])
        if self.font_manager.lang not in ['zh', 'zh-CHT'] and result != '':
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

        if card_json.get('class', '') == '守卫者':
            card_json['class'] = '守护者'

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

        if 'level' in card_json and card_json['level'] == '无':
            card_json['level'] = -1
        if card_json['body'] != '':
            text = card_json['body']
            text = text.replace('】。', '】<font name="加粗字体">\uff61</font>')
            text = text.replace('。】', '】<font name="加粗字体">\uff61</font>')
            text = re.sub(r'(?<!\n)<hr>', r'\n<hr>', text)

            card_json['body'] = text
        if card_json.get('class', '') == '弱点' and 'weakness_type' not in card_json:
            card_json['weakness_type'] = '弱点'

        if card_json.get('class', '') == '':
            card_json['class'] = '中立'

        # 复仇点
        if card_json.get('vengeance', None):
            victory = card_json.get('victory', None)
            if not (victory and isinstance(victory, str)):
                if card_json.get('victory', None):
                    victory_text = (f"复仇{card_json.get('vengeance')}。\n"
                                    f"胜利{card_json.get('victory')}。")
                else:
                    victory_text = f"复仇{card_json.get('vengeance')}。"
                card_json['victory'] = victory_text

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

            # 1. 安全地获取和设置默认值
            # 使用 .get() 方法，如果键不存在则返回默认值，代码更简洁
            location_type = data.get('location_type')
            if location_type not in ['未揭示', '已揭示']:
                location_type = '已揭示'

            has_subtitle = data.get('subtitle', '') != ''
            is_virtual = card_json.get('virtual', False)
            is_no_encounter = not data.get('encounter_group', '')  # 新增：从card_json获取无遭遇状态

            # 2. 使用列表构建图片名称的各个部分
            image_name_parts = [
                data['type'],  # 基础类型，如 "地点卡"
                location_type  # "已揭示" 或 "未揭示"
            ]

            # 3. 根据条件向列表中添加组件
            if is_enemy:
                image_name_parts.append('敌人')
                if has_subtitle:
                    image_name_parts.append('副标题')
            else:
                # 非敌人卡片的逻辑
                if has_subtitle:
                    image_name_parts.append('副标题')

                # 根据 virtual 的值添加 "-半" 或 "-虚拟"
                if is_virtual == '半':
                    image_name_parts.append('半')
                    image_name_parts.append('虚拟')  # 假设“半虚拟”对应文件名 "地点卡-已揭示-半-虚拟.png"
                elif is_virtual:
                    image_name_parts.append('虚拟')

            # 4. 新增：根据“无遭遇”条件添加组件
            # 这个判断可以放在 subtitle 等组件之后，以匹配文件名 "xx-xx-副标题-无遭遇.png"
            if is_no_encounter:
                image_name_parts.append('无遭遇')

            # 5. 将所有部分用连字符'-'连接起来，生成最终的图片名称
            image_name = '-'.join(image_name_parts)

            # 6. 调用图片管理器
            # 无论逻辑多复杂，最终都只需要调用一次
            card.paste_image(self.image_manager.get_image(image_name), (0, 0), 'contain')

        if self.transparent_encounter and dp:
            card.copy_circle_to_image(dp, (370, 518, 30), (370, 518, 30))

        # 写卡牌类型字体
        card.draw_centered_text(
            position=(370, 562),
            text=self.font_manager.get_font_text("地点"),
            font_name="卡牌类型字体",
            font_size=26,
            font_color=(0, 0, 0),
            max_length=None, debug_line=False
        )

        # 写标题
        card.draw_centered_text(
            position=(370, 30),
            text=data['name'],
            font_name="标题字体",
            font_size=48,
            font_color=(0, 0, 0),
            max_length=540, debug_line=False
        )

        # 写副标题
        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text(
                position=(370, 88),
                text=data['subtitle'],
                font_name="副标题字体",
                font_size=32,
                font_color=(0, 0, 0),
                max_length=370, debug_line=False
            )

        # 写特性
        card.draw_centered_text(
            position=(370, 606) if not is_enemy else (370, 690),
            text=self._integrate_traits_text(data.get('traits', [])),
            font_name="特性字体",
            font_size=32,
            font_color=(0, 0, 0),
            max_length=530, debug_line=False
        )

        # 整合body和flavor
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_padding=self._get_flavor_padding(data))

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
            default_font_name='正文字体',
            default_size=32,
            padding=18,
            draw_virtual_box=False,
            boundary_offset=self._get_text_boundary_offset(data, 'body')
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
        card.draw_victory_points(
            position=(675, 907),
            victory_value=data.get('victory')
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

        # 写卡牌类型字体
        card.draw_centered_text(
            position=(370, 576),
            text=self.font_manager.get_font_text("诡计"),
            font_name="卡牌类型字体",
            font_size=24,
            font_color=(0, 0, 0),
            max_length=None, debug_line=False
        )

        # 写标题
        card.draw_centered_text(
            position=(370, 628),
            text=data['name'],
            font_name="标题字体",
            font_size=48,
            font_color=(0, 0, 0),
            max_length=600, debug_line=False
        )

        # 写特性
        card.draw_centered_text(
            position=(370, 686),
            text=self._integrate_traits_text(data.get('traits', [])),
            font_name="特性字体",
            font_size=32,
            font_color=(0, 0, 0),
            max_length=620, debug_line=False
        )

        # 整合body和flavor
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_padding=self._get_flavor_padding(data))

        # 写正文和风味
        card.draw_text(
            text=body,
            vertices=[
                (38, 700), (704, 700), (704, 984),
                (523, 1010), (216, 1010), (38, 984)
            ],
            default_font_name='正文字体',
            default_size=32,
            padding=18,
            draw_virtual_box=False,
            boundary_offset=self._get_text_boundary_offset(data, 'body'))

        # 画胜利点
        card.draw_victory_points(
            position=(378, 980),
            victory_value=data.get('victory')
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
            ui_name = data["type"]
            if 'subtitle' in data and data['subtitle'] != '':
                ui_name += '-副标题'
            if not data.get('encounter_group', ''):
                ui_name += '-无遭遇'
            card.paste_image(self.image_manager.get_image(ui_name), (0, 0))

        # 贴遭遇组
        if self.transparent_encounter and dp:
            card.copy_circle_to_image(dp, (370, 570, 32), (370, 570, 32))

        # 写卡牌类型字体
        card.draw_centered_text(
            position=(364, 617),
            text=self.font_manager.get_font_text("敌人"),
            font_name="卡牌类型字体",
            font_size=24,
            font_color=(0, 0, 0)
        )

        # 写标题
        card.draw_centered_text(
            position=(370, 28),
            text=data['name'],
            font_name="标题字体",
            font_size=48,
            font_color=(0, 0, 0)
        )

        # 写副标题
        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text(
                position=(370, 78),
                text=data['subtitle'],
                font_name="副标题字体",
                font_size=32,
                font_color=(0, 0, 0)
            )

        # 写特性
        card.draw_centered_text(
            position=(370, 212),
            text=self._integrate_traits_text(data.get('traits', [])),
            font_name="特性字体",
            font_size=32,
            font_color=(0, 0, 0)
        )

        # 整合body和flavor
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_padding=self._get_flavor_padding(data))

        # 写胜利点数和正文
        if data.get('victory') is not None:
            card.draw_victory_points(
                position=(380, 512),
                victory_value=data.get('victory')
            )
            card.draw_text(
                text=body,
                vertices=[
                    (90, 234), (645, 234), (716, 270), (716, 458),
                    (538, 510), (190, 510), (20, 458), (20, 270)
                ],
                default_font_name='正文字体',
                default_size=32,
                padding=15,
                draw_virtual_box=False,
                boundary_offset=self._get_text_boundary_offset(data, 'body'))
        else:
            card.draw_text(
                text=body,
                vertices=[
                    (90, 234), (645, 234), (716, 270), (716, 458),
                    (538, 540), (190, 540), (20, 458), (20, 270)
                ],
                default_font_name='正文字体',
                default_size=32,
                padding=15,
                draw_virtual_box=False,
                boundary_offset=self._get_text_boundary_offset(data, 'body'))

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
            font_name="标题字体",
            font_size=52,
            font_color=(0, 0, 0)
        )

        # 写正文
        card.draw_text(
            text=data['body'],
            vertices=[(38, 186), (700, 186), (700, 1009), (38, 1009)],
            default_font_name='正文字体',
            default_size=32,
            padding=18,
            draw_virtual_box=False,
            boundary_offset=self._get_text_boundary_offset(data, 'body'))

        # 写卡牌类型
        font_size = 22
        if self.font_manager.lang == 'pl':
            font_size = 19
        card.draw_centered_text((368, 1013), self.font_manager.get_font_text("升级项"), "卡牌类型字体", font_size,
                                (0, 0, 0))

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
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_padding=self._get_flavor_padding(data))
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
        card.draw_centered_text((76, 133), self.font_manager.get_font_text("事件"), "卡牌类型字体", 22, (0, 0, 0),
                                max_length=None, debug_line=False)
        card.draw_centered_text((370, 618), data['name'], "标题字体", 48, (0, 0, 0),
                                max_length=600, debug_line=False)
        card.draw_centered_text((370, 673), self.font_manager.get_font_text(data['weakness_type']), "副标题字体", 28,
                                (0, 0, 0), max_length=None, debug_line=False)
        card.draw_centered_text((370, 705), self._integrate_traits_text(data.get('traits', [])), "特性字体", 32,
                                (0, 0, 0), max_length=620, debug_line=False)

        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])

        card.draw_text(
            body,
            vertices=[(38, 720), (704, 720), (706, 757), (704, 817), (680, 887), (670, 952),
                      (598, 980), (135, 980), (77, 949), (61, 907), (31, 793)],
            default_font_name='正文字体', default_size=32, padding=18, draw_virtual_box=False,
            boundary_offset=self._get_text_boundary_offset(data, 'body'))

    def _create_weakness_support_card(self, card, data, body, dp):
        """创建弱点支援卡"""
        if dp:
            # 贴底图
            self._paste_background_image(card, None, data, dp)

        if 'subtitle' in data and data['subtitle'] != '':
            card.paste_image(self.image_manager.get_image(f'{data["class"]}-{data["type"]}-副标题'), (0, 0), 'contain')
        else:
            card.paste_image(self.image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')

        card.draw_centered_text((76, 131), self.font_manager.get_font_text("支援"), "卡牌类型字体", 22, (0, 0, 0),
                                max_length=None, debug_line=False)
        card.draw_centered_text((370, 48), data['name'], "标题字体", 48, (0, 0, 0),
                                max_length=500, debug_line=False)

        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text((370, 103), data['subtitle'], "副标题字体", 31, (0, 0, 0),
                                    max_length=400, debug_line=False)

        card.draw_centered_text((370, 609), self.font_manager.get_font_text(data['weakness_type']), "卡牌类型字体", 28,
                                (0, 0, 0), max_length=None, debug_line=False)
        card.draw_centered_text((370, 642), self._integrate_traits_text(data.get('traits', [])), "特性字体", 32,
                                (0, 0, 0), max_length=700, debug_line=False)

        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])
        vertices = [(19, 658), (718, 658), (718, 908), (290, 908), (73, 950), (19, 950)]
        if data.get('flavor') or self.font_manager.lang not in ['zh', 'zh-CHT']:
            vertices = [(19, 658), (718, 658), (718, 920), (19, 920)]

        card.draw_text(body, vertices=vertices,
                       default_font_name='正文字体', default_size=32, padding=15, draw_virtual_box=False,
                       boundary_offset=self._get_text_boundary_offset(data, 'body'))

        if 'slots' in data and isinstance(data['slots'], str):
            card.add_slots(data['slots'])
        if 'slots2' in data and isinstance(data['slots2'], str):
            card.add_slots(data['slots2'])

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

        card.draw_centered_text((76, 130), self.font_manager.get_font_text("技能"), "卡牌类型字体", 22, (0, 0, 0),
                                max_length=None, debug_line=False)
        card.draw_left_text((140, 28), data['name'], "标题字体", 48, (0, 0, 0),
                            max_length=580, debug_line=False)

        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text((378, 101), data['subtitle'], "副标题字体", 32, (0, 0, 0),
                                    max_length=400, debug_line=False)

        card.draw_centered_text((368, 703), self.font_manager.get_font_text(data['weakness_type']), "副标题字体", 28,
                                (0, 0, 0), max_length=None, debug_line=False)
        card.draw_centered_text((368, 742), self._integrate_traits_text(data.get('traits', [])), "特性字体", 30,
                                (0, 0, 0), max_length=580, debug_line=False)

        offset = 16
        card.draw_text(
            body,
            vertices=[(75, 758), (682 + offset, 758), (692 + offset, 770), (704 + offset, 838), (701 + offset, 914),
                      (679 + offset, 989),
                      (74, 989), (91, 920), (96, 844)],
            default_font_name='正文字体', default_size=32, padding=15, draw_virtual_box=False,
            boundary_offset=self._get_text_boundary_offset(data, 'body'))

        if 'submit_icon' in data and isinstance(data['submit_icon'], list):
            for icon in data['submit_icon']:
                card.add_submit_icon(icon)

    def _create_weakness_treachery_card(self, card, data, body, dp):
        """创建弱点诡计卡"""
        if dp:
            # 贴底图
            self._paste_background_image(card, None, data, dp)

        card.paste_image(self.image_manager.get_image(f'{data["class"]}-{data["type"]}'), (0, 0), 'contain')
        card.draw_centered_text((370, 580), self.font_manager.get_font_text("诡计"), "卡牌类型字体", 24, (0, 0, 0),
                                max_length=None, debug_line=False)
        card.draw_centered_text((370, 625), data['name'], "标题字体", 48, (0, 0, 0),
                                max_length=600, debug_line=False)
        card.draw_centered_text((370, 681),
                                self.font_manager.get_font_text(data['weakness_type']),
                                "副标题字体", 28, (0, 0, 0),
                                max_length=None, debug_line=False)
        card.draw_centered_text((370, 715), self._integrate_traits_text(data.get('traits', [])), "特性字体", 32,
                                (0, 0, 0), max_length=620, debug_line=False)

        card.draw_text(body,
                       vertices=[
                           (38, 726), (704, 726), (704, 960),
                           (519, 1010), (219, 1010), (38, 960),
                       ],
                       default_font_name='正文字体', default_size=32, padding=18, draw_virtual_box=False,
                       boundary_offset=self._get_text_boundary_offset(data, 'body'))

    def _create_weakness_enemy_card(self, card, data, body, dp):
        """创建弱点敌人卡"""
        if dp:
            # 贴底图
            self._paste_background_image(card, None, data, dp)
        ui_name = f'{data["class"]}-{data["type"]}'
        if data.get('is_encounter', False) or data['weakness_type'] == '基础弱点':
            ui_name += '-遭遇'
        card.paste_image(self.image_manager.get_image(ui_name), (0, 0), 'contain')

        if data['weakness_type'] == '基础弱点':
            card.draw_centered_text((367, 572), '0', "arkham-icons", 50, (0, 0, 0),
                                    max_length=None, debug_line=False)
        card.draw_centered_text((370, 618), self.font_manager.get_font_text("敌人"), "卡牌类型字体", 24, (0, 0, 0),
                                max_length=None, debug_line=False)
        card.draw_centered_text((370, 28), data['name'], "标题字体", 48, (0, 0, 0),
                                max_length=520, debug_line=False)
        card.draw_centered_text((370, 79), self.font_manager.get_font_text(data['weakness_type'])
                                , "副标题字体", 28, (0, 0, 0),
                                max_length=None, debug_line=False)
        card.draw_centered_text((370, 212), self._integrate_traits_text(data.get('traits', [])), "特性字体", 32,
                                (0, 0, 0), max_length=530, debug_line=False)

        if data.get('victory') is not None:
            card.draw_victory_points(
                position=(380, 512),
                victory_value=data.get('victory')
            )
            vertices = [(90, 234), (645, 234), (716, 270), (716, 458),
                        (538, 510), (190, 510), (20, 458), (20, 270)]
        else:
            vertices = [(90, 234), (645, 234), (716, 270), (716, 458),
                        (538, 540), (190, 540), (20, 458), (20, 270)]

        card.draw_text(body, vertices=vertices, default_font_name='正文字体', default_size=32, padding=15,
                       draw_virtual_box=False,
                       boundary_offset=self._get_text_boundary_offset(data, 'body'))

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

    def build_investigators_card_back_test(self, card_back: dict) -> str:
        """构建调查员卡背文本"""
        test_text = ""
        if 'size' in card_back and card_back['size'] > 0:
            test_text += f"【{self.font_manager.get_font_text('牌库卡牌张数')}】" \
                         f"{self.font_manager.get_font_text('：')}" \
                         f"{card_back['size']}" \
                         f"{self.font_manager.get_font_text('。')}\n"
        if 'option' in card_back and card_back['option']:
            option_text = '，'.join(card_back['option']) + '。' if \
                isinstance(card_back['option'], list) else card_back['option']
            test_text += f"【{self.font_manager.get_font_text('牌库构筑选项')}】" \
                         f"{self.font_manager.get_font_text('：')}" \
                         f"{option_text}\n"
        if 'requirement' in card_back and card_back['requirement'] != '':
            test_text += f"【{self.font_manager.get_font_text('牌库构筑需求')}】" \
                         f"({self.font_manager.get_font_text('不计入卡牌张数')})" \
                         f"{self.font_manager.get_font_text('：')}" \
                         f"{card_back['requirement']}" \
                         f"{self.font_manager.get_font_text('。')}\n"
        if 'other' in card_back and card_back['other'] != '':
            test_text += card_back['other'] + '\n'
        return test_text

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
            is_back=True,
            card_class=data['class']
        )

        dp = self._open_picture(card_json, picture_path)

        # 贴底图
        if not self.transparent_background:
            self._paste_background_image(card, picture_path, data, dp)
        ui_name = f'调查员卡-{data["class"]}'
        title_color = (0, 0, 0)
        if data.get('subtype', '常规') == '平行':
            ui_name += '-平行'
            title_color = (255, 255, 255)
        ui_name += '-卡背'
        card.paste_image(self.image_manager.get_image(ui_name), (0, 0), 'contain')
        card.draw_centered_text((750, 32), data['name'], "标题字体", 48, title_color,
                                max_length=520, debug_line=False)
        card.draw_centered_text((750, 86), data['subtitle'], "副标题字体", 32, title_color,
                                max_length=340, debug_line=False)

        if card_json['body'] is not None and card_json['body'] != '':
            card_back['other'] = card_json['body']

        test_text = ""
        if 'size' in card_back and card_back['size'] > 0:
            test_text += f"【{self.font_manager.get_font_text('牌库卡牌张数')}】" \
                         f"{self.font_manager.get_font_text('：')}" \
                         f"{card_back['size']}" \
                         f"{self.font_manager.get_font_text('。')}\n"
        if 'option' in card_back and card_back['option']:
            option_text = '，'.join(card_back['option']) + '。' if \
                isinstance(card_back['option'], list) else card_back['option']
            test_text += f"【{self.font_manager.get_font_text('牌库构筑选项')}】" \
                         f"{self.font_manager.get_font_text('：')}" \
                         f"{option_text}\n"
        if 'requirement' in card_back and card_back['requirement'] != '':
            test_text += f"【{self.font_manager.get_font_text('牌库构筑需求')}】" \
                         f"({self.font_manager.get_font_text('不计入卡牌张数')})" \
                         f"{self.font_manager.get_font_text('：')}" \
                         f"{card_back['requirement']}" \
                         f"\n"
        if 'other' in card_back and card_back['other'] != '':
            test_text += card_back['other'] + '\n'
        if 'story' in card_back and card_back['story'] != '':
            test_text = self._tidy_body_flavor(test_text, card_back['story'], align='left',
                                               flavor_padding=self._get_flavor_padding(data))

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

        card.draw_text(test_text, vertices=vertices, default_font_name='正文字体', default_size=32,
                       padding=15, draw_virtual_box=False,
                       boundary_offset=self._get_text_boundary_offset(data, 'body'))

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

        title_color = (0, 0, 0)

        if data.get('subtype', '常规') == '平行':
            card.paste_image(self.image_manager.get_image(f'{data["type"]}-{data["class"]}-平行'), (0, 0), 'contain')
            title_color = (255, 255, 255)
        else:
            card.paste_image(self.image_manager.get_image(f'{data["type"]}-{data["class"]}-UI'), (0, 0), 'contain')
        card.draw_centered_text((320, 36), data['name'], "标题字体", 48, title_color,
                                max_length=460, debug_line=False)
        card.draw_centered_text((320, 88), data['subtitle'], "副标题字体", 32, title_color,
                                max_length=340, debug_line=False)

        # 写四维
        if 'attribute' in data and isinstance(data['attribute'], list):
            for i, attr in enumerate(data['attribute']):
                card.draw_centered_text((600 + 120 * i, 57), str(attr), "Bolton", 48, title_color,
                                        max_length=None, debug_line=False)

        traits = self._integrate_traits_text(data.get('traits', []))
        card.draw_centered_text((810, 160), traits, "特性字体", 32, (0, 0, 0),
                                max_length=400, debug_line=False)

        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_padding=self._get_flavor_padding(data))
        card.draw_text(body, vertices=[(596, 178), (1016, 178),
                                       (1016, 600), (596, 600)],
                       default_font_name='正文字体', default_size=32, padding=10, draw_virtual_box=False,
                       boundary_offset=self._get_text_boundary_offset(data, 'body'))

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
        card.draw_centered_text((73, 134), self.font_manager.get_font_text("技能"), "卡牌类型字体", 22, (0, 0, 0),
                                max_length=None, debug_line=False)

    def _setup_event_card_base(self, card, data, picture_path):
        """设置事件卡基础"""
        dp = self._open_picture(data, picture_path)

        if not self.transparent_background:
            # 贴底图
            self._paste_background_image(card, picture_path, data, dp)

        card.paste_image(self.image_manager.get_image(f'{data["type"]}-{data["class"]}'), (0, 0), 'contain')
        card.draw_centered_text((73, 134), self.font_manager.get_font_text("事件"), "卡牌类型字体", 22, (0, 0, 0),
                                max_length=None, debug_line=False)

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
        card.draw_centered_text((73, 134), self.font_manager.get_font_text("支援"), "卡牌类型字体", 22, (0, 0, 0),
                                max_length=None, debug_line=False)

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
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_padding=self._get_flavor_padding(data))

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
        card.draw_left_text((140, 30), data['name'], "标题字体", 48, (0, 0, 0),
                            max_length=580, debug_line=False)
        card.draw_centered_text((368, 707), traits, "特性字体", 32, (0, 0, 0),
                                max_length=580, debug_line=False)
        vertices = [(75, 725), (682, 725), (692, 770), (704, 838), (701, 914), (679, 995),
                    (74, 995), (91, 920), (96, 844)]
        if 'victory' in data and data.get('victory') is not None:
            vertices = [(75, 725), (682, 725), (692, 770), (704, 838), (701, 914), (682, 970),
                        (77, 970), (91, 920), (96, 844)]
        card.draw_text(
            body,
            vertices=vertices,
            default_font_name='正文字体', default_size=32, padding=15, draw_virtual_box=False,
            boundary_offset=self._get_text_boundary_offset(data, 'body'))
        card.draw_victory_points(
            position=(378, 973),
            victory_value=data.get('victory')
        )

    def _setup_event_card_content(self, card, data, traits, body):
        """设置事件卡内容"""
        offset = {'潜修者': -3, '守护者': -1, '生存者': -1, '中立': -3}.get(data.get('class', ''), 0)
        card.draw_centered_text((370, 621 + offset), data['name'], "标题字体", 48, (0, 0, 0),
                                max_length=600, debug_line=False)
        card.draw_centered_text((368, 675), traits, "特性字体", 32, (0, 0, 0),
                                max_length=620, debug_line=False)
        vertices = [(45, 690), (694, 690), (706, 757), (704, 817), (680, 887), (670, 952),
                    (598, 992), (135, 992), (77, 949), (61, 907), (31, 793)]

        if 'victory' in data and data.get('victory') is not None:
            vertices = [(45, 690), (694, 690), (706, 757), (704, 817), (680, 887), (670, 960),
                        (77, 960), (61, 907), (31, 793)]
        card.draw_text(
            body,
            vertices=vertices,
            default_font_name='正文字体', default_size=32, padding=18, draw_virtual_box=False,
            boundary_offset=self._get_text_boundary_offset(data, 'body'))

        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])

        card.draw_victory_points(
            position=(378, 960),
            victory_value=data.get('victory')
        )

    def _setup_support_card_content(self, card, data, traits, body):
        """设置支援卡内容"""

        subclass = data.get('subclass', [])
        name_offset = 0
        max_length = 500
        if len(subclass) == 3:
            name_offset = -80
            max_length = 340
        elif len(subclass) == 2:
            name_offset = -40
            max_length = 420

        card.draw_centered_text((375 + name_offset, 46), data['name'], "标题字体", 48, (0, 0, 0),
                                max_length=max_length, debug_line=False)

        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text((378, 98), data['subtitle'], "副标题字体", 31, (0, 0, 0),
                                    max_length=340, debug_line=False)

        card.draw_centered_text((375, 642), traits, "特性字体", 32, (0, 0, 0),
                                max_length=700, debug_line=False)
        vertices = [(19, 658), (718, 658), (718, 908), (290, 908), (73, 950), (19, 950)]
        if data.get('flavor') or self.font_manager.lang not in ['zh', 'zh-CHT']:
            vertices = [(19, 658), (718, 658), (718, 920), (19, 920)]
        card.draw_text(body, vertices=vertices, default_font_name='正文字体', default_size=32, padding=15,
                       draw_virtual_box=False,
                       boundary_offset=self._get_text_boundary_offset(data, 'body'))

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

        if data.get('victory') is not None:
            pos = (379, 885)
            if 'slots' not in data or not data.get('slots'):
                pos = (675, 933)
            card.draw_victory_points(
                position=pos,
                victory_value=data.get('victory')
            )

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

        title_y = 510 if data['type'] == '场景卡-大画' else 461
        card.draw_centered_text((520, title_y), data['name'], "标题字体", 48, (0, 0, 0),
                                max_length=660, debug_line=False)

        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_type=1,
                                      flavor_padding=self._get_flavor_padding(data))
        text_y = 556 if data['type'] == '场景卡-大画' else 512
        card.draw_text(body, vertices=[(28, text_y), (1016, text_y), (1016, 686), (28, 686)],
                       default_font_name='正文字体', default_size=32, padding=15, draw_virtual_box=False,
                       boundary_offset=self._get_text_boundary_offset(data, 'body'))

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

        mirror = data.get('mirror')

        card = Card(1049, 739, self.font_manager, self.image_manager, data['type'], is_mirror=mirror)
        dp = self._open_picture(card_json, picture_path)

        # 贴底图
        if not self.transparent_background:
            self._paste_background_image(card, picture_path, data, dp)

        # 透明列表
        encounter_list = [[(533, 628, 42), (528, 622, 42)], [(270, 74, 34), (288, 74, 34)]]
        if data['type'] != '场景卡':
            encounter_list = [[(520, 636, 44), (500, 630, 44)], [(288 + 473, 76, 34), (288 + 473, 76, 34)]]

        if mirror:
            card.paste_image(self.image_manager.get_image(f'{data["type"]}-镜像'), (0, 0), 'contain')
        else:
            card.paste_image(self.image_manager.get_image(f'{data["type"]}'), (0, 0), 'contain')

        # 贴遭遇组
        if self.transparent_encounter and dp:
            for item in encounter_list:
                card.copy_circle_to_image(dp, item[0], item[1])

        # 写序列号
        if mirror:
            if data['type'] == '场景卡':
                card.draw_centered_text((740 + 26, 30), f"{self.font_manager.get_font_text('场景')}"
                                                        f"{data.get('serial_number', '')}", "卡牌类型字体", 28,
                                        (0, 0, 0), max_length=None, debug_line=False)
            else:
                card.draw_centered_text((280 + 26, 38), f"{self.font_manager.get_font_text('密谋')}"
                                                        f"{data.get('serial_number', '')}", "卡牌类型字体", 28,
                                        (0, 0, 0), max_length=None, debug_line=False)
        else:
            if data['type'] == '场景卡':
                card.draw_centered_text((280, 30), f"{self.font_manager.get_font_text('场景')}"
                                                   f"{data.get('serial_number', '')}", "卡牌类型字体", 28, (0, 0, 0),
                                        max_length=None, debug_line=False)
            else:
                card.draw_centered_text((740, 38), f"{self.font_manager.get_font_text('密谋')}"
                                                   f"{data.get('serial_number', '')}", "卡牌类型字体", 28, (0, 0, 0),
                                        max_length=None, debug_line=False)

        # 写标题
        if mirror:
            title_x = 740 + 26 if data['type'] == '场景卡' else 280 + 26
        else:
            title_x = 280 if data['type'] == '场景卡' else 740
        card.draw_centered_text((title_x, 140), data['name'], "标题字体", 48, (0, 0, 0),
                                max_length=520, debug_line=False)

        if mirror:
            offset_x = 12
            vertices = [(10 + offset_x, 185), (560 + offset_x, 185), (560 + offset_x, 574), (470 + offset_x, 574),
                        (470 + offset_x, 678), (10 + offset_x, 678)]
            offset_x = 2
            if data['type'] != '密谋卡':
                vertices = [
                    (10 + 480 + offset_x, 185), (560 + 480 + offset_x, 185),
                    (560 + 480 + offset_x, 678), (10 + 480 + 80 + offset_x, 678),
                    (10 + 480 + 80 + offset_x, 574), (10 + 480 + offset_x, 574)
                ]
        else:
            vertices = [(10, 185), (560, 185), (560, 574), (470, 574), (470, 678), (10, 678)]
            offset_x = -20
            if data['type'] != '场景卡':
                vertices = [
                    (10 + 480 + offset_x, 185), (560 + 480 + offset_x, 185),
                    (560 + 480 + offset_x, 678), (10 + 480 + 80 + offset_x, 678),
                    (10 + 480 + 80 + offset_x, 574), (10 + 480 + offset_x, 574)
                ]

        # 写正文
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_type=1, align='left',
                                      flavor_padding=self._get_flavor_padding(data))
        card.draw_text(body, vertices=vertices, default_font_name='正文字体', default_size=32,
                       padding=15, draw_virtual_box=False,
                       boundary_offset=self._get_text_boundary_offset(data, 'body'))

        # 写阈值
        if 'threshold' in data:
            if mirror:
                threshold_pos = (498 + 24, 624) if data['type'] == '场景卡' else (523 + 22, 624)
            else:
                threshold_pos = (523, 626) if data['type'] == '场景卡' else (498, 624)
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
        small_words = self.font_manager.get_font_text('场景') if data['type'] == '场景卡' \
            else self.font_manager.get_font_text('密谋')
        small_words = small_words.upper()
        if self.font_manager.lang not in ['zh', 'zh-CHT'] and data['type'] != '场景卡':
            font_size = 21
            if self.font_manager.lang == 'pl':
                font_size -= 4
            card.draw_centered_text((98, 60), small_words.strip(), "卡牌类型字体", font_size, (0, 0, 0),
                                    max_length=None, debug_line=False)
            card.draw_centered_text((98, 78), data.get('serial_number', ''), "卡牌类型字体", font_size, (0, 0, 0),
                                    max_length=None, debug_line=False)
        else:
            small_words += data.get('serial_number', '')
            card.draw_centered_text((98, 68), small_words, "卡牌类型字体", 28, (0, 0, 0),
                                    max_length=None, debug_line=False)

        # 写标题
        if self.font_manager.lang in ['zh', 'zh-CHT']:
            card.draw_centered_text((98, 422), data['name'], "标题字体", 48, (0, 0, 0), vertical=True,
                                    max_length=None, debug_line=False)
            pass
        else:
            title = Card(450, 100, self.font_manager, self.image_manager)
            title.draw_centered_text((225, 50), data['name'], "标题字体", 48, (0, 0, 0),
                                     max_length=None, debug_line=False)
            title_img = title.image.rotate(90, expand=True)
            card.paste_image(title_img, (40, 208), 'cover')

        # 写正文
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_type=1, align='left', quote=True,
                                      flavor_padding=self._get_flavor_padding(data))
        offset = -8
        card.draw_text(
            body,
            vertices=[(210 + offset, 67), (977 + offset, 67), (977 + offset, 672), (210 + offset, 672)],
            default_font_name='正文字体', default_size=32, padding=15, draw_virtual_box=False,
            boundary_offset=self._get_text_boundary_offset(data, 'body'))

        # 画胜利点
        card.draw_victory_points(
            position=(590, 680),
            victory_value=data.get('victory')
        )

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
            card.copy_circle_to_image(dp, (643, 92, 42), (643, 99, 42))

        card.draw_centered_text((328, 90), data['name'], "标题字体", 48, (0, 0, 0),
                                max_length=500, debug_line=False)
        card.draw_centered_text((370, 1012), self.font_manager.get_font_text('剧情'), "卡牌类型字体", 30, (0, 0, 0),
                                max_length=None, debug_line=False)

        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_type=1, align='left', quote=True,
                                      flavor_padding=self._get_flavor_padding(data))
        card.draw_text(body, vertices=[(50, 207), (685, 207), (685, 960), (50, 960)],
                       default_font_name='正文字体', default_size=32, padding=15, draw_virtual_box=False,
                       boundary_offset=self._get_text_boundary_offset(data, 'body'))

        card.draw_victory_points(
            position=(386, 970),
            victory_value=data.get('victory')
        )

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

        card.draw_centered_text((374, 85), data['name'], "标题字体", 48, (0, 0, 0),
                                max_length=540, debug_line=False)
        card.draw_centered_text((372, 980), '行动', "卡牌类型字体", 24, (0, 0, 0),
                                max_length=None, debug_line=False)

        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_padding=self._get_flavor_padding(data))
        card.draw_text(body, vertices, default_font_name='正文字体', default_size=32,
                       padding=15, draw_virtual_box=False,
                       boundary_offset=self._get_text_boundary_offset(data, 'body'))

        card.draw_victory_points(
            position=(386, 970),
            victory_value=data.get('victory')
        )

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

        card.draw_centered_text((369, 210), data['name'], "标题字体", 48, (0, 0, 0), underline=True,
                                max_length=600, debug_line=False)

        if data.get('scenario_type', 0) == 2:
            # 辅助卡
            body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_padding=self._get_flavor_padding(data))
            vertices = [(56, 250), (685, 250), (685, 920), (56, 920)]
            if not data['name']:
                vertices = [(56, 210), (685, 210), (685, 920), (56, 920)]
            card.draw_text(body, vertices=vertices,
                           default_font_name='正文字体', default_size=32, padding=15, draw_virtual_box=False,
                           boundary_offset=self._get_text_boundary_offset(data, 'body'))
        else:
            # 写副标题
            if 'subtitle' in data and data['subtitle'] != '':
                card.draw_centered_text((369, 265), data['subtitle'], "副标题字体",
                                        26 if self.font_manager.lang in ['zh', 'zh-CHT'] else 30
                                        , (0, 0, 0), max_length=600, debug_line=False)

            # 画正文
            scenario_card = data.get('scenario_card', {})
            card.draw_scenario_card(scenario_card, resource_name=scenario_card.get('resource_name', ''))

        return card

    def create_rule_mini_card(self, card_json: dict) -> Card:
        """生成规则小卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])
        if 'type' not in data or data['type'] != '规则小卡':
            raise ValueError('卡牌类型错误')

        card = Card(739, 1049, self.font_manager, self.image_manager, data['type'], is_back=True)

        # 贴底图
        base_image = self.image_manager.get_image('规则小卡')
        if base_image:
            card.paste_image(base_image, (0, 0, 739, 1049), 'contain')
        # 贴页码
        max_height = 950
        if data.get('page_number'):
            page_frame = self.image_manager.get_image('规则小卡-页码')
            card.paste_image(page_frame, (0, 0, 739, 1049), 'contain')
            max_height = 970
            self._draw_rule_card_page_number(card, data.get('page_number'))

        # 标题 & 正文区域
        title = data.get('name', '').strip()
        text_vertices = [(76, 90), (665, 90), (665, max_height), (76, max_height)]
        if title:
            card.draw_centered_text((369, 100), title, "标题字体", 48, (0, 0, 0),
                                    max_length=600, debug_line=False)
            text_vertices = [(76, 140), (665, 140), (665, max_height), (76, max_height)]

        body = self._tidy_body_flavor(
            data.get('body', ''),
            '',
            flavor_padding=self._get_flavor_padding(data)
        )
        card.draw_text(
            body,
            vertices=text_vertices,
            default_font_name='正文字体',
            default_size=32,
            padding=15,
            draw_virtual_box=False,
            boundary_offset=self._get_text_boundary_offset(data, 'body')
        )

        return card

    def _draw_rule_card_page_number(self, card: Card, page_number: Union[str, int, None]):
        """根据位数绘制规则小卡的页码"""
        if page_number is None:
            return

        page_text = str(page_number).strip()
        if page_text == '':
            return
        try:
            page_value = int(page_text)
        except ValueError:
            return

        if page_value <= 0 or page_value > 999:
            return

        digits = len(str(page_value))
        font_size_map = {1: 56, 2: 56, 3: 42}
        font_size = font_size_map.get(digits, 48)

        card.draw_centered_text(
            (371, 986),
            str(page_value),
            "Arkhamic",
            font_size,
            (0, 0, 0),
            max_length=None,
            debug_line=False
        )

    def create_card_bottom_map(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作底图"""
        self.font_manager.silence = True
        card_json = card_json.copy()
        if card_json.get('type', '') == '支援卡':
            # 支援卡
            if card_json.get('health', -1) != -1 or card_json.get('horror', -1) != -1:
                card_json['health'] = -999
                card_json['horror'] = -999
        else:
            card_json['health'] = -999
            card_json['horror'] = -999
        card_object = self.create_card(card_json, picture_path)
        self.font_manager.silence = False
        return card_object

    def _extract_thumbnail(self, image: Image.Image, card_type: str) -> Image.Image:
        """
        从卡牌图片中提取缩略图

        Args:
            image: PIL Image对象
            card_type: 卡牌类型（支持中文或英文）

        Returns:
            Image.Image: 提取的缩略图
        """
        MAJOR_AXIS = 420
        MINOR_AXIS = 300

        w, h = image.size

        # 确定基准尺寸
        base_h = MINOR_AXIS if w > h else MAJOR_AXIS
        base_w = MAJOR_AXIS if w > h else MINOR_AXIS

        # 转换为英文类型名
        card_type_en = CARD_TYPE_MAP.get(card_type, card_type.lower())

        # 获取裁剪区域
        if card_type_en not in THUMBNAIL_REGIONS:
            # 如果没有匹配的类型，返回整个图片的缩放版本
            print(f"未找到卡牌类型 {card_type} ({card_type_en}) 的缩略图区域配置，使用默认缩放")
            return image.copy()

        region = THUMBNAIL_REGIONS[card_type_en]

        # 计算实际裁剪坐标
        left = round(region["x"] * (w / base_w))
        top = round(region["y"] * (h / base_h))
        width = round(region["width"] * (w / base_w))
        height = round(region["height"] * (h / base_h))

        # 检查并调整超出边界的情况
        if top + height > h:
            diff = top + height - h
            print(f"高度不足，减少提取区域 {diff}px")
            height -= diff
            width -= diff

        if left + width > w:
            diff = left + width - w
            print(f"宽度不足，减少提取区域 {diff}px")
            width -= diff
            height -= diff

        # 确保尺寸为正数
        if width <= 0 or height <= 0:
            print(f"计算的裁剪区域无效，使用整个图片")
            return image.copy()

        # 裁剪图片
        cropped = image.crop((left, top, left + width, top + height))

        return cropped

    def create_special_pictures(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作特殊图片"""
        craft_type = card_json.get('craft_type')
        dp = self._open_picture(card_json, picture_path)

        if dp is None:
            raise ValueError("未提供图片")

        if craft_type == '盒子模型图片':
            box_cover = self.image_manager.get_image('box-cover')
            card = Card(0, 0, image=box_cover)
            card.paste_image(
                dp,
                (420, 420, 780, 782),
                'cover'
            )
            return card

        elif craft_type == '缩略图':
            # 获取卡牌类型参数，默认为'支援卡'
            thumbnail_card_type = card_json.get('thumbnail_type', '支援卡')

            # 提取缩略图
            thumbnail = self._extract_thumbnail(dp, thumbnail_card_type)

            # 可选：调整缩略图大小
            max_size = card_json.get('thumbnail_size', 300)  # 默认最大尺寸300px
            if max_size > 0 and max(thumbnail.size) > max_size:
                thumbnail.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            card = Card(0, 0, image=thumbnail)
            return card

        else:
            # 其他类型直接返回原图
            card = Card(0, 0, image=dp)
            return card

    def _apply_image_filter(self, img: Image.Image, image_filter: Optional[str]) -> Image.Image:
        """根据 image_filter 应用滤镜（支持 grayscale）"""
        try:
            if not image_filter or image_filter == 'normal':
                return img
            if image_filter == 'grayscale':
                # 转为灰度并保持 Alpha 通道（无Alpha时填充不透明）
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                l = img.convert('L')
                a = img.getchannel('A') if 'A' in img.getbands() else Image.new('L', img.size, 255)
                gray = Image.merge('RGBA', (l, l, l, a))
                return gray
        except Exception:
            pass
        return img

    def create_investigator_mini_card(self, card_json: dict,
                                      picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作调查员小卡（固定 484x744）"""
        width, height = 484, 744
        card = Card(width, height, self.font_manager, self.image_manager, card_json.get('type', '调查员小卡'))

        dp = self._open_picture(card_json, picture_path)
        if dp is None:
            return card

        # 应用滤镜
        image_filter = card_json.get('image_filter', 'normal')
        dp = self._apply_image_filter(dp, image_filter)

        # 粘贴插画
        picture_layout = card_json.get('picture_layout', {})
        if picture_layout.get('mode') == 'custom':
            card.paste_image_with_transform(dp, (0, 0, width, height), picture_layout)
        else:
            card.paste_image(dp, (0, 0, width, height), 'cover')

        return card

    def create_skill_large_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作大画技能卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])

        card = Card(739, 1049, self.font_manager, self.image_manager, data['type'], data['class'])
        dp = self._open_picture(card_json, picture_path)

        # 贴底图
        if not self.transparent_background:
            self._paste_background_image(card, picture_path, data, dp)

        # 贴牌框
        ui_name = f'{data["type"]}-文本框-{data["class"]}'
        card.paste_image(self.image_manager.get_image(ui_name), (-4, - 4), 'contain')

        # 画等级
        card.set_card_level(data.get('level', -1))

        card.draw_centered_text((74, 134), self.font_manager.get_font_text("事件"), "卡牌类型字体", 22, (255, 255, 255),
                                max_length=None, debug_line=False)

        # 画内容
        traits = self._integrate_traits_text(data.get('traits', []))
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_padding=self._get_flavor_padding(data))

        effects = [
            {"type": "shadow", "size": 8, "spread": 16, "opacity": 100, "color": (3, 0, 0)},
        ]
        card.draw_left_text((140, 22), data['name'], "标题字体", 48, (255, 255, 255),
                            max_length=580, debug_line=False, effects=effects)
        card.draw_centered_text((370, 707), traits, "特性字体", 32, (255, 255, 255),
                                max_length=580, debug_line=False, effects=effects)

        vertices = [(75, 725), (682, 725), (692, 770), (704, 838), (701, 914), (679, 995),
                    (74, 995), (91, 920), (96, 844)]
        if 'victory' in data and data.get('victory') is not None:
            vertices = [(75, 725), (682, 725), (692, 770), (704, 838), (701, 914), (682, 970),
                        (77, 970), (91, 920), (96, 844)]
        card.draw_text(
            body,
            vertices=vertices,
            color=(255, 255, 255),
            default_font_name='正文字体', default_size=32, padding=15, draw_virtual_box=False,
            boundary_offset=self._get_text_boundary_offset(data, 'body'), effects=effects)
        card.draw_victory_points(
            position=(378, 973),
            victory_value=data.get('victory')
        )

        # 画投入图标
        if 'submit_icon' in data and isinstance(data['submit_icon'], list):
            for icon in data['submit_icon']:
                card.add_submit_icon(icon)

        return card

    def create_event_large_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作大画事件卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])

        card = Card(739, 1049, self.font_manager, self.image_manager, data['type'], data['class'])
        dp = self._open_picture(card_json, picture_path)

        # 贴底图
        if not self.transparent_background:
            self._paste_background_image(card, picture_path, data, dp)

        # 贴牌框
        ui_name = f'{data["type"]}-文本框-{data["class"]}'
        card.paste_image(self.image_manager.get_image(ui_name), (-4, 497 - 4), 'contain')

        # 画等级
        card.set_card_level(data.get('level', -1))

        card.draw_centered_text((78, 134), self.font_manager.get_font_text("事件"), "卡牌类型字体", 22, (255, 255, 255),
                                max_length=None, debug_line=False)
        # 画费用
        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])

        # 画内容
        traits = self._integrate_traits_text(data.get('traits', []))
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_padding=self._get_flavor_padding(data))

        offset = {'潜修者': -3, '守护者': -1, '生存者': -1, '中立': -3}.get(data.get('class', ''), 0)
        card.draw_centered_text((370, 623 + offset), data['name'], "标题字体", 48, (255, 255, 255),
                                max_length=600, debug_line=False,
                                effects=[
                                    {"type": "shadow", "size": 8, "spread": 16, "opacity": 100, "color": (3, 0, 0)},
                                ])
        card.draw_centered_text((368, 675), traits, "特性字体", 32, (255, 255, 255),
                                max_length=620, debug_line=False,
                                effects=[
                                    {"type": "shadow", "size": 8, "spread": 16, "opacity": 100, "color": (3, 0, 0)},
                                ])

        vertices = [(45, 690), (694, 690), (706, 757), (704, 817), (680, 887), (670, 952),
                    (598, 992), (135, 992), (77, 949), (61, 907), (31, 793)]

        if 'victory' in data and data.get('victory') is not None:
            vertices = [(45, 690), (694, 690), (706, 757), (704, 817), (680, 887), (670, 960),
                        (77, 960), (61, 907), (31, 793)]
        card.draw_text(
            body,
            vertices=vertices,
            default_font_name='正文字体', default_size=32, padding=18, draw_virtual_box=False,
            color=(255, 255, 255),
            boundary_offset=self._get_text_boundary_offset(data, 'body'),
            effects=[
                {"type": "shadow", "size": 8, "spread": 16, "opacity": 100, "color": (3, 0, 0)},
            ]
        )

        card.draw_victory_points(
            position=(370, 961),
            victory_value=data.get('victory')
        )

        # 画投入图标
        if 'submit_icon' in data and isinstance(data['submit_icon'], list):
            for icon in data['submit_icon']:
                card.add_submit_icon(icon)

        return card

    def create_asset_large_card(self, card_json: dict, picture_path: Union[str, Image.Image, None] = None) -> Card:
        """制作大画支援卡"""
        data = card_json
        if 'msg' in data and data['msg'] != '':
            raise ValueError(data['msg'])

        card = Card(739, 1049, self.font_manager, self.image_manager, data['type'], data['class'])
        dp = self._open_picture(card_json, picture_path)

        # 贴底图
        if not self.transparent_background:
            self._paste_background_image(card, picture_path, data, dp)

        health = data.get('health', -1) if isinstance(data.get('health'), int) else -1
        horror = data.get('horror', -1) if isinstance(data.get('horror'), int) else -1

        # 贴牌框
        ui_name = f'{data["type"]}-标题栏-{data["class"]}'
        if 'subtitle' in data and data['subtitle'] != '':
            ui_name = f'{data["type"]}-标题栏-副标题-{data["class"]}'
        card.paste_image(self.image_manager.get_image(ui_name), (0, 0), 'contain')
        ui_name = f'{data["type"]}-文本框-{data["class"]}'
        if health != -1 or horror != -1:
            ui_name += '-BS'
        card.paste_image(self.image_manager.get_image(ui_name), (-4, 564 - 4), 'contain')
        if data["class"] not in ['弱点', '中立']:
            ui_name = f'大画-支援卡-职业图标-{data["class"]}'
            card.paste_image(self.image_manager.get_image(ui_name), (149 - 4, 37 - 4), 'contain')

        # 画等级
        card.set_card_level(data.get('level', -1))

        card.draw_centered_text((78, 134), self.font_manager.get_font_text("支援"), "卡牌类型字体", 22, (255, 255, 255),
                                max_length=None, debug_line=False)
        # 画费用
        if 'cost' in data and isinstance(data['cost'], int):
            card.set_card_cost(data['cost'])

        # 画槽位
        clots_cont = 0
        if 'slots' in data and isinstance(data['slots'], str):
            card.add_slots(data['slots'])
            clots_cont += 1
        if 'slots2' in data and isinstance(data['slots2'], str):
            card.add_slots(data['slots2'])
            clots_cont += 1

        # 画内容
        traits = self._integrate_traits_text(data.get('traits', []))
        body = self._tidy_body_flavor(data['body'], data['flavor'], flavor_padding=self._get_flavor_padding(data))

        name_pos, name_max_length = (410, 55), 520
        if clots_cont == 1:
            name_pos, name_max_length = (385, 55), 475
        elif clots_cont == 2:
            name_pos, name_max_length = (370, 55), 430
        card.draw_centered_text(name_pos, data['name'], "标题字体", 48, (255, 255, 255),
                                max_length=name_max_length, debug_line=False,
                                effects=[
                                    {"type": "shadow", "size": 8, "spread": 16, "opacity": 100, "color": (3, 0, 0)},
                                ])

        if 'subtitle' in data and data['subtitle'] != '':
            card.draw_centered_text((418, 111), data['subtitle'], "副标题字体", 32, (255, 255, 255),
                                    max_length=370, debug_line=False,
                                    effects=[
                                        {"type": "shadow", "size": 8, "spread": 16, "opacity": 100, "color": (3, 0, 0)},
                                    ])
        traits_pos, traits_max_length = (368, 640), 620
        if health != -1 or horror != -1:
            traits_pos, traits_max_length = (310, 640), 510
        card.draw_centered_text(traits_pos, traits, "特性字体", 32, (255, 255, 255),
                                max_length=traits_max_length, debug_line=False,
                                effects=[
                                    {"type": "shadow", "size": 8, "spread": 16, "opacity": 100, "color": (3, 0, 0)},
                                ])
        max_bottom = 970
        if data.get('victory') is not None:
            max_bottom = 950
        vertices = [(19, 662), (718, 662), (718, max_bottom), (19, max_bottom)]
        if health != -1 or horror != -1:
            vertices = [(19, 662), (594, 662), (718, 705), (718, max_bottom), (19, max_bottom)]
        card.draw_text(
            body,
            vertices=vertices,
            default_font_name='正文字体', default_size=32, padding=15, draw_virtual_box=False,
            color=(255, 255, 255),
            boundary_offset=self._get_text_boundary_offset(data, 'body'),
            effects=[
                {"type": "shadow", "size": 8, "spread": 16, "opacity": 100, "color": (3, 0, 0)},
            ]
        )
        card.draw_victory_points(
            position=(370, 961),
            victory_value=data.get('victory')
        )

        if health != -1 or horror != -1:
            card.set_health_and_horror(health, horror)

        # 画投入图标
        if 'submit_icon' in data and isinstance(data['submit_icon'], list):
            for icon in data['submit_icon']:
                card.add_submit_icon(icon)

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
        # 标签适配器
        adapter = CardAdapter(card_json, self.font_manager)
        card_json = adapter.convert()
        # 预处理
        card_json = self._preprocessing_json(card_json)

        if picture_path is None:
            picture_path = card_json.get('picture_path', None)

        _self_image_mode = self.image_mode
        if 'image_mode' in card_json and isinstance(card_json['image_mode'], int):
            self.image_mode = card_json['image_mode']
        try:

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
            elif card_type == '大画-技能卡':
                return self.create_skill_large_card(card_json, picture_path)
            elif card_type == '大画-事件卡':
                return self.create_event_large_card(card_json, picture_path)
            elif card_type == '大画-支援卡':
                return self.create_asset_large_card(card_json, picture_path)
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
            elif card_type == '规则小卡':
                return self.create_rule_mini_card(card_json)
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
            elif card_type == '特殊图片':
                return self.create_special_pictures(card_json, picture_path)
            elif card_type == '调查员小卡':
                return self.create_investigator_mini_card(card_json, picture_path)
            else:
                if 'class' not in card_json:
                    card_json['class'] = '中立'
                    if 'level' not in card_json:
                        card_json['level'] = -1
                return self.create_player_cards(card_json, picture_path)
        finally:
            self.image_mode = _self_image_mode


# 使用示例
if __name__ == '__main__':
    json_data = {
        "type": "大画-技能卡",
        "class": "流浪者",
        "special_type": 1,
        "level": 1,
        "cost": -1,
        "health": 3,
        "horror": 1,
        # "victory": 1,
        "slots": '手部',
        "slots2": '法术',
        "name": "测试",
        "subtitle": "副标题",
        "id": "",
        "created_at": "",
        "version": "2.0",
        "language": "zh",
        "submit_icon": ['战力', '意志'],
        "traits": ['悖论', '勇气'],
        "back": {},
        "body": "大画卡牌组专用。\n"
                "【显现】 – 从对应职阶图层中选择一项：\n"
                "<点>守卫者。              <点>探求者。\n"
                "<点>流浪者。             <点>潜修者。",
        "picture_path": r"C:\Users\xziyi\Desktop\卡图.png"
    }

    # 创建字体和图片管理器
    fm = FontManager('fonts')
    im = ImageManager('images')
    im.load_images('icons')

    # 创建卡牌创建器
    creator = CardCreator(
        font_manager=fm,
        image_manager=im
    )

    # 创建卡牌 - 支持PIL图片对象
    # picture = Image.open("path/to/image.jpg")  # 也可以传入PIL图片对象
    # fm.set_lang('en')
    # card = creator.create_card(json_data, picture_path=None)
    # card.image.show()
    profiler = cProfile.Profile()
    profiler.enable()

    fm.set_lang('zh')
    card = creator.create_card(json_data, picture_path=json_data.get('picture_path', None))
    # 画页脚
    illustrator = "HVNT TCHEKT"
    footer_copyright = "© Copyleft"
    encounter_group_number = ""
    card_number = "P0P357"
    card.set_footer_information(
        illustrator,
        footer_copyright,
        encounter_group_number,
        card_number
    )

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('tottime')  # 按函数自身花费时间排序
    stats.print_stats(10)  # 打印耗时最长的前10个函数
    card.image.convert('RGB').show()

    # card_end = creator.create_card_bottom_map(json_data, picture_path=json_data.get('picture_path', None))
    # card_end.image.show()

    # from create_pdf import PDFVectorDrawer

    # drawer = PDFVectorDrawer('output_with_borders.pdf', fm)
    # drawer.add_page(card_end.image, card.get_text_layer_metadata())
    # drawer.save()
