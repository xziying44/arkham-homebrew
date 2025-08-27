import json
import sys
from typing import Optional

import webview
from flask import Flask, jsonify, request, send_from_directory, Response
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import os

from openai import OpenAI

from bin.file_manager import QuickStart
from bin.workspace_manager import WorkspaceManager
# 在文件顶部添加导入
from bin.gitHub_image import GitHubImageHost

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

        # 生成卡图
        card = current_workspace.generate_card_image(json_data)
        card_image = card.image

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
                "box_position": card.get_upgrade_card_box_position()
            }
        ))

    except Exception as e:
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


def get_prompt_content(prompt_filename: str) -> Optional[str]:
    """获取提示词文件内容（从程序目录下的prompt文件夹）"""
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, 'prompt', prompt_filename)

        # 如果是PyInstaller打包的程序
        if hasattr(sys, '_MEIPASS'):
            prompt_path = os.path.join(sys._MEIPASS, 'prompt', prompt_filename)

        if not os.path.exists(prompt_path):
            print(f"提示词文件不存在: {prompt_path}")
            return None

        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    except Exception as e:
        print(f"读取提示词文件失败: {e}")
        return None


# ================= OpenAI卡牌生成相关接口 =================

def process_json_str(json_str):
    """处理json字符串"""
    # 如果返回了markdown的代码块，需要去除，保留原始的json字符串
    if '```json' in json_str and '```' in json_str:
        # 取回```json和```之间的内容
        json_str = json_str[json_str.find('```json') + 7:json_str.rfind('```')]
    elif '```' in json_str:
        # 处理没有指定语言的代码块
        start = json_str.find('```')
        end = json_str.rfind('```')
        if start != end:
            json_str = json_str[start + 3:end]

    json_str = json_str.strip()

    # 尝试解析json字符串
    try:
        # 尝试解析JSON
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError as e:
        # 主要修复点：补全image_prompt字段的闭合引号
        fixed_json = json_str.strip()

        # 如果最后一个字段没有闭合引号，尝试添加
        if not fixed_json.endswith('"') and fixed_json.endswith('...'):
            fixed_json = fixed_json[:-3] + '"'
        elif not fixed_json.endswith('"') and '"' in fixed_json:
            # 找到最后一个未闭合的引号位置
            lines = fixed_json.split('\n')
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i].strip()
                if ':' in line and not line.endswith('"') and not line.endswith(','):
                    lines[i] = line + '"'
                    break
            fixed_json = '\n'.join(lines)

        # 如果没有闭合的大括号，尝试添加
        if not fixed_json.endswith('}'):
            fixed_json += '}'
        try:
            data = json.loads(fixed_json)
            return data
        except json.JSONDecodeError as e:
            # 抛出异常
            raise RuntimeError(f'JSON解析错误: {str(e)}')


@app.route('/api/parse-card-json', methods=['POST'])
def parse_card_json():
    """解析并验证卡牌JSON"""
    try:
        data = request.get_json()
        if not data or 'json_text' not in data:
            return jsonify(create_response(
                code=7006,
                msg="请提供JSON文本"
            )), 400
        json_text = data['json_text']

        # 使用处理函数解析JSON
        try:
            card_json = process_json_str(json_text)
        except RuntimeError as e:
            return jsonify(create_response(
                code=7007,
                msg=str(e)
            )), 400
        except Exception as e:
            return jsonify(create_response(
                code=7007,
                msg=f"JSON处理失败: {str(e)}"
            )), 400
        # 检查AI返回的错误信息
        if 'msg' in card_json and card_json['msg']:
            return jsonify(create_response(
                code=7008,
                msg=f"AI返回错误: {card_json['msg']}"
            )), 400
        # 验证必要字段
        required_fields = ['type', 'name', 'body']
        missing_fields = []
        for field in required_fields:
            if field not in card_json:
                missing_fields.append(field)
        if missing_fields:
            return jsonify(create_response(
                code=7009,
                msg=f"缺少必要字段: {', '.join(missing_fields)}"
            )), 400
        # 清除msg字段（如果为空）
        if 'msg' in card_json and not card_json['msg']:
            del card_json['msg']
        return jsonify(create_response(
            msg="JSON解析成功",
            data={"card_json": card_json}
        ))
    except Exception as e:
        return jsonify(create_response(
            code=7010,
            msg=f"解析JSON失败: {str(e)}"
        )), 500


@app.route('/api/generate-card-info', methods=['POST'])
def generate_card_info():
    """使用OpenAI生成卡牌JSON信息（流输出，包含思考过程）"""
    error_response = check_workspace()
    if error_response:
        return error_response
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify(create_response(
                code=7001,
                msg="请提供卡牌描述内容"
            )), 400
        user_content = data['content']

        # 读取提示词文件
        prompt_content = get_prompt_content('player_card_picture.txt')
        if not prompt_content:
            return jsonify(create_response(
                code=7002,
                msg="无法读取提示词文件"
            )), 500

        # 获取配置中的OpenAI设置
        config = current_workspace.get_config()
        ai_api_key = config.get('ai_api_key', '')
        ai_endpoint = config.get('ai_endpoint', 'https://api.openai.com/v1')
        ai_model = config.get('ai_model', 'gpt-3.5-turbo')

        if not ai_api_key:
            return jsonify(create_response(
                code=7003,
                msg="请在配置中设置AI API密钥"
            )), 400

        # 创建OpenAI客户端
        try:
            client = OpenAI(
                api_key=ai_api_key,
                base_url=ai_endpoint
            )
        except Exception as e:
            return jsonify(create_response(
                code=7004,
                msg=f"创建OpenAI客户端失败: {str(e)}"
            )), 500

        # 构建消息
        messages = [
            {
                "role": "system",
                "content": prompt_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ]

        # 创建流式响应
        def generate():
            try:
                # 调用OpenAI API，启用流式输出
                response = client.chat.completions.create(
                    model=ai_model,
                    messages=messages,
                    stream=True,
                    temperature=1
                )

                # 流式输出结果
                for chunk in response:
                    # 处理思考内容
                    if (hasattr(chunk.choices[0].delta, 'reasoning_content') and
                            chunk.choices[0].delta.reasoning_content):
                        reasoning_content = chunk.choices[0].delta.reasoning_content
                        # 发送思考内容
                        yield f"data: {json.dumps({'reasoning': reasoning_content}, ensure_ascii=False)}\n\n"

                    # 处理普通内容
                    elif (hasattr(chunk.choices[0].delta, 'content') and
                          chunk.choices[0].delta.content is not None):
                        content = chunk.choices[0].delta.content
                        # 发送普通内容
                        yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"

                # 发送完成信号
                yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"

            except Exception as e:
                error_msg = f"OpenAI API调用失败: {str(e)}"
                yield f"data: {json.dumps({'error': error_msg}, ensure_ascii=False)}\n\n"

        # 返回SSE流
        return Response(
            generate(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
    except Exception as e:
        return jsonify(create_response(
            code=7005,
            msg=f"生成卡牌信息失败: {str(e)}"
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


if __name__ == '__main__':
    print("=" * 60)
    print("文件管理服务启动")
    print("服务地址: http://localhost:5000")
    print("")
    print("快速开始接口:")
    print("  选择目录: GET /api/select-directory")
    print("  最近目录: GET /api/recent-directories")
    print("  打开工作空间: POST /api/open-workspace")
    print("")
    print("工作空间接口:")
    print("  文件树: GET /api/file-tree")
    print("  创建目录: POST /api/create-directory")
    print("  创建文件: POST /api/create-file")
    print("  重命名: PUT /api/rename-item")
    print("  删除: DELETE /api/delete-item")
    print("  文件内容: GET/PUT /api/file-content")
    print("")
    print("系统接口:")
    print("  服务状态: GET /api/status")
    print("=" * 60)

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        threaded=True
    )
