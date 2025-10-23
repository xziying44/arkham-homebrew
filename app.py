# app.py
import argparse
import io
import os
import sys

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
            "阿卡姆印牌姬-V2.9-beta-8",
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
