# -*- coding: utf-8 -*-
import os

# 应用名称
app_name = "Arkham Card Maker"

# DMG 卷标名称（由构建脚本动态设置，包含架构信息）
volume_name = "Arkham Card Maker"

# 应用路径
app_path = os.path.join("dist", app_name + ".app")

# 卷标图标
badge_icon = "favicon.icns"

# DMG 背景（可选，当前未使用）
background = None

# 窗口设置（位置 + 大小）
# 对应 create-dmg: --window-pos 200 120 --window-size 800 400
window_rect = ((200, 120), (800, 400))

# 图标大小（对应 create-dmg: --icon-size 100）
icon_size = 100

# 文字大小
text_size = 12

# 图标位置
# 对应 create-dmg: --icon "Arkham Card Maker.app" 200 190
#                  --app-drop-link 600 185
icon_locations = {
    app_name + '.app': (200, 190),
    'Applications': (600, 185)
}

# 符号链接（对应 create-dmg: --app-drop-link）
symlinks = {
    'Applications': '/Applications'
}

# 格式设置
format = 'UDBZ'  # 压缩格式（Universal Disk Image BZip2）
size = None      # 自动计算大小

# 文件配置
files = [app_path]

# 视图选项（对应 create-dmg: --hide-extension）
show_icon_preview = False
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
sidebar_width = 180

# 排列选项
arrange_by = None
grid_offset = (0, 0)
grid_spacing = 100
scroll_position = (0, 0)
label_pos = 'bottom'
icon_view_options = 'auto'

# 许可协议（可选）
license = None
