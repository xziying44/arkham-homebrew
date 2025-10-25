# app_android.py - 完整版本，支持目录选择
import os
import sys
import threading
import time
from functools import partial

# 设置 Android 环境标识
os.environ['ANDROID_ARGUMENT'] = '1'
os.environ['APP_MODE'] = 'normal'

# 导入 Flask 应用
from server import app

# Android 必要的导入
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.logger import Logger
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path
from android import activity, mActivity
from jnius import autoclass, cast

# Java 类导入
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')
DocumentsContract = autoclass('android.provider.DocumentsContract')
Environment = autoclass('android.os.Environment')
ContentResolver = autoclass('android.content.ContentResolver')

# 请求必要的权限
Logger.info("Android: 请求权限...")
request_permissions([
    Permission.READ_EXTERNAL_STORAGE,
    Permission.WRITE_EXTERNAL_STORAGE,
    Permission.INTERNET,
    Permission.ACCESS_NETWORK_STATE
])


class AndroidDirectoryPicker:
    """Android 目录选择器"""

    REQUEST_CODE = 42

    def __init__(self):
        self.callback = None
        self.selected_path = None

        # 绑定 Activity 结果处理
        activity.bind(on_activity_result=self.on_activity_result)

    def pick_directory(self, callback):
        """
        打开目录选择对话框

        Args:
            callback: 回调函数，接收选中的目录路径 callback(path)
        """
        self.callback = callback

        try:
            Logger.info("Android: 打开目录选择对话框...")

            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)

            # 创建 Intent
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)

            # 设置初始目录（可选）
            # initial_uri = Uri.parse("content://com.android.externalstorage.documents/tree/primary:")
            # intent.putExtra(DocumentsContract.EXTRA_INITIAL_URI, initial_uri)

            # 启动选择器
            currentActivity.startActivityForResult(intent, self.REQUEST_CODE)

        except Exception as e:
            Logger.error(f"Android: 打开目录选择器失败: {e}")
            if self.callback:
                self.callback(None)

    def on_activity_result(self, request_code, result_code, data):
        """处理 Activity 返回结果"""
        Logger.info(f"Android: Activity 返回 - code={request_code}, result={result_code}")

        if request_code != self.REQUEST_CODE:
            return

        Activity = autoclass('android.app.Activity')

        if result_code == Activity.RESULT_OK and data:
            try:
                # 获取选中的 URI
                uri = data.getData()
                Logger.info(f"Android: 选中的 URI: {uri.toString()}")

                # 请求持久化权限
                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                contentResolver = currentActivity.getContentResolver()

                flags = (Intent.FLAG_GRANT_READ_URI_PERMISSION |
                         Intent.FLAG_GRANT_WRITE_URI_PERMISSION)

                try:
                    contentResolver.takePersistableUriPermission(uri, flags)
                    Logger.info("Android: 已获取持久化权限")
                except Exception as e:
                    Logger.warning(f"Android: 获取持久化权限失败: {e}")

                # 转换 URI 为真实路径
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
        """
        将 content:// URI 转换为真实文件路径

        Args:
            uri: Android URI 对象

        Returns:
            str: 真实文件路径
        """
        try:
            uri_string = uri.toString()
            Logger.info(f"Android: URI 字符串: {uri_string}")

            # 解析 URI
            if "primary:" in uri_string:
                # 主存储设备
                path_parts = uri_string.split("primary:")
                if len(path_parts) > 1:
                    relative_path = path_parts[1]
                    # 移除可能的 URL 编码
                    relative_path = relative_path.replace("%3A", "/").replace("%2F", "/")

                    # 获取外部存储根路径
                    storage_path = Environment.getExternalStorageDirectory().getAbsolutePath()

                    if relative_path:
                        full_path = os.path.join(storage_path, relative_path)
                    else:
                        full_path = storage_path

                    Logger.info(f"Android: 主存储路径: {full_path}")
                    return full_path

            # 如果无法解析，返回默认路径
            Logger.warning("Android: 无法解析 URI，使用默认路径")
            return primary_external_storage_path()

        except Exception as e:
            Logger.error(f"Android: URI 转换失败: {e}")
            return primary_external_storage_path()


class ArkhamCardMakerApp(App):
    """阿卡姆印牌姬 Android 应用"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.flask_thread = None
        self.flask_started = False
        self.directory_picker = AndroidDirectoryPicker()

        # 注册目录选择器到 Flask app
        app.android_directory_picker = self.directory_picker

    def build(self):
        """构建应用界面"""
        Logger.info("Android: 构建应用界面...")

        # 创建主布局
        layout = BoxLayout(orientation='vertical')

        # 启动 Flask 服务器
        self.start_flask_server()

        # 等待服务器启动
        loading_label = Label(
            text='正在启动服务器...',
            font_size='20sp',
            halign='center',
            valign='middle'
        )
        layout.add_widget(loading_label)

        # 延迟加载 WebView
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.load_webview(layout, loading_label), 3)

        return layout

    def start_flask_server(self):
        """在后台线程启动 Flask 服务器"""

        def run_flask():
            try:
                Logger.info("Android: 启动 Flask 服务器 (127.0.0.1:5000)...")
                app.run(
                    host='127.0.0.1',
                    port=5000,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                Logger.error(f"Android: Flask 服务器启动失败: {e}")

        self.flask_thread = threading.Thread(target=run_flask, daemon=True)
        self.flask_thread.start()
        self.flask_started = True
        Logger.info("Android: Flask 服务器线程已启动")

    def load_webview(self, layout, loading_label):
        """加载 WebView"""
        try:
            Logger.info("Android: 加载 WebView...")

            # 移除加载标签
            layout.remove_widget(loading_label)

            # 创建 WebView
            from kivy.uix.webview import WebView

            webview = WebView(
                url='http://127.0.0.1:5000',
                enable_javascript=True,
                enable_downloads=False
            )

            layout.add_widget(webview)
            Logger.info("Android: WebView 加载成功")

        except ImportError:
            Logger.warning("Android: WebView 不可用，使用备用方案...")
            self.open_in_browser(layout, loading_label)
        except Exception as e:
            Logger.error(f"Android: WebView 加载失败: {e}")
            error_label = Label(
                text=f'加载失败: {str(e)}\n\n请尝试在浏览器中打开:\nhttp://127.0.0.1:5000',
                font_size='16sp',
                halign='center',
                valign='middle'
            )
            layout.remove_widget(loading_label)
            layout.add_widget(error_label)

    def open_in_browser(self, layout, loading_label):
        """在系统浏览器中打开应用"""
        try:
            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setData(Uri.parse('http://127.0.0.1:5000'))

            currentActivity = PythonActivity.mActivity
            currentActivity.startActivity(intent)

            Logger.info("Android: 已在浏览器中打开应用")

            layout.remove_widget(loading_label)
            info_label = Label(
                text='应用已在浏览器中打开\n\n如果没有自动跳转，\n请手动访问:\nhttp://127.0.0.1:5000',
                font_size='18sp',
                halign='center',
                valign='middle'
            )
            layout.add_widget(info_label)

        except Exception as e:
            Logger.error(f"Android: 打开浏览器失败: {e}")
            layout.remove_widget(loading_label)
            error_label = Label(
                text=f'无法打开浏览器\n\n请手动访问:\nhttp://127.0.0.1:5000',
                font_size='18sp',
                halign='center',
                valign='middle'
            )
            layout.add_widget(error_label)

    def on_pause(self):
        """应用暂停时的处理"""
        Logger.info("Android: 应用暂停")
        return True

    def on_resume(self):
        """应用恢复时的处理"""
        Logger.info("Android: 应用恢复")

    def on_stop(self):
        """应用停止时的处理"""
        Logger.info("Android: 应用停止")


def main():
    """主入口函数"""
    Logger.info("=" * 60)
    Logger.info("阿卡姆印牌姬 - Android 版本")
    Logger.info("版本: 2.9.9")
    Logger.info("=" * 60)

    try:
        # 启动应用
        ArkhamCardMakerApp().run()

    except Exception as e:
        Logger.error(f"Android: 应用启动失败: {e}")
        import traceback
        Logger.error(traceback.format_exc())


if __name__ == '__main__':
    main()
