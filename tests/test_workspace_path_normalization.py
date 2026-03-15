import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path


def _load_workspace_manager_module():
    module_name = "workspace_manager_under_test"
    module_path = Path(__file__).resolve().parents[1] / "bin" / "workspace_manager.py"

    pil_module = types.ModuleType("PIL")
    pil_image_module = types.SimpleNamespace(Image=type("Image", (), {}))
    pil_module.Image = pil_image_module
    sys.modules.setdefault("PIL", pil_module)

    resource_manager = types.ModuleType("ResourceManager")
    resource_manager.FontManager = type("FontManager", (), {})
    resource_manager.ImageManager = type("ImageManager", (), {})
    sys.modules.setdefault("ResourceManager", resource_manager)

    create_card = types.ModuleType("create_card")
    create_card.CardCreator = type("CardCreator", (), {})
    sys.modules.setdefault("create_card", create_card)

    card_module = types.ModuleType("Card")
    card_module.Card = type("Card", (), {})
    sys.modules.setdefault("Card", card_module)

    bin_package = types.ModuleType("bin")
    bin_package.__path__ = []
    sys.modules.setdefault("bin", bin_package)

    config_directory_manager = types.ModuleType("bin.config_directory_manager")
    config_directory_manager.config_dir_manager = types.SimpleNamespace(
        get_user_font_dir=lambda: ""
    )
    sys.modules.setdefault("bin.config_directory_manager", config_directory_manager)

    deck_exporter = types.ModuleType("bin.deck_exporter")
    deck_exporter.DeckExporter = type("DeckExporter", (), {})
    sys.modules.setdefault("bin.deck_exporter", deck_exporter)

    logger_module = types.ModuleType("bin.logger")
    logger_module.logger_manager = types.SimpleNamespace(
        info=lambda *args, **kwargs: None,
        warning=lambda *args, **kwargs: None,
        error=lambda *args, **kwargs: None,
        exception=lambda *args, **kwargs: None,
        debug=lambda *args, **kwargs: None,
    )
    sys.modules.setdefault("bin.logger", logger_module)

    tts_card_converter = types.ModuleType("bin.tts_card_converter")
    tts_card_converter.TTSCardConverter = type("TTSCardConverter", (), {})
    sys.modules.setdefault("bin.tts_card_converter", tts_card_converter)

    content_package_manager = types.ModuleType("bin.content_package_manager")
    content_package_manager.ContentPackageManager = type("ContentPackageManager", (), {})
    sys.modules.setdefault("bin.content_package_manager", content_package_manager)

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _load_tts_script_generator_module():
    module_name = "tts_script_generator_under_test"
    module_path = Path(__file__).resolve().parents[1] / "bin" / "tts_script_generator.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class WorkspacePathNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.workspace_module = _load_workspace_manager_module()
        self.WorkspaceManager = self.workspace_module.WorkspaceManager
        self.tts_module = _load_tts_script_generator_module()
        self.TtsScriptGenerator = self.tts_module.TtsScriptGenerator

    def _build_workspace_manager(self, workspace_path: str):
        manager = object.__new__(self.WorkspaceManager)
        manager.workspace_path = workspace_path
        return manager

    def test_get_absolute_path_supports_windows_relative_separator(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = self._build_workspace_manager(tmpdir)

            actual = manager._get_absolute_path(r"凯尔希\ins.card")
            expected = os.path.join(tmpdir, "凯尔希", "ins.card")

            self.assertEqual(actual, expected)

    def test_is_path_in_workspace_accepts_windows_relative_separator(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = self._build_workspace_manager(tmpdir)

            self.assertTrue(manager._is_path_in_workspace(r"凯尔希\ins.card"))

    def test_tts_script_generator_can_read_bound_card_with_windows_separator(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            card_dir = Path(tmpdir) / "凯尔希"
            card_dir.mkdir()
            card_path = card_dir / "ins.card"
            card_path.write_text(
                json.dumps({"name": "凯尔希", "type": "调查员"}, ensure_ascii=False),
                encoding="utf-8",
            )

            manager = self._build_workspace_manager(tmpdir)
            generator = self.TtsScriptGenerator(workspace_manager=manager)

            card_json = generator._read_card_json_by_path(r"凯尔希\ins.card")

            self.assertIsNotNone(card_json)
            self.assertEqual(card_json["name"], "凯尔希")


if __name__ == "__main__":
    unittest.main()
