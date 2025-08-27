# setup.py
import os
from setuptools import setup

# --- 全局变量 ---
APP_NAME = "阿卡姆印牌姬"
APP_VERSION = "2.5"
APP_SCRIPT = 'app.py'  # 你的主入口 Python 文件

# --- py2app 配置 ---
OPTIONS = {
    'argv_emulation': True,  # 允许通过拖拽文件到 App 图标上打开
    'iconfile': 'favicon.icns',  # 你的 App 图标文件，需要是 .icns 格式
    'packages': ['webview', 'flask'],  # 强制包含一些可能被忽略的库
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleVersion': APP_VERSION,
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleIdentifier': 'cn.xziying.arkhamcardmaker',  # App 的唯一标识符，建议修改
        'NSHumanReadableCopyright': 'Copyright © 2025 by 小小银同学. All rights reserved.'
    }
}


# --- 数据文件 ---
# 自动查找 templates 和 static 文件夹下的所有文件
def find_data_files(source_dir):
    data_files = []
    for root, dirs, files in os.walk(source_dir):
        # 创建一个相对于源目录的文件列表
        file_list = [os.path.join(root, f) for f in files]
        # 目标目录是相对于 app 包的 Contents/Resources/
        # 我们希望保持原来的目录结构，比如 'templates/index.html'
        dest_dir = os.path.relpath(root, '.')
        data_files.append((dest_dir, file_list))
    return data_files


# 将 templates 和 static 文件夹打包进去
DATA_FILES = find_data_files('fonts') + find_data_files('images') + find_data_files('static') + \
             find_data_files('prompt') + find_data_files('cardback')

# --- setup 函数 ---
setup(
    app=[APP_SCRIPT],  # 主程序脚本
    name=APP_NAME,  # 应用名
    version=APP_VERSION,
    data_files=DATA_FILES,  # 需要包含的数据文件
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
