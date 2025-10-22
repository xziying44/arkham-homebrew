# app.py
import argparse
import io
import os
import sys
import subprocess
from pathlib import Path


# ==================== DLL 解锁功能 ====================
def unlock_dlls(force=False):
    """
    解锁 _internal 目录下的所有 DLL 文件（仅 Windows 平台）

    Args:
        force: 是否强制解锁（忽略标记文件）
    """
    # 仅在 Windows 平台且打包模式下执行
    if os.name != 'nt':  # 不是 Windows 平台
        return

    if not hasattr(sys, '_MEIPASS'):  # 不是打包模式
        return

    try:
        # 获取程序根目录
        if getattr(sys, 'frozen', False):
            app_root = Path(sys.executable).parent
        else:
            app_root = Path(__file__).parent

        # 检查标记文件
        marker_file = app_root / 'recent_directories.json'

        # 如果不是强制模式且标记文件存在，跳过解锁
        if not force and marker_file.exists():
            return

        # 获取 _internal 目录路径
        base_path = Path(sys._MEIPASS)

        # 查找所有 .dll 文件
        dll_files = list(base_path.rglob('*.dll'))

        if not dll_files:
            return

        # 构建 PowerShell 命令
        ps_command = f'''
        Get-ChildItem -Path "{base_path}" -Filter "*.dll" -Recurse | ForEach-Object {{
            try {{
                Unblock-File -Path $_.FullName -ErrorAction SilentlyContinue
            }} catch {{
                # 忽略错误
            }}
        }}
        '''

        # 执行 PowerShell 命令
        subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,  # Windows 特有标志
            timeout=30
        )

    except Exception:
        pass


# 检测是否在 Android 平台
IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ

# 解析命令行参数
if not IS_ANDROID:
    parser = argparse.ArgumentParser(description="阿卡姆印牌姬-启动器")
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='以调试模式运行，显示开发者工具并保留控制台窗口。'
    )
    parser.add_argument(
        '-m', '--mode',
        type=str,
        default='normal',
        choices=['normal', 'check'],
        help='设置运行模式 (normal/check)'
    )
    parser.add_argument(
        '--force-unlock',
        action='store_true',
        help='强制执行 DLL 解锁，忽略标记文件（仅 Windows）'
    )
    args = parser.parse_args()
    DEBUG_MODE = args.debug
    IMAGE_MODE = args.mode
    FORCE_UNLOCK = args.force_unlock
else:
    DEBUG_MODE = False
    IMAGE_MODE = 'normal'
    FORCE_UNLOCK = False

# 执行 DLL 解锁（仅 Windows 平台）
unlock_dlls(force=FORCE_UNLOCK)

# 在最开始处添加
if hasattr(sys, '_MEIPASS'):  # 打包模式
    sys.stdout = io.TextIOWrapper(
        open(os.devnull, 'wb'),
        encoding='utf-8',
        errors='ignore'
    )
    sys.stderr = sys.stdout

os.environ['APP_MODE'] = IMAGE_MODE

from server import app

app.window = None

if __name__ == '__main__':
    try:
        import webview

        window = webview.create_window(
            "阿卡姆印牌姬-V2.9-beta-7",
            app,
            width=1500,
            height=800,
            resizable=True,
            maximized=not IS_ANDROID
        )

        app.window = window
        webview.start(debug=DEBUG_MODE)

    except Exception as e:
        print(f"启动错误: {e}")
        if IS_ANDROID:
            app.run(host='0.0.0.0', port=5000, debug=DEBUG_MODE)
        else:
            raise
