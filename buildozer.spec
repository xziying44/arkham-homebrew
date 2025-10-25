[app]
# 应用信息
title = 阿卡姆印牌姬
package.name = arkhamcardmaker
package.domain = cn.xziying

# 源代码
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,ttf,otf,woff,woff2,ico,icns,html,css,js
# 2. 包含所有的资源和自定义Python模块目录
source.include_dirs = ., assets, fonts, images, cardback, templates, static, prompt, bin, export_helper, rich_text_render

# 排除文件
source.exclude_exts = spec,md
source.exclude_dirs = tests,venv,venv-android,__pycache__,.git,.github,build,dist
source.exclude_patterns = license,images/original/*,app.py,setup.py,dmg_settings.py,macapp.py,*.spec,*.md,requirements*.txt,README*

# 入口文件
source.main = main.py

# 版本
version = 2.9.9

# 依赖
requirements = python3,kivy==2.3.0,flask==2.2.5,pillow,requests,numpy,cloudinary,pydantic<2,android

# Android 配置
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,MANAGE_EXTERNAL_STORAGE

# ============ 新增：允许明文HTTP流量（用于本地Flask服务器）============
android.add_manifest_application_attributes = android:usesCleartextTraffic="true"
# ===================================================================

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
