import json
import os
import sys
import traceback
from typing import Dict, List, Optional, Any

from PIL import Image


class DeckExporter:
    """牌库导出器，负责导出牌库图片和PDF"""

    def __init__(self, workspace_manager):
        """
        初始化牌库导出器

        Args:
            workspace_manager: WorkspaceManager实例，用于访问文件和生成卡图
        """
        self.workspace_manager = workspace_manager

    def export_deck_image(self, deck_name: str, export_format: str = 'PNG', quality: int = 95) -> bool:
        """
        导出牌库图片

        Args:
            deck_name: 牌库名称（DeckBuilder文件夹中的文件名）
            export_format: 导出格式（JPG或PNG）
            quality: 图片质量百分比（1-100）

        Returns:
            bool: 导出是否成功
        """
        try:
            from PIL import Image

            # 1. 读取牌库JSON文件
            deck_builder_path = os.path.join(self.workspace_manager.workspace_path, 'DeckBuilder')
            if not os.path.exists(deck_builder_path):
                print("DeckBuilder目录不存在")
                return False

            deck_file_path = os.path.join(deck_builder_path, deck_name)
            if not os.path.exists(deck_file_path):
                print(f"牌库文件不存在: {deck_name}")
                return False

            with open(deck_file_path, 'r', encoding='utf-8') as f:
                deck_data = json.load(f)

            # 2. 获取底图尺寸
            width = deck_data.get('width', 1)
            height = deck_data.get('height', 1)

            # 单元大小
            card_width = 750
            card_height = 1050

            # 创建正面底图（黑色背景）
            canvas_width = width * card_width
            canvas_height = height * card_height
            front_image = Image.new('RGB', (canvas_width, canvas_height), (0, 0, 0))

            # 3. 处理正面卡片和背面卡片
            front_cards = deck_data.get('frontCards', [])
            back_cards = deck_data.get('backCards', [])
            is_shared_back = deck_data.get('isSharedBack', False)
            shared_back_card = deck_data.get('sharedBackCard', {})

            # 收集所有需要处理的位置
            positions_to_process = set()
            for card in front_cards:
                positions_to_process.add(card.get('index', 0))

            # 处理正面卡片
            for position in positions_to_process:
                # 计算位置坐标（从左到右，从上到下）
                col = position % width
                row = position // width
                x = col * card_width
                y = row * card_height

                # 处理正面卡片
                front_card_image = self._get_card_image_for_position(front_cards, position)
                if front_card_image:
                    processed_front = self._process_card_image_for_export(front_card_image, card_width, card_height)
                    front_image.paste(processed_front, (x, y))

            # 4. 处理背面图片
            if is_shared_back and shared_back_card:
                # 共享背面：导出单张卡牌大小的背面
                shared_back_image = self._load_card_image(shared_back_card)
                if shared_back_image:
                    back_image = self._process_card_image_for_export(shared_back_image, card_width, card_height)
                else:
                    # 如果无法加载共享背面，创建黑色背景
                    back_image = Image.new('RGB', (card_width, card_height), (0, 0, 0))
            else:
                # 独立背面：创建大拼图
                back_image = Image.new('RGB', (canvas_width, canvas_height), (0, 0, 0))

                for position in positions_to_process:
                    col = position % width
                    row = position // width
                    x = col * card_width
                    y = row * card_height

                    back_card_image = self._get_card_image_for_position(back_cards, position)
                    if back_card_image:
                        processed_back = self._process_card_image_for_export(back_card_image, card_width, card_height)
                        back_image.paste(processed_back, (x, y))

            # 5. 保存图片
            deck_base_name = os.path.splitext(deck_name)[0]  # 去掉后缀

            front_filename = f"{deck_base_name}_front.{export_format.lower()}"
            back_filename = f"{deck_base_name}_back.{export_format.lower()}"

            front_path = os.path.join(deck_builder_path, front_filename)
            back_path = os.path.join(deck_builder_path, back_filename)

            save_kwargs = {}
            if export_format == 'JPG':
                save_kwargs['quality'] = quality
                save_kwargs['format'] = 'JPEG'
            else:
                save_kwargs['format'] = 'PNG'

            front_image.save(front_path, **save_kwargs)
            back_image.save(back_path, **save_kwargs)

            print(f"牌库图片已导出:")
            print(f"  正面: {self.workspace_manager._get_relative_path(front_path)}")
            print(
                f"  背面: {self.workspace_manager._get_relative_path(back_path)} {'(共享背面)' if is_shared_back else '(独立背面)'}")

            return True

        except Exception as e:
            print(f"导出牌库图片失败: {e}")
            return False

    def export_deck_pdf(self, deck_name: str, pdf_filename: Optional[str] = None) -> bool:
        """
        导出牌库PDF

        Args:
            deck_name: 牌库名称（DeckBuilder文件夹中的文件名）
            pdf_filename: PDF文件名，如果为None则使用deck_name生成

        Returns:
            bool: 导出是否成功
        """
        try:
            from create_pdf import PDFVectorDrawer, RotationDirection

            # 1. 读取牌库JSON文件
            deck_builder_path = os.path.join(self.workspace_manager.workspace_path, 'DeckBuilder')
            if not os.path.exists(deck_builder_path):
                print("DeckBuilder目录不存在")
                return False

            deck_file_path = os.path.join(deck_builder_path, deck_name)
            if not os.path.exists(deck_file_path):
                print(f"牌库文件不存在: {deck_name}")
                return False

            with open(deck_file_path, 'r', encoding='utf-8') as f:
                deck_data = json.load(f)

            # 2. 生成PDF文件名
            if pdf_filename is None:
                deck_base_name = os.path.splitext(deck_name)[0]
                pdf_filename = f"{deck_base_name}.pdf"

            pdf_path = os.path.join(deck_builder_path, pdf_filename)

            # 3. 创建PDF绘图器
            drawer = PDFVectorDrawer(pdf_path, self.workspace_manager.font_manager)

            # 4. 获取牌库尺寸和卡片列表
            width = deck_data.get('width', 1)
            height = deck_data.get('height', 1)
            front_cards = deck_data.get('frontCards', [])
            back_cards = deck_data.get('backCards', [])
            is_shared_back = deck_data.get('isSharedBack', False)
            shared_back_card = deck_data.get('sharedBackCard', {})

            # 5. 收集所有需要处理的位置
            positions_to_process = set()
            for card in front_cards:
                positions_to_process.add(card.get('index', 0))

            positions_to_process = sorted(positions_to_process)

            # 6. 按从左到右，从上到下，先正面，后背面的顺序添加页面
            for position in positions_to_process:
                # 处理正面卡片
                front_card_image = self._get_card_image_for_position(front_cards, position)
                if front_card_image:
                    # 检测图片是否横向
                    is_landscape = front_card_image.size[0] > front_card_image.size[1]
                    # 正面顺时针旋转
                    rotation = RotationDirection.RIGHT if is_landscape else RotationDirection.NORMAL

                    # 获取卡片的文本层元数据（如果是生成的卡图）
                    card_bottom_map, text_metadata = self._get_card_text_metadata(front_cards, position)
                    if card_bottom_map:
                        front_card_image = card_bottom_map

                    drawer.add_page(front_card_image, text_metadata, rotation)

                # 处理背面卡片
                if is_shared_back and shared_back_card:
                    # 共享背面：每张正面卡片后面都添加相同的共享背面
                    shared_back_image = self._load_card_image(shared_back_card)
                    if shared_back_image:
                        is_landscape = shared_back_image.size[0] > shared_back_image.size[1]
                        rotation = RotationDirection.LEFT if is_landscape else RotationDirection.NORMAL

                        card_bottom_map, text_metadata = self._get_shared_back_text_metadata(shared_back_card)
                        if card_bottom_map:
                            shared_back_image = card_bottom_map

                        drawer.add_page(shared_back_image, text_metadata, rotation)
                else:
                    # 独立背面：使用位置对应的背面
                    back_card_image = self._get_card_image_for_position(back_cards, position)
                    if back_card_image:
                        is_landscape = back_card_image.size[0] > back_card_image.size[1]
                        rotation = RotationDirection.LEFT if is_landscape else RotationDirection.NORMAL

                        card_bottom_map, text_metadata = self._get_card_text_metadata(back_cards, position)
                        if card_bottom_map:
                            back_card_image = card_bottom_map

                        drawer.add_page(back_card_image, text_metadata, rotation)

            # 7. 保存PDF
            drawer.save()

            print(f"牌库PDF已导出: {self.workspace_manager._get_relative_path(pdf_path)}")
            return True

        except Exception as e:
            print(f"导出牌库PDF失败: {e}")
            return False

    def _get_card_image_for_position(self, cards: List[Dict], position: int) -> Optional[Image.Image]:
        """获取指定位置的卡片图片"""
        for card in cards:
            if card.get('index') == position:
                return self._load_card_image(card)
        return None

    def _load_card_image(self, card_data: Dict) -> Optional[Image.Image]:
        """根据卡片数据加载图片"""
        try:
            from PIL import Image

            card_type = card_data.get('type')
            card_path = card_data.get('path')

            if card_type == 'image':
                # 直接读取图片文件（相对工作目录路径）
                image_path = self.workspace_manager._get_absolute_path(card_path)
                if os.path.exists(image_path):
                    return Image.open(image_path)

            elif card_type == 'cardback':
                # 固定的卡牌背面，从程序目录读取
                if card_path == 'player':
                    cardback_filename = 'cardback/player-back.jpg'
                elif card_path == 'encounter':
                    cardback_filename = 'cardback/encounter-back.jpg'
                else:
                    return None

                # 从程序目录读取
                cardback_path = os.path.join('.', cardback_filename)

                # 如果是PyInstaller打包的程序
                if hasattr(sys, '_MEIPASS'):
                    cardback_path = os.path.join(sys._MEIPASS, cardback_filename)

                print(f"正在读取卡牌背面图片: {cardback_path} {os.path.exists(cardback_path)}")
                if os.path.exists(cardback_path):
                    return Image.open(cardback_path)

            elif card_type == 'card':
                # 卡牌对象，需要读取卡牌JSON并生成图片
                card_json_path = self.workspace_manager._get_absolute_path(card_path)
                if os.path.exists(card_json_path):
                    with open(card_json_path, 'r', encoding='utf-8') as f:
                        card_json_data = json.load(f)
                    return self.workspace_manager.generate_card_image(card_json_data).image

            return None

        except Exception as e:
            print(f"加载卡片图片失败: {e}")
            return None

    def _process_card_image_for_export(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """处理卡片图片用于导出（检测方向、旋转、拉伸）- 所有横向图片都顺时针旋转90度"""
        try:
            # 检测图片是横向还是纵向
            img_width, img_height = image.size
            is_landscape = img_width > img_height

            if is_landscape:
                # 横向图片统一顺时针旋转90度
                image = image.rotate(-90, expand=True)

            # 拉伸到目标尺寸
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

            return image

        except Exception as e:
            print(f"处理卡片图片失败: {e}")
            return image

    def _get_card_text_metadata(self, cards: List[Dict], position: int) -> tuple[Image, List[Dict[str, Any]]]:
        """获取指定位置卡片的文本层元数据"""
        for card in cards:
            if card.get('index') == position:
                card_type = card.get('type')
                card_path = card.get('path')

                if card_type == 'card':
                    # 如果是卡牌对象，尝试获取文本元数据
                    card_json_path = self.workspace_manager._get_absolute_path(card_path)
                    if os.path.exists(card_json_path):
                        try:
                            with open(card_json_path, 'r', encoding='utf-8') as f:
                                card_json_data = json.load(f)

                            # 生成卡图并获取文本层元数据
                            card = self.workspace_manager.generate_card_image(card_json_data)
                            card_bottom = self.workspace_manager.generate_card_image(card_json_data, True)
                            return card_bottom.image, card.get_text_layer_metadata()
                        except Exception as e:
                            # 打印异常栈
                            traceback.print_exc()
                            print(f"获取文本元数据失败: {e}")

        # 如果没有文本元数据，返回空列表
        return None, []

    def _get_shared_back_text_metadata(self, shared_back_card: Dict) -> tuple[Image, List[Dict[str, Any]]]:
        """获取共享背面卡片的文本层元数据"""
        card_type = shared_back_card.get('type')
        card_path = shared_back_card.get('path')

        if card_type == 'card':
            card_json_path = self.workspace_manager._get_absolute_path(card_path)
            if os.path.exists(card_json_path):
                try:
                    with open(card_json_path, 'r', encoding='utf-8') as f:
                        card_json_data = json.load(f)

                    # 生成卡图并获取文本层元数据
                    card = self.workspace_manager.generate_card_image(card_json_data)
                    card_bottom = self.workspace_manager.generate_card_image(card_json_data, True)
                    return card_bottom.image, card.get_text_layer_metadata()
                except Exception as e:
                    traceback.print_exc()
                    print(f"获取共享背面文本元数据失败: {e}")

        return None, []
