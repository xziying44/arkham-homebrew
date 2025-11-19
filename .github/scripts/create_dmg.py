#!/usr/bin/env python3
"""
DMG 创建脚本
用于在 GitHub Actions 中创建 macOS DMG 安装包
"""
import sys
import os
import argparse


def create_dmg(dmg_filename: str, volume_name: str):
    """
    创建 DMG 文件

    Args:
        dmg_filename: 输出的 DMG 文件名
        volume_name: DMG 卷标名称
    """
    try:
        import dmgbuild

        # 获取 dmg_settings.py 的绝对路径（与此脚本在同一目录）
        script_dir = os.path.dirname(os.path.abspath(__file__))
        settings_file = os.path.join(script_dir, 'dmg_settings.py')

        print(f"Building DMG with volume name: {volume_name}")
        print(f"Output file: {dmg_filename}")
        print(f"Settings file: {settings_file}")

        dmgbuild.build_dmg(
            filename=dmg_filename,
            volume_name=volume_name,
            settings_file=settings_file
        )

        print(f"✅ DMG created successfully: {dmg_filename}")
        return 0

    except Exception as e:
        print(f"❌ DMG creation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def main():
    parser = argparse.ArgumentParser(description='Create DMG package for macOS')
    parser.add_argument('--output', '-o', required=True, help='Output DMG filename')
    parser.add_argument('--volume-name', '-v', required=True, help='DMG volume name')

    args = parser.parse_args()

    exit_code = create_dmg(args.output, args.volume_name)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
