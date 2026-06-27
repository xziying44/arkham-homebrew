import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image

from ExportHelper import ExportHelper, ExportSize


class _FakeWorkspaceManager:
    """仅提供 ExportHelper 构造所需的最小依赖（config 字典）。"""

    def __init__(self):
        self.config = {"lama_baseurl": "http://localhost:8080"}


class CardBackDpiScalingTests(unittest.TestCase):
    """回归：卡背等无文字层的纯图片卡在 DPI>300 时未跟随正面尺寸。"""

    def _make_helper(self, dpi, bleed_mode="裁剪"):
        params = {
            "format": "PNG",
            "size": ExportSize.POKER_SIZE.value,
            "dpi": dpi,
            "bleed": 2,
            "bleed_mode": bleed_mode,
            "bleed_model": "镜像出血",
            "quality": 95,
        }
        return ExportHelper(params, _FakeWorkspaceManager())

    def _bleeding_intermediate(self, helper):
        """模拟 _bleeding 在无文字层卡背上的中间产物（按默认 300 DPI 计算的尺寸）。"""
        base_w, base_h = helper.calculate_pixel_dimensions(
            dpi=300, bleed=helper.bleed, size=helper.size
        )
        return Image.new("RGB", (base_w, base_h), (123, 200, 50))

    def test_crop_mode_imageonly_card_scales_to_dpi_dimensions(self):
        dpi = 600
        helper = self._make_helper(dpi, bleed_mode="裁剪")
        card_map = self._bleeding_intermediate(helper)

        # 卡背没有文字层：generate_card_image 直接塞图片，get_text_layer_metadata() 返回 None
        result = helper._draw_text_layer(card_map, None)

        self.assertEqual(
            result.size,
            (helper.pixel_width, helper.pixel_height),
            "裁剪模式下无文字层的卡背未缩放到目标 DPI 尺寸，导致与正面尺寸不一致",
        )

    def test_stretch_mode_imageonly_card_scales_to_dpi_dimensions(self):
        dpi = 600
        helper = self._make_helper(dpi, bleed_mode="拉伸")
        card_map = self._bleeding_intermediate(helper)

        result = helper._draw_text_layer(card_map, [])

        self.assertEqual(
            result.size,
            (helper.pixel_width, helper.pixel_height),
            "拉伸模式下无文字层的卡背未缩放到目标 DPI 尺寸，导致与正面尺寸不一致",
        )


if __name__ == "__main__":
    unittest.main()
