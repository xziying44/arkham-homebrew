[app]

# 应用名称（显示名称）
title = Arkham Card Maker

# 包名（必须是唯一的，格式：域名反写）
package.name = arkhamcardmaker

# 包的域名
package.domain = cn.xziying

# 主入口文件
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt,ico,css,js,html,ttf,otf,woff,woff2

# 版本号
version = 2.8.4

# 依赖包
requirements = python3,flask,pywebview,pillow,reportlab,requests,pydantic,httpx,jinja2,werkzeug,bottle,click,cffi,pycparser

# 要包含的数据文件和文件夹
source.include_patterns = fonts/*,images/*,static/*,prompt/*,cardback/*,*.ico

# 要排除的文件
source.exclude_patterns = venv/*,*.pyc,*.pyo,*.spec,build/*,dist/*,__pycache__/*

# Android 权限
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android API 版本
android.api = 33
android.minapi = 21
android.ndk = 25b

# 图标（如果有的话，建议准备 512x512 的 PNG）
icon.filename = favicon.png

# 方向（landscape, portrait, sensor）
orientation = landscape

# 全屏模式
fullscreen = 0

# Android 架构
android.archs = arm64-v8a,armeabi-v7a

# 启用 Android 服务（如果需要后台服务）
#services = NAME:service.py

# 引导程序
android.bootstrap = sdl2

# 白名单
android.whitelist = lib-dynload/termios.so

# Android 添加 Java 类（如果需要）
#android.add_src =

# p4a 目录（可选）
#p4a.source_dir =

# 额外的 p4a 参数
#p4a.extra_args =

# 日志级别
log_level = 2

# 警告模式
warn_on_root = 1

[buildozer]

# 日志级别 (0 = error only, 1 = info, 2 = debug)
log_level = 2

# 警告忽略
warn_on_root = 1
