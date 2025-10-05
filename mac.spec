# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('fonts', 'fonts'),
        ('images', 'images'),
        ('static', 'static'),
        ('prompt', 'prompt'),
        ('cardback', 'cardback'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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
    icon='favicon.icns',  # macOS 使用 .icns 格式图标
    bundle_identifier='cn.xziying.arkhamcardmaker',  # 修改为你的应用标识符
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '2.8.4',
        'CFBundleVersion': '1',
    },
)

# 如果安装了 dmgbuild
import os
if os.system('which dmgbuild') == 0:
    os.system('dmgbuild -s dmg_settings.py "Arkham Card Maker" "dist/Arkham-Card-Maker.dmg"')