import os
from flaskwebgui import FlaskUI, browser_path_dispacher, OPERATING_SYSTEM
from server import *


def find_edge_or_chrome():
    """查找 Edge 或 Chrome 浏览器"""
    import platform
    system = platform.system().lower()

    browsers = {
        'windows': [
            # Edge paths
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            # Chrome paths
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ],
        'darwin': [
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ],
        'linux': [
            "/usr/bin/microsoft-edge", "/usr/bin/microsoft-edge-stable",
            "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium-browser"
        ]
    }

    for path in browsers.get(system, []):
        if os.path.exists(path):
            return path
    return None


if __name__ == '__main__':
    # 首先使用程序自带的浏览器查找方法
    try:
        default_browser_path = browser_path_dispacher.get(OPERATING_SYSTEM)()
        print(f"程序自带查找结果: {default_browser_path}")

        # 检查路径是否有效
        if default_browser_path and os.path.exists(default_browser_path):
            browser_path = default_browser_path
            print(f"使用程序自带方法找到的浏览器: {browser_path}")
        else:
            # 使用备用查找方法
            print("程序自带方法无效，使用备用查找...")
            browser_path = find_edge_or_chrome()
            if browser_path:
                print(f"备用方法找到浏览器: {browser_path}")
            else:
                print("备用方法也未找到浏览器，将使用系统默认")
                browser_path = None
    except Exception as e:
        print(f"程序自带查找方法出错: {e}")
        browser_path = find_edge_or_chrome()

    # 创建并运行 FlaskUI
    if browser_path:
        FlaskUI(app=app, server="flask", width=1500, height=800, browser_path=browser_path).run()
    else:
        FlaskUI(app=app, server="flask", width=1500, height=800).run()
