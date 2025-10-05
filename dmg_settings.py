# -*- coding: utf-8 -*-
import os

# 应用名称
app_name = "Arkham Card Maker"

# DMG 文件名
dmg_name = "Arkham-Card-Maker"

# 应用路径
app_path = os.path.join("dist", app_name + ".app")

# DMG 设置
files = [app_path]
symlinks = {'Applications': '/Applications'}
icon_locations = {
    app_name + '.app': (140, 120),
    'Applications': (500, 120)
}

# 背景和窗口设置
background = None  # 可以设置为背景图片路径
window_rect = ((100, 100), (640, 400))
icon_size = 128
text_size = 16
