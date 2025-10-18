import argparse
import io
import os
import sys

# 在最开始处添加
if hasattr(sys, '_MEIPASS'):  # 打包模式
    # 重定向 stdout 和 stderr 到空设备或日志文件
    sys.stdout = io.TextIOWrapper(
        open(os.devnull, 'wb'),
        encoding='utf-8',
        errors='ignore'
    )
    sys.stderr = sys.stdout

# 检测是否在 Android 平台
IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ

# Android 平台不支持某些参数解析
if not IS_ANDROID:
    parser = argparse.ArgumentParser(description="阿卡姆印牌姬-V2.8.4 启动器")
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
    args = parser.parse_args()
    DEBUG_MODE = args.debug
    IMAGE_MODE = args.mode
else:
    DEBUG_MODE = False
    IMAGE_MODE = 'normal'

os.environ['APP_MODE'] = IMAGE_MODE

from server import app

app.window = None

if __name__ == '__main__':
    try:
        import webview

        # 创建窗口
        window = webview.create_window(
            "阿卡姆印牌姬-V2.9-Bate",
            app,
            width=1500,
            height=800,
            resizable=True,
            maximized=not IS_ANDROID  # Android 不最大化
        )

        app.window = window
        webview.start(debug=DEBUG_MODE)

    except Exception as e:
        print(f"启动错误: {e}")
        # Android 上直接运行 Flask（备用方案）
        if IS_ANDROID:
            app.run(host='0.0.0.0', port=5000, debug=DEBUG_MODE)
        else:
            raise
