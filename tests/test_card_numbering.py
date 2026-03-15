import importlib.util
import unittest
from pathlib import Path


def _load_card_numbering_module():
    module_name = "card_numbering_under_test"
    module_path = Path(__file__).resolve().parents[1] / "bin" / "card_numbering.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class CardNumberingTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_card_numbering_module()

    def _generate_plan(self, cards):
        return self.module.generate_numbering_plan(
            cards_data=cards,
            encounter_sets=[],
            no_encounter_position="before",
            start_number=1,
        )

    def test_player_cards_follow_fixed_class_order_and_level_sorting(self):
        cards = [
            {"filename": "guardian-2.card", "name": "守护二级", "type": "事件卡", "class": "守护者", "level": 2},
            {"filename": "seeker-0.card", "name": "探求零级", "type": "技能卡", "class": "探求者", "level": 0},
            {"filename": "guardian-0.card", "name": "守护零级", "type": "支援卡", "class": "守护者", "level": 0},
            {"filename": "mystic-1.card", "name": "潜修一级", "type": "事件卡", "class": "潜修者", "level": 1},
            {"filename": "rogue-0.card", "name": "流浪零级", "type": "事件卡", "class": "流浪者", "level": 0},
            {"filename": "survivor-3.card", "name": "生存三级", "type": "支援卡", "class": "生存者", "level": 3},
            {"filename": "multiclass-0.card", "name": "多职零级", "type": "事件卡", "class": "多职阶", "level": 0},
            {"filename": "neutral-0.card", "name": "中立零级", "type": "支援卡", "class": "中立", "level": 0},
        ]

        plan = self._generate_plan(cards)

        self.assertEqual(
            [item["filename"] for item in plan],
            [
                "guardian-0.card",
                "guardian-2.card",
                "seeker-0.card",
                "mystic-1.card",
                "rogue-0.card",
                "survivor-3.card",
                "multiclass-0.card",
                "neutral-0.card",
            ],
        )

    def test_investigator_is_followed_by_signature_cards(self):
        cards = [
            {
                "filename": "zoey.card",
                "name": "柔伊",
                "type": "调查员",
                "class": "守护者",
                "tts_config": {
                    "version": "v2",
                    "signatures": [
                        {"path": "sig-weapon.card", "count": 1},
                        {"path": "sig-weakness.card", "count": 1},
                        {"path": "sig-location.card", "count": 1},
                    ],
                },
            },
            {"filename": "sig-weapon.card", "name": "十字架", "type": "支援卡", "class": "守护者", "level": 0},
            {"filename": "sig-location.card", "name": "隐秘小巷", "type": "地点卡", "class": "弱点", "level": -1},
            {"filename": "sig-weakness.card", "name": "猎物", "type": "诡计卡", "class": "弱点", "level": -1},
            {"filename": "guardian-other.card", "name": "守护泛用卡", "type": "事件卡", "class": "守护者", "level": 0},
        ]

        plan = self._generate_plan(cards)

        self.assertEqual(
            [item["filename"] for item in plan[:5]],
            [
                "zoey.card",
                "sig-weapon.card",
                "sig-location.card",
                "sig-weakness.card",
                "guardian-other.card",
            ],
        )

    def test_large_art_signature_cards_use_their_base_type_priority(self):
        cards = [
            {
                "filename": "platinum/ins.card",
                "name": "白金",
                "type": "调查员",
                "class": "守护者",
                "tts_config": {
                    "version": "v2",
                    "signatures": [
                        {"path": "platinum/weak.card", "count": 1},
                        {"path": "platinum/asset.card", "count": 1},
                    ],
                },
            },
            {
                "filename": "platinum/weak.card",
                "name": "厌烦",
                "type": "诡计卡",
                "class": "弱点",
                "level": -1,
            },
            {
                "filename": "platinum/asset.card",
                "name": "天马视域",
                "type": "大画-支援卡",
                "class": "守护者",
                "level": 0,
            },
        ]

        plan = self._generate_plan(cards)

        self.assertEqual(
            [item["filename"] for item in plan],
            [
                "platinum/ins.card",
                "platinum/asset.card",
                "platinum/weak.card",
            ],
        )

    def test_bonded_cards_follow_parent_card(self):
        cards = [
            {
                "filename": "tome.card",
                "name": "古卷",
                "type": "支援卡",
                "class": "探求者",
                "level": 2,
                "id": "tome-base",
            },
            {
                "filename": "secret.card",
                "name": "秘语",
                "type": "事件卡",
                "class": "探求者",
                "level": 0,
                "bonded_to": "tome-base",
            },
            {
                "filename": "other.card",
                "name": "别的探求者卡",
                "type": "支援卡",
                "class": "探求者",
                "level": 3,
            },
        ]

        plan = self._generate_plan(cards)

        self.assertEqual(
            [item["filename"] for item in plan],
            ["tome.card", "secret.card", "other.card"],
        )

    def test_investigator_mini_cards_are_ignored_during_numbering(self):
        cards = [
            {"filename": "mini.card", "name": "柔伊小卡", "type": "调查员小卡", "class": "守护者"},
            {"filename": "guardian.card", "name": "守护卡", "type": "事件卡", "class": "守护者", "level": 0},
        ]

        plan = self._generate_plan(cards)

        self.assertEqual([item["filename"] for item in plan], ["guardian.card"])


if __name__ == "__main__":
    unittest.main()
