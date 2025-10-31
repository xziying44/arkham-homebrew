import json
import mimetypes
import os
import platform
import queue
import sys
import threading
import traceback
from typing import Optional
from functools import wraps

from PIL import Image
from flask import Flask, jsonify, request, send_from_directory, Response

from bin.config_directory_manager import config_dir_manager
from bin.file_manager import QuickStart
from bin.gitHub_image import GitHubImageHost
from bin.logger import logger_manager
from bin.workspace_manager import WorkspaceManager
from bin.image_uploader import create_uploader

mimetypes.init()
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/javascript', '.mjs')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('image/svg+xml', '.svg')
mimetypes.add_type('application/json', '.json')
mimetypes.add_type('font/woff', '.woff')
mimetypes.add_type('font/woff2', '.woff2')
mimetypes.add_type('font/ttf', '.ttf')
mimetypes.add_type('font/otf', '.otf')


# 导入日志系统
# ============================================
# 辅助函数：获取用户可写的配置目录
# ============================================
def get_user_config_directory():
    return config_dir_manager.get_global_config_dir()


app = Flask(__name__)
if not hasattr(app, 'window'):
    app.window = None

# 全局状态锁，防止同时打开多个选择对话框
selection_lock = threading.Lock()
is_selecting = False

# 全局实例
quick_start = QuickStart(config_dir_manager.get_recent_directories_file_path())
current_workspace: WorkspaceManager = None
github_image_host = None

# ArkhamDB导入管理器
arkham_builder = {}

# PNP导出实时日志缓存
# 使用字典存储不同任务的日志，key为任务ID，value为日志列表和状态
pnp_export_logs = {}
pnp_export_logs_lock = threading.Lock()

# 记录服务启动
logger_manager.info("=" * 60)
logger_manager.info("阿卡姆印牌姬")
logger_manager.info("=" * 60)


# ================= 错误处理装饰器 =================

def handle_api_error(func):
    """
    API错误处理装饰器
    - 捕获所有异常
    - 返回具体的异常信息给用户
    - 在日志中记录完整的异常栈
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 获取完整的异常堆栈信息
            exc_type = type(e).__name__
            exc_message = str(e)
            exc_traceback = traceback.format_exc()

            # 在日志中记录完整的异常信息
            logger_manager.error(
                f"API错误 [{func.__name__}]: {exc_type}: {exc_message}\n{exc_traceback}"
            )

            # 构建用户友好的错误响应
            error_response = {
                "code": 9999,
                "msg": f"{exc_type}: {exc_message}",
                "data": {
                    "error_type": exc_type,
                    "error_detail": exc_message,
                    "endpoint": func.__name__
                }
            }

            return jsonify(error_response), 500

    return wrapper


def create_response(code=0, msg="操作成功", data=None):
    """创建统一的响应格式"""
    return {
        "code": code,
        "msg": msg,
        "data": data
    }


# ================= 辅助函数 =================

def _handle_directory_selection(selected_directory: Optional[str]):
    """处理选定的目录，无论是来自pywebview还是tkinter"""
    global current_workspace
    if selected_directory:
        logger_manager.info(f"用户选择目录: {selected_directory}")
        # 添加到最近记录
        quick_start.add_recent_directory(selected_directory)
        # 创建工作空间实例
        try:
            current_workspace = WorkspaceManager(selected_directory)
            logger_manager.info(f"工作空间创建成功: {selected_directory}")
            return jsonify(create_response(
                msg="目录选择成功",
                data={"directory": selected_directory}
            ))
        except Exception as e:
            logger_manager.exception(f"创建工作空间失败: {selected_directory}")
            return jsonify(create_response(
                code=1007,
                msg=f"创建工作空间失败: {type(e).__name__}: {str(e)}"
            )), 500
    else:
        logger_manager.info("用户取消了目录选择")
        return jsonify(create_response(
            code=1003,
            msg="用户取消了选择"
        ))


def check_workspace():
    """检查工作空间是否已初始化"""
    if current_workspace is None:
        logger_manager.warning("尝试访问未初始化的工作空间")
        return jsonify(create_response(
            code=3001,
            msg="请先选择或打开工作目录"
        )), 400
    return None


def get_or_create_github_host():
    """获取或创建GitHub图床实例（改进版）"""
    global github_image_host, current_workspace

    if not current_workspace:
        return None, "请先选择工作空间"

    # 如果全局对象存在且已认证，直接返回
    if github_image_host and github_image_host.is_authenticated:
        return github_image_host, None

    # 获取GitHub配置进行静默登录
    config = current_workspace.get_config()
    github_token = config.get("github_token", "")

    if not github_token:
        return None, "请先配置GitHub Token"

    # 创建新实例并尝试静默登录
    temp_github_host = GitHubImageHost()
    if not temp_github_host.silent_login(github_token):
        return None, temp_github_host.get_last_error()

    # 只有登录成功后才赋值给全局变量（新登录替换旧登录）
    github_image_host = temp_github_host
    return github_image_host, None


# ================= 快速开始相关接口 =================

@app.route('/api/select-directory', methods=['GET'])
@handle_api_error
def api_select_directory():
    """API接口：打开目录选择对话框"""
    global is_selecting
    logger_manager.info("收到目录选择请求")
    # 检测 Android 环境
    IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ

    if IS_ANDROID:
        logger_manager.debug("Android 环境：使用原生目录选择器")

        # 防止重复调用
        if not selection_lock.acquire(blocking=False):
            logger_manager.warning("目录选择操作已在进行中")
            return jsonify(create_response(
                code=1001,
                msg="目录选择操作正在进行中，请稍后再试"
            )), 409

        try:
            is_selecting = True
            result_queue = queue.Queue()

            def on_directory_selected(path):
                """目录选择回调"""
                logger_manager.info(f"Android 目录选择回调: {path}")
                result_queue.put(path)

            # 调用 Android 目录选择器
            if hasattr(app, 'android_directory_picker'):
                app.android_directory_picker.pick_directory(on_directory_selected)

                # 等待用户选择（最多60秒）
                try:
                    selected_path = result_queue.get(timeout=60)
                    return _handle_directory_selection(selected_path)
                except queue.Empty:
                    logger_manager.error("Android 目录选择超时")
                    return jsonify(create_response(
                        code=1002,
                        msg="目录选择超时，请重试"
                    )), 408
            else:
                logger_manager.error("Android 目录选择器未初始化")
                # 降级方案：使用默认路径
                from android.storage import primary_external_storage_path
                default_path = os.path.join(
                    primary_external_storage_path(),
                    "ArkhamCardMaker"
                )
                os.makedirs(default_path, exist_ok=True)
                return _handle_directory_selection(default_path)

        finally:
            is_selecting = False
            selection_lock.release()

    # 判断是否在 pywebview 环境中运行
    if hasattr(app, 'window') and app.window:
        import webview
        # --- pywebview 模式 ---
        logger_manager.debug("使用 pywebview 模式打开目录选择对话框")
        result = app.window.create_file_dialog(webview.FOLDER_DIALOG)
        selected_dir = result[0] if result and len(result) > 0 else None
        return _handle_directory_selection(selected_dir)
    else:
        # --- server 模式 (回退到 tkinter) ---
        logger_manager.debug("使用 tkinter 模式打开目录选择对话框")

        if not selection_lock.acquire(blocking=False):
            logger_manager.warning("目录选择操作已在进行中")
            return jsonify(create_response(
                code=1001,
                msg="目录选择操作正在进行中，请稍后再试"
            )), 409
        try:
            is_selecting = True
            result_queue = queue.Queue()

            def worker():
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.lift()
                root.attributes("-topmost", True)
                try:
                    directory = filedialog.askdirectory(
                        title="请选择目录 (调试模式)",
                        initialdir=os.getcwd()
                    )
                    result_queue.put(('success', directory))
                except Exception as e:
                    logger_manager.exception("tkinter 目录选择对话框出错")
                    result_queue.put(('error', str(e)))
                finally:
                    root.destroy()

            thread = threading.Thread(target=worker, daemon=True)
            thread.start()
            thread.join(timeout=300)

            if thread.is_alive():
                logger_manager.error("目录选择操作超时")
                return jsonify(create_response(code=1002, msg="操作超时，请重试")), 408

            try:
                status, result = result_queue.get_nowait()
                if status == 'success':
                    return _handle_directory_selection(result)
                else:
                    logger_manager.error(f"选择目录时出错: {result}")
                    return jsonify(create_response(code=1004, msg=f"选择目录时出错: {result}")), 500
            except queue.Empty:
                logger_manager.error("未能获取选择结果")
                return jsonify(create_response(code=1005, msg="未能获取选择结果")), 500
        finally:
            is_selecting = False
            selection_lock.release()


@app.route('/api/recent-directories', methods=['GET'])
@handle_api_error
def get_recent_directories():
    """获取最近打开的目录列表"""
    logger_manager.debug("获取最近目录列表")
    records = quick_start.get_recent_directories()
    return jsonify(create_response(
        msg="获取最近目录成功",
        data={"directories": records}
    ))


@app.route('/api/recent-directories', methods=['DELETE'])
@handle_api_error
def clear_recent_directories():
    """清空最近目录记录"""
    logger_manager.info("清空最近目录记录")
    success = quick_start.clear_recent_directories()
    if success:
        logger_manager.info("最近目录记录已清空")
        return jsonify(create_response(msg="清空最近目录成功"))
    else:
        logger_manager.error("清空最近目录失败")
        return jsonify(create_response(
            code=2002,
            msg="清空最近目录失败"
        )), 500


@app.route('/api/recent-directories/<path:directory_path>', methods=['DELETE'])
@handle_api_error
def remove_recent_directory(directory_path):
    """移除指定的最近目录"""
    logger_manager.info(f"移除最近目录: {directory_path}")
    success = quick_start.remove_recent_directory(directory_path)
    if success:
        logger_manager.info(f"目录已移除: {directory_path}")
        return jsonify(create_response(msg="移除目录成功"))
    else:
        logger_manager.warning(f"目录不存在或移除失败: {directory_path}")
        return jsonify(create_response(
            code=2004,
            msg="目录不存在或移除失败"
        )), 404


@app.route('/api/open-workspace', methods=['POST'])
@handle_api_error
def open_workspace():
    """打开指定的工作空间"""
    global current_workspace

    data = request.get_json()
    if not data or 'directory' not in data:
        return jsonify(create_response(
            code=2006,
            msg="请提供目录路径"
        )), 400

    directory = data['directory']
    logger_manager.info(f"打开工作空间: {directory}")

    if not os.path.exists(directory):
        logger_manager.warning(f"目录不存在: {directory}")
        return jsonify(create_response(
            code=2007,
            msg="目录不存在"
        )), 404

    # 创建工作空间实例
    current_workspace = WorkspaceManager(directory)

    # 添加到最近记录
    quick_start.add_recent_directory(directory)

    logger_manager.info(f"工作空间已打开: {directory}")
    return jsonify(create_response(
        msg="工作空间打开成功",
        data={"directory": directory}
    ))


# ================= 工作空间相关接口 =================

@app.route('/api/file-tree', methods=['GET'])
@handle_api_error
def get_file_tree():
    """获取文件树"""
    error_response = check_workspace()
    if error_response:
        return error_response

    include_hidden = request.args.get('include_hidden', 'false').lower() == 'true'
    logger_manager.debug(f"获取文件树, include_hidden={include_hidden}")

    file_tree = current_workspace.get_file_tree(include_hidden)

    return jsonify(create_response(
        msg="获取文件树成功",
        data={"fileTree": file_tree}
    ))


@app.route('/api/create-directory', methods=['POST'])
@handle_api_error
def create_directory():
    """创建目录"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify(create_response(
            code=3003,
            msg="请提供目录名称"
        )), 400

    dir_name = data['name']
    parent_path = data.get('parent_path')

    logger_manager.info(f"创建目录: {dir_name}, parent: {parent_path}")

    success = current_workspace.create_directory(dir_name, parent_path)

    if success:
        logger_manager.info(f"目录创建成功: {dir_name}")
        return jsonify(create_response(msg="目录创建成功"))
    else:
        logger_manager.error(f"目录创建失败: {dir_name}")
        return jsonify(create_response(
            code=3004,
            msg="目录创建失败"
        )), 500


@app.route('/api/create-file', methods=['POST'])
@handle_api_error
def create_file():
    """创建文件"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify(create_response(
            code=3006,
            msg="请提供文件名称"
        )), 400

    file_name = data['name']
    content = data.get('content', '')
    parent_path = data.get('parent_path')

    logger_manager.info(f"创建文件: {file_name}, parent: {parent_path}")

    success = current_workspace.create_file(file_name, content, parent_path)

    if success:
        logger_manager.info(f"文件创建成功: {file_name}")
        return jsonify(create_response(msg="文件创建成功"))
    else:
        logger_manager.error(f"文件创建失败: {file_name}")
        return jsonify(create_response(
            code=3007,
            msg="文件创建失败"
        )), 500


@app.route('/api/rename-item', methods=['PUT'])
@handle_api_error
def rename_item():
    """重命名文件或目录"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'old_path' not in data or 'new_name' not in data:
        return jsonify(create_response(
            code=3009,
            msg="请提供原路径和新名称"
        )), 400

    old_path = data['old_path']
    new_name = data['new_name']

    logger_manager.info(f"重命名: {old_path} -> {new_name}")

    success = current_workspace.rename_item(old_path, new_name)

    if success:
        logger_manager.info(f"重命名成功: {old_path} -> {new_name}")
        return jsonify(create_response(msg="重命名成功"))
    else:
        logger_manager.warning(f"重命名失败: {old_path} -> {new_name}")
        return jsonify(create_response(
            code=3010,
            msg="重命名失败，可能是目标名称已存在或路径无效"
        )), 400


@app.route('/api/delete-item', methods=['DELETE'])
@handle_api_error
def delete_item():
    """删除文件或目录"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'path' not in data:
        return jsonify(create_response(
            code=3012,
            msg="请提供要删除的路径"
        )), 400

    item_path = data['path']

    logger_manager.info(f"删除项目: {item_path}")

    success = current_workspace.delete_item(item_path)

    if success:
        logger_manager.info(f"删除成功: {item_path}")
        return jsonify(create_response(msg="删除成功"))
    else:
        logger_manager.warning(f"删除失败: {item_path}")
        return jsonify(create_response(
            code=3013,
            msg="删除失败，路径可能无效或不存在"
        )), 400


@app.route('/api/file-content', methods=['GET'])
@handle_api_error
def get_file_content():
    """获取文件内容"""
    error_response = check_workspace()
    if error_response:
        return error_response

    file_path = request.args.get('path')
    if not file_path:
        return jsonify(create_response(
            code=3015,
            msg="请提供文件路径"
        )), 400

    logger_manager.debug(f"获取文件内容: {file_path}")

    content = current_workspace.get_file_content(file_path)

    if content is not None:
        return jsonify(create_response(
            msg="获取文件内容成功",
            data={"content": content}
        ))
    else:
        logger_manager.warning(f"文件不存在或无法读取: {file_path}")
        return jsonify(create_response(
            code=3016,
            msg="文件不存在或无法读取"
        )), 404


@app.route('/api/file-content', methods=['PUT'])
@handle_api_error
def save_file_content():
    """保存文件内容"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'path' not in data or 'content' not in data:
        return jsonify(create_response(
            code=3018,
            msg="请提供文件路径和内容"
        )), 400

    file_path = data['path']
    content = data['content']

    logger_manager.info(f"保存文件: {file_path}")

    success = current_workspace.save_file_content(file_path, content)

    if success:
        logger_manager.info(f"文件保存成功: {file_path}")
        return jsonify(create_response(msg="保存文件成功"))
    else:
        logger_manager.error(f"文件保存失败: {file_path}")
        return jsonify(create_response(
            code=3019,
            msg="保存文件失败"
        )), 500


@app.route('/api/image-content', methods=['GET'])
@handle_api_error
def get_image_content():
    """获取图片内容（base64格式）"""
    error_response = check_workspace()
    if error_response:
        return error_response

    image_path = request.args.get('path')
    if not image_path:
        return jsonify(create_response(
            code=5001,
            msg="请提供图片路径"
        )), 400

    logger_manager.debug(f"获取图片内容: {image_path}")

    image_base64 = current_workspace.get_image_as_base64(image_path)

    if image_base64 is not None:
        return jsonify(create_response(
            msg="获取图片内容成功",
            data={"content": image_base64}
        ))
    else:
        logger_manager.warning(f"图片文件不存在或无法读取: {image_path}")
        return jsonify(create_response(
            code=5002,
            msg="图片文件不存在或无法读取"
        )), 404


@app.route('/api/file-info', methods=['GET'])
@handle_api_error
def get_file_info():
    """获取文件信息"""
    error_response = check_workspace()
    if error_response:
        return error_response

    file_path = request.args.get('path')
    if not file_path:
        return jsonify(create_response(
            code=5004,
            msg="请提供文件路径"
        )), 400

    logger_manager.debug(f"获取文件信息: {file_path}")

    file_info = current_workspace.get_file_info(file_path)

    if file_info is not None:
        return jsonify(create_response(
            msg="获取文件信息成功",
            data={"fileInfo": file_info}
        ))
    else:
        logger_manager.warning(f"文件不存在或无法访问: {file_path}")
        return jsonify(create_response(
            code=5005,
            msg="文件不存在或无法访问"
        )), 404


@app.route('/api/status', methods=['GET'])
@handle_api_error
def get_status():
    """获取服务状态"""
    return jsonify(create_response(
        msg="服务正常运行",
        data={
            "service": "file-manager",
            "version": "2.0.0",
            "is_selecting": is_selecting,
            "has_workspace": current_workspace is not None,
            "workspace_path": current_workspace.workspace_path if current_workspace else None
        }
    ))


# ================= 卡牌生成相关接口 =================

@app.route('/api/generate-card', methods=['POST'])
@handle_api_error
def generate_card():
    """生成卡图"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'json_data' not in data:
        return jsonify(create_response(
            code=4001,
            msg="请提供卡牌JSON数据"
        )), 400

    json_data = data['json_data']
    card_name = json_data.get('name', 'Unknown')
    logger_manager.info(f"生成卡图: {card_name}")

    # 处理引用卡牌
    json_data = current_workspace.resolve_reference_card(json_data, allow_reference=True)

    # 检查版本号判断是否为双面卡牌
    version = json_data.get('version', '')

    card = None
    card_image = None
    back_image = None

    if version == "2.0":
        logger_manager.debug("生成双面卡牌")
        # 双面卡牌处理
        double_sided_result = current_workspace.generate_double_sided_card_image(json_data)
        if double_sided_result is None:
            logger_manager.error(f"生成双面卡图失败: {card_name}")
            return jsonify(create_response(
                code=4002,
                msg="生成双面卡图失败"
            )), 500

        front_card = double_sided_result['front']
        back_card = double_sided_result['back']

        card_image = front_card.image if front_card else None
        back_image = back_card.image if back_card else None
        card = front_card
    else:
        logger_manager.debug("生成单面卡牌")
        # 单面卡牌处理
        card = current_workspace.generate_card_image(json_data)
        card_image = card.image

        # 判断是否为勘误模式
        if os.environ.get('APP_MODE', 'normal') == 'check':
            try:
                logger_manager.debug("勘误模式: 生成对比图")
                original_image = current_workspace.get_card_base64(json_data)
                # 如果picture_path为str则读取PIL图片
                if isinstance(original_image, str):
                    original_image = Image.open(original_image)

                # 处理图片旋转
                if card_image.width > card_image.height and original_image.width < original_image.height:
                    original_image = original_image.rotate(90, expand=True)

                # 缩放到图片大小
                original_image = original_image.resize((card_image.width, card_image.height))

                # 判断是否为横向图片
                if card_image.width > card_image.height:
                    # 横向图片：上下拼接（原图在上，生成图在下）
                    card_errata = Image.new('RGB', (card_image.width, card_image.height * 2), (255, 255, 255))
                    card_errata.paste(original_image, (0, 0))
                    card_errata.paste(card_image, (0, card_image.height))
                else:
                    # 纵向图片：左右拼接（原图在左，生成图在右）
                    card_errata = Image.new('RGB', (card_image.width * 2, card_image.height), (255, 255, 255))
                    card_errata.paste(original_image, (0, 0))
                    card_errata.paste(card_image, (card_image.width, 0))

                card_image = card_errata
            except Exception as e:
                logger_manager.warning(f"勘误模式生成对比图失败: {str(e)}")

    if card_image is None:
        logger_manager.error(f"生成卡图失败: {card_name}")
        return jsonify(create_response(
            code=4002,
            msg="生成卡图失败"
        )), 500

    # 将图片转换为base64返回
    import io
    import base64

    img_buffer = io.BytesIO()
    card_image.save(img_buffer, format='PNG')
    img_str = base64.b64encode(img_buffer.getvalue()).decode()

    # 构建响应数据
    response_data = {
        "image": f"data:image/png;base64,{img_str}",
        "box_position": card.get_upgrade_card_box_position() if card else []
    }

    # 如果有背面图片，也转换为base64并添加到响应中
    if back_image is not None:
        back_buffer = io.BytesIO()
        back_image.save(back_buffer, format='PNG')
        back_str = base64.b64encode(back_buffer.getvalue()).decode()
        response_data["back_image"] = f"data:image/png;base64,{back_str}"

    logger_manager.info(f"卡图生成成功: {card_name}")
    return jsonify(create_response(
        msg="生成卡图成功",
        data=response_data
    ))


@app.route('/api/save-card', methods=['POST'])
@handle_api_error
def save_card():
    """保存卡图到文件（支持双面卡牌、多种格式和质量设置，以及内容包导出旋转）"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    required_fields = ['json_data', 'filename']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify(create_response(
            code=4004,
            msg=f"请提供必要字段: {', '.join(missing_fields)}"
        )), 400

    json_data = data['json_data']
    filename = data['filename']
    parent_path = data.get('parent_path')

    # 新增参数：导出格式和质量
    export_format = data.get('format', 'JPG').upper()
    quality = data.get('quality', 95)
    rotate_landscape = data.get('rotate_landscape', False)

    logger_manager.info(f"保存卡图: {filename}, 格式: {export_format}, 质量: {quality}")

    # 验证格式参数
    if export_format not in ['PNG', 'JPG']:
        return jsonify(create_response(
            code=4007,
            msg="导出格式只支持PNG和JPG"
        )), 400

    # 验证质量参数
    if not isinstance(quality, int) or not (1 <= quality <= 100):
        return jsonify(create_response(
            code=4008,
            msg="图片质量必须是1-100之间的整数"
        )), 400

    # 保存卡图（支持双面卡牌、格式参数和旋转横向图片）
    saved_files = current_workspace.save_card_image_enhanced(
        json_data, filename, parent_path, export_format, quality, rotate_landscape
    )

    if saved_files and len(saved_files) > 0:
        logger_manager.info(f"卡图保存成功: {saved_files}")
        return jsonify(create_response(
            msg="保存卡图成功",
            data={"saved_files": saved_files}
        ))
    else:
        logger_manager.error(f"保存卡图失败: {filename}")
        return jsonify(create_response(
            code=4005,
            msg="保存卡图失败"
        )), 500


# ================= 配置项相关接口 =================

@app.route('/api/config', methods=['GET'])
@handle_api_error
def get_config():
    """获取配置项"""
    if current_workspace is None:
        # ✅ 修复：使用用户可写的配置目录
        config_dir = get_user_config_directory()
        temp_workspace = WorkspaceManager(config_dir)
        config = temp_workspace.get_global_config()
    else:
        config = current_workspace.get_config()
    logger_manager.debug("获取配置成功")
    return jsonify(create_response(
        msg="获取配置成功",
        data={"config": config}
    ))


@app.route('/api/config', methods=['PUT'])
@handle_api_error
def save_config():
    """保存配置项"""
    data = request.get_json()
    if not data or 'config' not in data:
        return jsonify(create_response(
            code=6002,
            msg="请提供配置数据"
        )), 400
    config = data['config']
    logger_manager.info("保存配置")
    if current_workspace is None:
        # ✅ 修复：使用用户可写的配置目录
        config_dir = get_user_config_directory()
        temp_workspace = WorkspaceManager(config_dir)
        success = temp_workspace.save_global_config(config)
    else:
        success = current_workspace.save_config(config)
    if success:
        logger_manager.info("配置保存成功")
        return jsonify(create_response(msg="保存配置成功"))
    else:
        logger_manager.error("配置保存失败")
        return jsonify(create_response(
            code=6003,
            msg="保存配置失败"
        )), 500


@app.route('/api/encounter-groups', methods=['GET'])
@handle_api_error
def get_encounter_groups():
    """获取遭遇组列表"""
    error_response = check_workspace()
    if error_response:
        return error_response

    logger_manager.debug("获取遭遇组列表")
    encounter_groups = current_workspace.get_encounter_groups()
    return jsonify(create_response(
        msg="获取遭遇组列表成功",
        data={"encounter_groups": encounter_groups}
    ))


@app.route('/api/content-package/encounter-groups', methods=['POST'])
@handle_api_error
def get_content_package_encounter_groups():
    """获取内容包中的遭遇组图片"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'package_path' not in data:
        return jsonify(create_response(
            code=16001,
            msg="请提供内容包文件路径"
        )), 400

    package_path = data['package_path']
    workspace_path = current_workspace.workspace_path

    logger_manager.info(f"获取内容包遭遇组: {package_path}")

    # 验证内容包文件路径
    if not current_workspace._is_path_in_workspace(package_path):
        logger_manager.warning(f"内容包路径不在工作空间内: {package_path}")
        return jsonify(create_response(
            code=16002,
            msg="内容包路径不在工作空间内"
        )), 400

    abs_package_path = current_workspace._get_absolute_path(package_path)
    if not os.path.exists(abs_package_path):
        logger_manager.warning(f"内容包文件不存在: {package_path}")
        return jsonify(create_response(
            code=16003,
            msg="内容包文件不存在"
        )), 404

    try:
        # 读取内容包文件
        with open(abs_package_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)

        # 创建内容包管理器
        from bin.content_package_manager import ContentPackageManager
        package_manager = ContentPackageManager(package_data, current_workspace)

        # 获取遭遇组
        encounter_groups = package_manager.get_encounter_groups_from_package()

        logger_manager.info(f"内容包 {package_path} 找到 {len(encounter_groups)} 个遭遇组")

        return jsonify(create_response(
            msg="获取内容包遭遇组成功",
            data={
                "workspace_path": workspace_path,
                "package_path": package_path,
                "encounter_groups_count": len(encounter_groups),
                "encounter_groups": encounter_groups,
                "logs": package_manager.logs.copy()
            }
        ))

    except Exception as e:
        logger_manager.exception(f"获取内容包遭遇组失败: {e}")
        return jsonify(create_response(
            code=16004,
            msg=f"获取遭遇组失败: {type(e).__name__}: {str(e)}"
        )), 500


@app.route('/api/content-package/all-encounter-groups', methods=['GET'])
@handle_api_error
def get_all_content_package_encounter_groups():
    """获取工作空间中所有内容包的遭遇组图片"""
    error_response = check_workspace()
    if error_response:
        return error_response

    workspace_path = current_workspace.workspace_path
    logger_manager.info(f"获取工作空间中所有内容包的遭遇组: {workspace_path}")

    try:
        # 查找所有.pack文件
        content_packages = []
        for root, dirs, files in os.walk(workspace_path):
            for file in files:
                if file.endswith('.pack'):
                    relative_path = os.path.relpath(os.path.join(root, file), workspace_path)
                    content_packages.append(relative_path)

        if not content_packages:
            logger_manager.warning("未找到任何内容包文件")
            return jsonify(create_response(
                code=16005,
                msg="未找到任何内容包文件"
            )), 404

        logger_manager.info(f"找到 {len(content_packages)} 个内容包文件")

        # 合并所有遭遇组
        all_encounter_groups = {}
        package_results = []

        for pack_file in content_packages:
            try:
                # 读取内容包文件
                pack_path = current_workspace._get_absolute_path(pack_file)
                with open(pack_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)

                # 创建内容包管理器
                from bin.content_package_manager import ContentPackageManager
                package_manager = ContentPackageManager(package_data, current_workspace)

                # 获取遭遇组
                encounter_groups = package_manager.get_encounter_groups_from_package()

                # 合并到总结果中（去重）
                for group in encounter_groups:
                    group_name = group['name']
                    if group_name not in all_encounter_groups:
                        all_encounter_groups[group_name] = group

                package_results.append({
                    "package": pack_file,
                    "encounter_groups_count": len(encounter_groups),
                    "logs": package_manager.logs.copy()
                })

                logger_manager.info(f"内容包 {pack_file} 找到 {len(encounter_groups)} 个遭遇组")

            except Exception as e:
                logger_manager.error(f"处理内容包 {pack_file} 时出错: {e}")
                package_results.append({
                    "package": pack_file,
                    "encounter_groups_count": 0,
                    "error": str(e)
                })
                continue

        # 转换为列表
        result_encounter_groups = list(all_encounter_groups.values())

        logger_manager.info(f"总共获取到 {len(result_encounter_groups)} 个唯一遭遇组")

        return jsonify(create_response(
            msg="获取所有内容包遭遇组成功",
            data={
                "workspace_path": workspace_path,
                "total_encounter_groups": len(result_encounter_groups),
                "encounter_groups": result_encounter_groups,
                "package_results": package_results,
                "packages_processed": len(content_packages)
            }
        ))

    except Exception as e:
        logger_manager.exception(f"获取所有内容包遭遇组失败: {e}")
        return jsonify(create_response(
            code=16006,
            msg=f"获取遭遇组失败: {type(e).__name__}: {str(e)}"
        )), 500


# ================= 牌库导出相关接口 =================

@app.route('/api/export-deck-image', methods=['POST'])
@handle_api_error
def export_deck_image():
    """导出牌库图片"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'deck_name' not in data:
        return jsonify(create_response(
            code=8001,
            msg="请提供牌库名称"
        )), 400

    deck_name = data['deck_name']
    export_format = data.get('format', 'PNG').upper()
    quality = data.get('quality', 95)

    logger_manager.info(f"导出牌库图片: {deck_name}, 格式: {export_format}, 质量: {quality}")

    if export_format not in ['JPG', 'PNG']:
        return jsonify(create_response(
            code=8002,
            msg="导出格式只支持JPG和PNG"
        )), 400

    if not (1 <= quality <= 100):
        return jsonify(create_response(
            code=8003,
            msg="图片质量必须在1-100之间"
        )), 400

    # 导出牌库图片
    success = current_workspace.export_deck_image(deck_name, export_format, quality)

    if success:
        logger_manager.info(f"牌库图片导出成功: {deck_name}")
        return jsonify(create_response(msg="牌库图片导出成功"))
    else:
        logger_manager.error(f"牌库图片导出失败: {deck_name}")
        return jsonify(create_response(
            code=8004,
            msg="牌库图片导出失败"
        )), 500


@app.route('/api/export-deck-pdf', methods=['POST'])
@handle_api_error
def export_deck_pdf():
    """导出牌库PDF"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'deck_name' not in data:
        return jsonify(create_response(
            code=8006,
            msg="请提供牌库名称"
        )), 400

    deck_name = data['deck_name']
    pdf_filename = data.get('pdf_filename', None)

    logger_manager.info(f"导出牌库PDF: {deck_name}")

    # 导出牌库PDF
    success = current_workspace.export_deck_pdf(deck_name, pdf_filename)

    if success:
        # 构建返回的文件路径信息
        deck_base_name = os.path.splitext(deck_name)[0]
        final_pdf_filename = pdf_filename or f"{deck_base_name}.pdf"

        logger_manager.info(f"牌库PDF导出成功: {final_pdf_filename}")
        return jsonify(create_response(
            msg="牌库PDF导出成功",
            data={
                "pdf_filename": final_pdf_filename,
                "deck_name": deck_name
            }
        ))
    else:
        logger_manager.error(f"牌库PDF导出失败: {deck_name}")
        return jsonify(create_response(
            code=8007,
            msg="牌库PDF导出失败"
        )), 500


@app.route('/api/open-directory', methods=['POST'])
@handle_api_error
def open_directory():
    """打开指定目录"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'directory_path' not in data:
        return jsonify(create_response(
            code=9001,
            msg="请提供目录路径"
        )), 400

    directory_path = data['directory_path']
    logger_manager.info(f"打开目录: {directory_path}")

    # 打开目录
    success = current_workspace.open_directory_in_explorer(directory_path)

    if success:
        logger_manager.info(f"目录已在资源管理器中打开: {directory_path}")
        return jsonify(create_response(msg="目录已在资源管理器中打开"))
    else:
        logger_manager.warning(f"打开目录失败: {directory_path}")
        return jsonify(create_response(
            code=9002,
            msg="打开目录失败，目录可能不存在"
        )), 400


# ================= GitHub图床相关接口 =================

@app.route('/api/github/login', methods=['POST'])
@handle_api_error
def github_login():
    """GitHub登录"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify(create_response(
            code=10001,
            msg="请提供GitHub Token"
        )), 400

    token = data['token']
    logger_manager.info("GitHub登录请求")

    # 创建新的GitHub图床实例
    temp_github_host = GitHubImageHost()

    # 尝试登录
    if not temp_github_host.login(token):
        logger_manager.error(f"GitHub登录失败: {temp_github_host.get_last_error()}")
        return jsonify(create_response(
            code=10002,
            msg=temp_github_host.get_last_error()
        )), 400

    # 只有登录成功后才赋值给全局变量（新登录替换旧登录）
    global github_image_host
    github_image_host = temp_github_host

    logger_manager.info(f"GitHub登录成功: {github_image_host.username}")
    return jsonify(create_response(
        msg="GitHub登录成功",
        data={
            "username": github_image_host.username
        }
    ))


@app.route('/api/github/logout', methods=['POST'])
@handle_api_error
def github_logout():
    """GitHub登出"""
    global github_image_host
    github_image_host = None
    logger_manager.info("GitHub登出成功")
    return jsonify(create_response(msg="GitHub登出成功"))


@app.route('/api/github/repositories', methods=['GET'])
@handle_api_error
def get_github_repositories():
    """获取GitHub仓库列表"""
    error_response = check_workspace()
    if error_response:
        return error_response

    logger_manager.debug("获取GitHub仓库列表")

    # 获取或创建GitHub实例（如果全局变量为空会自动静默登录）
    github_host, error_msg = get_or_create_github_host()
    if not github_host:
        logger_manager.warning(f"GitHub未登录: {error_msg}")
        return jsonify(create_response(
            code=10004,
            msg=error_msg
        )), 400

    # 获取仓库列表
    repositories, error_msg = github_host.list_repositories()
    if error_msg:
        logger_manager.error(f"获取仓库列表失败: {error_msg}")
        return jsonify(create_response(
            code=10005,
            msg=error_msg
        )), 500

    logger_manager.debug(f"获取到 {len(repositories)} 个仓库")
    return jsonify(create_response(
        msg="获取仓库列表成功",
        data={"repositories": repositories}
    ))


@app.route('/api/github/upload', methods=['POST'])
@handle_api_error
def github_upload_image():
    """上传图片到GitHub"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'image_path' not in data:
        return jsonify(create_response(
            code=10007,
            msg="请提供图片路径"
        )), 400

    image_path = data['image_path']
    logger_manager.info(f"上传图片到GitHub: {image_path}")

    # 获取或创建GitHub实例（如果全局变量为空会自动静默登录）
    github_host, error_msg = get_or_create_github_host()
    if not github_host:
        logger_manager.warning(f"GitHub未登录: {error_msg}")
        return jsonify(create_response(
            code=10008,
            msg=error_msg
        )), 400

    # 获取配置
    config = current_workspace.get_config()
    repo_name = config.get("github_repo", "")
    branch = config.get("github_branch", "main")
    folder = config.get("github_folder", "images")

    if not repo_name:
        logger_manager.warning("GitHub仓库未配置")
        return jsonify(create_response(
            code=10009,
            msg="请先在配置中设置GitHub仓库"
        )), 400

    # 转换为绝对路径
    if not current_workspace._is_path_in_workspace(image_path):
        logger_manager.warning(f"图片路径无效: {image_path}")
        return jsonify(create_response(
            code=10010,
            msg="图片路径无效"
        )), 400

    abs_image_path = current_workspace._get_absolute_path(image_path)

    # 上传图片
    download_url, error_msg = github_host.upload_image(
        image_path=abs_image_path,
        repo_name=repo_name,
        branch=branch,
        folder=folder
    )

    if error_msg:
        logger_manager.error(f"上传图片失败: {error_msg}")
        return jsonify(create_response(
            code=10011,
            msg=error_msg
        )), 500

    logger_manager.info(f"图片上传成功: {download_url}")
    return jsonify(create_response(
        msg="图片上传成功",
        data={
            "url": download_url,
            "repo": repo_name,
            "branch": branch,
            "folder": folder
        }
    ))


@app.route('/api/github/status', methods=['GET'])
@handle_api_error
def get_github_status():
    """获取GitHub状态"""
    error_response = check_workspace()
    if error_response:
        return error_response

    status = {
        "is_logged_in": False,
        "username": None,
        "has_config": False,
        "last_error": ""
    }

    # 检查配置
    config = current_workspace.get_config()
    if config.get("github_token") and config.get("github_repo"):
        status["has_config"] = True

    # 检查登录状态
    global github_image_host
    if github_image_host and github_image_host.is_authenticated:
        github_status = github_image_host.get_status()
        status["is_logged_in"] = github_status["is_authenticated"]
        status["username"] = github_status["username"]
        status["last_error"] = github_status["last_error"]

    logger_manager.debug(f"GitHub状态: {status}")
    return jsonify(create_response(
        msg="获取GitHub状态成功",
        data={"status": status}
    ))


# ================= TTS导出相关接口 =================

@app.route('/api/export-tts', methods=['POST'])
@handle_api_error
def export_tts():
    """导出TTS物品"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'deck_name' not in data or 'face_url' not in data or 'back_url' not in data:
        return jsonify(create_response(
            code=11001,
            msg="请提供牌库名称、正面URL和背面URL"
        )), 400

    deck_name = data['deck_name']
    face_url = data['face_url']
    back_url = data['back_url']

    logger_manager.info(f"导出TTS物品: {deck_name}")

    # 验证URL格式（简单验证）
    if not (face_url.startswith('http://') or face_url.startswith('https://')):
        return jsonify(create_response(
            code=11002,
            msg="正面URL格式无效"
        )), 400

    if not (back_url.startswith('http://') or back_url.startswith('https://')):
        return jsonify(create_response(
            code=11003,
            msg="背面URL格式无效"
        )), 400

    # 导出TTS物品
    success = current_workspace.export_deck_to_tts(deck_name, face_url, back_url)

    if success:
        logger_manager.info(f"TTS物品导出成功: {deck_name}")
        return jsonify(create_response(msg="TTS物品导出成功"))
    else:
        logger_manager.error(f"TTS物品导出失败: {deck_name}")
        return jsonify(create_response(
            code=11004,
            msg="TTS物品导出失败"
        )), 500


@app.route('/api/content-package/export-tts', methods=['POST'])
@handle_api_error
def export_content_package_to_tts():
    """导出内容包到TTS物品"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'package_path' not in data:
        return jsonify(create_response(
            code=14001,
            msg="请提供内容包文件路径"
        )), 400

    package_path = data['package_path']
    logger_manager.info(f"导出内容包到TTS: {package_path}")

    # 调用工作空间的导出方法
    result = current_workspace.export_content_package_to_tts(package_path)

    if result.get("success"):
        logger_manager.info(f"内容包导出TTS成功: {package_path}")
        return jsonify(create_response(
            msg="内容包导出TTS物品成功",
            data={
                "logs": result.get("logs", []),
                "tts_path": result.get("tts_path"),
                "local_path": result.get("local_path")
            }
        ))
    else:
        logger_manager.error(f"内容包导出TTS失败: {result.get('error', 'Unknown error')}")
        return jsonify(create_response(
            code=14002,
            msg=result.get("error", "内容包导出TTS物品失败"),
            data={"logs": result.get("logs", [])}
        )), 500


@app.route('/api/content-package/export-arkhamdb', methods=['POST'])
@handle_api_error
def export_content_package_to_arkhamdb():
    """导出内容包到ArkhamDB格式"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'package_path' not in data:
        return jsonify(create_response(
            code=14003,
            msg="请提供内容包文件路径"
        )), 400

    package_path = data['package_path']
    output_path = data.get('output_path')  # 可选的输出路径

    logger_manager.info(f"导出内容包到ArkhamDB: {package_path}")

    # 调用工作空间的导出方法
    result = current_workspace.export_content_package_to_arkhamdb(package_path, output_path)

    if result.get("success"):
        logger_manager.info(f"内容包导出ArkhamDB成功: {package_path}")
        return jsonify(create_response(
            msg="内容包导出ArkhamDB格式成功",
            data={
                "arkhamdb_data": result.get("arkhamdb_data"),
                "output_path": result.get("output_path"),
                "logs": result.get("logs", [])
            }
        ))
    else:
        logger_manager.error(f"内容包导出ArkhamDB失败: {result.get('error', 'Unknown error')}")
        return jsonify(create_response(
            code=14004,
            msg=result.get("error", "内容包导出ArkhamDB格式失败"),
            data={"logs": result.get("logs", [])}
        )), 500


@app.route('/api/content-package/generate-numbering-plan', methods=['POST'])
@handle_api_error
def generate_card_numbering_plan():
    """生成卡牌编号方案"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'package_path' not in data:
        return jsonify(create_response(
            code=14006,
            msg="请提供内容包文件路径"
        )), 400

    package_path = data['package_path']
    no_encounter_position = data.get('no_encounter_position', 'before')  # 'before' 或 'after'
    start_number = data.get('start_number', 1)
    footer_copyright = data.get('footer_copyright', '')
    footer_icon_path = data.get('footer_icon_path', '')

    logger_manager.info(f"生成卡牌编号方案: {package_path}")

    # 获取内容包
    content_package = current_workspace.get_content_package(package_path)

    # 调用工作空间的编号方法
    result = content_package.generate_card_numbering_plan(
        no_encounter_position,
        start_number,
        footer_copyright,
        footer_icon_path
    )

    if result.get("success"):
        logger_manager.info(f"卡牌编号方案生成成功: {package_path}")
        return jsonify(create_response(
            msg="卡牌编号方案生成成功",
            data={
                "numbering_plan": result.get("numbering_plan"),
                "logs": result.get("logs", [])
            }
        ))
    else:
        logger_manager.error(f"卡牌编号方案生成失败: {result.get('error', 'Unknown error')}")
        return jsonify(create_response(
            code=14007,
            msg=result.get("error", "卡牌编号方案生成失败"),
            data={"logs": result.get("logs", [])}
        )), 500


@app.route('/api/content-package/apply-numbering', methods=['POST'])
@handle_api_error
def apply_card_numbering():
    """应用卡牌编号方案"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'package_path' not in data or 'numbering_plan' not in data:
        return jsonify(create_response(
            code=14008,
            msg="请提供内容包文件路径和编号方案"
        )), 400

    package_path = data['package_path']
    numbering_plan = data['numbering_plan']

    logger_manager.info(f"应用卡牌编号方案: {package_path}")

    # 获取内容包
    content_package = current_workspace.get_content_package(package_path)

    # 调用工作空间的编号应用方法
    result = content_package.apply_card_numbering(numbering_plan)

    if result.get("success"):
        logger_manager.info(f"卡牌编号应用成功: {package_path}, 更新 {result.get('updated_count')} 张卡牌")
        return jsonify(create_response(
            msg="卡牌编号应用成功",
            data={
                "updated_count": result.get("updated_count"),
                "logs": result.get("logs", [])
            }
        ))
    else:
        logger_manager.error(f"卡牌编号应用失败: {result.get('error', 'Unknown error')}")
        return jsonify(create_response(
            code=14009,
            msg=result.get("error", "卡牌编号应用失败"),
            data={"logs": result.get("logs", [])}
        )), 500


@app.route('/api/content-package/export-pnp', methods=['POST'])
@handle_api_error
def export_content_package_to_pnp():
    """导出内容包为PNP PDF"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'package_path' not in data or 'export_params' not in data:
        return jsonify(create_response(
            code=14010,
            msg="请提供内容包文件路径和导出参数"
        )), 400

    package_path = data['package_path']
    export_params = data['export_params']
    output_filename = data.get('output_filename', 'pnp_export.pdf')
    mode = data.get('mode', 'single_card')  # 'single_card' 或 'print_sheet'
    paper_size = data.get('paper_size', 'A4')  # 'A4', 'A3', 'Letter'

    # 生成任务ID
    import uuid
    task_id = str(uuid.uuid4())

    # 初始化日志缓存
    with pnp_export_logs_lock:
        pnp_export_logs[task_id] = {
            'logs': [],
            'status': 'running',
            'result': None
        }

    logger_manager.info(f"导出内容包为PNP PDF: {package_path}, 模式: {mode}, 任务ID: {task_id}")

    # 定义异步执行的导出任务
    def export_task():
        try:
            # 获取内容包
            content_package = current_workspace.get_content_package(package_path)

            # 定义日志回调函数
            def log_callback(message: str):
                with pnp_export_logs_lock:
                    if task_id in pnp_export_logs:
                        pnp_export_logs[task_id]['logs'].append(message)

            # 调用导出方法（传入task_id和log_callback用于实时日志更新）
            result = content_package.export_to_pnp(
                export_params=export_params,
                output_filename=output_filename,
                mode=mode,
                paper_size=paper_size,
                task_id=task_id,
                log_callback=log_callback
            )

            # 更新最终状态
            with pnp_export_logs_lock:
                if task_id in pnp_export_logs:
                    pnp_export_logs[task_id]['status'] = 'completed' if result.get("success") else 'failed'
                    pnp_export_logs[task_id]['result'] = result

            if result.get("success"):
                logger_manager.info(f"内容包PNP PDF导出成功: {package_path}")
            else:
                logger_manager.error(f"内容包PNP PDF导出失败: {result.get('error', 'Unknown error')}")

        except Exception as e:
            logger_manager.error(f"导出任务执行失败: {e}")
            import traceback
            traceback.print_exc()
            with pnp_export_logs_lock:
                if task_id in pnp_export_logs:
                    pnp_export_logs[task_id]['status'] = 'failed'
                    pnp_export_logs[task_id]['logs'].append(f"❌ 导出失败: {str(e)}")
                    pnp_export_logs[task_id]['result'] = {
                        'success': False,
                        'error': str(e),
                        'logs': pnp_export_logs[task_id]['logs']
                    }

    # 在新线程中启动导出任务
    import threading
    export_thread = threading.Thread(target=export_task)
    export_thread.daemon = True
    export_thread.start()

    # 立即返回task_id，不等待导出完成
    return jsonify(create_response(
        msg="PNP导出任务已启动",
        data={
            "task_id": task_id,
            "status": "running"
        }
    ))


@app.route('/api/content-package/export-pnp/logs/<task_id>', methods=['GET'])
@handle_api_error
def get_pnp_export_logs(task_id):
    """获取PNP导出任务的实时日志"""
    with pnp_export_logs_lock:
        if task_id not in pnp_export_logs:
            return jsonify(create_response(
                code=14012,
                msg="任务ID不存在"
            )), 404

        task_data = pnp_export_logs[task_id]

        # 返回日志和状态
        return jsonify(create_response(
            msg="获取日志成功",
            data={
                "logs": task_data['logs'],
                "status": task_data['status'],
                "result": task_data['result']
            }
        ))


# ================= ArkhamDB导入相关接口 =================

@app.route('/api/arkhamdb/import', methods=['POST'])
@handle_api_error
def import_arkhamdb():
    """导入ArkhamDB内容包"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'content_pack' not in data:
        return jsonify(create_response(
            code=15001,
            msg="请提供ArkhamDB内容包数据"
        )), 400

    content_pack = data['content_pack']

    logger_manager.info("开始导入ArkhamDB内容包")

    work_dir = current_workspace.workspace_path

    try:
        # 导入ArkhamCardBuilder
        from ArkhamCardBuilder import ArkhamCardBuilder

        # 创建构建器实例
        builder = ArkhamCardBuilder(content_pack, work_dir)

        # 保存构建器实例以供后续获取日志
        arkham_builder['build'] = builder

        # 处理内容包
        saved_count, cards, is_valid, errors = builder.process_content_pack()

        if not is_valid:
            logger_manager.error(f"ArkhamDB内容包验证失败: {errors}")
            return jsonify(create_response(
                code=15002,
                msg=f"内容包验证失败: {'; '.join(errors)}",
                data={
                    "errors": errors,
                    "validation_failed": True
                }
            )), 400

        logger_manager.info(f"ArkhamDB内容包导入成功: 保存{saved_count}张卡牌工作空间目录。")

        return jsonify(create_response(
            msg="ArkhamDB内容包导入成功",
            data={
                "saved_count": saved_count,
                "total_cards": len(cards),
                "work_dir_name": '',
                "work_dir": '',
                "language": builder.language,
                "sample_cards": [
                    {
                        "name": card.get('name', 'Unknown'),
                        "type": card.get('type', 'Unknown'),
                        "code": card.get('code', ''),
                        "position": card.get('position', 0)
                    }
                    for card in cards[:5]  # 显示前5张卡牌作为示例
                ] if cards else []
            }
        ))

    except ImportError as e:
        logger_manager.error(f"导入ArkhamCardBuilder模块失败: {str(e)}")
        return jsonify(create_response(
            code=15003,
            msg=f"导入模块失败: {str(e)}"
        )), 500
    except Exception as e:
        logger_manager.exception("导入ArkhamDB内容包时发生未知错误")
        return jsonify(create_response(
            code=15004,
            msg=f"导入失败: {type(e).__name__}: {str(e)}"
        )), 500


@app.route('/api/arkhamdb/logs', methods=['GET'])
@handle_api_error
def get_arkhamdb_logs():
    """获取ArkhamDB导入的日志信息"""
    error_response = check_workspace()
    if error_response:
        return error_response

    if not arkham_builder.get('build'):
        return jsonify(create_response(
            code=15005,
            msg="当前工作区没有ArkhamDB导入记录"
        )), 404

    try:
        builder = arkham_builder.get('build')
        logs = builder.get_logs()

        logger_manager.debug("获取ArkhamDB导入日志")

        return jsonify(create_response(
            msg="获取日志成功",
            data={
                "logs": logs,
                "log_length": len(logs) if logs else 0,
                "has_logs": bool(logs and logs.strip())
            }
        ))

    except Exception as e:
        logger_manager.exception("获取ArkhamDB日志时发生错误")
        return jsonify(create_response(
            code=15006,
            msg=f"获取日志失败: {type(e).__name__}: {str(e)}"
        )), 500


@app.route('/api/arkhamdb/validate', methods=['POST'])
@handle_api_error
def validate_arkhamdb():
    """验证ArkhamDB内容包结构（不进行实际导入）"""
    data = request.get_json()
    if not data or 'content_pack' not in data:
        return jsonify(create_response(
            code=15007,
            msg="请提供ArkhamDB内容包数据"
        )), 400

    content_pack = data['content_pack']

    logger_manager.info("开始验证ArkhamDB内容包结构")

    try:
        # 导入ArkhamCardBuilder
        from ArkhamCardBuilder import ArkhamCardBuilder

        # 创建临时构建器实例（仅用于验证）
        temp_builder = ArkhamCardBuilder(content_pack, os.path.join(os.getcwd(), 'temp_validation'))

        # 验证内容包结构
        is_valid, errors = temp_builder.validate_content_pack_structure()

        if is_valid:
            # 统计信息
            cards = content_pack.get('data', {}).get('cards', [])
            packs = content_pack.get('data', {}).get('packs', [])
            meta = content_pack.get('meta', {})

            logger_manager.info(f"ArkhamDB内容包验证成功: {len(cards)}张卡牌, {len(packs)}个包")

            return jsonify(create_response(
                msg="内容包验证通过",
                data={
                    "is_valid": True,
                    "errors": [],
                    "statistics": {
                        "cards_count": len(cards),
                        "packs_count": len(packs),
                        "language": meta.get('language', 'en'),
                        "name": meta.get('name', 'Unknown'),
                        "version": meta.get('version', 'Unknown')
                    }
                }
            ))
        else:
            logger_manager.warning(f"ArkhamDB内容包验证失败: {errors}")

            return jsonify(create_response(
                code=15008,
                msg=f"内容包验证失败: {'; '.join(errors)}",
                data={
                    "is_valid": False,
                    "errors": errors,
                    "statistics": None
                }
            )), 400

    except ImportError as e:
        logger_manager.error(f"导入ArkhamCardBuilder模块失败: {str(e)}")
        return jsonify(create_response(
            code=15009,
            msg=f"导入模块失败: {str(e)}"
        )), 500
    except Exception as e:
        logger_manager.exception("验证ArkhamDB内容包时发生未知错误")
        return jsonify(create_response(
            code=15010,
            msg=f"验证失败: {type(e).__name__}: {str(e)}"
        )), 500


# ================= 卡牌导出相关接口 =================

@app.route('/api/export-card', methods=['POST'])
@handle_api_error
def export_card():
    """导出卡牌"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'card_path' not in data or 'export_filename' not in data or 'export_params' not in data or 'params_hash' not in data:
        return jsonify(create_response(
            code=12001,
            msg="请提供卡牌路径、导出文件名、导出参数和参数哈希"
        )), 400

    card_path = data['card_path']
    export_filename = data['export_filename']
    export_params = data['export_params']
    params_hash = data['params_hash']

    logger_manager.info(f"导出卡牌: {card_path} -> {export_filename}")

    # 导出卡牌
    success = current_workspace.export_card_with_params(
        card_path, export_filename, export_params, params_hash
    )

    if success:
        logger_manager.info(f"卡牌导出成功: {export_filename}")
        return jsonify(create_response(msg="卡牌导出成功"))
    else:
        logger_manager.error(f"卡牌导出失败: {export_filename}")
        return jsonify(create_response(
            code=12002,
            msg="卡牌导出失败"
        )), 500


# ================= 图床上传相关接口 =================

@app.route('/api/image-host/upload', methods=['POST'])
@handle_api_error
def upload_to_image_host():
    """上传图片到图床"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'image_path' not in data or 'host_type' not in data:
        return jsonify(create_response(
            code=13001,
            msg="请提供图片路径和图床类型"
        )), 400

    image_path = data['image_path']
    host_type = data['host_type']
    online_name = data.get('online_name')

    logger_manager.info(f"上传图片到图床: {image_path}, 类型: {host_type}")

    # 验证图床类型
    if host_type not in ['cloudinary', 'imgbb']:
        return jsonify(create_response(
            code=13002,
            msg="图床类型只支持 cloudinary 和 imgbb"
        )), 400

    # 获取配置
    config = current_workspace.get_config()

    # 根据图床类型验证配置
    if host_type == 'cloudinary':
        required_fields = ['cloud_name', 'api_key', 'api_secret']
        missing_fields = [field for field in required_fields if not config.get(field)]
        if missing_fields:
            logger_manager.warning(f"Cloudinary配置缺失: {missing_fields}")
            return jsonify(create_response(
                code=13003,
                msg=f"Cloudinary配置缺失: {', '.join(missing_fields)}"
            )), 400
    elif host_type == 'imgbb':
        if not config.get('imgbb_api_key'):
            logger_manager.warning("ImgBB API Key 未配置")
            return jsonify(create_response(
                code=13004,
                msg="ImgBB API Key 未配置"
            )), 400

    # 验证图片路径
    if not current_workspace._is_path_in_workspace(image_path):
        logger_manager.warning(f"图片路径无效: {image_path}")
        return jsonify(create_response(
            code=13005,
            msg="图片路径无效"
        )), 400

    abs_image_path = current_workspace._get_absolute_path(image_path)

    if not os.path.exists(abs_image_path):
        logger_manager.warning(f"图片文件不存在: {abs_image_path}")
        return jsonify(create_response(
            code=13006,
            msg="图片文件不存在"
        )), 404

    # 准备图床配置
    host_config = config.copy()
    host_config['image_host'] = host_type

    # 创建图床上传器
    uploader = create_uploader(host_config)

    # 生成在线文件名
    if not online_name:
        online_name = os.path.splitext(os.path.basename(abs_image_path))[0]

    # 上传图片
    upload_url = uploader.upload_file(online_name, abs_image_path)

    if upload_url:
        logger_manager.info(f"图片上传成功: {upload_url}")
        return jsonify(create_response(
            msg="图片上传成功",
            data={
                "url": upload_url,
                "host_type": host_type,
                "online_name": online_name
            }
        ))
    else:
        logger_manager.error(f"图片上传失败: {image_path}")
        return jsonify(create_response(
            code=13007,
            msg="图片上传失败"
        )), 500


@app.route('/api/image-host/check', methods=['POST'])
@handle_api_error
def check_image_exists():
    """检查图片是否已存在于图床"""
    error_response = check_workspace()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'online_name' not in data or 'host_type' not in data:
        return jsonify(create_response(
            code=13009,
            msg="请提供在线文件名和图床类型"
        )), 400

    online_name = data['online_name']
    host_type = data['host_type']

    logger_manager.debug(f"检查图片是否存在: {online_name}, 类型: {host_type}")

    # 验证图床类型
    if host_type not in ['cloudinary', 'imgbb']:
        return jsonify(create_response(
            code=13010,
            msg="图床类型只支持 cloudinary 和 imgbb"
        )), 400

    # 获取配置
    config = current_workspace.get_config()

    # 根据图床类型验证配置
    if host_type == 'cloudinary':
        required_fields = ['cloud_name', 'api_key', 'api_secret']
        missing_fields = [field for field in required_fields if not config.get(field)]
        if missing_fields:
            return jsonify(create_response(
                code=13011,
                msg=f"Cloudinary配置缺失: {', '.join(missing_fields)}"
            )), 400
    elif host_type == 'imgbb':
        if not config.get('imgbb_api_key'):
            return jsonify(create_response(
                code=13012,
                msg="ImgBB API Key 未配置"
            )), 400

    # 准备图床配置
    host_config = config.copy()
    host_config['image_host'] = host_type

    # 创建图床上传器
    uploader = create_uploader(host_config)

    # 检查文件是否存在
    existing_url = uploader.check_file_exists(online_name)

    logger_manager.debug(f"图片存在检查结果: {existing_url is not None}")
    return jsonify(create_response(
        msg="检查完成",
        data={
            "exists": existing_url is not None,
            "url": existing_url,
            "host_type": host_type,
            "online_name": online_name
        }
    ))


# ================= 静态文件服务 =================

@app.route('/')
def index():
    """服务Vue应用的入口文件"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static_files(path):
    """服务Vue应用的静态文件（兼容旧浏览器）"""
    try:
        # 构建完整的文件路径
        file_path = os.path.join(app.static_folder, path)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 对于 Vue Router 的 history 模式，返回 index.html
            return send_from_directory(app.static_folder, 'index.html', mimetype='text/html')

        # 获取文件扩展名
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        # 定义 MIME 类型映射表（优先级高于 mimetypes.guess_type）
        mime_map = {
            '.js': 'application/javascript',
            '.mjs': 'application/javascript',
            '.css': 'text/css',
            '.html': 'text/html',
            '.json': 'application/json',
            '.svg': 'image/svg+xml',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.ico': 'image/x-icon',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.otf': 'font/otf',
            '.eot': 'application/vnd.ms-fontobject',
            '.map': 'application/json',  # Source maps
        }

        # 优先使用映射表，否则使用 mimetypes.guess_type
        mimetype = mime_map.get(ext) or mimetypes.guess_type(path)[0] or 'application/octet-stream'

        # 发送文件并设置正确的 MIME 类型
        response = send_from_directory(app.static_folder, path)
        response.headers['Content-Type'] = mimetype

        # 为 JavaScript 模块添加额外的头部（提升兼容性）
        if ext in ['.js', '.mjs']:
            response.headers['X-Content-Type-Options'] = 'nosniff'

        return response

    except Exception as e:
        logger_manager.exception(f"服务静态文件失败: {path}")
        # 出错时返回 index.html
        return send_from_directory(app.static_folder, 'index.html', mimetype='text/html')


# ================= 全局错误处理 =================

@app.errorhandler(404)
def not_found(error):
    logger_manager.warning(f"404错误: {request.url}")
    return jsonify(create_response(
        code=9001,
        msg="接口不存在"
    )), 404


@app.errorhandler(405)
def method_not_allowed(error):
    logger_manager.warning(f"405错误: {request.method} {request.url}")
    return jsonify(create_response(
        code=9002,
        msg="请求方法不支持"
    )), 405


@app.errorhandler(500)
def internal_error(error):
    logger_manager.exception("500错误: 服务器内部错误")
    return jsonify(create_response(
        code=9003,
        msg=f"服务器内部错误: {type(error).__name__}: {str(error)}"
    )), 500


# ================= 主程序入口 =================

if __name__ == '__main__':
    # 设置控制台编码为UTF-8
    if sys.platform == 'win32':
        os.system('chcp 65001 >nul')

    # 强制刷新输出缓冲区
    sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')
    sys.stderr.reconfigure(line_buffering=True, encoding='utf-8')

    logger_manager.info("启动Flask服务...")
    logger_manager.info("Host: 127.0.0.1, Port: 5000, Debug: True")

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        threaded=True
    )
