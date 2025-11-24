import base64
import hashlib
import io
import json
import mimetypes
import os
import re
import sys
import threading
import time
import traceback
from typing import List, Dict, Any, Optional, Union, Tuple, TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from PIL import Image

from bin.config_directory_manager import config_dir_manager
from bin.deck_exporter import DeckExporter
from bin.logger import logger_manager
from bin.tts_card_converter import TTSCardConverter
from bin.content_package_manager import ContentPackageManager
from Card import Card

# 导入卡牌生成相关模块
try:
    from ResourceManager import FontManager, ImageManager
    from create_card import CardCreator

    CARD_GENERATION_AVAILABLE = True
except ImportError:
    CARD_GENERATION_AVAILABLE = False
    print("警告: 无法导入卡牌生成模块，卡牌生成功能将不可用")


# === 新增: 分层扫描架构核心类 ===

class CacheManager:
    """缓存管理器: 负责缓存验证与持久化(使用mtime验证)"""

    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.cache_dir = os.path.join(workspace_root, '.cache')
        self.cache_file = os.path.join(self.cache_dir, 'file_cache.json')
        self._cache = self._load_cache()
        self._lock = threading.Lock()

    def _load_cache(self) -> Dict:
        """加载缓存数据"""
        if not os.path.exists(self.cache_file):
            return {'files': {}}

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger_manager.warning(f"缓存加载失败: {e}")
            return {'files': {}}

    def get_cached_card_type(self, file_path: str) -> Optional[str]:
        """获取缓存的card_type(含mtime验证)"""
        rel_path = os.path.relpath(file_path, self.workspace_root)

        with self._lock:
            cached = self._cache['files'].get(rel_path)
            if not cached:
                return None

            # mtime验证
            try:
                current_mtime = os.stat(file_path).st_mtime
                if abs(current_mtime - cached.get('mtime', 0)) < 1e-6:
                    return cached.get('card_type')
            except OSError:
                pass

            return None

    def update_cache(self, file_path: str, card_type: Optional[str]):
        """更新缓存"""
        rel_path = os.path.relpath(file_path, self.workspace_root)

        try:
            mtime = os.stat(file_path).st_mtime

            with self._lock:
                self._cache['files'][rel_path] = {
                    'card_type': card_type,
                    'mtime': mtime
                }
        except OSError as e:
            logger_manager.warning(f"更新缓存失败 {file_path}: {e}")

    def save_cache(self):
        """持久化缓存到磁盘"""
        os.makedirs(self.cache_dir, exist_ok=True)

        with self._lock:
            try:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self._cache, f, indent=2)
            except Exception as e:
                logger_manager.error(f"缓存保存失败: {e}")

    def clear_cache(self):
        """清空缓存"""
        with self._lock:
            self._cache = {'files': {}}


class ScanProgressTracker:
    """扫描进度追踪器: 管理多个扫描任务(最多2个并发)"""

    # 错误码常量
    ERROR_PERMISSION_DENIED = 'PERMISSION_DENIED'
    ERROR_JSON_PARSE = 'JSON_PARSE_ERROR'
    ERROR_FILE_NOT_FOUND = 'FILE_NOT_FOUND'
    ERROR_FILE_TOO_LARGE = 'FILE_TOO_LARGE'
    ERROR_UNKNOWN = 'UNKNOWN_ERROR'

    def __init__(self):
        self._scans = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='workspace_scan')

    def start_scan(self, workspace_path: str, scanner: 'WorkspaceScanner') -> str:
        """启动扫描任务"""
        scan_id = f"scan_{int(time.time() * 1000)}"

        with self._lock:
            if len([s for s in self._scans.values() if s['status'] == 'scanning']) >= 2:
                raise RuntimeError("并发扫描数已达上限(最多2个)")

            # 预填充扫描队列（相对路径），用于可见优先重排
            try:
                initial_queue = scanner.collect_card_files()
            except Exception:
                initial_queue = []

            self._scans[scan_id] = {
                'status': 'scanning',
                'progress': {'total': 0, 'scanned': 0, 'percentage': 0.0},
                'data': [],
                'queue': initial_queue,  # 相对路径
                'error_count': 0
            }

        def progress_callback(update):
            with self._lock:
                if scan_id in self._scans:
                    scan = self._scans[scan_id]
                    scan['progress']['scanned'] = update.get('scanned', 0)
                    scan['progress']['total'] = update.get('total', 0)
                    scan['progress']['percentage'] = update.get('percentage', 0.0)
                    scan['data'].append(update.get('data', {}))

                    # 错误追踪
                    if update.get('data', {}).get('error'):
                        scan['error_count'] += 1
                        total = scan['progress']['total']
                        if total > 0 and (scan['error_count'] / total) > 0.1:
                            logger_manager.warning(
                                f"扫描 {scan_id} 错误率超过10%: {scan['error_count']}/{total}"
                            )

        def scan_complete():
            with self._lock:
                if scan_id in self._scans:
                    self._scans[scan_id]['status'] = 'completed'

        future = self._executor.submit(
            self._run_scan, scan_id, scanner, progress_callback, scan_complete
        )

        return scan_id

    def _run_scan(self, scan_id: str, scanner, progress_callback, complete_callback):
        """执行扫描任务（以共享队列为唯一数据源，支持优先级动态调整）"""
        try:
            # 读取总量
            with self._lock:
                scan = self._scans.get(scan_id)
                if not scan:
                    return
                total = len(scan.get('queue', []))
                scan['progress']['total'] = total

            scanned = 0
            while True:
                # 取下一项（受优先级调整影响）
                with self._lock:
                    scan = self._scans.get(scan_id)
                    if not scan:
                        break
                    if scan.get('cancelled'):
                        break
                    queue = scan.get('queue', [])
                    if not queue:
                        break
                    rel_path = queue.pop(0)

                abs_path = os.path.join(scanner.workspace_root, rel_path)
                result = scanner._extract_card_type_with_error(abs_path)
                if not result.get('error'):
                    scanner.cache_manager.update_cache(abs_path, result.get('card_type'))

                try:
                    stat_info = os.stat(abs_path)
                    mtime = stat_info.st_mtime
                    size = stat_info.st_size
                except OSError:
                    mtime = 0
                    size = 0

                scanned += 1
                level = min(5, rel_path.count(os.sep) + 1)
                progress_callback({
                    'data': {
                        'path': rel_path,
                        'card_type': result.get('card_type'),
                        'level': level,
                        'mtime': mtime,
                        'size': size,
                        'error': result.get('error')
                    },
                    'scanned': scanned,
                    'total': total,
                    'percentage': (scanned / total * 100) if total > 0 else 0
                })

                # 节流避免占用
                if scanned % 200 == 0:
                    time.sleep(0.02)

            # 扫描完成后持久化两套缓存
            try:
                scanner.cache_manager.save_cache()
            except Exception as e:
                logger_manager.warning(f"文件类型缓存保存失败: {e}")
            # 兼容旧缓存：尽量写入 WorkspaceManager 的 card_types.json
            try:
                # 使用 WorkspaceManager 的更新接口可能不可见，这里仅确保目录存在
                cache_dir = os.path.join(scanner.workspace_root, '.cache')
                os.makedirs(cache_dir, exist_ok=True)
            except Exception:
                pass

            complete_callback()
        except Exception as e:
            logger_manager.error(f"扫描失败: {e}", exc_info=True)

    def get_progress(self, scan_id: str) -> Dict:
        """获取扫描进度"""
        with self._lock:
            return self._scans.get(scan_id, {'error': 'Scan not found'})

    def cancel_scan(self, scan_id: str):
        with self._lock:
            if scan_id in self._scans:
                self._scans[scan_id]['cancelled'] = True
                self._scans[scan_id]['queue'] = []
                self._scans[scan_id]['status'] = 'cancelled'

    def cancel_all(self):
        with self._lock:
            for sid, scan in self._scans.items():
                scan['cancelled'] = True
                scan['queue'] = []
                scan['status'] = 'cancelled'

    def prioritize_visible_nodes(self, scan_id: str, visible_paths: List[str]):
        """调整扫描队列,优先处理可见节点"""
        with self._lock:
            if scan_id not in self._scans:
                return

            scan_data = self._scans[scan_id]
            scan_queue = scan_data.get('queue', [])

            # 统一路径分隔符为正斜杠，提升跨平台匹配准确性
            def norm(p: str) -> str:
                return p.replace('\\', '/').lstrip('./')
            normalized_queue = [norm(p) for p in scan_queue]
            normalized_visible = [norm(p) for p in visible_paths]

            # 收集可见路径下的所有文件
            priority_set = set()
            for visible_path in normalized_visible:
                for idx, file_path in enumerate(normalized_queue):
                    if file_path.startswith(visible_path):
                        priority_set.add(idx)

            # 将可见节点移到队列前端
            if priority_set:
                # 按原相对顺序重建：优先项 + 其他项
                prioritized = [scan_queue[i] for i in sorted(priority_set)]
                others = [p for j, p in enumerate(scan_queue) if j not in priority_set]
                scan_data['queue'] = prioritized + others

            logger_manager.info(f"优先扫描 {len(priority_set)} 个可见文件 (scan {scan_id})")


class WorkspaceScanner:
    """工作空间扫描器: 负责分层扫描逻辑"""

    # 最大JSON文件大小限制(5MB)
    MAX_JSON_SIZE = 5 * 1024 * 1024

    # 预编译正则表达式
    _TYPE_RE = re.compile(r'"type"\s*:\s*"([^"]+)"')

    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.cache_manager = CacheManager(workspace_root)

    def scan_structure(self, include_hidden: bool = False, include_card_type: bool = False) -> Dict:
        """快速扫描目录结构
        :param include_hidden: 是否包含隐藏文件
        :param include_card_type: 是否包含卡牌类型（将尽可能使用缓存，避免重新解析）
        """
        return self._build_tree_recursive(
            self.workspace_root,
            include_hidden=include_hidden,
            include_card_type=include_card_type
        )

    def scan_card_types_async(self, callback):
        """异步扫描card_type字段(广度优先分批)"""
        # 按层级分批扫描
        for level in range(1, 6):  # 最多扫描5层
            files = self._collect_json_files_by_level(self.workspace_root, level)
            total = len(files)

            for i, file_path in enumerate(files):
                result = self._extract_card_type_with_error(file_path)

                # 更新缓存
                if not result.get('error'):
                    self.cache_manager.update_cache(file_path, result.get('card_type'))

                # 获取文件元数据
                try:
                    stat_info = os.stat(file_path)
                    mtime = stat_info.st_mtime
                    size = stat_info.st_size
                except OSError:
                    mtime = 0
                    size = 0

                # 回调推送数据
                callback({
                    'data': {
                        'path': os.path.relpath(file_path, self.workspace_root),
                        'card_type': result.get('card_type'),
                        'level': level,
                        'mtime': mtime,
                        'size': size,
                        'error': result.get('error')
                    },
                    'scanned': i + 1,
                    'total': total,
                    'percentage': ((i + 1) / total * 100) if total > 0 else 0
                })

            # 批次推送(每200个文件短暂休眠，减少CPU抖动)
            if (i + 1) % 200 == 0:
                time.sleep(0.02)

            # 每层扫描完成后短暂休眠
            time.sleep(0.05)

        # 扫描完成后持久化缓存
        self.cache_manager.save_cache()

    def _build_tree_recursive(
        self,
        path: str,
        include_hidden: bool = False,
        include_card_type: bool = True,
        level: int = 1
    ) -> List[Dict[str, Any]]:
        """递归构建目录树(支持include_card_type参数)"""
        items = []

        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if not include_hidden and entry.name.startswith('.'):
                        continue

                    relative_path = os.path.relpath(entry.path, self.workspace_root)
                    item_key = f"{relative_path}_{int(time.time() * 1000000)}"

                    # 获取文件元数据(一次性stat调用)
                    try:
                        stat_info = entry.stat()
                        mtime = stat_info.st_mtime
                        size = stat_info.st_size
                    except OSError:
                        mtime = 0
                        size = 0

                    if entry.is_dir():
                        # 处理目录
                        children = self._build_tree_recursive(
                            entry.path,
                            include_hidden,
                            include_card_type,
                            level + 1
                        )
                        children = self._sort_items(children)

                        items.append({
                            'label': entry.name,
                            'key': item_key,
                            'type': 'directory',
                            'path': relative_path,
                            'level': level,
                            'mtime': mtime,
                            'size': 0,  # 目录大小设为0
                            'children': children
                        })

                    elif entry.is_file():
                        # 处理文件
                        file_type = self._get_file_type(entry.name)
                        item_info = {
                            'label': entry.name,
                            'key': item_key,
                            'type': file_type,
                            'path': relative_path,
                            'level': level,
                            'mtime': mtime,
                            'size': size
                        }

                        # 当文件类型为card时,提取card_type
                        if file_type == 'card':
                            if include_card_type:
                                # 尝试从缓存加载
                                cached = self.cache_manager.get_cached_card_type(entry.path)
                                if cached:
                                    item_info['card_type'] = cached
                                else:
                                    result = self._extract_card_type_with_error(entry.path)
                                    item_info['card_type'] = result.get('card_type')
                                    if result.get('error'):
                                        item_info['error'] = result['error']
                            else:
                                item_info['card_type'] = None

                        items.append(item_info)

        except PermissionError:
            logger_manager.warning(f"权限拒绝: {path}")
        except Exception as e:
            logger_manager.error(f"构建目录树失败 {path}: {e}")

        return self._sort_items(items)

    def collect_card_files(self) -> List[str]:
        """收集全部 .card 相对路径（广度层序同 _collect_json_files_by_level）"""
        files: List[str] = []
        for level in range(1, 6):
            abs_files = self._collect_json_files_by_level(self.workspace_root, level)
            for abs_path in abs_files:
                rel = os.path.relpath(abs_path, self.workspace_root)
                files.append(rel)
        return files

    def scan_card_types_async_with_queue(self, queue: List[str], callback):
        """按照给定队列顺序扫描（相对路径队列）"""
        total = len(queue)
        scanned = 0
        for rel_path in queue:
            abs_path = os.path.join(self.workspace_root, rel_path)
            result = self._extract_card_type_with_error(abs_path)

            # 更新缓存（仅当无错误时）
            if not result.get('error'):
                self.cache_manager.update_cache(abs_path, result.get('card_type'))

            # 元数据
            try:
                stat_info = os.stat(abs_path)
                mtime = stat_info.st_mtime
                size = stat_info.st_size
            except OSError:
                mtime = 0
                size = 0

            scanned += 1
            level = min(5, rel_path.count(os.sep) + 1)
            callback({
                'data': {
                    'path': rel_path,
                    'card_type': result.get('card_type'),
                    'level': level,
                    'mtime': mtime,
                    'size': size,
                    'error': result.get('error')
                },
                'scanned': scanned,
                'total': total,
                'percentage': (scanned / total * 100) if total > 0 else 0
            })

            # 适度让出执行权（每200个）
            if scanned % 200 == 0:
                time.sleep(0.02)

    def _collect_json_files_by_level(
        self,
        path: str,
        target_level: int,
        current_level: int = 1
    ) -> List[str]:
        """收集指定层级的JSON文件路径"""
        files = []
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        files.extend(self._collect_json_files_by_level(
                            entry.path,
                            target_level,
                            current_level + 1
                        ))
                    elif entry.name.endswith('.card') and current_level == target_level:
                        files.append(entry.path)
        except PermissionError:
            pass
        return files

    def _extract_card_type_with_error(self, file_path: str) -> Dict:
        """容错的card_type提取,返回结果或错误信息"""
        try:
            # 读取card_type(重试3次)
            for attempt in range(3):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        chunk = f.read(4096)
                    match = self._TYPE_RE.search(chunk)
                    if match:
                        return {
                            'card_type': match.group(1),
                            'error': None
                        }
                    return {'card_type': None, 'error': None}

                except json.JSONDecodeError as e:
                    if attempt < 2:
                        time.sleep(0.1)
                        continue
                    logger_manager.warning(f"JSON解析失败: {file_path}")
                    return {
                        'card_type': None,
                        'error': {
                            'code': ScanProgressTracker.ERROR_JSON_PARSE,
                            'message': f'JSON格式错误: {str(e)}'
                        }
                    }

        except PermissionError:
            return {
                'card_type': None,
                'error': {
                    'code': ScanProgressTracker.ERROR_PERMISSION_DENIED,
                    'message': '无权访问文件'
                }
            }

        except FileNotFoundError:
            return {
                'card_type': None,
                'error': {
                    'code': ScanProgressTracker.ERROR_FILE_NOT_FOUND,
                    'message': '文件已删除'
                }
            }

        except Exception as e:
            logger_manager.error(f"读取文件失败: {file_path} - {e}", exc_info=True)
            return {
                'card_type': None,
                'error': {
                    'code': ScanProgressTracker.ERROR_UNKNOWN,
                    'message': f'未知错误: {str(e)}'
                }
            }

    def _get_file_type(self, filename: str) -> str:
        """根据文件扩展名确定文件类型"""
        ext = os.path.splitext(filename)[1].lower()

        type_mapping = {
            '.card': 'card',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.gif': 'image',
            '.json': 'config',
            '.txt': 'text',
        }

        return type_mapping.get(ext, 'file')

    def _get_type_priority(self, item_type: str) -> int:
        """获取类型优先级"""
        type_priorities = {
            'directory': 0,
            'card': 1,
            'image': 2,
            'config': 3,
            'text': 4,
            'file': 7,
        }
        return type_priorities.get(item_type, 99)

    def _sort_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对文件和目录进行排序"""
        def sort_key(item):
            type_priority = self._get_type_priority(item.get('type', 'file'))
            name = item.get('label', '').lower()
            return (type_priority, name)

        return sorted(items, key=sort_key)


class WorkspaceManager:
    """工作空间管理类，负责文件和目录操作"""
    # 预编译正则表达式，提高性能
    _TYPE_RE = re.compile(r'"type"\s*:\s*"([^"]+)"')

    # 系统配置字段定义 - 这些字段会保存到全局配置文件中
    SYSTEM_CONFIG_FIELDS = [
        "github_token",  # GitHub访问令牌
        "github_repo",  # GitHub仓库名
        "github_branch",  # GitHub分支名
        "github_folder",  # GitHub文件夹
        "language",  # 界面语言
        "first_visit_completed",  # 首次访问是否完成
        # Cloudinary图床配置
        "cloud_name",  # Cloudinary云名称
        "api_key",  # Cloudinary API密钥
        "api_secret",  # Cloudinary API密钥
        "folder",  # Cloudinary自定义上传目录
        # ImgBB图床配置
        "imgbb_api_key",  # ImgBB API密钥
        "imgbb_expiration",  # ImgBB图片过期时间
        "advanced_export_params",  # 高级导出参数缓存
        "pnp_export_params",  # 内容包实体导出参数缓存
        # 可以在这里添加更多系统级配置字段
    ]

    # 工作空间配置字段定义 - 这些字段会保存到工作空间的config.json中
    WORKSPACE_CONFIG_FIELDS = [
        "encounter_groups_dir",  # 遭遇组目录
        "footer_copyright",  # 页脚版权信息
        "footer_icon_dir",  # 页脚图标目录
        "file_tree_bookmarks",  # 标签记录
        # 可以在这里添加更多工作空间级配置字段
    ]

    def __init__(self, workspace_path: str):
        if not os.path.exists(workspace_path):
            raise ValueError(f"工作目录不存在: {workspace_path}")
        if not os.path.isdir(workspace_path):
            raise ValueError(f"指定路径不是目录: {workspace_path}")

        self.workspace_path = os.path.abspath(workspace_path)

        # 初始化卡牌生成相关管理器
        if CARD_GENERATION_AVAILABLE:
            try:
                app_mode = os.environ.get('APP_MODE', 'normal')

                self.font_manager = FontManager()
                self.image_manager = ImageManager()
                self.font_manager.add_font_folder(config_dir_manager.get_user_font_dir())

                workspace_fonts_dir = os.path.join(self.workspace_path, 'fonts')
                if os.path.exists(workspace_fonts_dir) and os.path.isdir(workspace_fonts_dir):
                    self.font_manager.add_font_folder(workspace_fonts_dir)
                # 设置图片工作目录
                self.image_manager.set_working_directory(workspace_path)
                self.creator = CardCreator(
                    font_manager=self.font_manager,
                    image_manager=self.image_manager,
                    image_mode=0 if app_mode == 'normal' else 1
                )

            except Exception as e:
                print(f"初始化字体和图像管理器失败: {e}")
                self.font_manager = None
                self.image_manager = None
        else:
            self.font_manager = None
            self.image_manager = None

        self.config = self.get_config()
        # 初始化牌库导出器
        self.deck_exporter = DeckExporter(self)

        self._export_helper = None
        self.card_lock = threading.Lock()

        # 初始化缓存相关属性
        self._card_type_cache = {}
        self._cache_lock = threading.Lock()
        self._cache_file_path = os.path.join(self.workspace_path, '.cache', 'card_types.json')
        self._cache_modified = False

        # 加载缓存
        self._load_card_type_cache()

    def _load_card_type_cache(self):
        """加载卡牌类型缓存"""
        try:
            with self._cache_lock:
                if os.path.exists(self._cache_file_path):
                    with open(self._cache_file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                        self._card_type_cache = cache_data.get('card_types', {})
                        logger_manager.info(f"加载卡牌类型缓存: {len(self._card_type_cache)} 条记录")
                else:
                    # 首次运行：创建空文件，避免每次提示
                    self._card_type_cache = {}
                    os.makedirs(os.path.dirname(self._cache_file_path), exist_ok=True)
                    with open(self._cache_file_path, 'w', encoding='utf-8') as f:
                        json.dump({'card_types': {}, 'last_updated': time.time()}, f, ensure_ascii=False, indent=2)
                    logger_manager.info("未找到缓存文件，已创建空的卡牌类型缓存")
        except Exception as e:
            logger_manager.error(f"加载卡牌类型缓存失败: {e}")
            self._card_type_cache = {}

    def _save_card_type_cache(self):
        """保存卡牌类型缓存"""
        try:
            with self._cache_lock:
                if self._cache_modified:
                    # 确保缓存目录存在
                    cache_dir = os.path.dirname(self._cache_file_path)
                    os.makedirs(cache_dir, exist_ok=True)

                    cache_data = {
                        'card_types': self._card_type_cache,
                        'last_updated': time.time()
                    }

                    with open(self._cache_file_path, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)

                    self._cache_modified = False
                    logger_manager.info(f"保存卡牌类型缓存: {len(self._card_type_cache)} 条记录")
        except Exception as e:
            logger_manager.error(f"保存卡牌类型缓存失败: {e}")

    def _get_file_hash(self, file_path: str) -> str:
        """获取文件的哈希值，用于判断文件是否被修改"""
        try:
            # 使用文件大小和修改时间作为轻量级的哈希
            stat = os.stat(file_path)
            hash_data = f"{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(hash_data.encode()).hexdigest()
        except Exception:
            return ""

    def _update_card_type_cache(self, file_path: str, card_type: str):
        """更新卡牌类型缓存"""
        try:
            with self._cache_lock:
                relative_path = self._get_relative_path(file_path)
                file_hash = self._get_file_hash(file_path)

                self._card_type_cache[relative_path] = {
                    'type': card_type,
                    'hash': file_hash,
                    'last_accessed': time.time()
                }
                self._cache_modified = True
        except Exception as e:
            logger_manager.error(f"更新卡牌类型缓存失败: {e}")

    def _remove_from_cache(self, file_path: str):
        """从缓存中移除指定文件"""
        try:
            with self._cache_lock:
                relative_path = self._get_relative_path(file_path)
                if relative_path in self._card_type_cache:
                    del self._card_type_cache[relative_path]
                    self._cache_modified = True
        except Exception as e:
            logger_manager.error(f"从缓存中移除文件失败: {e}")

    def _remove_directory_from_cache(self, dir_path: str):
        """从缓存中移除指定目录下的所有卡牌文件"""
        try:
            with self._cache_lock:
                dir_relative_path = self._get_relative_path(dir_path)
                if not dir_relative_path.endswith('/'):
                    dir_relative_path += '/'

                # 找到所有在该目录下的卡牌文件
                to_remove = []
                for relative_path in self._card_type_cache:
                    if relative_path.startswith(dir_relative_path) and relative_path.endswith('.card'):
                        to_remove.append(relative_path)

                # 从缓存中移除
                for path in to_remove:
                    del self._card_type_cache[path]
                    self._cache_modified = True

                if to_remove:
                    logger_manager.info(f"从缓存中移除目录 {dir_path} 下的 {len(to_remove)} 个卡牌文件")
        except Exception as e:
            logger_manager.error(f"从缓存中移除目录文件失败: {e}")

    def _rename_directory_in_cache(self, old_dir_path: str, new_dir_path: str):
        """重命名缓存中指定目录下的所有卡牌文件"""
        try:
            with self._cache_lock:
                old_relative_path = self._get_relative_path(old_dir_path)
                new_relative_path = new_dir_path
                if not old_relative_path.endswith('/'):
                    old_relative_path += '/'
                if not new_relative_path.endswith('/'):
                    new_relative_path += '/'

                # 找到所有需要重命名的卡牌文件
                to_rename = {}
                for relative_path in self._card_type_cache:
                    if relative_path.startswith(old_relative_path) and relative_path.endswith('.card'):
                        new_path = relative_path.replace(old_relative_path, new_relative_path, 1)
                        to_rename[relative_path] = new_path

                # 重命名缓存中的路径
                for old_path, new_path in to_rename.items():
                    self._card_type_cache[new_path] = self._card_type_cache[old_path]
                    del self._card_type_cache[old_path]
                    self._cache_modified = True

                if to_rename:
                    logger_manager.info(f"重命名缓存中目录 {old_dir_path} 下的 {len(to_rename)} 个卡牌文件")
        except Exception as e:
            logger_manager.error(f"重命名缓存中目录文件失败: {e}")

    def clear_card_type_cache(self):
        """清理卡牌类型缓存"""
        try:
            with self._cache_lock:
                self._card_type_cache.clear()
                self._cache_modified = True
                self._save_card_type_cache()
                logger_manager.info("卡牌类型缓存已清理")
        except Exception as e:
            logger_manager.error(f"清理卡牌类型缓存失败: {e}")

    def __del__(self):
        """析构函数，确保在对象销毁时保存缓存"""
        try:
            self._save_card_type_cache()
        except Exception:
            # 析构函数中不应抛出异常
            pass

    def save_cache_on_exit(self):
        """在程序退出前保存缓存"""
        self._save_card_type_cache()

    def _get_relative_path(self, absolute_path: str) -> str:
        """将绝对路径转换为相对于工作目录的相对路径"""
        try:
            return os.path.relpath(absolute_path, self.workspace_path)
        except Exception:
            return absolute_path

    def _get_absolute_path(self, relative_path: str) -> str:
        """将相对路径转换为绝对路径"""
        if os.path.isabs(relative_path):
            return relative_path
        return os.path.join(self.workspace_path, relative_path)

    def _is_path_in_workspace(self, path: str) -> bool:
        """检查路径是否在工作目录内"""
        abs_path = self._get_absolute_path(path)
        return abs_path.startswith(self.workspace_path)

    def _get_file_type(self, file_path: str) -> str:
        """根据文件扩展名确定文件类型"""
        ext = os.path.splitext(file_path)[1].lower()

        type_mapping = {
            '.card': 'card',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.gif': 'image',
            '.svg': 'image',
            '.bmp': 'image',
            '.webp': 'image',
            '.tiff': 'image',
            '.ico': 'image',
            '.json': 'config',
            '.xml': 'data',
            '.css': 'style',
            '.txt': 'text',
            '.md': 'text',
            '.yml': 'config',
            '.yaml': 'config',
        }

        return type_mapping.get(ext, 'file')

    def _get_card_type(self, item_path: str) -> str:
        """快速读取 JSON 文件中的 'type' 字段，优先从缓存获取"""
        try:
            # 获取相对路径
            relative_path = self._get_relative_path(item_path)

            # 首先尝试从缓存获取
            with self._cache_lock:
                if relative_path in self._card_type_cache:
                    cache_entry = self._card_type_cache[relative_path]

                    # 检查文件是否被修改
                    current_hash = self._get_file_hash(item_path)
                    if current_hash == cache_entry.get('hash', ''):
                        # 文件未修改，使用缓存数据
                        cache_entry['last_accessed'] = time.time()
                        return cache_entry.get('type', '')
                    else:
                        # 文件已修改，从缓存中移除
                        del self._card_type_cache[relative_path]

            # 缓存中没有或文件已修改，从文件读取
            with open(item_path, 'r', encoding='utf-8') as f:
                # 只读取前几 KB，足够覆盖大多数 JSON 的前部字段
                chunk = f.read(4096)
            match = self._TYPE_RE.search(chunk)
            if match:
                card_type = match.group(1)
                # 更新缓存
                self._update_card_type_cache(item_path, card_type)
                return card_type
        except Exception as e:
            # 可根据需要打印日志或忽略
            logger_manager.warning(f"无法读取 {item_path}: {e}")
        return ''

    def _is_image_file(self, file_path: str) -> bool:
        """检查是否是图片文件"""
        return self._get_file_type(file_path) == 'image'

    def _get_type_priority(self, item_type: str) -> int:
        """获取类型优先级，数字越小优先级越高"""
        type_priorities = {
            'directory': 0,  # 目录最优先
            'card': 1,
            'image': 2,
            'config': 3,
            'text': 4,
            'style': 5,
            'data': 6,
            'file': 7,  # 其他文件类型最低优先级
        }
        return type_priorities.get(item_type, 99)

    def _sort_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对文件和目录进行排序：先按类型，再按名称"""

        def sort_key(item):
            # 第一排序键：类型优先级
            type_priority = self._get_type_priority(item.get('type', 'file'))
            # 第二排序键：文件名（不区分大小写）
            name = item.get('label', '').lower()
            return (type_priority, name)

        return sorted(items, key=sort_key)

    def _build_tree_recursive(self, path: str, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """递归构建目录树"""
        items = []

        try:
            for item in os.listdir(path):
                if not include_hidden and item.startswith('.'):
                    continue

                item_path = os.path.join(path, item)
                # 获取相对于工作目录的相对路径
                relative_path = self._get_relative_path(item_path)
                item_key = f"{relative_path}_{int(time.time() * 1000000)}"  # 使用相对路径+时间戳生成唯一key

                if os.path.isdir(item_path):
                    # 处理目录，递归获取子项并排序
                    children = self._build_tree_recursive(item_path, include_hidden)
                    children = self._sort_items(children)  # 对子项进行排序

                    items.append({
                        'label': item,
                        'key': item_key,
                        'type': 'directory',
                        'path': relative_path,  # 使用相对路径
                        'children': children
                    })

                elif os.path.isfile(item_path):
                    # 处理文件
                    file_type = self._get_file_type(item)
                    item_info = {
                        'label': item,
                        'key': item_key,
                        'type': file_type,
                        'path': relative_path,  # 使用相对路径
                    }

                    # 当文件类型为 card 时，额外提取 card_type
                    if file_type == 'card':
                        item_info['card_type'] = self._get_card_type(item_path)

                    items.append(item_info)

        except PermissionError:
            # 如果没有权限访问目录，跳过
            pass
        except Exception as e:
            print(f"构建目录树失败 {path}: {e}")

        # 对当前级别的项目进行排序
        return self._sort_items(items)

    def get_file_tree(self, include_hidden: bool = False) -> Dict[str, Any]:
        """获取工作目录的文件树结构"""
        try:
            workspace_name = os.path.basename(self.workspace_path) or self.workspace_path
            children = self._build_tree_recursive(self.workspace_path, include_hidden)

            # 返回工作空间根节点
            return {
                'label': workspace_name,
                'key': f"workspace_{int(time.time() * 1000000)}",
                'type': 'workspace',
                'path': '.',  # 工作目录使用相对路径 '.'
                'children': children
            }

        except Exception as e:
            print(f"获取文件树失败: {e}")
            return {
                'label': 'Error',
                'key': 'error',
                'type': 'error',
                'path': '.',
                'children': []
            }

    def create_directory(self, dir_name: str, parent_path: Optional[str] = None) -> bool:
        """创建目录"""
        try:
            # ✅ 修复：处理 '.' 作为 parent_path 的情况
            if parent_path and parent_path != '.':
                # 确保parent_path在工作目录内
                if not self._is_path_in_workspace(parent_path):
                    logger_manager.error(f"路径不在工作目录内: {parent_path}")
                    return False
                target_path = self._get_absolute_path(os.path.join(parent_path, dir_name))
            else:
                # parent_path 为 None 或 '.' 时，直接在工作目录创建
                target_path = os.path.join(self.workspace_path, dir_name)

            logger_manager.info(f"创建目录: {target_path}")
            os.makedirs(target_path, exist_ok=True)
            logger_manager.info(f"目录创建成功: {target_path}")
            return True

        except PermissionError as e:
            logger_manager.error(f"权限错误: {e}")
            logger_manager.error(f"目标路径: {target_path}")
            return False
        except Exception as e:
            logger_manager.exception(f"创建目录失败: {e}")
            return False

    def create_file(self, file_name: str, content: str = "", parent_path: Optional[str] = None) -> bool:
        """创建文件"""
        try:
            # ✅ 修复：处理 '.' 作为 parent_path 的情况
            if parent_path and parent_path != '.':
                # 确保parent_path在工作目录内
                if not self._is_path_in_workspace(parent_path):
                    logger_manager.error(f"路径不在工作目录内: {parent_path}")
                    return False
                target_path = self._get_absolute_path(os.path.join(parent_path, file_name))
            else:
                # parent_path 为 None 或 '.' 时，直接在工作目录创建
                target_path = os.path.join(self.workspace_path, file_name)

            logger_manager.info(f"创建文件: {target_path}")

            # 确保父目录存在
            parent_dir = os.path.dirname(target_path)
            os.makedirs(parent_dir, exist_ok=True)

            # ✅ 添加详细的错误日志
            try:
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger_manager.info(f"文件创建成功: {target_path}")
                return True
            except PermissionError as e:
                logger_manager.error(f"权限错误: {e}")
                logger_manager.error(f"目标路径: {target_path}")
                logger_manager.error(f"工作目录: {self.workspace_path}")
                logger_manager.error("请确保应用有写入权限")
                return False

        except Exception as e:
            logger_manager.exception(f"创建文件失败: {e}")
            return False

    def rename_item(self, old_path: str, new_name: str) -> bool:
        """重命名文件或目录"""
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(old_path):
                return False

            abs_old_path = self._get_absolute_path(old_path)
            if not os.path.exists(abs_old_path):
                return False

            parent_dir = os.path.dirname(abs_old_path)
            new_path = os.path.join(parent_dir, new_name)
            new_relative_path = self._get_relative_path(new_path)

            if os.path.exists(new_path):
                return False  # 目标名称已存在

            # 处理缓存更新
            if os.path.isfile(abs_old_path):
                # 重命名文件
                if old_path.endswith('.card'):
                    # 从缓存中移除旧路径
                    self._remove_from_cache(old_path)
                    if new_path.endswith('.card'):
                        # 如果新文件仍是卡牌文件，移除缓存以便重新读取
                        self._remove_from_cache(new_relative_path)
            elif os.path.isdir(abs_old_path):
                # 重命名目录，需要处理目录下所有卡牌文件的缓存
                self._rename_directory_in_cache(old_path, new_relative_path)

            os.rename(abs_old_path, new_path)
            return True

        except Exception as e:
            print(f"重命名失败: {e}")
            return False

    def delete_item(self, item_path: str) -> bool:
        """删除文件或目录"""
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(item_path):
                return False

            abs_item_path = self._get_absolute_path(item_path)
            if not os.path.exists(abs_item_path):
                return False

            if os.path.isfile(abs_item_path):
                # 如果是卡牌文件，从缓存中移除
                if item_path.endswith('.card'):
                    self._remove_from_cache(item_path)
                os.remove(abs_item_path)
            elif os.path.isdir(abs_item_path):
                # 如果是目录，需要清理其中所有卡牌文件的缓存
                self._remove_directory_from_cache(item_path)
                import shutil
                shutil.rmtree(abs_item_path)

            return True

        except Exception as e:
            print(f"删除失败: {e}")
            return False

    def get_file_content(self, file_path: str) -> Optional[str]:
        """获取文本文件内容"""
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(file_path):
                print(f"路径不在工作目录内: {file_path}")
                return None

            abs_file_path = self._get_absolute_path(file_path)
            print(f"获取文件内容: {abs_file_path}")
            print(f"   - 文件是否存在: {os.path.exists(abs_file_path)}")
            print(f"   - 是否为文件: {os.path.isfile(abs_file_path)}")

            if not os.path.isfile(abs_file_path):
                print(f"文件不存在或不是文件")
                return None

            # 尝试以不同编码读取文件
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
            last_error = None

            for encoding in encodings:
                try:
                    with open(abs_file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    print(f"使用 {encoding} 编码成功读取文件")
                    return content
                except UnicodeDecodeError as e:
                    last_error = e
                    print(f"使用 {encoding} 编码失败: {str(e)[:50]}")
                    continue

            print(f"所有编码尝试失败，最后错误: {last_error}")
            return None

        except Exception as e:
            print(f"读取文件内容失败: {e}")
            traceback.print_exc()
            return None

    def get_image_as_base64(self, image_path: str) -> Optional[str]:
        """
        获取图片文件并转换为base64格式

        Args:
            image_path: 图片文件相对路径

        Returns:
            str: base64格式的图片数据（包含data URL前缀），失败时返回None
        """
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(image_path):
                return None

            abs_image_path = self._get_absolute_path(image_path)
            if not os.path.isfile(abs_image_path):
                return None

            # 检查是否是图片文件
            if not self._is_image_file(abs_image_path):
                return None

            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(abs_image_path)
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/png'  # 默认MIME类型

            # 读取图片文件的二进制数据
            with open(abs_image_path, 'rb') as f:
                image_data = f.read()

            # 转换为base64
            base64_data = base64.b64encode(image_data).decode('utf-8')

            # 返回完整的data URL
            return f"data:{mime_type};base64,{base64_data}"

        except Exception as e:
            print(f"读取图片文件失败: {e}")
            return None

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息

        Args:
            file_path: 文件相对路径

        Returns:
            dict: 文件信息，包含type、size、modified等
        """
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(file_path):
                return None

            abs_file_path = self._get_absolute_path(file_path)
            if not os.path.exists(abs_file_path):
                return None

            stat_info = os.stat(abs_file_path)
            file_type = self._get_file_type(abs_file_path)

            return {
                'path': file_path,  # 返回相对路径
                'type': file_type,
                'is_file': os.path.isfile(abs_file_path),
                'is_directory': os.path.isdir(abs_file_path),
                'is_image': self._is_image_file(abs_file_path),
                'size': stat_info.st_size,
                'modified': stat_info.st_mtime,
                'modified_formatted': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat_info.st_mtime))
            }

        except Exception as e:
            print(f"获取文件信息失败: {e}")
            return None

    def save_file_content(self, file_path: str, content: str) -> bool:
        """保存文件内容"""
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(file_path):
                logger_manager.error(f"路径不在工作目录内: {file_path}")
                return False

            abs_file_path = self._get_absolute_path(file_path)
            logger_manager.info(f"保存文件内容: {abs_file_path}")

            # 确保父目录存在
            parent_dir = os.path.dirname(abs_file_path)
            os.makedirs(parent_dir, exist_ok=True)

            # ✅ 添加详细的错误日志
            try:
                with open(abs_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger_manager.info(f"文件内容保存成功: {abs_file_path}")

                # 如果是卡牌文件，更新缓存
                if file_path.endswith('.card'):
                    self._remove_from_cache(file_path)  # 移除旧缓存，下次会重新读取

                return True
            except PermissionError as e:
                logger_manager.error(f"权限错误: {e}")
                logger_manager.error(f"文件路径: {abs_file_path}")
                logger_manager.error("请确保应用有写入权限")
                return False

        except Exception as e:
            logger_manager.exception(f"保存文件内容失败: {e}")
            return False

    def get_card_base64(self, json_data: Dict[str, Any], field: str = 'picture_base64') -> Union[
        str, Image.Image, None]:
        """
        获取卡牌的base64图片数据

        Args:
            json_data: 卡牌数据的JSON字典

        Returns:
            str: base64格式的图片数据（包含data URL前缀），失败时返回None
        """
        # 获取图片路径
        picture_path = json_data.get('picture_path', None)

        # 检查 picture_base64 字段
        picture_base64 = json_data.get(field, '')

        if picture_base64 and picture_base64.strip():
            try:
                # 解码base64数据
                if picture_base64.startswith('data:image/'):
                    # 去掉data URL前缀
                    base64_data = picture_base64.split(',', 1)[1]
                else:
                    base64_data = picture_base64

                image_data = base64.b64decode(base64_data)
                # 2. 将二进制数据读入一个内存中的字节流对象
                image_stream = io.BytesIO(image_data)
                # 3. 使用 PIL 的 Image.open() 从字节流中打开图片并复制到内存
                with Image.open(image_stream) as img:
                    picture_path = img.copy()  # 复制到内存，确保流可以安全关闭
            except Exception as e:
                print(f"解码base64图片数据失败: {e}")
                return None
        # 如果picture_path是相对路径，转换为绝对路径
        elif picture_path and not os.path.isabs(picture_path):
            full_picture_path = self._get_absolute_path(picture_path)
            if os.path.exists(full_picture_path):
                picture_path = full_picture_path
        return picture_path

    @staticmethod
    def center_crop_if_larger(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """
        如果图片大于目标大小，则中心裁剪到目标大小；否则返回原图

        Args:
            image: PIL图片对象
            target_size: 目标大小，格式为 (width, height)

        Returns:
            处理后的PIL图片对象
        """
        target_width, target_height = target_size
        img_width, img_height = image.size

        # 如果图片的宽度和高度都小于目标大小，返回原图
        if img_width <= target_width and img_height <= target_height:
            return image

        # 计算裁剪区域
        # 如果某个维度小于目标大小，使用原始大小
        crop_width = min(img_width, target_width)
        crop_height = min(img_height, target_height)

        # 计算中心点裁剪的左上角坐标
        left = (img_width - crop_width) // 2
        top = (img_height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height

        # 裁剪图片
        cropped_image = image.crop((left, top, right, bottom))

        return cropped_image

    def generate_card_image(self, json_data: Dict[str, Any], silence=False):
        """
        生成卡图

        Args:
            json_data: 卡牌数据的JSON字典

        Returns:
            Card对象，如果生成失败返回None
        """
        if not CARD_GENERATION_AVAILABLE:
            print("卡牌生成功能不可用：缺少必要的模块")
            return None

        if not self.font_manager or not self.image_manager:
            print("字体或图像管理器未初始化")
            return None

        try:
            # 检查是否为卡背类型
            card_type = json_data.get('type', '')
            cardback_filename = None
            if card_type == '玩家卡背':
                cardback_filename = 'cardback/player-back.jpg'
            elif card_type == '遭遇卡背':
                cardback_filename = 'cardback/encounter-back.jpg'
            elif card_type == '定制卡背':
                cardback_filename = 'cardback/upgrade-back.png'
            elif card_type == '敌库卡背':
                cardback_filename = 'cardback/enemy-back.png'
            if cardback_filename:
                cardback_path = os.path.join('.', cardback_filename)
                # 如果是PyInstaller打包的程序
                if hasattr(sys, '_MEIPASS'):
                    cardback_path = os.path.join(sys._MEIPASS, cardback_filename)

                if os.path.exists(cardback_path):
                    # 创建Card对象并设置图片
                    with Image.open(cardback_path) as img:
                        cardback_pil = img.copy()  # 复制到内存
                    # 裁剪图片到指定大小
                    cardback_pil = self.center_crop_if_larger(cardback_pil, (739, 1049))
                    card = Card(cardback_pil.width, cardback_pil.height, image=cardback_pil)
                    card.image = cardback_pil
                    return card
                else:
                    print(f"遭遇卡背图片不存在: {cardback_path}")
                    return None
            if json_data.get('use_external_image', 0) == 1:
                external_image = self.get_card_base64(json_data, 'external_image')
                if external_image and isinstance(external_image, Image.Image):
                    target_size = (739, 1049)
                    if card_type in ['调查员', '调查员卡', '调查员背面', '调查员卡背', '密谋卡', '密谋卡-大画',
                                     '场景卡', '场景卡-大画']:
                        target_size = (1049, 739)

                    # === 等比例缩放 ===
                    target_w, target_h = target_size
                    src_w, src_h = external_image.size
                    src_ratio = src_w / src_h
                    target_ratio = target_w / target_h

                    if src_ratio > target_ratio:
                        # 图片偏宽 → 以高度为基准缩放
                        new_h = target_h
                        new_w = int(src_ratio * new_h)
                    else:
                        # 图片偏高 → 以宽度为基准缩放
                        new_w = target_w
                        new_h = int(new_w / src_ratio)

                    external_image = external_image.resize((new_w, new_h), Image.LANCZOS)

                    # === 居中裁剪 ===
                    left = max((new_w - target_w) // 2, 0)
                    top = max((new_h - target_h) // 2, 0)
                    right = left + target_w
                    bottom = top + target_h
                    external_image = external_image.crop((left, top, right, bottom))

                    # === 创建卡牌 ===
                    card = Card(external_image.width, external_image.height, image=external_image)
                    card.image = external_image
                    return card

            # 检测卡牌语言
            language = json_data.get('language', 'zh')
            self.font_manager.set_lang(language)

            with self.card_lock:
                # 调用process_card_json生成卡牌
                if silence:
                    card = self.creator.create_card_bottom_map(
                        json_data,
                        picture_path=self.get_card_base64(json_data)
                    )
                else:
                    card = self.creator.create_card(
                        json_data,
                        picture_path=self.get_card_base64(json_data)
                    )

            # 检测是否有遭遇组
            encounter_group = json_data.get('encounter_group', None)
            encounter_groups_dir = self.config.get('encounter_groups_dir', None)
            if encounter_group and encounter_groups_dir:
                # 获取遭遇组图片路径
                encounter_group_picture_path = self._get_absolute_path(
                    os.path.join(encounter_groups_dir, encounter_group + '.png')
                )
                print(f"获取遭遇组图片路径: {encounter_group_picture_path}")
                # 检查路径是否存在
                if os.path.exists(encounter_group_picture_path):
                    with Image.open(encounter_group_picture_path) as encounter_img:
                        card.set_encounter_icon(encounter_img.copy())

            # 画页脚
            illustrator = ""
            footer_copyright = ""
            encounter_group_number = ""
            card_number = ""
            if not silence:
                illustrator = json_data.get('illustrator', '')
                footer_copyright = json_data.get('footer_copyright', '')
                if (footer_copyright and footer_copyright == '') or not footer_copyright:
                    footer_copyright = self.config.get('footer_copyright', '')

                encounter_group_number = json_data.get('encounter_group_number', '')
                card_number = json_data.get('card_number', '')
            # 调查员小卡为纯图片卡牌，不绘制页脚信息
            if card_type != '调查员小卡':
                # 画图标
                footer_icon_name = json_data.get('footer_icon_path', '')
                if not footer_icon_name:
                    footer_icon_name = self.config.get('footer_icon_dir', '')
                footer_icon_font_value = json_data.get('footer_icon_font', '') or None
                footer_icon = None
                if not footer_icon_font_value and footer_icon_name:
                    footer_icon_path = self._get_absolute_path(footer_icon_name)
                    if os.path.exists(footer_icon_path):
                        with Image.open(footer_icon_path) as icon_img:
                            footer_icon = icon_img.copy()

                footer_effects = None
                footer_opacity = None
                footer_font_color = None
                if card_type == '调查员':
                    footer_style = json_data.get('investigator_footer_type', 'normal')
                    if footer_style == 'big-art':
                        footer_effects = [
                            {"type": "glow", "size": 8, "spread": 22, "opacity": 36, "color": (3, 0, 0)},
                            {"type": "stroke", "size": 2, "opacity": 63, "color": (165, 157, 153)}
                        ]
                        footer_opacity = 75
                        footer_font_color = (3, 0, 0)

                card.set_footer_information(
                    illustrator,
                    footer_copyright,
                    encounter_group_number,
                    card_number,
                    footer_icon=footer_icon if not footer_icon_font_value else None,
                    footer_icon_font=footer_icon_font_value if footer_icon_font_value else None,
                    footer_effects=footer_effects,
                    footer_opacity=footer_opacity,
                    footer_font_color=footer_font_color
                )
            return card

        except Exception as e:
            # 打印异常栈
            logger_manager.exception(e)
            print(f"生成卡图失败: {e}")
            return None

    def generate_double_sided_card_image(self, json_data: Dict[str, Any], silence: bool = False):
        """
        生成双面卡图

        Args:
            json_data: 卡牌数据的JSON字典
            silence: 是否静默模式

        Returns:
            dict: 包含正面和背面卡牌的字典，格式为 {'front': card, 'back': card}
        """
        try:
            # 生成正面卡牌
            front_card = self.generate_card_image(json_data, silence)
            if front_card is None:
                print("生成正面卡牌失败")
                return None

            # 获取背面数据
            back_json_data = json_data.get('back', {})
            if not back_json_data:
                print("双面卡牌缺少背面数据")
                return {
                    'front': front_card,
                    'back': None
                }

            # 继承其他必要字段
            if 'version' not in back_json_data:
                back_json_data['version'] = json_data.get('version', '2.0')

            # 为背面注入正面名称，便于 CardAdapter 获取 <fullnameb>
            if 'front_name' not in back_json_data and isinstance(json_data.get('name'), str):
                back_json_data['front_name'] = json_data.get('name')

            # 标记背面，确保适配器可判定对侧名称来源
            back_json_data['is_back'] = True

            # 在生成背面卡牌前，处理共享正面插画与设置
            try:
                share_flag = back_json_data.get('share_front_picture', 0)
                if isinstance(share_flag, str):
                    share_flag = 1 if share_flag == '1' else 0
                if share_flag:
                    # 复制插画与插画布局设置
                    if 'picture_base64' in json_data and json_data.get('picture_base64'):
                        back_json_data['picture_base64'] = json_data.get('picture_base64')
                    if 'picture_layout' in json_data and json_data.get('picture_layout'):
                        back_json_data['picture_layout'] = json_data.get('picture_layout')
                    # 默认将背面标记为背面
                    back_json_data['is_back'] = True
                    # 若未设置滤镜，默认黑白
                    if 'image_filter' not in back_json_data or not back_json_data.get('image_filter'):
                        back_json_data['image_filter'] = 'grayscale'
            except Exception:
                pass

            # 生成背面卡牌
            back_card = self.generate_card_image(back_json_data, silence)
            if back_card is None:
                print("生成背面卡牌失败")
                return {
                    'front': front_card,
                    'back': None
                }

            return {
                'front': front_card,
                'back': back_card
            }

        except Exception as e:
            print(f"生成双面卡图失败: {e}")
            traceback.print_exc()
            return None

    def resolve_reference_card(self, json_data: Dict[str, Any], allow_reference: bool = True) -> Dict[str, Any]:
        """
        解析引用卡牌

        Args:
            json_data: 卡牌数据的JSON字典
            allow_reference: 是否允许解析引用（防止无限引用）

        Returns:
            dict: 解析后的卡牌数据
        """
        try:
            card_type = json_data.get('type', '')

            # 检查是否为引用类型
            if card_type == '引用卡牌' and allow_reference:
                reference_path = json_data.get('reference_path', '')
                reference_side = json_data.get('reference_side', 'front')

                if not reference_path:
                    print("引用卡牌缺少引用地址")
                    return json_data

                # 确保路径在工作目录内
                if not self._is_path_in_workspace(reference_path):
                    print(f"引用路径不在工作目录内: {reference_path}")
                    return json_data

                # 读取引用的卡牌文件
                abs_reference_path = self._get_absolute_path(reference_path)
                if not os.path.exists(abs_reference_path):
                    print(f"引用的卡牌文件不存在: {reference_path}")
                    return json_data

                with open(abs_reference_path, 'r', encoding='utf-8') as f:
                    referenced_card_data = json.load(f)

                # 检查引用目标卡牌的版本
                referenced_version = referenced_card_data.get('version', '')

                if referenced_version == '2.0':
                    # 版本2.0，需要区分正面和反面
                    if reference_side == 'back':
                        # 使用背面数据
                        if 'back' in referenced_card_data:
                            # 复制背面数据，但保持当前卡牌的一些基本属性
                            result_data = referenced_card_data['back'].copy()
                            result_data['language'] = json_data.get('language',
                                                                    referenced_card_data.get('language', 'zh'))
                            result_data['version'] = referenced_version
                            return result_data
                        else:
                            print("引用的卡牌没有背面数据")
                            return json_data
                    else:
                        # 使用正面数据（默认）
                        result_data = referenced_card_data.copy()
                        # 移除背面数据，因为我们只需要正面
                        if 'back' in result_data:
                            del result_data['back']
                        return result_data
                else:
                    # 非2.0版本，直接使用整个数据
                    return referenced_card_data
            else:
                # 非引用类型或不允许引用，直接返回原数据
                return json_data

        except Exception as e:
            print(f"解析引用卡牌失败: {e}")
            return json_data

    def save_card_image(self, json_data: Dict[str, Any], filename: str, parent_path: Optional[str] = None) -> bool:
        """
        保存卡图到文件

        Args:
            json_data: 卡牌数据的JSON字典
            filename: 保存的文件名（包含扩展名）
            parent_path: 保存的父目录相对路径，如果为None或'.'则保存到工作目录

        Returns:
            bool: 保存是否成功
        """
        try:
            # 生成卡图
            card = self.generate_card_image(json_data)
            if card is None or card.image is None:
                logger_manager.error("生成卡图失败")
                return False

            # ✅ 修复：处理 '.' 作为 parent_path 的情况
            if parent_path and parent_path != '.':
                # 确保parent_path在工作目录内
                if not self._is_path_in_workspace(parent_path):
                    logger_manager.error(f"路径不在工作目录内: {parent_path}")
                    return False
                save_path = self._get_absolute_path(os.path.join(parent_path, filename))
            else:
                # parent_path 为 None 或 '.' 时，直接保存到工作目录
                save_path = os.path.join(self.workspace_path, filename)

            logger_manager.info(f"保存卡图到: {save_path}")

            # 确保父目录存在
            parent_dir = os.path.dirname(save_path)
            os.makedirs(parent_dir, exist_ok=True)

            # 保存图片
            card.image.save(save_path)
            logger_manager.info(f"卡图保存成功: {self._get_relative_path(save_path)}")
            return True

        except PermissionError as e:
            logger_manager.error(f"权限错误: {e}")
            logger_manager.error(f"保存路径: {save_path}")
            return False
        except Exception as e:
            logger_manager.exception(f"保存卡图失败: {e}")
            return False

    def save_card_image_enhanced(self, json_data: Dict[str, Any], filename: str,
                                 parent_path: Optional[str] = None, export_format: str = 'JPG',
                                 quality: int = 95, rotate_landscape: bool = False) -> Dict[str, Any]:
        """
        保存卡图到文件（增强版：支持双面卡牌、格式选择、质量设置和横向图片旋转）

        Args:
            json_data: 卡牌数据的JSON字典
            filename: 保存的文件名（不包含扩展名）
            parent_path: 保存的父目录相对路径，如果为None则保存到工作目录
            export_format: 导出格式（PNG或JPG），默认JPG
            quality: 图片质量（1-100），仅对JPG有效，默认95
            rotate_landscape: 是否旋转横向图片（宽大于高），默认False

        Returns:
            List[str]: 保存成功的文件路径列表（相对路径），失败时返回空列表
        """
        saved_files = []
        result: dict[str, list[Any] | str | None] = {
            'saved_files': saved_files,
            'front_url': None,
            'back_url': None,
            'original_front_url': None,
            'original_back_url': None,
            'front_thumbnail_url': None,
            'back_thumbnail_url': None
        }

        try:
            # 检查版本号判断是否为双面卡牌
            version = json_data.get('version', '')

            if version == '2.0':
                # 双面卡牌处理
                print("检测到双面卡牌，开始保存正面和背面")
                double_sided_result = self.generate_double_sided_card_image(json_data)

                if double_sided_result is None:
                    print("生成双面卡图失败")
                    return result

                for side in ['front', 'back']:
                    item_card = double_sided_result.get(side)
                    if not (item_card and item_card.image):
                        # 如果图片不存在则跳过
                        continue
                    side_filename = f"{filename}_{side}.{export_format.lower()}"
                    if rotate_landscape:
                        # 启动横向图片处理
                        width, height = item_card.image.size
                        if width > height:
                            # 横向保留一份源文件
                            original_side_filename = f"{filename}_{side}_original.{export_format.lower()}"
                            front_path = self._save_single_image(
                                item_card.image, original_side_filename, parent_path, export_format, quality, False
                            )
                            if front_path:
                                saved_files.append(front_path)
                                result[f'original_{side}_url'] = front_path
                        # 生成缩略图
                        json_data_side = json_data
                        if side == 'back':
                            json_data_side = json_data.get('back', {})
                        card_thumbnail = self._generate_thumbnail(json_data_side, item_card.image)
                        side_thumbnail_filename = f"{filename}_{side}_thumbnail.jpg"
                        front_path = self._save_single_image(
                            card_thumbnail.image, side_thumbnail_filename, parent_path, 'JPG', 60, False
                        )
                        if front_path:
                            saved_files.append(front_path)
                            result[f'{side}_thumbnail_url'] = front_path
                        pass
                    # 正常处理
                    front_path = self._save_single_image(
                        item_card.image, side_filename, parent_path, export_format, quality, rotate_landscape
                    )
                    if front_path:
                        saved_files.append(front_path)
                        result[f'{side}_url'] = front_path
                        if not result[f'original_{side}_url']:
                            result[f'original_{side}_url'] = front_path
                print(f"双面卡牌保存完成，共保存 {len(saved_files)} 个文件")
            elif json_data.get('type', '') == '封面制作':
                # 封面制作
                front_card_json = {
                    'type': '特殊图片',
                    'picture_base64': json_data.get('picture_base64')
                }
                back_card_json = {
                    'type': '特殊图片',
                    'craft_type': '盒子模型图片',
                    'picture_base64': json_data.get('picture_base64')
                }
                front_card = self.generate_card_image(front_card_json)
                back_card = self.generate_card_image(back_card_json)
                if front_card is None or front_card.image is None:
                    print("生成卡图失败")
                    return result
                # 保存
                final_filename = f"{filename}.{export_format.lower()}"
                save_path = self._save_single_image(
                    front_card.image, final_filename, parent_path, export_format, quality, False
                )
                if save_path:
                    result['front_url'] = save_path
                    saved_files.append(save_path)
                if front_card is None or front_card.image is None:
                    return result
                final_filename = f"{filename}_box.{export_format.lower()}"
                save_path = self._save_single_image(
                    back_card.image, final_filename, parent_path, export_format, quality, False
                )
                if save_path:
                    result['back_url'] = save_path
                    saved_files.append(save_path)

            else:
                # 单面卡牌处理
                print("检测到单面卡牌，开始保存")
                card = self.generate_card_image(json_data)

                if card is None or card.image is None:
                    print("生成卡图失败")
                    return result

                # 保存单面图片
                final_filename = f"{filename}.{export_format.lower()}"
                save_path = self._save_single_image(
                    card.image, final_filename, parent_path, export_format, quality, rotate_landscape
                )
                if save_path:
                    saved_files.append(save_path)

                print("单面卡牌保存完成")

            return result

        except Exception as e:
            print(f"保存卡图失败: {e}")
            traceback.print_exc()
            return result

    def _save_single_image(self, image: Image.Image, filename: str, parent_path: Optional[str],
                           export_format: str, quality: int, rotate_landscape: bool = False) -> Optional[str]:
        """
        保存单张图片到文件

        Args:
            image: PIL图片对象
            filename: 文件名（包含扩展名）
            parent_path: 父目录相对路径
            export_format: 导出格式
            quality: 图片质量
            rotate_landscape: 是否旋转横向图片（宽大于高）

        Returns:
            str: 保存成功的文件相对路径，失败时返回None
        """
        try:
            # 处理横向图片旋转
            if rotate_landscape:
                width, height = image.size
                if width > height:
                    # 横向图片顺时针旋转90度
                    image = image.rotate(-90, expand=True)
                    logger_manager.info(f"横向图片已旋转90度，原尺寸: {width}x{height}，新尺寸: {image.size}")

            # ✅ 修复：处理 '.' 作为 parent_path 的情况
            if parent_path and parent_path != '.':
                # 确保parent_path在工作目录内
                if not self._is_path_in_workspace(parent_path):
                    logger_manager.error(f"路径不在工作目录内: {parent_path}")
                    return None
                save_path = self._get_absolute_path(os.path.join(parent_path, filename))
            else:
                # parent_path 为 None 或 '.' 时，直接保存到工作目录
                save_path = os.path.join(self.workspace_path, filename)

            logger_manager.info(f"保存图片到: {save_path}")

            # 确保父目录存在
            parent_dir = os.path.dirname(save_path)
            os.makedirs(parent_dir, exist_ok=True)

            # 根据格式保存图片
            if export_format == 'JPG':
                # JPG格式需要转换为RGB模式
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(save_path, format='JPEG', quality=quality, optimize=True)
            else:
                # PNG格式保持透明通道
                image.save(save_path, format='PNG', optimize=True)

            logger_manager.info(f"图片保存成功: {self._get_relative_path(save_path)}")
            return self._get_relative_path(save_path)

        except PermissionError as e:
            logger_manager.error(f"权限错误: {e}")
            logger_manager.error(f"保存路径: {save_path}")
            return None
        except Exception as e:
            logger_manager.exception(f"保存图片失败: {e}")
            return None

    def _generate_thumbnail(self, json_data: Dict[str, Any], image: Image.Image) -> 'Card':
        """
        生成卡牌缩略图（通过调用卡牌生成API）
        Args:
            json_data: 卡牌数据的JSON字典
            image: PIL图片对象（用于备用方案）
        Returns:
            str: 缩略图文件相对路径，失败时返回None
        """
        try:
            # 创建缩略图JSON数据
            thumbnail_json = {
                "type": "特殊图片",
                "craft_type": "缩略图",
                "thumbnail_type": json_data.get('type', '未知')
            }
            # 调用卡牌生成API生成缩略图
            print(f"正在生成缩略图: {thumbnail_json['thumbnail_type']}")
            thumbnail_card = self.creator.create_card(thumbnail_json, image)
            return thumbnail_card
        except Exception as e:
            print(f"生成缩略图失败: {e}")
            traceback.print_exc()
            return None

    @staticmethod
    def _get_global_config_path() -> str:
        """获取全局配置文件路径"""
        return config_dir_manager.get_global_config_file_path()

    def _get_default_global_config(self) -> Dict[str, Any]:
        """获取默认全局配置"""
        config = {}
        for field in self.SYSTEM_CONFIG_FIELDS:
            if field == "github_branch":
                config[field] = "main"
            elif field == "github_folder":
                config[field] = "images"
            elif field == "language":
                config[field] = "zh"
            elif field == "first_visit_completed":
                config[field] = False
            elif field == "folder":
                config[field] = "AH_LCG"  # Cloudinary默认文件夹
            elif field == "imgbb_expiration":
                config[field] = 0  # ImgBB默认永不过期
            elif field in ("advanced_export_params", "pnp_export_params"):
                config[field] = {}
            else:
                config[field] = ""
        return config

    def _get_default_workspace_config(self) -> Dict[str, Any]:
        """获取默认工作空间配置"""
        config = {}
        for field in self.WORKSPACE_CONFIG_FIELDS:
            if field == "encounter_groups_dir":
                config[field] = "encounter_groups"
            else:
                config[field] = ""
        return config

    def _load_config_file(self, file_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"加载配置文件失败 {file_path}: {e}")
            return {}

    def _save_config_file(self, file_path: str, config: Dict[str, Any]) -> bool:
        """保存配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败 {file_path}: {e}")
            return False

    def _filter_config_by_fields(self, config: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """根据字段列表过滤配置"""
        return {key: value for key, value in config.items() if key in fields}

    def get_global_config(self) -> Dict[str, Any]:
        """获取全局配置"""
        try:
            global_config_path = self._get_global_config_path()
            loaded_config = self._load_config_file(global_config_path)

            # 合并默认配置和加载的配置
            default_config = self._get_default_global_config()
            default_config.update(loaded_config)

            return default_config
        except Exception as e:
            print(f"获取全局配置失败: {e}")
            return self._get_default_global_config()

    def save_global_config(self, global_config: Dict[str, Any]) -> bool:
        """保存全局配置"""
        try:
            # 只保存系统配置字段
            filtered_config = self._filter_config_by_fields(global_config, self.SYSTEM_CONFIG_FIELDS)

            global_config_path = self._get_global_config_path()
            return self._save_config_file(global_config_path, filtered_config)
        except Exception as e:
            print(f"保存全局配置失败: {e}")
            return False

    def get_workspace_config(self) -> Dict[str, Any]:
        """获取工作空间配置"""
        try:
            config_path = os.path.join(self.workspace_path, 'config.json')
            loaded_config = self._load_config_file(config_path)

            # 合并默认配置和加载的配置
            default_config = self._get_default_workspace_config()
            default_config.update(loaded_config)

            return default_config
        except Exception as e:
            print(f"获取工作空间配置失败: {e}")
            return self._get_default_workspace_config()

    def save_workspace_config(self, workspace_config: Dict[str, Any]) -> bool:
        """保存工作空间配置"""
        try:
            # 只保存工作空间配置字段
            filtered_config = self._filter_config_by_fields(workspace_config, self.WORKSPACE_CONFIG_FIELDS)

            config_path = os.path.join(self.workspace_path, 'config.json')
            return self._save_config_file(config_path, filtered_config)
        except Exception as e:
            print(f"保存工作空间配置失败: {e}")
            return False

    def get_github_config(self) -> Dict[str, Any]:
        """获取GitHub配置"""
        global_config = self.get_global_config()
        github_fields = ["github_token", "github_repo", "github_branch", "github_folder"]
        return self._filter_config_by_fields(global_config, github_fields)

    def save_github_config(self, github_config: Dict[str, Any]) -> bool:
        """保存GitHub配置"""
        try:
            # 读取现有全局配置
            existing_global_config = self.get_global_config()

            # 更新GitHub相关配置
            github_fields = ["github_token", "github_repo", "github_branch", "github_folder"]
            for key in github_fields:
                if key in github_config:
                    existing_global_config[key] = github_config[key]

            # 保存全局配置
            return self.save_global_config(existing_global_config)
        except Exception as e:
            print(f"保存GitHub配置失败: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """获取配置项（合并全局配置和工作目录配置）"""
        try:
            # 获取全局配置和工作空间配置
            global_config = self.get_global_config()
            workspace_config = self.get_workspace_config()

            # 合并配置，工作空间配置优先
            combined_config = global_config.copy()
            combined_config.update(workspace_config)

            return combined_config

        except Exception as e:
            print(f"读取配置文件失败: {e}")
            # 返回默认配置
            default_config = self._get_default_global_config()
            default_config.update(self._get_default_workspace_config())
            return default_config

    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置项（分别保存全局配置和工作目录配置）"""
        try:
            # 分离系统配置和工作空间配置
            global_config = self._filter_config_by_fields(config, self.SYSTEM_CONFIG_FIELDS)
            workspace_config = self._filter_config_by_fields(config, self.WORKSPACE_CONFIG_FIELDS)

            # 保存全局配置
            if global_config:
                # 读取现有全局配置，然后更新
                existing_global_config = self.get_global_config()
                existing_global_config.update(global_config)

                if not self.save_global_config(existing_global_config):
                    return False

            # 保存工作空间配置
            if workspace_config:
                # 读取现有工作空间配置，然后更新
                existing_workspace_config = self.get_workspace_config()
                existing_workspace_config.update(workspace_config)

                if not self.save_workspace_config(existing_workspace_config):
                    return False

            # 更新内存中的配置
            self.config = self.get_config()
            return True

        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get_encounter_groups(self) -> List[str]:
        """获取遭遇组列表"""
        try:
            # 获取配置
            config = self.config
            encounter_dir = config.get('encounter_groups_dir', '')

            if not encounter_dir:
                print("配置中未设置遭遇组目录")
                return []

            # 构建遭遇组目录的绝对路径
            encounter_path = self._get_absolute_path(encounter_dir)

            if not os.path.exists(encounter_path):
                print(f"遭遇组目录不存在: {encounter_dir}")
                return []

            if not os.path.isdir(encounter_path):
                print(f"指定路径不是目录: {encounter_dir}")
                return []

            # 搜索所有png图片文件
            encounter_groups = []
            for file in os.listdir(encounter_path):
                if file.lower().endswith('.png'):
                    # 去掉扩展名
                    name = os.path.splitext(file)[0]
                    encounter_groups.append(name)

            # 按名称排序
            encounter_groups.sort()
            return encounter_groups

        except Exception as e:
            print(f"获取遭遇组列表失败: {e}")
            return []

    def export_deck_image(self, deck_name: str, export_format: str = 'PNG', quality: int = 95) -> bool:
        """
        导出牌库图片

        Args:
            deck_name: 牌库名称（DeckBuilder文件夹中的文件名）
            export_format: 导出格式（JPG或PNG）
            quality: 图片质量百分比（1-100）

        Returns:
            bool: 导出是否成功
        """
        return self.deck_exporter.export_deck_image(deck_name, export_format, quality)

    def export_deck_pdf(self, deck_name: str, pdf_filename: Optional[str] = None) -> bool:
        """导出牌库PDF"""
        return self.deck_exporter.export_deck_pdf(deck_name, pdf_filename)

    def _get_card_image_for_position(self, cards: List[Dict], position: int) -> Optional[Image.Image]:
        """获取指定位置的卡片图片"""
        for card in cards:
            if card.get('index') == position:
                return self._load_card_image(card)
        return None

    def _load_card_image(self, card_data: Dict) -> Optional[Image.Image]:
        """根据卡片数据加载图片"""
        try:
            from PIL import Image

            card_type = card_data.get('type')
            card_path = card_data.get('path')

            if card_type == 'image':
                # 直接读取图片文件（相对工作目录路径）
                image_path = self._get_absolute_path(card_path)
                if os.path.exists(image_path):
                    with Image.open(image_path) as img:
                        return img.copy()  # 复制到内存并返回

            elif card_type == 'cardback':
                # 固定的卡牌背面，从程序目录读取
                if card_path == 'player':
                    cardback_filename = 'cardback/player-back.jpg'
                elif card_path == 'encounter':
                    cardback_filename = 'cardback/encounter-back.jpg'
                else:
                    return None

                # 从程序目录读取
                cardback_path = os.path.join('.', cardback_filename)

                # 如果是PyInstaller打包的程序
                if hasattr(sys, '_MEIPASS'):
                    cardback_path = os.path.join(sys._MEIPASS, cardback_filename)

                print(f"正在读取卡牌背面图片: {cardback_path} {os.path.exists(cardback_path)}")
                if os.path.exists(cardback_path):
                    with Image.open(cardback_path) as img:
                        return img.copy()  # 复制到内存并返回

            elif card_type == 'card':
                # 卡牌对象，需要读取卡牌JSON并生成图片
                card_json_path = self._get_absolute_path(card_path)
                if os.path.exists(card_json_path):
                    with open(card_json_path, 'r', encoding='utf-8') as f:
                        card_json_data = json.load(f)
                    return self.generate_card_image(card_json_data).image

            return None

        except Exception as e:
            print(f"加载卡片图片失败: {e}")
            return None

    def _process_card_image(self, image: Image.Image, is_front: bool, target_width: int,
                            target_height: int) -> Image.Image:
        """处理卡片图片（检测方向、旋转、拉伸）"""
        try:
            # 检测图片是横向还是纵向
            img_width, img_height = image.size
            is_landscape = img_width > img_height

            if is_landscape:
                # 横向图片需要旋转
                if is_front:
                    # 正面顺时针旋转90度
                    image = image.rotate(-90, expand=True)
                else:
                    # 背面逆时针旋转90度
                    image = image.rotate(90, expand=True)

            # 拉伸到目标尺寸
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

            return image

        except Exception as e:
            print(f"处理卡片图片失败: {e}")
            return image

    def open_directory_in_explorer(self, directory_path: str, bring_to_front: bool = True) -> bool:
        """
        在系统资源管理器中打开指定目录

        Args:
            directory_path: 相对于工作目录的目录路径
            bring_to_front: 是否将打开的窗口置顶

        Returns:
            bool: 是否成功打开
        """
        try:
            import subprocess
            import platform

            # 确保路径在工作目录内
            if not self._is_path_in_workspace(directory_path):
                print(f"路径不在工作目录内: {directory_path}")
                return False

            # 获取绝对路径
            abs_directory_path = self._get_absolute_path(directory_path)

            # 检查目录是否存在
            if not os.path.exists(abs_directory_path):
                print(f"目录不存在: {abs_directory_path}")
                return False

            if not os.path.isdir(abs_directory_path):
                print(f"指定路径不是目录: {abs_directory_path}")
                return False

            # 检查是否为Windows系统
            system = platform.system()
            if system != "Windows":
                print(f"不支持的操作系统: {system}")
                return False

            # Windows系统打开目录
            if bring_to_front:
                self._open_directory_windows_with_focus(abs_directory_path)
            else:
                # 简单打开
                os.startfile(abs_directory_path)

            print(f"已在资源管理器中打开目录: {self._get_relative_path(abs_directory_path)}")
            return True

        except Exception as e:
            print(f"打开目录失败: {e}")
            return False

    def _open_directory_windows_with_focus(self, abs_directory_path: str):
        """Windows系统打开目录并置顶"""
        try:
            import subprocess
            import time

            # 打开资源管理器
            subprocess.Popen(['explorer', abs_directory_path])

            # 等待一小段时间让窗口打开
            time.sleep(0.5)

            try:
                # 尝试使用Windows API将资源管理器窗口置顶
                import win32gui
                import win32con

                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        class_name = win32gui.GetClassName(hwnd)

                        # 查找资源管理器窗口
                        if (class_name == "CabinetWClass" or class_name == "ExploreWClass"):
                            # 检查窗口标题是否包含目录名
                            folder_name = os.path.basename(abs_directory_path)
                            if folder_name in window_title or abs_directory_path in window_title:
                                windows.append(hwnd)
                    return True

                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)

                # 将找到的窗口置顶
                for hwnd in windows:
                    win32gui.SetWindowPos(
                        hwnd,
                        win32con.HWND_TOPMOST,
                        0, 0, 0, 0,
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                    )
                    # 取消置顶状态，只是激活到前台
                    win32gui.SetWindowPos(
                        hwnd,
                        win32con.HWND_NOTOPMOST,
                        0, 0, 0, 0,
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                    )
                    win32gui.SetForegroundWindow(hwnd)
                    break

            except ImportError:
                # 如果没有安装pywin32，使用备用方案
                print("提示: 安装 pywin32 可获得更好的窗口置顶效果")
                print("安装命令: pip install pywin32")

        except Exception as e:
            print(f"Windows打开目录失败: {e}")
            # 回退到简单打开
            os.startfile(abs_directory_path)

    def _get_tts_save_directory(self) -> Optional[str]:
        """获取TTS保存目录，不存在则创建"""
        try:
            # 获取我的文档路径
            import os
            user_home = os.path.expanduser("~")
            documents_path = os.path.join(user_home, "Documents")

            # 如果Documents目录不存在，尝试中文版本
            if not os.path.exists(documents_path):
                documents_path = os.path.join(user_home, "文档")

            if not os.path.exists(documents_path):
                print("无法找到我的文档目录")
                return None

            # 构建完整路径
            tts_path = os.path.join(
                documents_path,
                "My Games",
                "Tabletop Simulator",
                "Saves",
                "Saved Objects",
                "阿卡姆姬制作"
            )

            # 创建目录（如果不存在）
            os.makedirs(tts_path, exist_ok=True)

            print(f"TTS保存目录: {tts_path}")
            return tts_path

        except Exception as e:
            print(f"创建TTS保存目录失败: {e}")
            return None

    def _generate_tts_cover(self, deck_config: Dict[str, Any]) -> Optional[Image.Image]:
        """生成TTS物品封面图片（256x256，等比缩放，透明背景）"""
        try:
            from PIL import Image

            # 获取前面卡片列表
            front_cards = deck_config.get("frontCards", [])

            if not front_cards:
                print("牌库中没有正面卡片")
                return None

            # 寻找第一个有效的对象作为封面
            for card_data in front_cards:
                try:
                    card_type = card_data.get('type')
                    card_path = card_data.get('path')

                    source_image = None

                    if card_type == 'card':
                        # 读取卡牌JSON并生成图片
                        card_json_path = self._get_absolute_path(card_path)
                        if os.path.exists(card_json_path):
                            with open(card_json_path, 'r', encoding='utf-8') as f:
                                card_json_data = json.load(f)

                            # 生成卡图
                            source_image = self.generate_card_image(card_json_data).image

                    elif card_type == 'image':
                        # 直接读取图片文件
                        image_path = self._get_absolute_path(card_path)
                        if os.path.exists(image_path):
                            with Image.open(image_path) as img:
                                source_image = img.copy()  # 复制到内存

                    elif card_type == 'cardback':
                        # 使用卡背图片
                        cardback_filename = None
                        if card_path == 'player':
                            cardback_filename = 'cardback/player-back.jpg'
                        elif card_path == 'encounter':
                            cardback_filename = 'cardback/encounter-back.jpg'

                        if cardback_filename:
                            cardback_path = os.path.join('.', cardback_filename)

                            # 如果是PyInstaller打包的程序
                            if hasattr(sys, '_MEIPASS'):
                                cardback_path = os.path.join(sys._MEIPASS, cardback_filename)

                            if os.path.exists(cardback_path):
                                with Image.open(cardback_path) as img:
                                    source_image = img.copy()  # 复制到内存

                    # 如果成功获取到源图片，进行等比缩放处理
                    if source_image:
                        # 创建透明背景的256x256画布
                        cover_image = Image.new('RGBA', (256, 256), (0, 0, 0, 0))

                        # 计算等比缩放尺寸
                        source_width, source_height = source_image.size
                        aspect_ratio = source_width / source_height

                        if aspect_ratio > 1:  # 宽图
                            scaled_width = 256
                            scaled_height = int(256 / aspect_ratio)
                        else:  # 高图或正方形
                            scaled_width = int(256 * aspect_ratio)
                            scaled_height = 256

                        # 等比缩放源图片
                        scaled_image = source_image.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)

                        # 计算居中位置
                        x = (256 - scaled_width) // 2
                        y = (256 - scaled_height) // 2

                        # 如果源图片有alpha通道，直接粘贴；否则转换为RGBA
                        if scaled_image.mode != 'RGBA':
                            scaled_image = scaled_image.convert('RGBA')

                        # 将缩放后的图片粘贴到透明背景上
                        cover_image.paste(scaled_image, (x, y), scaled_image)

                        return cover_image

                except Exception as e:
                    print(f"处理封面卡片时出错 {card_data.get('path', 'unknown')}: {e}")
                    continue

            # 如果没有找到有效的卡片，创建一个默认透明封面
            print("未找到有效的封面卡片，创建默认封面")
            default_cover = Image.new('RGBA', (256, 256), (50, 50, 50, 128))  # 半透明灰色
            return default_cover

        except Exception as e:
            print(f"生成TTS封面失败: {e}")
            return None

    def _get_next_file_number(self, base_name: str, save_dir: str) -> int:
        """获取下一个可用的文件编号"""
        try:
            max_number = 0

            # 扫描目录中已存在的文件
            if os.path.exists(save_dir):
                for filename in os.listdir(save_dir):
                    # 匹配格式：base_name_数字.扩展名
                    if filename.startswith(f"{base_name}_") and (
                            filename.endswith('.json') or filename.endswith('.png')):
                        try:
                            # 提取数字部分
                            name_part = filename[len(base_name) + 1:]  # 去掉前缀和下划线
                            number_part = name_part.split('.')[0]  # 去掉扩展名

                            if number_part.isdigit():
                                number = int(number_part)
                                max_number = max(max_number, number)
                        except (ValueError, IndexError):
                            continue

            return max_number + 1

        except Exception as e:
            print(f"获取文件编号失败: {e}")
            return 1

    def export_deck_to_tts(self, deck_name: str, face_url: str, back_url: str) -> bool:
        """
        导出TTS物品

        Args:
            deck_name: 牌库名称（DeckBuilder文件夹中的文件名）
            face_url: 正面图片URL
            back_url: 背面图片URL

        Returns:
            bool: 导出是否成功
        """
        try:
            from PIL import Image

            # 1. 检查牌库文件是否存在
            deck_builder_path = os.path.join(self.workspace_path, 'DeckBuilder')
            if not os.path.exists(deck_builder_path):
                print("DeckBuilder目录不存在")
                return False

            deck_file_path = os.path.join(deck_builder_path, deck_name)
            if not os.path.exists(deck_file_path):
                print(f"牌库文件不存在: {deck_name}")
                return False

            # 2. 读取牌库配置
            with open(deck_file_path, 'r', encoding='utf-8') as f:
                deck_config = json.load(f)

            # 3. 创建TTS转换器并转换
            converter = TTSCardConverter(self.workspace_path)
            tts_json = converter.convert_deck_to_tts(deck_config, face_url, back_url)

            # 4. 生成封面图片（256x256，等比缩放，透明背景）
            cover_image = self._generate_tts_cover(deck_config)
            if cover_image is None:
                print("无法生成封面图片")
                return False

            # 5. 确定保存路径
            save_dir = self._get_tts_save_directory()
            if not save_dir:
                return False

            # 6. 生成文件名（去掉原文件扩展名）
            base_name = os.path.splitext(deck_name)[0]

            # 获取下一个可用的编号
            file_number = self._get_next_file_number(base_name, save_dir)

            json_filename = f"{base_name}_{file_number:03d}.json"  # 使用3位数字，例如001, 002, 003
            cover_filename = f"{base_name}_{file_number:03d}.png"

            json_path = os.path.join(save_dir, json_filename)
            cover_path = os.path.join(save_dir, cover_filename)

            # 7. 保存JSON文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(tts_json, f, indent=2, ensure_ascii=False)

            # 8. 保存封面图片
            cover_image.save(cover_path, 'PNG')

            print(f"TTS物品已导出:")
            print(f"  JSON: {json_path}")
            print(f"  封面: {cover_path}")

            return True

        except Exception as e:
            print(f"导出TTS物品失败: {e}")
            return False

    def export_card_with_params(self, card_path: str, export_filename: str, export_params: Dict[str, Any]) -> bool:
        """
        使用指定的导出参数导出卡牌（支持单面和双面卡牌）

        Args:
            card_path: 卡牌文件相对路径
            export_filename: 导出文件名（不包含扩展名）
            export_params: 导出参数

        Returns:
            bool: 导出是否成功
        """
        try:
            # 确保路径在工作目录内
            if not self._is_path_in_workspace(card_path):
                print(f"卡牌路径不在工作目录内: {card_path}")
                return False

            # 检查导出目录是否存在，不存在则创建
            export_dir = os.path.join(self.workspace_path, 'export')
            os.makedirs(export_dir, exist_ok=True)

            # 获取导出格式
            export_format = export_params.get('format', 'PNG').upper()
            if export_format not in ['PNG', 'JPG']:
                print(f"不支持的导出格式: {export_format}")
                return False

            from ExportHelper import ExportHelper
            # 直接基于传入参数构造导出助手（保持与前端同步参数）
            export_helper = ExportHelper(export_params, self)
            self._export_helper = export_helper

            # 导出卡牌（自动判断单面或双面）
            result = export_helper.export_card_auto(card_path)
            if result is None:
                print("导出卡牌失败")
                return False

            # 判断是单面还是双面卡牌
            if isinstance(result, dict):
                # 双面卡牌
                print("检测到双面卡牌，导出正面和背面")

                # 保存正面
                front_image = result.get('front')
                if front_image:
                    front_filepath = os.path.join(export_dir, f"{export_filename}_a.{export_format.lower()}")

                    # 确保导出文件的父目录存在
                    os.makedirs(os.path.dirname(front_filepath), exist_ok=True)

                    # 保存正面图片
                    dpi_info = (export_helper.dpi, export_helper.dpi)
                    if export_format == 'JPG':
                        quality = export_params.get('quality', 95)
                        front_image = front_image.convert('RGB')
                        front_image.save(front_filepath, format='JPEG', quality=quality, dpi=dpi_info)
                    else:
                        front_image.save(front_filepath, format='PNG', dpi=dpi_info)
                    print(f"正面已导出到: {front_filepath}")
                else:
                    print("警告：正面图片为空")
                    return False

                # 保存背面
                back_image = result.get('back')
                if back_image:
                    back_filepath = os.path.join(export_dir, f"{export_filename}_b.{export_format.lower()}")

                    # 确保导出文件的父目录存在
                    os.makedirs(os.path.dirname(back_filepath), exist_ok=True)

                    # 保存背面图片
                    dpi_info = (export_helper.dpi, export_helper.dpi)
                    if export_format == 'JPG':
                        quality = export_params.get('quality', 95)
                        back_image = back_image.convert('RGB')
                        back_image.save(back_filepath, format='JPEG', quality=quality, dpi=dpi_info)
                    else:
                        back_image.save(back_filepath, format='PNG', dpi=dpi_info)
                    print(f"背面已导出到: {back_filepath}")
                else:
                    print("警告：背面图片为空，仅导出正面")

                print("双面卡牌导出完成")
                return True

            else:
                # 单面卡牌
                print("检测到单面卡牌")
                card_image = result

                # 构建完整的导出文件名
                export_filepath = os.path.join(export_dir, f"{export_filename}.{export_format.lower()}")

                # 确保导出文件的父目录存在
                export_parent_dir = os.path.dirname(export_filepath)
                os.makedirs(export_parent_dir, exist_ok=True)

                # 保存图片
                dpi_info = (export_helper.dpi, export_helper.dpi)
                if export_format == 'JPG':
                    quality = export_params.get('quality', 95)
                    # 转为RGB
                    card_image = card_image.convert('RGB')
                    card_image.save(export_filepath, format='JPEG', quality=quality, dpi=dpi_info)
                else:
                    card_image.save(export_filepath, format='PNG', dpi=dpi_info)

                print(f"卡牌已导出到: {export_filepath}")
                return True

        except Exception as e:
            print(f"导出卡牌失败: {e}")
            traceback.print_exc()
            return False

    def export_content_package_to_tts(self, package_relative_path: str) -> Dict[str, Any]:
        """
        导出内容包到TTS物品

        Args:
            package_relative_path: 内容包文件的相对路径

        Returns:
            dict: 包含成功状态和日志信息的字典
        """
        try:
            # 确保路径在工作空间内
            if not self._is_path_in_workspace(package_relative_path):
                return {
                    "success": False,
                    "logs": [f"内容包路径不在工作空间内: {package_relative_path}"],
                    "error": "路径安全检查失败"
                }

            # 读取内容包文件
            package_path = self._get_absolute_path(package_relative_path)
            if not os.path.exists(package_path):
                return {
                    "success": False,
                    "logs": [f"内容包文件不存在: {package_relative_path}"],
                    "error": "文件不存在"
                }

            with open(package_path, 'r', encoding='utf-8') as f:
                content_package_data = json.load(f)

            # 创建内容包管理器并导出
            manager = ContentPackageManager(content_package_data, self)
            result = manager.export_to_tts()

            if not result.get("success"):
                return result

            # 保存到TTS保存目录（Windows系统）
            if os.name == 'nt':  # Windows系统
                try:
                    tts_save_dir = self._get_tts_save_directory()
                    if tts_save_dir:
                        # 生成文件名
                        package_dir = os.path.dirname(package_relative_path)
                        package_name = os.path.splitext(os.path.basename(package_relative_path))[0]
                        tts_filename = f"{package_name}_tts.json"
                        tts_path = os.path.join(tts_save_dir, tts_filename)

                        # 保存JSON文件
                        with open(tts_path, 'w', encoding='utf-8') as f:
                            json.dump(result["box_json"], f, indent=2, ensure_ascii=False)

                        result["logs"].append(f"TTS物品已保存到: {tts_path}")
                        result["tts_path"] = tts_path
                except Exception as e:
                    result["logs"].append(f"保存到TTS目录失败（不影响导出）: {e}")

            # 保存到内容包目录
            try:
                package_dir = os.path.dirname(package_relative_path)
                package_name = os.path.splitext(os.path.basename(package_relative_path))[0]
                local_filename = f"{package_name}_tts.json"
                local_path = self._get_absolute_path(os.path.join(package_dir, local_filename))

                # 确保目录存在
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                # 保存JSON文件
                with open(local_path, 'w', encoding='utf-8') as f:
                    json.dump(result["box_json"], f, indent=2, ensure_ascii=False)

                result["logs"].append(f"TTS物品已保存到内容包目录: {os.path.join(package_dir, local_filename)}")
                result["local_path"] = os.path.join(package_dir, local_filename)

            except Exception as e:
                result["logs"].append(f"保存到内容包目录失败: {e}")
                result["success"] = False

            return result

        except Exception as e:
            error_msg = f"导出内容包到TTS失败: {e}"
            print(error_msg)
            return {
                "success": False,
                "logs": [error_msg],
                "error": str(e)
            }

    def export_content_package_to_arkhamdb(self, package_relative_path: str, output_path: str = None) -> Dict[str, Any]:
        """
        导出内容包到ArkhamDB格式

        Args:
            package_relative_path: 内容包文件的相对路径
            output_path: 可选的输出文件路径

        Returns:
            dict: 包含成功状态、数据和日志信息的字典
        """
        try:
            # 确保路径在工作空间内
            if not self._is_path_in_workspace(package_relative_path):
                return {
                    "success": False,
                    "logs": [f"内容包路径不在工作空间内: {package_relative_path}"],
                    "error": "路径安全检查失败"
                }

            # 读取内容包文件
            package_path = self._get_absolute_path(package_relative_path)
            if not os.path.exists(package_path):
                return {
                    "success": False,
                    "logs": [f"内容包文件不存在: {package_relative_path}"],
                    "error": "文件不存在"
                }

            with open(package_path, 'r', encoding='utf-8') as f:
                content_package_data = json.load(f)

            # 创建内容包管理器并导出
            manager = ContentPackageManager(content_package_data, self)
            result = manager.export_to_arkhamdb(output_path)

            if not result.get("success"):
                return result

            # 添加额外的成功日志
            result["logs"].append("ArkhamDB格式导出完成")

            return result

        except Exception as e:
            error_msg = f"导出内容包到ArkhamDB失败: {e}"
            print(error_msg)
            return {
                "success": False,
                "logs": [error_msg],
                "error": str(e)
            }

    def get_content_package(self, package_relative_path: str) -> Optional['ContentPackageManager']:
        """
        通过相对路径获取内容包管理器对象

        Args:
            package_relative_path: 内容包文件的相对路径

        Returns:
            ContentPackageManager: 内容包管理器对象，失败时返回None
        """
        try:
            # 确保路径在工作空间内
            if not self._is_path_in_workspace(package_relative_path):
                logger_manager.error(f"内容包路径不在工作空间内: {package_relative_path}")
                return None

            # 获取绝对路径
            package_path = self._get_absolute_path(package_relative_path)

            # 检查文件是否存在
            if not os.path.exists(package_path):
                logger_manager.error(f"内容包文件不存在: {package_relative_path}")
                return None

            # 检查是否为文件
            if not os.path.isfile(package_path):
                logger_manager.error(f"指定路径不是文件: {package_relative_path}")
                return None

            # 读取并解析JSON文件
            with open(package_path, 'r', encoding='utf-8') as f:
                content_package_data = json.load(f)

            # 创建并返回ContentPackageManager对象
            manager = ContentPackageManager(content_package_data, self)
            logger_manager.info(f"成功创建内容包管理器: {package_relative_path}")
            return manager

        except json.JSONDecodeError as e:
            logger_manager.error(f"内容包JSON格式错误 {package_relative_path}: {e}")
            return None
        except Exception as e:
            logger_manager.exception(f"创建内容包管理器失败 {package_relative_path}: {e}")
            return None
