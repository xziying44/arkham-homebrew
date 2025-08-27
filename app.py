import webview
import argparse  # 1. 导入 argparse 模块
from server import app  # 假设你的 Flask app 实例在 server.py 文件中

# 2. 创建一个命令行参数解析器
parser = argparse.ArgumentParser(description="阿卡姆印牌姬-V2.5 启动器")
parser.add_argument(
    '-d', '--debug',
    action='store_true',  # 当出现 --debug 参数时，这个值就为 True
    help='以调试模式运行，显示开发者工具并保留控制台窗口。'
)
args = parser.parse_args()

# args.debug 现在是一个布尔值 (True 或 False)
# 如果你运行 `python app.py --debug`，它就是 True
# 如果你运行 `python app.py`，它就是 False
DEBUG_MODE = args.debug

if __name__ == '__main__':
    # 创建一个 pywebview 窗口
    window = webview.create_window(
        "阿卡姆印牌姬-V2.5 by.小小银同学",
        app,
        width=1500,
        height=800,
        resizable=True,
        maximized=True
    )

    # 3. 使用解析出来的参数来决定 debug 的值
    # 这样，只有在命令行提供了 --debug 参数时，pywebview 的调试工具才会开启
    webview.start(debug=DEBUG_MODE)
