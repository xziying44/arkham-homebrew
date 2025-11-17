#!/bin/bash
# Post-install script for arkham-card-maker

# 确保 .desktop 文件有正确的权限
chmod 644 /usr/share/applications/arkham-card-maker.desktop

# 更新桌面数据库以使应用图标立即显示
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi

# 更新图标缓存
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/pixmaps 2>/dev/null || true
fi

# 刷新应用菜单缓存（针对不同桌面环境）
if command -v xdg-desktop-menu >/dev/null 2>&1; then
    xdg-desktop-menu forceupdate 2>/dev/null || true
fi

exit 0
