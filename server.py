import json
import os
import queue
import sys
import threading
import traceback
from typing import Optional

import webview
from PIL import Image
from flask import Flask, jsonify, request, send_from_directory, Response

from bin.file_manager import QuickStart
# 在文件顶部添加导入
from bin.gitHub_image import GitHubImageHost
from bin.workspace_manager import WorkspaceManager

app = Flask(__name__)
if not hasattr(app, 'window'):
    app.window = None

# 全局状态锁，防止同时打开多个选择对话框
selection_lock = threading.Lock()
is_selecting = False

# 全局实例
quick_start = QuickStart()
current_workspace: WorkspaceManager = None
github_image_host = None


def create_response(code=0, msg="操作成功", data=None):
    """创建统一的响应格式"""
    return {
        "code": code,
        "msg": msg,
        "data": data
    }


# 【重构】将选择目录后的处理逻辑提取出来，方便复用
def _handle_directory_selection(selected_directory: Optional[str]):
    """处理选定的目录，无论是来自pywebview还是tkinter"""
    global current_workspace
    if selected_directory:
        # 添加到最近记录
        quick_start.add_recent_directory(selected_directory)
        # 创建工作空间实例
        try:
            current_workspace = WorkspaceManager(selected_directory)
            return jsonify(create_response(
                msg="目录选择成功",
                data={"directory": selected_directory}
            ))
        except Exception as e:
            return jsonify(create_response(
                code=1007,
                msg=f"创建工作空间失败: {str(e)}"
            )), 500
    else:
        # 用户取消了选择
        return jsonify(create_response(
            code=1003,
            msg="用户取消了选择"
        ))


# ================= 快速开始相关接口 =================
@app.route('/api/select-directory', methods=['GET'])
def api_select_directory():
    """
    API接口：打开目录选择对话框。
    - 在 pywebview 环境下，使用原生的对话框。
    - 在独立的 server 模式下，回退到 tkinter 对话框。
    """
    global is_selecting
    # 【★★★ 核心修改逻辑 ★★★】
    # 判断是否在 pywebview 环境中运行
    if hasattr(app, 'window') and app.window:
        # --- pywebview 模式 ---
        try:
            # create_file_dialog 是一个阻塞调用，会等待用户操作完成
            result = app.window.create_file_dialog(webview.FOLDER_DIALOG)
            # result 是一个元组，如果用户选择了一个目录，元组里会有一个元素
            selected_dir = result[0] if result and len(result) > 0 else None

            # 使用统一的处理函数返回结果
            return _handle_directory_selection(selected_dir)
        except Exception as e:
            # pywebview 对话框也可能出错
            return jsonify(create_response(
                code=1006,
                msg=f"服务器错误: {str(e)}"
            )), 500
    else:
        # --- server 模式 (回退到 tkinter) ---
        if not selection_lock.acquire(blocking=False):
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
                # 这个 select_directory 函数是原来的 tkinter 实现
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
                    result_queue.put(('error', str(e)))
                finally:
                    root.destroy()

            thread = threading.Thread(target=worker, daemon=True)
            thread.start()
            thread.join(timeout=300)  # 等待线程完成
            if thread.is_alive():
                return jsonify(create_response(code=1002, msg="操作超时，请重试")), 408
            try:
                status, result = result_queue.get_nowait()
                if status == 'success':
                    return _handle_directory_selection(result)
                else:
                    return jsonify(create_response(code=1004, msg=f"选择目录时出错: {result}")), 500
            except queue.Empty:
                return jsonify(create_response(code=1005, msg="未能获取选择结果")), 500
        except Exception as e:
            return jsonify(create_response(code=1006, msg=f"服务器错误: {str(e)}")), 500
        finally:
            is_selecting = False
            selection_lock.release()


@app.route('/api/recent-directories', methods=['GET'])
def get_recent_directories():
    """获取最近打开的目录列表"""
    try:
        records = quick_start.get_recent_directories()
        return jsonify(create_response(
            msg="获取最近目录成功",
            data={"directories": records}
        ))
    except Exception as e:
        return jsonify(create_response(
            code=2001,
            msg=f"获取最近目录失败: {str(e)}"
        )), 500


@app.route('/api/recent-directories', methods=['DELETE'])
def clear_recent_directories():
    """清空最近目录记录"""
    try:
        success = quick_start.clear_recent_directories()
        if success:
            return jsonify(create_response(msg="清空最近目录成功"))
        else:
            return jsonify(create_response(
                code=2002,
                msg="清空最近目录失败"
            )), 500
    except Exception as e:
        return jsonify(create_response(
            code=2003,
            msg=f"清空最近目录失败: {str(e)}"
        )), 500


@app.route('/api/recent-directories/<path:directory_path>', methods=['DELETE'])
def remove_recent_directory(directory_path):
    """移除指定的最近目录"""
    try:
        success = quick_start.remove_recent_directory(directory_path)
        if success:
            return jsonify(create_response(msg="移除目录成功"))
        else:
            return jsonify(create_response(
                code=2004,
                msg="目录不存在或移除失败"
            )), 404
    except Exception as e:
        return jsonify(create_response(
            code=2005,
            msg=f"移除目录失败: {str(e)}"
        )), 500


@app.route('/api/open-workspace', methods=['POST'])
def open_workspace():
    """打开指定的工作空间"""
    global current_workspace

    try:
        data = request.get_json()
        if not data or 'directory' not in data:
            return jsonify(create_response(
                code=2006,
                msg="请提供目录路径"
            )), 400

        directory = data['directory']

        if not os.path.exists(directory):
            return jsonify(create_response(
                code=2007,
                msg="目录不存在"
            )), 404

        # 创建工作空间实例
        current_workspace = WorkspaceManager(directory)

        # 添加到最近记录
        quick_start.add_recent_directory(directory)

        return jsonify(create_response(
            msg="工作空间打开成功",
            data={"directory": directory}
        ))

    except Exception as e:
        return jsonify(create_response(
            code=2008,
            msg=f"打开工作空间失败: {str(e)}"
        )), 500


# ================= 工作空间相关接口 =================

def check_workspace():
    """检查工作空间是否已初始化"""
    if current_workspace is None:
        return jsonify(create_response(
            code=3001,
            msg="请先选择或打开工作目录"
        )), 400
    return None


@app.route('/api/file-tree', methods=['GET'])
def get_file_tree():
    """获取文件树"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        include_hidden = request.args.get('include_hidden', 'false').lower() == 'true'
        file_tree = current_workspace.get_file_tree(include_hidden)

        return jsonify(create_response(
            msg="获取文件树成功",
            data={"fileTree": file_tree}
        ))
    except Exception as e:
        return jsonify(create_response(
            code=3002,
            msg=f"获取文件树失败: {str(e)}"
        )), 500


@app.route('/api/create-directory', methods=['POST'])
def create_directory():
    """创建目录"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify(create_response(
                code=3003,
                msg="请提供目录名称"
            )), 400

        dir_name = data['name']
        parent_path = data.get('parent_path')

        success = current_workspace.create_directory(dir_name, parent_path)

        if success:
            return jsonify(create_response(msg="目录创建成功"))
        else:
            return jsonify(create_response(
                code=3004,
                msg="目录创建失败"
            )), 500

    except Exception as e:
        return jsonify(create_response(
            code=3005,
            msg=f"创建目录失败: {str(e)}"
        )), 500


@app.route('/api/create-file', methods=['POST'])
def create_file():
    """创建文件"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify(create_response(
                code=3006,
                msg="请提供文件名称"
            )), 400

        file_name = data['name']
        content = data.get('content', '')
        parent_path = data.get('parent_path')

        success = current_workspace.create_file(file_name, content, parent_path)

        if success:
            return jsonify(create_response(msg="文件创建成功"))
        else:
            return jsonify(create_response(
                code=3007,
                msg="文件创建失败"
            )), 500

    except Exception as e:
        return jsonify(create_response(
            code=3008,
            msg=f"创建文件失败: {str(e)}"
        )), 500


@app.route('/api/rename-item', methods=['PUT'])
def rename_item():
    """重命名文件或目录"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'old_path' not in data or 'new_name' not in data:
            return jsonify(create_response(
                code=3009,
                msg="请提供原路径和新名称"
            )), 400

        old_path = data['old_path']
        new_name = data['new_name']

        success = current_workspace.rename_item(old_path, new_name)

        if success:
            return jsonify(create_response(msg="重命名成功"))
        else:
            return jsonify(create_response(
                code=3010,
                msg="重命名失败，可能是目标名称已存在或路径无效"
            )), 400

    except Exception as e:
        return jsonify(create_response(
            code=3011,
            msg=f"重命名失败: {str(e)}"
        )), 500


@app.route('/api/delete-item', methods=['DELETE'])
def delete_item():
    """删除文件或目录"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'path' not in data:
            return jsonify(create_response(
                code=3012,
                msg="请提供要删除的路径"
            )), 400

        item_path = data['path']

        success = current_workspace.delete_item(item_path)

        if success:
            return jsonify(create_response(msg="删除成功"))
        else:
            return jsonify(create_response(
                code=3013,
                msg="删除失败，路径可能无效或不存在"
            )), 400

    except Exception as e:
        return jsonify(create_response(
            code=3014,
            msg=f"删除失败: {str(e)}"
        )), 500


@app.route('/api/file-content', methods=['GET'])
def get_file_content():
    """获取文件内容"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        file_path = request.args.get('path')
        if not file_path:
            return jsonify(create_response(
                code=3015,
                msg="请提供文件路径"
            )), 400

        content = current_workspace.get_file_content(file_path)

        if content is not None:
            return jsonify(create_response(
                msg="获取文件内容成功",
                data={"content": content}
            ))
        else:
            return jsonify(create_response(
                code=3016,
                msg="文件不存在或无法读取"
            )), 404

    except Exception as e:
        return jsonify(create_response(
            code=3017,
            msg=f"获取文件内容失败: {str(e)}"
        )), 500


@app.route('/api/file-content', methods=['PUT'])
def save_file_content():
    """保存文件内容"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'path' not in data or 'content' not in data:
            return jsonify(create_response(
                code=3018,
                msg="请提供文件路径和内容"
            )), 400

        file_path = data['path']
        content = data['content']

        success = current_workspace.save_file_content(file_path, content)

        if success:
            return jsonify(create_response(msg="保存文件成功"))
        else:
            return jsonify(create_response(
                code=3019,
                msg="保存文件失败"
            )), 500

    except Exception as e:
        return jsonify(create_response(
            code=3020,
            msg=f"保存文件失败: {str(e)}"
        )), 500


# 在server.py中添加以下接口

@app.route('/api/image-content', methods=['GET'])
def get_image_content():
    """获取图片内容（base64格式）"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        image_path = request.args.get('path')
        if not image_path:
            return jsonify(create_response(
                code=5001,
                msg="请提供图片路径"
            )), 400

        image_base64 = current_workspace.get_image_as_base64(image_path)

        if image_base64 is not None:
            return jsonify(create_response(
                msg="获取图片内容成功",
                data={"content": image_base64}
            ))
        else:
            return jsonify(create_response(
                code=5002,
                msg="图片文件不存在或无法读取"
            )), 404

    except Exception as e:
        return jsonify(create_response(
            code=5003,
            msg=f"获取图片内容失败: {str(e)}"
        )), 500


@app.route('/api/file-info', methods=['GET'])
def get_file_info():
    """获取文件信息"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        file_path = request.args.get('path')
        if not file_path:
            return jsonify(create_response(
                code=5004,
                msg="请提供文件路径"
            )), 400

        file_info = current_workspace.get_file_info(file_path)

        if file_info is not None:
            return jsonify(create_response(
                msg="获取文件信息成功",
                data={"fileInfo": file_info}
            ))
        else:
            return jsonify(create_response(
                code=5005,
                msg="文件不存在或无法访问"
            )), 404

    except Exception as e:
        return jsonify(create_response(
            code=5006,
            msg=f"获取文件信息失败: {str(e)}"
        )), 500


@app.route('/api/status', methods=['GET'])
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


# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify(create_response(
        code=9001,
        msg="接口不存在"
    )), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(create_response(
        code=9002,
        msg="请求方法不支持"
    )), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify(create_response(
        code=9003,
        msg="服务器内部错误"
    )), 500


# 在server.py中添加以下接口

@app.route('/api/generate-card', methods=['POST'])
def generate_card():
    """生成卡图"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'json_data' not in data:
            return jsonify(create_response(
                code=4001,
                msg="请提供卡牌JSON数据"
            )), 400

        json_data = data['json_data']

        card_type = json_data.get('type', '')
        cardback_filename = None
        if card_type == '玩家卡背':
            cardback_filename = 'cardback/player-back.jpg'
        elif card_type == '遭遇卡背':
            cardback_filename = 'cardback/encounter-back.jpg'
        print(cardback_filename)
        if cardback_filename:
            # 从程序目录读取
            cardback_path = os.path.join('.', cardback_filename)
            # 如果是PyInstaller打包的程序
            if hasattr(sys, '_MEIPASS'):
                cardback_path = os.path.join(sys._MEIPASS, cardback_filename)
            card_image = Image.open(cardback_path)
            card = None
        else:
            # 生成卡图
            card = current_workspace.generate_card_image(json_data)
            card_image = card.image

            # 判断是否为勘误模式
            if os.environ.get('APP_MODE', 'normal') == 'check':
                try:
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
                    pass

        if card_image is None:
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

        return jsonify(create_response(
            msg="生成卡图成功",
            data={
                "image": f"data:image/png;base64,{img_str}",
                "box_position": card.get_upgrade_card_box_position() if card else []
            }
        ))

    except Exception as e:
        # 打印异常栈
        return jsonify(create_response(
            code=4003,
            msg=f"生成卡图失败: {str(e)}"
        )), 500


@app.route('/api/save-card', methods=['POST'])
def save_card():
    """保存卡图到文件"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'json_data' not in data or 'filename' not in data:
            return jsonify(create_response(
                code=4004,
                msg="请提供卡牌JSON数据和文件名"
            )), 400

        json_data = data['json_data']
        filename = data['filename']
        parent_path = data.get('parent_path')

        # 保存卡图
        success = current_workspace.save_card_image(json_data, filename, parent_path)

        if success:
            return jsonify(create_response(msg="保存卡图成功"))
        else:
            return jsonify(create_response(
                code=4005,
                msg="保存卡图失败"
            )), 500

    except Exception as e:
        return jsonify(create_response(
            code=4006,
            msg=f"保存卡图失败: {str(e)}"
        )), 500


@app.route('/')
def index():
    """服务Vue应用的入口文件"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static_files(path):
    """服务Vue应用的静态文件"""
    # 首先尝试提供静态文件
    try:
        return send_from_directory(app.static_folder, path)
    except:
        # 如果文件不存在，返回index.html（用于Vue Router的history模式）
        return send_from_directory(app.static_folder, 'index.html')


# ================= 配置项相关接口 =================

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置项"""
    try:
        if current_workspace is None:
            config = WorkspaceManager.get_global_config()
        else:
            config = current_workspace.get_config()
        return jsonify(create_response(
            msg="获取配置成功",
            data={"config": config}
        ))
    except Exception as e:
        return jsonify(create_response(
            code=6001,
            msg=f"获取配置失败: {str(e)}"
        )), 500


@app.route('/api/config', methods=['PUT'])
def save_config():
    """保存配置项"""
    try:
        data = request.get_json()
        if not data or 'config' not in data:
            return jsonify(create_response(
                code=6002,
                msg="请提供配置数据"
            )), 400

        config = data['config']
        if current_workspace is None:
            success = WorkspaceManager.save_global_config(config)
        else:
            success = current_workspace.save_config(config)

        if success:
            return jsonify(create_response(msg="保存配置成功"))
        else:
            return jsonify(create_response(
                code=6003,
                msg="保存配置失败"
            )), 500

    except Exception as e:
        return jsonify(create_response(
            code=6004,
            msg=f"保存配置失败: {str(e)}"
        )), 500


@app.route('/api/encounter-groups', methods=['GET'])
def get_encounter_groups():
    """获取遭遇组列表"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        encounter_groups = current_workspace.get_encounter_groups()
        return jsonify(create_response(
            msg="获取遭遇组列表成功",
            data={"encounter_groups": encounter_groups}
        ))
    except Exception as e:
        return jsonify(create_response(
            code=6005,
            msg=f"获取遭遇组列表失败: {str(e)}"
        )), 500



@app.route('/api/export-deck-image', methods=['POST'])
def export_deck_image():
    """导出牌库图片"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'deck_name' not in data:
            return jsonify(create_response(
                code=8001,
                msg="请提供牌库名称"
            )), 400

        deck_name = data['deck_name']
        export_format = data.get('format', 'PNG').upper()  # JPG或PNG
        quality = data.get('quality', 95)  # 图片质量百分比

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
            return jsonify(create_response(msg="牌库图片导出成功"))
        else:
            return jsonify(create_response(
                code=8004,
                msg="牌库图片导出失败"
            )), 500

    except Exception as e:
        return jsonify(create_response(
            code=8005,
            msg=f"导出牌库图片失败: {str(e)}"
        )), 500


@app.route('/api/open-directory', methods=['POST'])
def open_directory():
    """打开指定目录"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'directory_path' not in data:
            return jsonify(create_response(
                code=9001,
                msg="请提供目录路径"
            )), 400

        directory_path = data['directory_path']

        # 打开目录
        success = current_workspace.open_directory_in_explorer(directory_path)

        if success:
            return jsonify(create_response(msg="目录已在资源管理器中打开"))
        else:
            return jsonify(create_response(
                code=9002,
                msg="打开目录失败，目录可能不存在"
            )), 400

    except Exception as e:
        return jsonify(create_response(
            code=9003,
            msg=f"打开目录失败: {str(e)}"
        )), 500


# ================= GitHub图床相关接口 =================

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


@app.route('/api/github/login', methods=['POST'])
def github_login():
    """GitHub登录"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'token' not in data:
            return jsonify(create_response(
                code=10001,
                msg="请提供GitHub Token"
            )), 400

        token = data['token']

        # 创建新的GitHub图床实例
        temp_github_host = GitHubImageHost()

        # 尝试登录
        if not temp_github_host.login(token):
            return jsonify(create_response(
                code=10002,
                msg=temp_github_host.get_last_error()
            )), 400

        # 只有登录成功后才赋值给全局变量（新登录替换旧登录）
        global github_image_host
        github_image_host = temp_github_host

        return jsonify(create_response(
            msg="GitHub登录成功",
            data={
                "username": github_image_host.username
            }
        ))

    except Exception as e:
        return jsonify(create_response(
            code=10003,
            msg=f"GitHub登录失败: {str(e)}"
        )), 500


@app.route('/api/github/logout', methods=['POST'])
def github_logout():
    """GitHub登出"""
    try:
        global github_image_host
        github_image_host = None

        return jsonify(create_response(msg="GitHub登出成功"))
    except Exception as e:
        return jsonify(create_response(
            code=10017,
            msg=f"GitHub登出失败: {str(e)}"
        )), 500


@app.route('/api/github/repositories', methods=['GET'])
def get_github_repositories():
    """获取GitHub仓库列表"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        # 获取或创建GitHub实例（如果全局变量为空会自动静默登录）
        github_host, error_msg = get_or_create_github_host()
        if not github_host:
            return jsonify(create_response(
                code=10004,
                msg=error_msg
            )), 400

        # 获取仓库列表
        repositories, error_msg = github_host.list_repositories()
        if error_msg:
            return jsonify(create_response(
                code=10005,
                msg=error_msg
            )), 500

        return jsonify(create_response(
            msg="获取仓库列表成功",
            data={"repositories": repositories}
        ))

    except Exception as e:
        return jsonify(create_response(
            code=10006,
            msg=f"获取仓库列表失败: {str(e)}"
        )), 500


@app.route('/api/github/upload', methods=['POST'])
def github_upload_image():
    """上传图片到GitHub"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'image_path' not in data:
            return jsonify(create_response(
                code=10007,
                msg="请提供图片路径"
            )), 400

        image_path = data['image_path']

        # 获取或创建GitHub实例（如果全局变量为空会自动静默登录）
        github_host, error_msg = get_or_create_github_host()
        if not github_host:
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
            return jsonify(create_response(
                code=10009,
                msg="请先在配置中设置GitHub仓库"
            )), 400

        # 转换为绝对路径
        if not current_workspace._is_path_in_workspace(image_path):
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
            return jsonify(create_response(
                code=10011,
                msg=error_msg
            )), 500

        return jsonify(create_response(
            msg="图片上传成功",
            data={
                "url": download_url,
                "repo": repo_name,
                "branch": branch,
                "folder": folder
            }
        ))

    except Exception as e:
        return jsonify(create_response(
            code=10012,
            msg=f"上传图片失败: {str(e)}"
        )), 500


@app.route('/api/github/status', methods=['GET'])
def get_github_status():
    """获取GitHub状态"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
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

        return jsonify(create_response(
            msg="获取GitHub状态成功",
            data={"status": status}
        ))

    except Exception as e:
        return jsonify(create_response(
            code=10013,
            msg=f"获取GitHub状态失败: {str(e)}"
        )), 500


@app.route('/api/export-tts', methods=['POST'])
def export_tts():
    """导出TTS物品"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'deck_name' not in data or 'face_url' not in data or 'back_url' not in data:
            return jsonify(create_response(
                code=11001,
                msg="请提供牌库名称、正面URL和背面URL"
            )), 400

        deck_name = data['deck_name']
        face_url = data['face_url']
        back_url = data['back_url']

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
            return jsonify(create_response(msg="TTS物品导出成功"))
        else:
            return jsonify(create_response(
                code=11004,
                msg="TTS物品导出失败"
            )), 500

    except Exception as e:
        return jsonify(create_response(
            code=11005,
            msg=f"导出TTS物品失败: {str(e)}"
        )), 500


@app.route('/api/export-deck-pdf', methods=['POST'])
def export_deck_pdf():
    """导出牌库PDF"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'deck_name' not in data:
            return jsonify(create_response(
                code=8006,
                msg="请提供牌库名称"
            )), 400

        deck_name = data['deck_name']
        pdf_filename = data.get('pdf_filename', None)  # 可选的PDF文件名

        # 导出牌库PDF
        success = current_workspace.export_deck_pdf(deck_name, pdf_filename)

        if success:
            # 构建返回的文件路径信息
            deck_base_name = os.path.splitext(deck_name)[0]
            final_pdf_filename = pdf_filename or f"{deck_base_name}.pdf"

            return jsonify(create_response(
                msg="牌库PDF导出成功",
                data={
                    "pdf_filename": final_pdf_filename,
                    "deck_name": deck_name
                }
            ))
        else:
            return jsonify(create_response(
                code=8007,
                msg="牌库PDF导出失败"
            )), 500

    except Exception as e:
        # 打印详细错误信息用于调试
        traceback.print_exc()
        return jsonify(create_response(
            code=8008,
            msg=f"导出牌库PDF失败: {str(e)}"
        )), 500


@app.route('/api/export-card', methods=['POST'])
def export_card():
    """导出卡牌"""
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
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

        # 导出卡牌
        success = current_workspace.export_card_with_params(
            card_path, export_filename, export_params, params_hash
        )

        if success:
            return jsonify(create_response(msg="卡牌导出成功"))
        else:
            return jsonify(create_response(
                code=12002,
                msg="卡牌导出失败"
            )), 500

    except Exception as e:
        return jsonify(create_response(
            code=12003,
            msg=f"导出卡牌失败: {str(e)}"
        )), 500


if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        threaded=True
    )
