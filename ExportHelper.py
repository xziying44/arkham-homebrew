import enum
import json
import math
import time
from typing import Dict, Any, Tuple, TypeVar, Type

import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

from bin.workspace_manager import WorkspaceManager
from export_helper.LamaCleaner import LamaCleaner

# 定义泛型类型变量
T = TypeVar('T', bound=enum.Enum)


# --- 1. 使用枚举定义固定选项 ---

class ExportFormat(enum.Enum):
    """导出格式"""
    PNG = "PNG"
    JPG = "JPG"


class ExportSize(enum.Enum):
    """导出规格 (预设尺寸)"""
    SIZE_61_88 = "61mm × 88mm"
    SIZE_61_5_88 = "61.5mm × 88mm"
    SIZE_62_88 = "62mm × 88mm"
    POKER_SIZE = "63.5mm × 88.9mm (2.5″ × 3.5″)"  # 标准扑克牌尺寸


class ExportBleed(enum.Enum):
    """出血规格 (单位: mm)"""
    NONE = 0
    TWO_MM = 2
    THREE_MM = 3


class BleedMode(enum.Enum):
    """出血模式"""
    CROP = "裁剪"  # 裁剪模式：保持图片比例，裁剪多余部分
    STRETCH = "拉伸"  # 拉伸模式：拉伸图片填满整个尺寸


class BleedModel(enum.Enum):
    """出血模型"""
    MIRROR = "镜像出血"  # 镜像出血
    LAMA = "LaMa模型出血"  # LaMa模型出血


# --- 2. 导出助手类实现 ---

class ExportHelper:
    """
    一个用于处理和计算图像导出参数的助手类。
    它负责验证参数、合并配置并计算最终的像素尺寸。
    """
    # 毫米/英寸转换比
    MM_PER_INCH = 25.4

    # 预设的规格尺寸 (宽, 高)，单位 mm
    SPECIFICATIONS: Dict[ExportSize, Tuple[float, float]] = {
        ExportSize.SIZE_61_88: (61.0, 88.0),
        ExportSize.SIZE_61_5_88: (61.5, 88.0),
        ExportSize.SIZE_62_88: (62.0, 88.0),
        ExportSize.POKER_SIZE: (63.5, 88.9),
    }

    def __init__(self, export_params: Dict[str, Any], workspace_manager: 'WorkspaceManager'):
        """
        初始化导出助手。

        :param system_config: 系统级别的默认配置 (字典)。
        :param export_params: 本次导出任务的特定参数 (字典)，会覆盖系统配置。
        """
        # 合并配置，export_params 优先
        self.workspace_manager: WorkspaceManager = workspace_manager
        config = export_params

        # --- 解析和验证参数 ---

        # 导出格式
        self.format: ExportFormat = self._parse_enum(config.get("format", "PNG"), ExportFormat, "格式")

        # 导出质量 (仅JPG有效)
        self.quality: int = int(config.get("quality", 95))
        if not (0 <= self.quality <= 100):
            raise ValueError("导出质量 (quality) 必须在 0 到 100 之间。")

        # 导出规格
        self.size: ExportSize = self._parse_enum(config.get("size", ExportSize.POKER_SIZE.value), ExportSize, "规格")

        # DPI
        self.dpi: int = int(config.get("dpi", 300))
        if self.dpi <= 0:
            raise ValueError("DPI 必须是正数。")

        # 出血规格
        # 支持传入数字或枚举值字符串
        bleed_value = config.get("bleed", 0)
        if isinstance(bleed_value, (int, float)):
            self.bleed: ExportBleed = self._parse_enum(int(bleed_value), ExportBleed, "出血")
        else:
            self.bleed: ExportBleed = self._parse_enum(bleed_value, ExportBleed, "出血")

        # 出血模式
        self.bleed_mode: BleedMode = self._parse_enum(config.get("bleed_mode", "裁剪"), BleedMode, "出血模式")

        # 出血模型
        self.bleed_model: BleedModel = self._parse_enum(config.get("bleed_model", "镜像出血"), BleedModel, "出血模型")

        # 图片参数 (饱和度/亮度/伽马)
        self.saturation: float = float(config.get("saturation", 1.0))
        self.brightness: float = float(config.get("brightness", 1.0))
        self.gamma: float = float(config.get("gamma", 1.0))

        # 预计算最终的像素尺寸
        self.pixel_width, self.pixel_height = self.calculate_pixel_dimensions(self.dpi, self.bleed, self.size)

        # 创建出血客户端
        self.lama_cleaner = LamaCleaner(
            base_url=self.workspace_manager.config.get('lama_baseurl', 'http://localhost:8080'),
        )
        # 字体缓存：缓存已加载的字体对象，避免重复加载
        self._font_cache: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}

    def _parse_enum(self, value: Any, enum_class: Type[T], param_name: str) -> T:
        """一个通用的帮助函数，用于将输入值转换为指定的枚举类型。"""
        try:
            # 尝试按值匹配
            if isinstance(value, enum_class):
                return value
            return enum_class(value)
        except ValueError:
            # 如果按值匹配失败，尝试按名称匹配 (例如 "PNG" -> ExportFormat.PNG)
            try:
                if isinstance(value, str):
                    return enum_class[value.upper()]
            except KeyError:
                pass  # 忽略错误，统一在下面抛出

            valid_options = ", ".join([f"'{e.value}'" for e in enum_class])
            raise ValueError(f"无效的参数 '{param_name}': '{value}'。有效选项为: {valid_options}")

    def calculate_pixel_dimensions(
            self,
            dpi: int = 300,
            bleed: ExportBleed = ExportBleed.TWO_MM,
            size=ExportSize.SIZE_61_88
    ) -> Tuple[int, int]:
        """
        根据规格、出血和DPI计算最终导出的像素尺寸。

        :return: 一个包含 (宽度, 高度) 的元组，单位为像素。
        """
        # 1. 获取基础物理尺寸 (mm)
        base_width_mm, base_height_mm = self.SPECIFICATIONS[size]

        # 2. 加上出血尺寸 (出血是加在四周的，所以总宽高各增加 2 * bleed)
        bleed_mm = bleed.value
        total_width_mm = base_width_mm + (2 * bleed_mm)
        total_height_mm = base_height_mm + (2 * bleed_mm)

        # 3. 将毫米转换为英寸
        total_width_inch = total_width_mm / self.MM_PER_INCH
        total_height_inch = total_height_mm / self.MM_PER_INCH

        # 4. 根据DPI计算像素值，并四舍五入为整数
        pixel_width = round(total_width_inch * dpi)
        pixel_height = round(total_height_inch * dpi)

        return pixel_width, pixel_height

    def get_export_settings(self) -> Dict[str, Any]:
        """
        获取一个包含所有处理过的导出参数的字典，方便传递给其他函数。
        """
        settings = {
            "format": self.format.value,
            "dpi": self.dpi,
            "pixel_dimensions": (self.pixel_width, self.pixel_height),
            "image_adjustments": {
                "saturation": self.saturation,
                "brightness": self.brightness,
                "gamma": self.gamma,
            },
            "bleed_mm": self.bleed.value,
            "bleed_mode": self.bleed_mode.value,
            "bleed_model": self.bleed_model.value,
            "spec_name": self.size.value,
        }
        if self.format == ExportFormat.JPG:
            settings["quality"] = self.quality

        return settings

    def __str__(self) -> str:
        """提供一个易于阅读的字符串表示形式，方便调试。"""
        summary = (
            f"--- 导出设置 ---\n"
            f"格式: {self.format.value}\n"
        )
        if self.format == ExportFormat.JPG:
            summary += f"质量: {self.quality}\n"

        summary += (
            f"规格: {self.size.value}\n"
            f"DPI: {self.dpi}\n"
            f"出血: {self.bleed.value}mm\n"
            f"出血模式: {self.bleed_mode.value}\n"
            f"出血模型: {self.bleed_model.value}\n"
            f"最终像素尺寸: {self.pixel_width}px × {self.pixel_height}px\n"
            f"图像调整:\n"
            f"  - 饱和度: {self.saturation}\n"
            f"  - 亮度: {self.brightness}\n"
            f"  - 伽马: {self.gamma}\n"
            f"-----------------\n"
        )
        return summary

    def _call_lama_cleaner(self, image: Image, target_width: int, target_height: int) -> Image.Image:
        if self.bleed_model == BleedModel.LAMA:
            return self.lama_cleaner.outpaint_extend(
                original_image=image,
                target_width=target_width,
                target_height=target_height
            )
        else:
            # 镜像
            return self.lama_cleaner.outpaint_mirror_extend(
                original_image=image,
                target_width=target_width,
                target_height=target_height
            )

    def _is_horizontal(self, image: Image.Image):
        return image.size[0] > image.size[1]

    def _standard_bleeding(self, card_json: dict, image: Image.Image):
        """标准出血"""
        # 先出血到标准出血尺寸768*1087
        if self._is_horizontal(image):
            card_map = self._call_lama_cleaner(image, 1087, 768)
        else:
            card_map = self._call_lama_cleaner(image, 768, 1087)

        ui_name = '出血_'
        card_type = card_json.get('type', '')
        if card_json.get('class', '') == '弱点':
            # 弱点卡
            ui_name += '弱点' + card_type
        elif card_type == '调查员卡背':
            ui_name += '调查员卡'
            ui_name += '-' + card_json.get('class', '')
            ui_name += '-卡背'
        else:
            # 其他卡牌
            ui_name += card_type
            if card_type in ['事件卡', '技能卡', '支援卡', '调查员卡']:
                ui_name += '-' + card_json.get('class', '')
        if card_type == '地点卡':
            ui_name += '-' + card_json.get('location_type', '已揭示')
        if card_type in ['支援卡', '地点卡'] and \
                card_json.get('subtitle', '') != '':
            ui_name += '-副标题'
        if card_type == '调查员卡':
            ui_name += '-底图'
        print(ui_name)
        ui = self.workspace_manager.creator.image_manager.get_image(ui_name)
        if ui:
            card_map.paste(ui, (0, 0, ui.size[0], ui.size[1]), ui)

        # 出血投入图标
        card_map = self._bleeding_submit_icon(card_json, card_map)
        return card_map

    def _bleeding_submit_icon(self, card_json: dict, card_map: Image.Image) -> Image:
        """出血投入图标"""
        submit_index = 0
        card_class = card_json.get('class', '')
        if 'submit_icon' in card_json and isinstance(card_json['submit_icon'], list):
            for icon in card_json['submit_icon']:
                img = self.workspace_manager.image_manager.get_image(f'投入-{card_class}-{icon}')
                # 将img裁剪为15*80
                img = img.crop((0, 0, 15, img.size[1]))
                card_map.paste(img, (0, 167 + submit_index * 80 + 19), img)
                submit_index += 1
        return card_map

    def _bleeding(self, card_json: dict, card_map: Image.Image) -> Image:
        # 判断为拉伸
        if self.bleed_mode == BleedMode.STRETCH:
            width, height = self.calculate_pixel_dimensions(bleed=self.bleed)
        else:
            width, height = self.calculate_pixel_dimensions(bleed=self.bleed, size=self.size)

        # if not (card_json.get('type') == '调查员卡' and card_json.get('is_back', False) is False):
        #     # 标准出血
        card_map = self._standard_bleeding(card_json, card_map)
        # 二次出血
        if self._is_horizontal(card_map):
            card_map = self._call_lama_cleaner(card_map, height, width)
        else:
            card_map = self._call_lama_cleaner(card_map, width, height)

        # 优化左上角
        if self.bleed_model == BleedModel.LAMA and self.bleed == ExportBleed.THREE_MM:
            # 创建一个优化mask，创建一个图片大小的白色背景图
            mask_optimized = Image.new("RGB", card_map.size, (0, 0, 0))
            # 创建画板
            draw = ImageDraw.Draw(mask_optimized)
            # 在左上角0,0的位置画一个30的黑色矩形
            draw.rectangle([0, 0, 30, 30], fill=(255, 255, 255))
            card_map = self.lama_cleaner.inpaint(
                image=card_map,
                mask=mask_optimized
            )

        return card_map

    def _load_font(self, font_name: str, font_size: int) -> ImageFont.FreeTypeFont:
        """
        加载字体，使用缓存机制避免重复加载相同的字体+大小组合

        :param font_name: 字体名称
        :param font_size: 字体大小
        :return: PIL字体对象
        """
        cache_key = (font_name, font_size)

        # 检查缓存中是否已存在
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        # 加载字体并缓存
        try:
            font = self.workspace_manager.creator.font_manager.get_font(font_name, font_size)
            self._font_cache[cache_key] = font
            return font
        except Exception as e:
            print(f"警告：无法加载字体 {font_name} 大小 {font_size}，使用默认字体: {e}")
            # 使用默认字体作为备选
            default_font = ImageFont.load_default()
            self._font_cache[cache_key] = default_font
            return default_font

    def _draw_text_layer(self, card_map: Image.Image, text_layer: list[dict[str, any]]) -> Image.Image:
        """
        绘制文字层
        :param card_map: 卡片图像
        :param text_layer: 文字层元数据列表
        """
        if not text_layer:
            return
        # 计算DPI缩放比例
        dpi_scale_factor = self.dpi / 300.0
        # 计算出血偏移量
        if self.bleed_mode == BleedMode.STRETCH:
            width, height = self.calculate_pixel_dimensions(bleed=self.bleed, size=ExportSize.SIZE_61_88)
            target_width, target_height = self.calculate_pixel_dimensions(self.dpi, self.bleed, ExportSize.SIZE_61_88)
        else:
            width, height = self.calculate_pixel_dimensions(bleed=self.bleed, size=self.size)
            target_width, target_height = self.pixel_width, self.pixel_height
        bleed_offset = (int((width - 739) / 2) * dpi_scale_factor, (int((height - 1049) / 2)) * dpi_scale_factor)
        # 先将card_map缩放到目标分辨率
        if self._is_horizontal(card_map):
            card_map = card_map.resize((target_height, target_width), Image.Resampling.LANCZOS)
        else:
            card_map = card_map.resize((target_width, target_height), Image.Resampling.LANCZOS)
        # 创建绘图对象
        draw = ImageDraw.Draw(card_map)

        if self._is_horizontal(card_map):
            bleed_offset_x = bleed_offset[1]
            bleed_offset_y = bleed_offset[0]
        else:
            bleed_offset_x = bleed_offset[0]
            bleed_offset_y = bleed_offset[1]
        # print(f"出血偏移量: ({bleed_offset_x}, {bleed_offset_y}), DPI缩放因子: {dpi_scale_factor}")
        for text_info in text_layer:
            try:
                # 提取文字信息并应用DPI缩放
                text = text_info.get('text', '')
                x = text_info.get('x', 0) * dpi_scale_factor + bleed_offset_x
                y = text_info.get('y', 0) * dpi_scale_factor + bleed_offset_y
                font_name = text_info.get('font', 'default')
                font_size = int(text_info.get('font_size', 12) * dpi_scale_factor)
                color = text_info.get('color', '#000000')
                border_width = int(text_info.get('border_width', 0) * dpi_scale_factor)
                border_color = text_info.get('border_color', '#FFFFFF')
                # 加载字体（使用缓存）
                font = self._load_font(font_name, font_size)
                # 绘制文字边框（如果有）
                if border_width > 0:
                    # 绘制边框：在主文字周围绘制多次偏移的文字
                    for dx in range(-border_width, border_width + 1):
                        for dy in range(-border_width, border_width + 1):
                            if dx != 0 or dy != 0:  # 不绘制中心位置
                                draw.text(
                                    (x + dx, y + dy),
                                    text,
                                    font=font,
                                    fill=border_color
                                )
                # 绘制主文字
                draw.text(
                    (x, y),
                    text,
                    font=font,
                    fill=color
                )
            except Exception as e:
                print(f"警告：绘制文字时发生错误 - 文字: '{text_info.get('text', 'N/A')}', 错误: {e}")
                continue
        if self.bleed_mode == BleedMode.STRETCH:
            if self._is_horizontal(card_map):
                card_map = card_map.resize((self.pixel_height, self.pixel_width), Image.Resampling.LANCZOS)
            else:
                card_map = card_map.resize((self.pixel_width, self.pixel_height), Image.Resampling.LANCZOS)
        return card_map

    def _clear_font_cache(self):
        """清除字体缓存"""
        self._font_cache.clear()

    @staticmethod
    def _apply_image_adjustments(image: Image.Image, saturation: float = 1.0,
                                 brightness: float = 1.0, gamma: float = 1.0) -> Image.Image:
        """
        应用饱和度、亮度和伽马调整到图像

        :param image: 输入的PIL图像
        :param saturation: 饱和度调整因子 (1.0表示不变)
        :param brightness: 亮度调整因子 (1.0表示不变)
        :param gamma: 伽马调整因子 (1.0表示不变)
        :return: 调整后的图像
        """
        # 应用饱和度调整
        if not math.isclose(saturation, 1.0):
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(saturation)

        # 应用亮度调整
        if not math.isclose(brightness, 1.0):
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)

        # 应用伽马调整
        if not math.isclose(gamma, 1.0):
            # 将图像转换为numpy数组进行处理
            img_array = np.array(image, dtype=np.float32) / 255.0
            # 应用伽马校正
            img_array = np.power(img_array, gamma)
            # 将值限制在0-1范围内
            img_array = np.clip(img_array, 0, 1)
            # 转换回0-255范围并创建图像
            img_array = (img_array * 255).astype(np.uint8)
            image = Image.fromarray(img_array)

        return image

    def export_card(self, card_path: str):
        """导出"""
        card_json = self.workspace_manager.get_file_content(card_path)
        if card_json is None:
            raise ValueError("无效的卡路径")
        card_json = json.loads(card_json)
        card_json = self.workspace_manager.creator._preprocessing_json(card_json)
        card_layer = self.workspace_manager.generate_card_image(card_json, False)
        card_map = self.workspace_manager.generate_card_image(card_json, True)
        card_map_image = self._bleeding(card_json, card_map.image)
        # 绘制文字层
        text_layer = card_layer.get_text_layer_metadata()
        card_map_image = self._draw_text_layer(card_map_image, text_layer)
        card_map_image = self._apply_image_adjustments(
            card_map_image,
            saturation=self.saturation,
            brightness=self.brightness,
            gamma=self.gamma
        )
        return card_map_image


if __name__ == "__main__":
    # 定义一个系统默认配置
    system_defaults = {
        "format": "PNG",
        "size": ExportSize.POKER_SIZE.value,  # "63.5mm × 88.9mm (2.5″ × 3.5″)"
        "dpi": 300,
        "bleed": 2,
        "bleed_mode": "拉伸",
        "bleed_model": "镜像出血",  # LaMa模型出血 镜像出血
        "quality": 90,  # 系统默认JPG质量
        "saturation": 1.0,
        "brightness": 1.0,
        "gamma": 1.0,
    }
    export_helper = ExportHelper(system_defaults, WorkspaceManager(r'D:\汉化文件夹\Test English Project'))
    print(export_helper)
    # 计算出血时间
    t = time.time()
    export_helper.export_card(r'5.card').show()
    # 输出耗时 单位秒 保留2位小数
    print(f'耗时: {round(time.time() - t, 2)}s')
    # export_helper = ExportHelper(system_defaults, WorkspaceManager(r'D:\汉化文件夹\测试工作空间'))
    # print(export_helper)
    # export_helper.export_card(r'支援卡.card')
