# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# 收集隐藏导入
hidden_imports = [
    'Flask',
    'pywebview',
    'Jinja2',
    'werkzeug',
    'requests',
    'httpx',
    'PIL',
    'numpy',
    'cloudinary',
    'psutil',
    'webview.platforms.cocoa',
    'objc',
    'Foundation',
    'AppKit',
    'WebKit',
]

# 数据文件
datas = [
    ('fonts', 'fonts'),
    ('images', 'images'),
    ('static', 'static'),
    ('prompt', 'prompt'),
    ('cardback', 'cardback'),
    ('templates', 'templates'),
]

# 收集 pywebview 相关数据
datas += collect_data_files('webview')

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
    target_arch='universal2',  # 支持 Intel 和 Apple Silicon
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
    bundle_identifier='com.arkham.cardmaker',
    version='2.9.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '2.9.0',
        'CFBundleVersion': '2.9.0',
        'NSHumanReadableCopyright': '© 2024 xziying',
        'LSMinimumSystemVersion': '10.13.0',
        'NSRequiresAquaSystemAppearance': 'False',
        'NSAppleEventsUsageDescription': 'This app needs to control other applications.',
    },
)
