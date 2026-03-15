import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path


def _load_image_uploader_module():
    module_name = "bin.image_uploader"
    module_path = Path(__file__).resolve().parents[1] / "bin" / "image_uploader.py"

    cloudinary_module = types.ModuleType("cloudinary")
    cloudinary_module.config = lambda **kwargs: None
    cloudinary_module.Search = lambda: None
    uploader_module = types.ModuleType("cloudinary.uploader")
    uploader_module.upload = lambda *args, **kwargs: {"secure_url": "https://example.invalid/test.jpg"}
    cloudinary_module.uploader = uploader_module

    requests_module = types.ModuleType("requests")
    requests_module.post = lambda *args, **kwargs: None

    sys.modules["cloudinary"] = cloudinary_module
    sys.modules["cloudinary.uploader"] = uploader_module
    sys.modules["requests"] = requests_module

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module


def _load_server_module():
    module_name = "server_under_test"
    module_path = Path(__file__).resolve().parents[1] / "server.py"

    class FakeJsonResponse:
        def __init__(self, payload):
            self.payload = payload

        def get_json(self):
            return self.payload

    class FakeFlask:
        def __init__(self, name):
            self.name = name
            self.window = None

        def route(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

        def errorhandler(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    flask_module = types.ModuleType("flask")
    flask_module.Flask = FakeFlask
    flask_module.jsonify = lambda payload: FakeJsonResponse(payload)
    flask_module.request = types.SimpleNamespace(get_json=lambda: None, args={})
    flask_module.send_from_directory = lambda directory, filename, **kwargs: {
        "directory": directory,
        "filename": filename,
    }
    flask_module.Response = type("Response", (), {})
    sys.modules["flask"] = flask_module

    pil_module = types.ModuleType("PIL")
    pil_module.Image = types.SimpleNamespace(Image=type("Image", (), {}))
    sys.modules["PIL"] = pil_module

    bin_package = types.ModuleType("bin")
    bin_package.__path__ = []
    sys.modules["bin"] = bin_package

    config_directory_manager = types.ModuleType("bin.config_directory_manager")
    config_directory_manager.config_dir_manager = types.SimpleNamespace(
        get_global_config_dir=lambda: "/tmp",
        get_recent_directories_file_path=lambda: "/tmp/recent.json",
        get_user_font_dir=lambda: "",
    )
    sys.modules["bin.config_directory_manager"] = config_directory_manager

    file_manager = types.ModuleType("bin.file_manager")
    file_manager.QuickStart = lambda *args, **kwargs: types.SimpleNamespace(add_recent_directory=lambda *a, **k: None)
    sys.modules["bin.file_manager"] = file_manager

    github_image = types.ModuleType("bin.gitHub_image")
    github_image.GitHubImageHost = type("GitHubImageHost", (), {})
    sys.modules["bin.gitHub_image"] = github_image

    logger_module = types.ModuleType("bin.logger")
    logger_module.logger_manager = types.SimpleNamespace(
        info=lambda *args, **kwargs: None,
        warning=lambda *args, **kwargs: None,
        error=lambda *args, **kwargs: None,
        exception=lambda *args, **kwargs: None,
        debug=lambda *args, **kwargs: None,
    )
    sys.modules["bin.logger"] = logger_module

    workspace_manager_module = types.ModuleType("bin.workspace_manager")
    workspace_manager_module.WorkspaceManager = type("WorkspaceManager", (), {})
    workspace_manager_module.ScanProgressTracker = lambda *args, **kwargs: object()
    sys.modules["bin.workspace_manager"] = workspace_manager_module

    tts_script_generator = types.ModuleType("bin.tts_script_generator")
    tts_script_generator.TtsScriptGenerator = type("TtsScriptGenerator", (), {})
    sys.modules["bin.tts_script_generator"] = tts_script_generator

    resource_manager = types.ModuleType("ResourceManager")
    resource_manager.get_resource_path = lambda path: path
    resource_manager.load_filename_mapping = lambda: {}
    sys.modules["ResourceManager"] = resource_manager

    _load_image_uploader_module()

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class SteamCloudRoutesTests(unittest.TestCase):
    def setUp(self):
        self.server = _load_server_module()

    def _build_workspace(self, workspace_path: str):
        class FakeWorkspace:
            def __init__(self, base_path: str):
                self.workspace_path = base_path

            def get_config(self):
                return {
                    "image_host": "steam",
                    "steam_base_url": "http://127.0.0.1:5000",
                    "workspace_path": self.workspace_path,
                }

            def _is_path_in_workspace(self, path: str):
                target = Path(path)
                if not target.is_absolute():
                    target = Path(self.workspace_path) / path
                try:
                    target.resolve().relative_to(Path(self.workspace_path).resolve())
                    return True
                except ValueError:
                    return False

            def _get_absolute_path(self, path: str):
                target = Path(path)
                if target.is_absolute():
                    return str(target)
                return str(Path(self.workspace_path) / path)

        return FakeWorkspace(workspace_path)

    def _unwrap_response(self, response):
        if isinstance(response, tuple):
            payload, status = response
        else:
            payload, status = response, 200

        if hasattr(payload, "get_json"):
            return payload.get_json(), status
        return payload, status

    def test_image_host_upload_accepts_steam(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cards_dir = Path(tmpdir) / ".cards" / "白金"
            cards_dir.mkdir(parents=True)
            image_path = cards_dir / "asset_front.jpg"
            image_path.write_bytes(b"test-image")

            self.server.current_workspace = self._build_workspace(tmpdir)
            self.server.request.get_json = lambda: {
                "image_path": str(image_path),
                "host_type": "steam",
                "online_name": "asset_front",
            }

            response = self.server.upload_to_image_host()
            payload, status = self._unwrap_response(response)

            self.assertEqual(status, 200)
            self.assertEqual(payload["code"], 0)
            self.assertIn("/api/image-host/steam/.cards/", payload["data"]["url"])

    def test_image_host_check_accepts_steam(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / ".cards" / "白金" / "asset_front.jpg"
            image_path.parent.mkdir(parents=True)
            image_path.write_bytes(b"test-image")

            self.server.current_workspace = self._build_workspace(tmpdir)
            self.server.request.get_json = lambda: {
                "online_name": str(image_path),
                "host_type": "steam",
            }

            response = self.server.check_image_exists()
            payload, status = self._unwrap_response(response)

            self.assertEqual(status, 200)
            self.assertEqual(payload["code"], 0)

    def test_steam_route_rejects_path_outside_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            outside_file = Path(tmpdir).parent / "outside.jpg"
            outside_file.write_bytes(b"test-image")

            self.server.current_workspace = self._build_workspace(tmpdir)

            response = self.server.serve_steam_cloud_image("../outside.jpg")
            payload, status = self._unwrap_response(response)

            self.assertIn(status, {400, 403, 404})


if __name__ == "__main__":
    unittest.main()
