import argparse
import os

import webview

# ... (你原来的 argparse 代码，无需改动)
parser = argparse.ArgumentParser(description="阿卡姆印牌姬-V2.5 启动器")
parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help='以调试模式运行，显示开发者工具并保留控制台窗口。'
)
# 添加 mode 参数
parser.add_argument(
    '-m', '--mode',
    type=str,
    default='normal',  # 设置默认值
    choices=['normal', 'check'],  # 可选的模式（根据你的需求调整）
    help='设置运行模式 (normal/advanced/simple)'
)
args = parser.parse_args()
DEBUG_MODE = args.debug
IMAGE_MODE = args.mode
os.environ['APP_MODE'] = args.mode

from server import app

# 【关键】为 Flask app 附加一个全局变量，用于判断运行模式
# 默认为 None，表示非 pywebview 环境
app.window = None

if __name__ == '__main__':
    # 创建一个 pywebview 窗口
    window = webview.create_window(
        "阿卡姆印牌姬-V2.8.2 by.小小银同学",
        app,
        width=1500,
        height=800,
        resizable=True,
        maximized=True
    )

    # 【★★★ 新增代码 ★★★】
    # 将 window 实例附加到 app 对象上
    # 这样在 server.py 中就可以通过 app.window 访问它了
    app.window = window

    webview.start(debug=DEBUG_MODE)
