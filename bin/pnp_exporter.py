"""
PNP (Print and Play) PDF导出模块

该模块负责将内容包中的卡牌导出为可打印的PDF文件，支持两种导出模式：
1. 单卡模式：一张卡一页，按正反面顺序排列
2. 打印纸模式：按指定纸张规格排版，带切割辅助线
"""

import json
import os
import re
import shutil
import tempfile
import uuid
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4, A3, letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from ExportHelper import ExportHelper


class PNPExporter:
    """PNP PDF导出器"""

    # 纸张规格定义 (宽, 高) 单位:mm
    PAPER_SIZES = {
        'A4': (210, 297),
        'A3': (297, 420),
        'Letter': (215.9, 279.4),
    }

    def __init__(self, export_params: Dict[str, Any], workspace_manager):
        """
        初始化PNP导出器

        Args:
            export_params: 导出参数，将传递给ExportHelper
            workspace_manager: 工作空间管理器
        """
        self.export_params = export_params
        self.workspace_manager = workspace_manager
        self.logs = []

        # 创建ExportHelper实例
        self.export_helper = ExportHelper(export_params, workspace_manager)

    def _add_log(self, message: str) -> None:
        """添加日志"""
        self.logs.append(message)
        print(f"[PNPExporter] {message}")

    def _extract_card_number(self, card_number_str: str) -> int:
        """
        从卡牌编号字符串中提取数字

        Args:
            card_number_str: 卡牌编号字符串

        Returns:
            提取的数字，如果提取失败则返回1
        """
        if not card_number_str:
            return 1

        # 使用正则提取数字
        match = re.search(r'\d+', str(card_number_str))
        if match:
            return int(match.group())
        return 1

    def _create_temp_directory(self) -> str:
        """
        在工作目录的.cache中创建临时文件夹

        Returns:
            临时文件夹的绝对路径
        """
        cache_dir = self.workspace_manager._get_absolute_path('.cache')
        os.makedirs(cache_dir, exist_ok=True)

        # 创建唯一的临时目录
        temp_dir_name = f"pnp_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        temp_dir = os.path.join(cache_dir, temp_dir_name)
        os.makedirs(temp_dir, exist_ok=True)

        self._add_log(f"创建临时目录: {temp_dir}")
        return temp_dir

    def _export_card_images(
            self,
            cards: List[Dict[str, Any]],
            temp_dir: str
    ) -> List[Dict[str, Any]]:
        """
        导出所有卡牌图片到临时目录

        Args:
            cards: 卡牌列表
            temp_dir: 临时目录路径

        Returns:
            导出结果列表，每项包含卡牌信息和导出的图片路径
        """
        exported_cards = []

        for i, card_meta in enumerate(cards):
            try:
                card_filename = card_meta.get('filename', '')
                if not card_filename:
                    self._add_log(f"✗ 跳过卡牌 {i + 1}: 缺少文件名")
                    continue

                # 读取卡牌数据
                card_data = self._read_card_json(card_filename)
                if not card_data:
                    self._add_log(f"✗ 跳过卡牌 {i + 1}: 无法读取卡牌数据")
                    continue

                card_name = card_data.get('name', f'Card_{i + 1}')
                card_number = card_data.get('card_number', '')
                quantity = card_data.get('quantity', 1)

                self._add_log(f"正在导出卡牌: {card_name} (编号: {card_number}, 数量: {quantity})")

                # 使用ExportHelper导出卡牌
                result = self.export_helper.export_card_auto(card_filename)

                # 检查是否为双面卡牌
                if isinstance(result, dict):
                    # 双面卡牌
                    front_image = result.get('front')
                    back_image = result.get('back')

                    if not front_image or not back_image:
                        self._add_log(f"✗ 错误: 卡牌 {card_name} 缺少正面或背面图片！")
                        continue

                    # 保存图片
                    front_path, back_path = self._save_card_images(
                        front_image, back_image, card_name, i, temp_dir
                    )

                    exported_cards.append({
                        'card_meta': card_meta,
                        'card_data': card_data,
                        'card_name': card_name,
                        'card_number': card_number,
                        'quantity': quantity,
                        'front_path': front_path,
                        'back_path': back_path,
                        'is_double_sided': True
                    })

                    self._add_log(f"✓ 成功导出双面卡牌: {card_name}")
                else:
                    # 单面卡牌 - 这不应该发生，因为我们要求所有卡牌都是双面的
                    self._add_log(f"✗ 错误: 卡牌 {card_name} 只有单面，无法导出PNP！")
                    continue

            except Exception as e:
                self._add_log(f"✗ 导出卡牌 {i + 1} 失败: {e}")
                continue

        return exported_cards

    def _read_card_json(self, card_filename: str) -> Optional[Dict[str, Any]]:
        """读取卡牌JSON数据"""
        try:
            card_content = self.workspace_manager.get_file_content(card_filename)
            if not card_content:
                return None
            return json.loads(card_content)
        except Exception as e:
            self._add_log(f"读取卡牌JSON失败 {card_filename}: {e}")
            return None

    def _save_card_images(
            self,
            front_image: Image.Image,
            back_image: Image.Image,
            card_name: str,
            index: int,
            temp_dir: str
    ) -> Tuple[str, str]:
        """
        保存卡牌图片，如果是横向卡牌则旋转

        Args:
            front_image: 正面图片
            back_image: 背面图片
            card_name: 卡牌名称
            index: 卡牌索引
            temp_dir: 临时目录

        Returns:
            (正面图片路径, 背面图片路径)
        """
        # 检查是否为横向卡牌
        is_landscape = front_image.width > front_image.height

        if is_landscape:
            # 横向卡牌：正面顺时针旋转90度，背面逆时针旋转90度
            front_image = front_image.rotate(-90, expand=True)
            back_image = back_image.rotate(90, expand=True)
            self._add_log(f"卡牌 {card_name} 为横向，已旋转")

        # 生成文件名（使用索引确保唯一性和排序）
        safe_name = "".join(c for c in card_name if c.isalnum() or c in (' ', '-', '_')).strip()
        front_filename = f"{index:04d}_{safe_name}_front.png"
        back_filename = f"{index:04d}_{safe_name}_back.png"

        front_path = os.path.join(temp_dir, front_filename)
        back_path = os.path.join(temp_dir, back_filename)

        # 保存图片
        front_image.save(front_path, 'PNG')
        back_image.save(back_path, 'PNG')

        return front_path, back_path

    def _sort_cards_by_number(self, exported_cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        按card_number排序卡牌

        Args:
            exported_cards: 导出的卡牌列表

        Returns:
            排序后的卡牌列表
        """
        return sorted(
            exported_cards,
            key=lambda x: self._extract_card_number(x['card_number'])
        )

    def _generate_single_card_pdf(
            self,
            exported_cards: List[Dict[str, Any]],
            output_path: str
    ) -> None:
        """
        生成单卡模式PDF（一张卡一页，按正反面顺序）

        Args:
            exported_cards: 导出的卡牌列表
            output_path: PDF输出路径
        """
        self._add_log("生成单卡模式PDF...")

        # 创建PDF
        c = canvas.Canvas(output_path)

        for card_info in exported_cards:
            quantity = card_info.get('quantity', 1)
            if quantity is None:
                quantity = 1

            front_path = card_info['front_path']
            back_path = card_info['back_path']

            # 根据quantity生成对应数量的副本
            for copy_num in range(quantity):
                # 读取图片获取尺寸
                from PIL import Image as PILImage
                front_img = PILImage.open(front_path)
                width_px, height_px = front_img.size
                front_img.close()

                # 转换为mm（假设DPI为300）
                dpi = self.export_params.get('dpi', 300)
                width_mm = (width_px / dpi) * 25.4
                height_mm = (height_px / dpi) * 25.4

                # 设置页面大小为卡牌实际尺寸
                c.setPageSize((width_mm * mm, height_mm * mm))

                # 添加正面
                c.drawImage(front_path, 0, 0, width=width_mm * mm, height=height_mm * mm)
                c.showPage()

                # 添加背面
                c.drawImage(back_path, 0, 0, width=width_mm * mm, height=height_mm * mm)
                c.showPage()

        c.save()
        self._add_log(f"单卡模式PDF生成完成: {output_path}")

    def _generate_print_sheet_pdf(
            self,
            exported_cards: List[Dict[str, Any]],
            output_path: str,
            paper_size: str = 'A4'
    ) -> None:
        """
        生成打印纸模式PDF（按纸张规格排版，带切割辅助线）

        Args:
            exported_cards: 导出的卡牌列表
            output_path: PDF输出路径
            paper_size: 纸张规格，默认A4
        """
        self._add_log(f"生成打印纸模式PDF (纸张: {paper_size})...")

        # 获取纸张尺寸
        if paper_size not in self.PAPER_SIZES:
            raise ValueError(f"不支持的纸张规格: {paper_size}")

        paper_width_mm, paper_height_mm = self.PAPER_SIZES[paper_size]

        # 读取第一张卡牌获取卡牌尺寸
        if not exported_cards:
            raise ValueError("没有卡牌可以导出")

        first_card = exported_cards[0]
        from PIL import Image as PILImage
        card_img = PILImage.open(first_card['front_path'])
        card_width_px, card_height_px = card_img.size
        card_img.close()

        # 转换为mm
        dpi = self.export_params.get('dpi', 300)
        card_width_mm = (card_width_px / dpi) * 25.4
        card_height_mm = (card_height_px / dpi) * 25.4

        # 计算每页可以放置多少张卡牌（无间隙）
        margin_mm = 5  # 边距
        card_gap_mm = 0  # 卡牌间距设为0

        cards_per_row = int((paper_width_mm - 2 * margin_mm) / card_width_mm)
        cards_per_col = int((paper_height_mm - 2 * margin_mm) / card_height_mm)
        cards_per_page = cards_per_row * cards_per_col

        if cards_per_page == 0:
            raise ValueError(
                f"卡牌尺寸 ({card_width_mm}x{card_height_mm}mm) 超过纸张尺寸 ({paper_width_mm}x{paper_height_mm}mm)")

        self._add_log(f"每页可放置: {cards_per_row}x{cards_per_col} = {cards_per_page} 张卡牌")

        # 创建PDF
        c = canvas.Canvas(output_path, pagesize=(paper_width_mm * mm, paper_height_mm * mm))

        # 准备卡牌列表（扩展quantity）
        all_cards = []
        for card_info in exported_cards:
            quantity = card_info.get('quantity', 1)
            if quantity is None:
                quantity = 1
            for _ in range(quantity):
                all_cards.append(card_info)

        # 分页处理
        total_cards = len(all_cards)
        total_pages = (total_cards + cards_per_page - 1) // cards_per_page * 2  # *2因为正反面

        self._add_log(f"总共 {total_cards} 张卡牌，需要 {total_pages} 页（正反面）")

        # 生成正面页和背面页
        for page_num in range(0, total_pages, 2):
            front_page_num = page_num // 2
            start_idx = front_page_num * cards_per_page
            end_idx = min(start_idx + cards_per_page, total_cards)
            page_cards = all_cards[start_idx:end_idx]

            # 正面页
            self._draw_card_page(
                c, page_cards, 'front',
                cards_per_row, cards_per_col,
                card_width_mm, card_height_mm,
                paper_width_mm, paper_height_mm,
                margin_mm, card_gap_mm
            )
            c.showPage()

            # 背面页（水平轴对应）
            self._draw_card_page(
                c, page_cards, 'back',
                cards_per_row, cards_per_col,
                card_width_mm, card_height_mm,
                paper_width_mm, paper_height_mm,
                margin_mm, card_gap_mm,
                mirror=True
            )
            c.showPage()

        c.save()
        self._add_log(f"打印纸模式PDF生成完成: {output_path}")

    def _draw_card_page(
            self,
            c: canvas.Canvas,
            cards: List[Dict[str, Any]],
            side: str,
            cards_per_row: int,
            cards_per_col: int,
            card_width_mm: float,
            card_height_mm: float,
            paper_width_mm: float,
            paper_height_mm: float,
            margin_mm: float,
            card_gap_mm: float,
            mirror: bool = False
    ) -> None:
        """
        绘制一页卡牌

        Args:
            c: PDF Canvas对象
            cards: 本页的卡牌列表
            side: 'front' 或 'back'
            cards_per_row: 每行卡牌数
            cards_per_col: 每列卡牌数
            card_width_mm: 卡牌宽度(mm)
            card_height_mm: 卡牌高度(mm)
            paper_width_mm: 纸张宽度(mm)
            paper_height_mm: 纸张高度(mm)
            margin_mm: 边距(mm)
            card_gap_mm: 卡牌间距(mm)
            mirror: 是否水平镜像（用于背面）
        """
        # 计算本页实际卡牌的行列数
        actual_cards = len(cards)
        actual_rows = (actual_cards + cards_per_row - 1) // cards_per_row
        actual_cols = min(actual_cards, cards_per_row)

        # 计算实际使用的总宽度和总高度
        total_content_width = actual_cols * card_width_mm + (actual_cols - 1) * card_gap_mm
        total_content_height = actual_rows * card_height_mm + (actual_rows - 1) * card_gap_mm

        # 计算起始偏移量，使内容居中
        start_x = (paper_width_mm - total_content_width) / 2
        start_y = (paper_height_mm - total_content_height) / 2

        for idx, card_info in enumerate(cards):
            row = idx // cards_per_row
            col = idx % cards_per_row

            # 如果是背面且需要镜像，则水平翻转列号
            if mirror:
                col = cards_per_row - 1 - col

            # 计算卡牌位置（居中排列）
            x = start_x + col * (card_width_mm + card_gap_mm)
            # 注意：PDF坐标系是左下角为原点，所以y坐标需要从下往上计算
            y = paper_height_mm - start_y - (row + 1) * card_height_mm - row * card_gap_mm

            # 获取图片路径
            image_path = card_info['front_path'] if side == 'front' else card_info['back_path']

            # 绘制卡牌
            c.drawImage(image_path, x * mm, y * mm, width=card_width_mm * mm, height=card_height_mm * mm)

            # 判断是否在边缘，只在边缘卡牌绘制外侧裁剪线
            is_left_edge = (col == 0)
            is_right_edge = (col == actual_cols - 1)
            is_top_edge = (row == 0)
            is_bottom_edge = (row == actual_rows - 1)

            self._draw_cut_marks(
                c, x, y, card_width_mm, card_height_mm,
                draw_left=is_left_edge,
                draw_right=is_right_edge,
                draw_top=is_top_edge,
                draw_bottom=is_bottom_edge
            )

    def _draw_cut_marks(
            self,
            c: canvas.Canvas,
            x_mm: float,
            y_mm: float,
            width_mm: float,
            height_mm: float,
            mark_length_mm: float = 3,
            mark_offset_mm: float = 0.5,
            draw_left: bool = True,
            draw_right: bool = True,
            draw_top: bool = True,
            draw_bottom: bool = True
    ) -> None:
        """
        绘制切割辅助线（每个角落2条线）

        Args:
            c: PDF Canvas对象
            x_mm: 卡牌左下角x坐标(mm)
            y_mm: 卡牌左下角y坐标(mm)
            width_mm: 卡牌宽度(mm)
            height_mm: 卡牌高度(mm)
            mark_length_mm: 辅助线长度(mm)
            mark_offset_mm: 辅助线与卡牌边缘的距离(mm)
            draw_left: 是否绘制左侧裁剪线
            draw_right: 是否绘制右侧裁剪线
            draw_top: 是否绘制顶部裁剪线
            draw_bottom: 是否绘制底部裁剪线
        """
        c.setStrokeColorRGB(0.5, 0.5, 0.5)  # 灰色
        c.setLineWidth(0.25)

        # 四个角的坐标及其对应的边缘
        corners = [
            (x_mm, y_mm, draw_left, draw_bottom),  # 左下
            (x_mm + width_mm, y_mm, draw_right, draw_bottom),  # 右下
            (x_mm, y_mm + height_mm, draw_left, draw_top),  # 左上
            (x_mm + width_mm, y_mm + height_mm, draw_right, draw_top),  # 右上
        ]

        for corner_x, corner_y, draw_horizontal_side, draw_vertical_side in corners:
            # 水平线
            if draw_horizontal_side:
                if corner_x == x_mm:  # 左侧
                    c.line(
                        (corner_x - mark_offset_mm - mark_length_mm) * mm, corner_y * mm,
                        (corner_x - mark_offset_mm) * mm, corner_y * mm
                    )
                else:  # 右侧
                    c.line(
                        (corner_x + mark_offset_mm) * mm, corner_y * mm,
                        (corner_x + mark_offset_mm + mark_length_mm) * mm, corner_y * mm
                    )

            # 垂直线
            if draw_vertical_side:
                if corner_y == y_mm:  # 下侧
                    c.line(
                        corner_x * mm, (corner_y - mark_offset_mm - mark_length_mm) * mm,
                        corner_x * mm, (corner_y - mark_offset_mm) * mm
                    )
                else:  # 上侧
                    c.line(
                        corner_x * mm, (corner_y + mark_offset_mm) * mm,
                        corner_x * mm, (corner_y + mark_offset_mm + mark_length_mm) * mm
                    )

    def export_pnp(
            self,
            cards: List[Dict[str, Any]],
            output_path: str,
            mode: str = 'single_card',
            paper_size: str = 'A4'
    ) -> Dict[str, Any]:
        """
        导出PNP PDF

        Args:
            cards: 内容包的卡牌列表
            output_path: PDF输出路径
            mode: 导出模式，'single_card' 或 'print_sheet'
            paper_size: 纸张规格（仅在print_sheet模式下使用）

        Returns:
            导出结果
        """
        try:
            self.logs = []
            self._add_log("开始导出PNP PDF...")
            self._add_log(f"导出模式: {mode}")
            self._add_log(f"总卡牌数: {len(cards)}")

            # 1. 创建临时目录
            temp_dir = self._create_temp_directory()

            try:
                # 2. 导出所有卡牌图片
                self._add_log("开始导出卡牌图片...")
                exported_cards = self._export_card_images(cards, temp_dir)

                if not exported_cards:
                    raise ValueError("没有成功导出任何卡牌图片")

                self._add_log(f"成功导出 {len(exported_cards)} 张卡牌图片")

                # 3. 按card_number排序
                exported_cards = self._sort_cards_by_number(exported_cards)
                self._add_log("卡牌已按编号排序")

                # 4. 生成PDF
                if mode == 'single_card':
                    self._generate_single_card_pdf(exported_cards, output_path)
                elif mode == 'print_sheet':
                    self._generate_print_sheet_pdf(exported_cards, output_path, paper_size)
                else:
                    raise ValueError(f"不支持的导出模式: {mode}")

                self._add_log("PNP PDF导出成功！")

                return {
                    'success': True,
                    'output_path': output_path,
                    'cards_exported': len(exported_cards),
                    'logs': self.logs.copy()
                }

            finally:
                # 5. 清理临时目录
                try:
                    shutil.rmtree(temp_dir)
                    self._add_log(f"清理临时目录: {temp_dir}")
                except Exception as e:
                    self._add_log(f"清理临时目录失败: {e}")

        except Exception as e:
            self._add_log(f"导出PNP PDF失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'logs': self.logs.copy()
            }
