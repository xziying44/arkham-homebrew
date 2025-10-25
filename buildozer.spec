[app]
# 应用信息
title = 阿卡姆印牌姬
package.name = arkhamcardmaker
package.domain = cn.xziying

# 源代码
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,ttf,otf,woff,woff2,ico,icns
source.include_patterns = assets/*,images/*,fonts/*,static/*,templates/*,prompt/*,cardback/*,bin/*

# 排除文件
source.exclude_exts = spec,md
source.exclude_dirs = tests,venv,venv-android,__pycache__,.git,.github,build,dist
source.exclude_patterns = license,images/original/*

# 入口文件
source.main = app_android.py

# 版本
version = 2.9.9

# 依赖
requirements = python3,kivy==2.3.0,flask==3.1.0,werkzeug==3.1.3,jinja2==3.1.5,click==8.1.8,markupsafe==3.0.2,itsdangerous==2.2.0,pillow==11.1.0,requests==2.32.5,urllib3==2.5.0,certifi==2025.1.31,charset-normalizer==3.4.3,idna==3.10,numpy==2.3.2,cloudinary==1.44.1,pydantic==2.10.6,pydantic_core==2.27.2,android

# Android 配置
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,MANAGE_EXTERNAL_STORAGE
# 添加 Android SDK 版本（需要支持 Storage Access Framework）
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

# 图标和启动画面（可选，需要准备对应图片）
icon.filename = favicon.png

# 方向
orientation = portrait

# 全屏
fullscreen = 0

# 应用主题
android.theme = @android:style/Theme.NoTitleBar

# 调试选项
# android.logcat_filters = *:S python:D

# 启用 AndroidX
android.enable_androidx = True

# Gradle 配置
android.gradle_dependencies =

# 其他选项
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
