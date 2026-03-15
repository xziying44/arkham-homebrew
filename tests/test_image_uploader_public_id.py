import importlib.util
import sys
import types
import unittest
from pathlib import Path


def _load_image_uploader_module():
    module_name = "image_uploader_under_test"
    module_path = Path(__file__).resolve().parents[1] / "bin" / "image_uploader.py"

    cloudinary_module = types.ModuleType("cloudinary")
    cloudinary_module.config = lambda **kwargs: None
    cloudinary_module.Search = lambda: None
    uploader_module = types.ModuleType("cloudinary.uploader")
    uploader_module.upload = lambda *args, **kwargs: {"secure_url": "https://example.invalid/test.jpg"}
    cloudinary_module.uploader = uploader_module

    sys.modules.setdefault("cloudinary", cloudinary_module)
    sys.modules.setdefault("cloudinary.uploader", uploader_module)

    requests_module = types.ModuleType("requests")
    requests_module.post = lambda *args, **kwargs: None
    sys.modules.setdefault("requests", requests_module)

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ImageUploaderPublicIdTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_image_uploader_module()
        self.CloudinaryUploader = self.module.CloudinaryUploader
        self.SteamCloudUploader = getattr(self.module, "SteamCloudUploader", None)
        self.uploader = self.CloudinaryUploader({
            "cloud_name": "demo",
            "api_key": "demo",
            "api_secret": "demo",
            "folder": "AH_LCG"
        })

    def test_same_online_name_from_different_card_directories_get_different_public_ids(self):
        star = self.uploader._build_public_id("weak_front", "/tmp/ws/.cards/星熊/weak_front.jpg")
        platinum = self.uploader._build_public_id("weak_front", "/tmp/ws/.cards/白金/weak_front.jpg")

        self.assertNotEqual(star, platinum)
        self.assertIn("星熊", star)
        self.assertIn("白金", platinum)

    def test_public_id_keeps_online_name_suffix_for_card_face_files(self):
        public_id = self.uploader._build_public_id("weak_front", "/tmp/ws/.cards/星熊/weak_front.jpg")

        self.assertTrue(public_id.endswith("weak_front"))

    def test_create_uploader_supports_steam_host(self):
        uploader = self.module.create_uploader({
            "image_host": "steam",
            "steam_base_url": "http://127.0.0.1:5000",
            "workspace_path": "/tmp/ws",
        })

        self.assertEqual(type(uploader).__name__, "SteamCloudUploader")

    def test_steam_urls_keep_relative_path_to_avoid_name_collisions(self):
        uploader = self.module.create_uploader({
            "image_host": "steam",
            "steam_base_url": "http://127.0.0.1:5000",
            "workspace_path": "/tmp/ws",
        })

        star = uploader.upload_file("weak_front", "/tmp/ws/.cards/星熊/weak_front.jpg")
        platinum = uploader.upload_file("weak_front", "/tmp/ws/.cards/白金/weak_front.jpg")

        self.assertNotEqual(star, platinum)
        self.assertIn(".cards/%E6%98%9F%E7%86%8A/weak_front.jpg", star)
        self.assertIn(".cards/%E7%99%BD%E9%87%91/weak_front.jpg", platinum)


if __name__ == "__main__":
    unittest.main()
