# main.py - 修复 WebViewClient 问题
import os
import sys
import threading
import time

# 设置 Android 环境标识
os.environ['ANDROID_ARGUMENT'] = '1'
os.environ['APP_MODE'] = 'normal'

# 导入 Flask 应用
from server import app

# Android 必要的导入
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.logger import Logger
from kivy.clock import Clock
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path
from android import activity
from jnius import autoclass, cast

# Java 类导入
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')
Environment = autoclass('android.os.Environment')
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
WebSettings = autoclass('android.webkit.WebSettings')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')

# 请求必要的权限
Logger.info("Android: 请求权限...")
request_permissions([
    Permission.READ_EXTERNAL_STORAGE,
    Permission.WRITE_EXTERNAL_STORAGE,
    Permission.INTERNET,
    Permission.ACCESS_NETWORK_STATE
])


class AndroidWebView(Widget):
    """Android WebView Widget"""

    def __init__(self, url='http://127.0.0.1:5000', **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.webview = None
        self._setup_webview()

    def _setup_webview(self):
        try:
            activity = PythonActivity.mActivity
            activity.runOnUiThread(lambda: self._create_webview(activity))
        except Exception as e:
            Logger.error(f"Android WebView: 设置失败 - {e}")

    def _create_webview(self, activity):
        try:
            Logger.info("Android WebView: 开始创建...")

            # 创建 WebView
            self.webview = WebView(activity)

            # 获取 Settings
            settings = self.webview.getSettings()

            # 基本设置
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setAllowFileAccess(True)
            settings.setDatabaseEnabled(True)

            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW)

            # 视口和缩放设置
            settings.setUseWideViewPort(True)
            settings.setLoadWithOverviewMode(True)
            settings.setSupportZoom(False)
            settings.setBuiltInZoomControls(False)

            # 缓存设置
            settings.setCacheMode(WebSettings.LOAD_DEFAULT)
            settings.setAppCacheEnabled(True)

            Logger.info("Android WebView: Settings 配置完成")

            # 使用默认的 WebViewClient
            web_client = WebViewClient()
            self.webview.setWebViewClient(web_client)

            Logger.info("Android WebView: WebViewClient 设置完成")

            # 直接设置为 Activity 的内容视图（最简单的方法）
            activity.setContentView(self.webview)

            Logger.info("Android WebView: 视图设置完成")

            # 加载 URL
            self.webview.loadUrl(self.url)
            Logger.info(f"Android WebView: 开始加载 - {self.url}")

        except Exception as e:
            Logger.error(f"Android WebView: 创建失败 - {e}")
            import traceback
            Logger.error(traceback.format_exc())

    def reload(self):
        """重新加载页面"""
        if self.webview:
            PythonActivity.mActivity.runOnUiThread(lambda: self.webview.reload())

    def go_back(self):
        """返回上一页"""
        if self.webview:
            PythonActivity.mActivity.runOnUiThread(lambda: self.webview.goBack())

    def can_go_back(self):
        """是否可以返回"""
        return self.webview.canGoBack() if self.webview else False


class AndroidDirectoryPicker:
    """Android 目录选择器"""
    REQUEST_CODE = 42

    def __init__(self):
        self.callback = None
        activity.bind(on_activity_result=self.on_activity_result)

    def pick_directory(self, callback):
        """打开目录选择对话框"""
        self.callback = callback
        try:
            Logger.info("Android: 打开目录选择对话框...")
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
            currentActivity.startActivityForResult(intent, self.REQUEST_CODE)
        except Exception as e:
            Logger.error(f"Android: 打开目录选择器失败: {e}")
            if self.callback:
                self.callback(None)

    def on_activity_result(self, request_code, result_code, data):
        """处理 Activity 返回结果"""
        if request_code != self.REQUEST_CODE:
            return

        Activity = autoclass('android.app.Activity')
        if result_code == Activity.RESULT_OK and data:
            try:
                uri = data.getData()
                Logger.info(f"Android: 选中的 URI: {uri.toString()}")

                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                contentResolver = currentActivity.getContentResolver()
                flags = (Intent.FLAG_GRANT_READ_URI_PERMISSION |
                         Intent.FLAG_GRANT_WRITE_URI_PERMISSION)

                try:
                    contentResolver.takePersistableUriPermission(uri, flags)
                    Logger.info("Android: 已获取持久化权限")
                except Exception as e:
                    Logger.warning(f"Android: 获取持久化权限失败: {e}")

                real_path = self.get_real_path_from_uri(uri)
                Logger.info(f"Android: 转换后的路径: {real_path}")

                if self.callback:
                    self.callback(real_path)

            except Exception as e:
                Logger.error(f"Android: 处理选择结果失败: {e}")
                if self.callback:
                    self.callback(None)
        else:
            Logger.info("Android: 用户取消了选择")
            if self.callback:
                self.callback(None)

    def get_real_path_from_uri(self, uri):
        """将 content:// URI 转换为真实文件路径"""
        try:
            uri_string = uri.toString()

            if "primary:" in uri_string:
                path_parts = uri_string.split("primary:")
                if len(path_parts) > 1:
                    relative_path = path_parts[1]
                    relative_path = relative_path.replace("%3A", "/").replace("%2F", "/")
                    storage_path = Environment.getExternalStorageDirectory().getAbsolutePath()

                    if relative_path:
                        full_path = os.path.join(storage_path, relative_path)
                    else:
                        full_path = storage_path

                    return full_path

            return primary_external_storage_path()

        except Exception as e:
            Logger.error(f"Android: URI 转换失败: {e}")
            return primary_external_storage_path()


class ArkhamCardMakerApp(App):
    """阿卡姆印牌姬 Android 应用"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.flask_thread = None
        self.directory_picker = AndroidDirectoryPicker()
        self.webview_widget = None
        app.android_directory_picker = self.directory_picker

    def build(self):
        """构建应用界面"""
        Logger.info("Android: 构建应用界面...")
        self.start_flask_server()
        Clock.schedule_once(self.load_webview, 2)
        return Widget()

    def start_flask_server(self):
        """在后台线程启动 Flask 服务器"""

        def run_flask():
            try:
                Logger.info("Android: 启动 Flask 服务器...")
                app.run(
                    host='127.0.0.1',
                    port=5000,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                Logger.error(f"Android: Flask 启动失败: {e}")

        self.flask_thread = threading.Thread(target=run_flask, daemon=True)
        self.flask_thread.start()
        Logger.info("Android: Flask 线程已启动")

    def load_webview(self, dt):
        """加载 WebView"""
        try:
            Logger.info("Android: 加载 WebView...")
            self.webview_widget = AndroidWebView(url='http://127.0.0.1:5000')
            Logger.info("Android: WebView 创建成功")
        except Exception as e:
            Logger.error(f"Android: WebView 加载失败: {e}")
            import traceback
            Logger.error(traceback.format_exc())

    def on_pause(self):
        """应用暂停"""
        Logger.info("Android: 应用暂停")
        return True

    def on_resume(self):
        """应用恢复"""
        Logger.info("Android: 应用恢复")

    def on_stop(self):
        """应用停止"""
        Logger.info("Android: 应用停止")


def main():
    """主入口函数"""
    Logger.info("=" * 60)
    Logger.info("阿卡姆印牌姬 - Android 版本 2.9.9")
    Logger.info("=" * 60)

    try:
        ArkhamCardMakerApp().run()
    except Exception as e:
        Logger.error(f"应用启动失败: {e}")
        import traceback
        Logger.error(traceback.format_exc())


if __name__ == '__main__':
    main()
