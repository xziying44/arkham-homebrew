import json
import os
import time
from typing import List, Dict, Any


class QuickStart:
    """快速开始类，负责目录选择和最近记录管理"""

    def __init__(self, config_file: str = "recent_directories.json"):
        self.config_file = config_file
        self.max_records = 20

    def _load_recent_records(self) -> List[Dict[str, Any]]:
        """加载最近打开的目录记录"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载最近记录失败: {e}")
        return []

    def _save_recent_records(self, records: List[Dict[str, Any]]):
        """保存最近打开的目录记录"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存最近记录失败: {e}")

    def add_recent_directory(self, directory_path: str) -> bool:
        """添加最近打开的目录"""
        try:
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return False

            records = self._load_recent_records()

            # 检查是否已存在，如果存在则移除旧记录
            records = [r for r in records if r.get('path') != directory_path]

            # 添加新记录到开头
            new_record = {
                'path': directory_path,
                'name': os.path.basename(directory_path) or directory_path,
                'timestamp': int(time.time()),
                'formatted_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            }

            records.insert(0, new_record)

            # 保持最多20条记录
            if len(records) > self.max_records:
                records = records[:self.max_records]

            self._save_recent_records(records)
            return True

        except Exception as e:
            print(f"添加最近目录失败: {e}")
            return False

    def get_recent_directories(self) -> List[Dict[str, Any]]:
        """获取最近打开的目录列表"""
        records = self._load_recent_records()

        # 验证目录是否仍然存在，移除不存在的记录
        valid_records = []
        for record in records:
            if os.path.exists(record.get('path', '')):
                valid_records.append(record)

        # 如果有无效记录被移除，保存更新后的列表
        if len(valid_records) != len(records):
            self._save_recent_records(valid_records)

        return valid_records

    def remove_recent_directory(self, directory_path: str) -> bool:
        """移除指定的最近目录记录"""
        try:
            records = self._load_recent_records()
            original_length = len(records)
            records = [r for r in records if r.get('path') != directory_path]

            if len(records) != original_length:
                self._save_recent_records(records)
                return True
            return False
        except Exception as e:
            print(f"移除最近目录失败: {e}")
            return False

    def clear_recent_directories(self) -> bool:
        """清空所有最近目录记录"""
        try:
            self._save_recent_records([])
            return True
        except Exception as e:
            print(f"清空最近目录失败: {e}")
            return False
