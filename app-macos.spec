# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集所有子模块
flask_submodules = collect_submodules('flask')
jinja2_submodules = collect_submodules('jinja2')
werkzeug_submodules = collect_submodules('werkzeug')
webview_submodules = collect_submodules('webview')
cv2_submodules = collect_submodules('cv2')

# 收集隐藏导入
hidden_imports = [
    # Flask 相关
    'flask',
    'flask.json',
    'flask.json.provider',
    'jinja2',
    'jinja2.ext',
    'werkzeug',
    'werkzeug.security',
    'werkzeug.routing',
    'click',
    'itsdangerous',
    'markupsafe',
    # PyWebView 相关
    'webview',
    'webview.window',
    'webview.menu',
    'webview.platforms.cocoa',
    # macOS 特定
    'objc',
    'Foundation',
    'AppKit',
    'WebKit',
    'Cocoa',
    # 其他依赖
    'requests',
    'httpx',
    'httpcore',
    'h11',
    'certifi',
    'urllib3',
    'PIL',
    'PIL._imaging',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'numpy',
    'psutil',
    'cloudinary',
    'pydantic',
    'pydantic_core',
] + flask_submodules + jinja2_submodules + werkzeug_submodules + webview_submodules + cv2_submodules

# 数据文件
datas = [
    ('fonts', 'fonts'),
    ('images', 'images'),
    ('static', 'static'),
    ('prompt', 'prompt'),
    ('cardback', 'cardback'),
    ('templates', 'templates'),
]

# 收集包的数据文件
datas += collect_data_files('webview')
datas += collect_data_files('certifi')
datas += collect_data_files('cloudinary')
datas += collect_data_files('cv2')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'pytest',
        'setuptools',
        'wheel',
        'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Arkham Card Maker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,  # 改为 None，自动检测当前架构
    codesign_identity=None,
    entitlements_file='entitlements.plist',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Arkham Card Maker',
)

app = BUNDLE(
    coll,
    name='Arkham Card Maker.app',
    icon='favicon.icns',
    bundle_identifier='cn.xziying.cardmaker',
    version='2.9.8',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '2.9.8',
        'CFBundleVersion': '2.9.8',
        'NSHumanReadableCopyright': '© 2024 xziying',
        'LSMinimumSystemVersion': '10.13.0',
        'NSRequiresAquaSystemAppearance': 'False',
        'NSAppleEventsUsageDescription': 'This app needs to control other applications.',
    },
)
