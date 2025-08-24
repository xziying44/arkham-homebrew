# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('fonts', 'fonts'),
        ('images', 'images'),
        ('static', 'static'),
        ('prompt', 'prompt'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ArkhamHomebrew',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.icns'  # Mac 使用 .icns 格式图标
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ArkhamHomebrew'
)

# 新增：创建 Mac .app 束文件
app = BUNDLE(
    coll,
    name='ArkhamHomebrew.app',
    icon='favicon.icns',  # 应用图标
    bundle_identifier='com.yourcompany.arkhamhomebrew',  # 修改为你的标识符
    version='1.0.0',  # 应用版本
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [],
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',  # 最低系统要求
        'NSRequiresAquaSystemAppearance': False,  # 支持暗色模式
    },
)
