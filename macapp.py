# app.py - 完整的生命周期管理版本
import os
import sys
import threading
import time
from pathlib import Path
import signal

if not hasattr(sys, '_MEIPASS'):
    if getattr(sys, 'frozen', False):
        exe_path = Path(sys.executable)
        resources_path = exe_path.parent.parent / 'Resources'
        sys._MEIPASS = str(resources_path)
        print(f"注入 sys._MEIPASS = {sys._MEIPASS}")
    else:
        sys._MEIPASS = str(Path(__file__).parent.resolve())
        print(f"开发环境注入._MEIPASS = {sys._MEIPASS}")
else:
    print(f"已有 sys._MEIPASS = {sys._MEIPASS}")


def get_resource_path(relative_path=''):
    """获取资源文件的绝对路径"""
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    if relative_path:
        return str(base_path / relative_path)
    return str(base_path)


# 设置环境变量和工作目录
if getattr(sys, 'frozen', False):
    resource_path = get_resource_path()
    os.chdir(resource_path)
    os.environ['RESOURCE_PATH'] = resource_path

    sys.path.insert(0, resource_path)
    sys.path.insert(0, get_resource_path('bin'))
    sys.path.insert(0, get_resource_path('export_helper'))
    sys.path.insert(0, get_resource_path('rich_text_render'))

    print(f"资源路径: {resource_path}")
    print(f"当前目录: {os.getcwd()}")
    print(f"Python 路径: {sys.path[:3]}")

from server import app
import webview

app.window = None
flask_thread = None
shutdown_event = threading.Event()  # 添加关闭事件


def start_flask():
    """启动 Flask 服务器"""
    try:
        print("启动 Flask 服务器...")
        app.run(
            host='127.0.0.1',
            port=5091,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"Flask 启动失败: {e}")
        import traceback
        traceback.print_exc()


def wait_for_server(url='http://127.0.0.1:5091/', timeout=10):
    """等待服务器就绪"""
    import requests
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print(f"服务器已就绪: {url}")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)

    print(f"等待服务器超时: {timeout}秒")
    return False


def shutdown_flask():
    """关闭 Flask 服务器"""
    try:
        import requests
        print("正在关闭 Flask 服务器...")
        # 发送关闭请求到 Flask
        requests.post('http://127.0.0.1:5091/shutdown', timeout=1)
    except:
        pass


def on_closing():
    """窗口关闭事件处理"""
    print("窗口正在关闭...")
    shutdown_event.set()

    # 关闭 Flask
    shutdown_flask()

    # 强制退出
    print("程序退出")
    os._exit(0)


def signal_handler(signum, frame):
    """处理系统信号"""
    print(f"收到信号 {signum}，正在退出...")
    on_closing()


if __name__ == '__main__':
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 启动 Flask（使用 daemon）
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # 等待服务器真正就绪
    print("等待服务器启动...")
    if not wait_for_server():
        print("服务器启动失败，退出")
        sys.exit(1)

    # 额外延迟确保服务器稳定
    time.sleep(1)

    # 创建窗口
    print("创建窗口...")

    try:
        window = webview.create_window(
            '阿卡姆印牌姬-V2.9-beta-6',
            'http://127.0.0.1:5091',
            width=1600,
            height=800,
            resizable=True,
            fullscreen=False,
            min_size=(800, 600),
            confirm_close=False,
            background_color='#FFFFFF'
        )
        app.window = window

        # 绑定关闭事件
        window.events.closing += on_closing

        print("启动 webview...")
        webview.start(debug=False, http_server=False)

        # webview.start() 是阻塞的，执行到这里说明窗口已关闭
        print("Webview 已关闭")
        on_closing()

    except Exception as e:
        print(f"Webview 启动失败: {e}")
        import traceback

        traceback.print_exc()
        on_closing()
