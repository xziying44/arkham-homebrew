# setup.py - 完整版本
from setuptools import setup
import os
from pathlib import Path

APP = ['macapp.py']
DATA_FILES = []

# 1. 添加所有资源目录
resource_dirs = ['fonts', 'images', 'cardback', 'templates', 'static']
for dir_name in resource_dirs:
    if os.path.exists(dir_name):
        for root, dirs, files in os.walk(dir_name):
            if files:
                # 过滤掉 __pycache__ 和 .DS_Store
                files = [f for f in files if not f.startswith('.') and f != '__pycache__']
                if files:
                    DATA_FILES.append((root, [os.path.join(root, f) for f in files]))

# 2. 添加 Python 模块目录（作为数据文件）
module_dirs = ['bin', 'export_helper', 'rich_text_render']
for dir_name in module_dirs:
    if os.path.exists(dir_name):
        py_files = []
        for root, dirs, files in os.walk(dir_name):
            # 排除 __pycache__
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))

        if py_files:
            DATA_FILES.append((dir_name, py_files))

# 3. 添加 server.py（如果它在根目录）
if os.path.exists('server.py'):
    DATA_FILES.append(('.',
                       ['server.py', 'Card.py', 'card_cdapter.py', 'create_card.py', 'create_pdf.py', 'ExportHelper.py',
                        'ResourceManager.py', 'ArkhamCardBuilder.py']))

OPTIONS = {
    'argv_emulation': False,
    'site_packages': True,
    'iconfile': 'favicon.icns',  # 应用图标

    'arch': 'universal2',
    'packages': [
        # 核心依赖
        'flask',
        'webview',
        'jinja2',
        'werkzeug',
        'PIL',
        'requests',
        'urllib3',
        'certifi',

        # PyObjC 依赖
        'objc',
        'Foundation',
        'WebKit',

        # 其他依赖
        'numpy',
        'psutil',
        'pydantic',
        'httpx',
        'httpcore',
        'h11',
    ],

    'includes': [
        # 编码支持
        'encodings',
        'encodings.utf_8',
        'encodings.idna',

        # 确保包含所有自定义模块
        'Card',
        'card_cdapter',
        'create_card',
        'ExportHelper',
        'ResourceManager',
        'create_pdf',
        'server',

        # bin 目录模块
        'bin.card2arkhamdb',
        'bin.content_package_manager',
        'bin.deck_exporter',
        'bin.file_manager',
        'bin.gitHub_image',
        'bin.image_uploader',
        'bin.logger',
        'bin.tts_card_converter',
        'bin.workspace_manager',

        # export_helper 模块
        'export_helper.LamaCleaner',

        # rich_text_render 模块
        'rich_text_render.HtmlTextParser',
        'rich_text_render.RichTextRenderer',
        'rich_text_render.VirtualTextBox',
    ],

    'excludes': [
        'PyInstaller',
        'pyinstaller',
        'test',
        'tests',
        'pytest',
        'matplotlib',
        'scipy',
        'pandas',
        'tkinter',
        'setuptools',
        'distutils',
    ],

    'plist': {
        'CFBundleName': 'Arkham Card Maker',
        'CFBundleDisplayName': 'Arkham Card Maker',
        'CFBundleVersion': '2.9.5',
        'CFBundleShortVersionString': '2.9.5',
        'CFBundleIdentifier': 'cn.xziying.arkhamcardmaker',
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
        'CFBundleDocumentTypes': [],
        'LSArchitecturePriority': ['arm64', 'x86_64'],
    },

    'strip': False,  # 保留调试信息
    'optimize': 0,
}

setup(
    app=APP,
    name='Arkham Card Maker',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

# 如果安装了 dmgbuild
import os

# if os.system('which dmgbuild') == 0:
#     os.system('dmgbuild -s dmg_settings.py "Arkham Card Maker" "dist/Arkham-Card-Maker.dmg"')
