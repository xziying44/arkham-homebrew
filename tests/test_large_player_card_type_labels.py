import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


class FakeFontManager:
    def __init__(self):
        self.lang = "zh"

    def get_font_text(self, text):
        return text


class FakeImageManager:
    def get_image(self, name):
        return {"name": name}


class FakeCard:
    instances = []

    def __init__(self, width, height, font_manager, image_manager, card_type, card_class):
        self.width = width
        self.height = height
        self.font_manager = font_manager
        self.image_manager = image_manager
        self.card_type = card_type
        self.card_class = card_class
        self.centered_text_calls = []
        FakeCard.instances.append(self)

    def paste_image(self, *args, **kwargs):
        return None

    def set_card_level(self, *args, **kwargs):
        return None

    def set_card_cost(self, *args, **kwargs):
        return None

    def draw_centered_text(self, position, text, *args, **kwargs):
        self.centered_text_calls.append((position, text))

    def draw_left_text(self, *args, **kwargs):
        return None

    def draw_text(self, *args, **kwargs):
        return None

    def draw_victory_points(self, *args, **kwargs):
        return None

    def add_submit_icon(self, *args, **kwargs):
        return None


def _load_create_card_module():
    module_name = "create_card_under_test"
    module_path = Path(__file__).resolve().parents[1] / "create_card.py"

    pil_module = types.ModuleType("PIL")
    pil_module.Image = types.SimpleNamespace(Image=type("Image", (), {}))
    pil_module.ImageEnhance = types.SimpleNamespace(Brightness=lambda image: image)
    sys.modules["PIL"] = pil_module

    resource_manager = types.ModuleType("ResourceManager")
    resource_manager.FontManager = type("FontManager", (), {})
    resource_manager.ImageManager = type("ImageManager", (), {})
    sys.modules["ResourceManager"] = resource_manager

    card_module = types.ModuleType("Card")
    card_module.Card = type("Card", (), {})
    sys.modules["Card"] = card_module

    card_adapter_module = types.ModuleType("card_cdapter")
    card_adapter_module.CardAdapter = type("CardAdapter", (), {})
    sys.modules["card_cdapter"] = card_adapter_module

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class LargePlayerCardTypeLabelTests(unittest.TestCase):
    def setUp(self):
        FakeCard.instances = []
        self.module = _load_create_card_module()
        self.creator = self.module.CardCreator(FakeFontManager(), FakeImageManager())

    def _build_card_data(self, card_type):
        return {
            "type": card_type,
            "class": "守护者",
            "name": "测试卡牌",
            "traits": ["法术"],
            "body": "测试效果",
            "flavor": "",
            "level": -1,
        }

    def _find_type_label(self, card):
        for position, text in card.centered_text_calls:
            if position in {(74, 134), (78, 134)}:
                return text
        self.fail("未找到左上角类型文字绘制调用")

    def test_create_skill_large_card_draws_skill_label(self):
        with mock.patch.object(self.module, "Card", FakeCard):
            self.creator.create_skill_large_card(self._build_card_data("大画-技能卡"))

        card = FakeCard.instances[-1]
        self.assertEqual(self._find_type_label(card), "技能")

    def test_create_event_large_card_keeps_event_label(self):
        with mock.patch.object(self.module, "Card", FakeCard):
            self.creator.create_event_large_card(self._build_card_data("大画-事件卡"))

        card = FakeCard.instances[-1]
        self.assertEqual(self._find_type_label(card), "事件")


if __name__ == "__main__":
    unittest.main()
