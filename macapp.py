# app.py - 完整版本
import os
import sys
import threading
import time
from pathlib import Path

if not hasattr(sys, '_MEIPASS'):
    if getattr(sys, 'frozen', False):
        # py2app 打包后可执行文件路径
        exe_path = Path(sys.executable)
        resources_path = exe_path.parent.parent / 'Resources'
        # 将 _MEIPASS 注入 sys 模块
        sys._MEIPASS = str(resources_path)
        print(f"注入 sys._MEIPASS = {sys._MEIPASS}")
    else:
        # 开发环境下，可以设置为当前脚本目录
        sys._MEIPASS = str(Path(__file__).parent.resolve())
        print(f"开发环境注入._MEIPASS = {sys._MEIPASS}")
else:
    print(f"已有 sys._MEIPASS = {sys._MEIPASS}")


def get_resource_path(relative_path=''):
    """获取资源文件的绝对路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的路径
        base_path = Path(sys._MEIPASS)
    else:
        # 开发模式
        base_path = Path(__file__).parent

    if relative_path:
        return str(base_path / relative_path)
    return str(base_path)


# 设置环境变量和工作目录
if getattr(sys, 'frozen', False):
    resource_path = get_resource_path()
    os.chdir(resource_path)

    # 设置环境变量供 Flask 使用
    os.environ['RESOURCE_PATH'] = resource_path

    # 添加到 Python 路径
    sys.path.insert(0, resource_path)
    sys.path.insert(0, get_resource_path('bin'))
    sys.path.insert(0, get_resource_path('export_helper'))
    sys.path.insert(0, get_resource_path('rich_text_render'))

    print(f"资源路径: {resource_path}")
    print(f"当前目录: {os.getcwd()}")
    print(f"Python 路径: {sys.path[:3]}")

# 导入 Flask 应用
from server import app
import webview

app.window=None
def start_flask():
    """启动 Flask 服务器"""
    try:
        print("启动 Flask 服务器...")
        app.run(host='127.0.0.1', port=5091, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"Flask 启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # 等待 Flask 启动
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)

    # 创建并启动 webview 窗口
    print("创建窗口...")
    window = webview.create_window(
        '阿卡姆印牌姬-V2.9-beta-6',
        'http://127.0.0.1:5091',
        width=1600,
        height=800
    )
    app.window=window

    print("启动 webview...")
    webview.start()
