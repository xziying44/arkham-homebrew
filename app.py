import json
import sys
from typing import Optional

from flask import Flask, jsonify, request, send_from_directory, Response
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import os

from flaskwebgui import FlaskUI
from openai import OpenAI

from file_manager import QuickStart, WorkspaceManager

app = Flask(__name__)

# 全局状态锁，防止同时打开多个选择对话框
selection_lock = threading.Lock()
is_selecting = False

# 全局实例
quick_start = QuickStart()
current_workspace = None


def create_response(code=0, msg="操作成功", data=None):
    """创建统一的响应格式"""
    return {
        "code": code,
        "msg": msg,
        "data": data
    }


def select_directory():
    """打开目录选择对话框"""
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)

    try:
        selected_directory = filedialog.askdirectory(
            title="请选择目录",
            initialdir=os.getcwd()
        )
        return selected_directory
    finally:
        root.destroy()


# ================= 快速开始相关接口 =================

@app.route('/api/select-directory', methods=['GET'])
def api_select_directory():
    """API接口：打开目录选择对话框"""
    global is_selecting, current_workspace

    if not selection_lock.acquire(blocking=False):
        return jsonify(create_response(
            code=1001,
            msg="目录选择操作正在进行中，请稍后再试"
        )), 409

    try:
        is_selecting = True
        result_queue = queue.Queue()

        def worker():
            try:
                directory = select_directory()
                result_queue.put(('success', directory))
            except Exception as e:
                result_queue.put(('error', str(e)))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        thread.join(timeout=300)

        if thread.is_alive():
            return jsonify(create_response(
                code=1002,
                msg="操作超时，请重试"
            )), 408

        try:
            status, result = result_queue.get_nowait()
            if status == 'success':
                if result:
                    # 添加到最近记录
                    quick_start.add_recent_directory(result)

                    # 创建工作空间实例
                    try:
                        current_workspace = WorkspaceManager(result)
                        return jsonify(create_response(
                            msg="目录选择成功",
                            data={"directory": result}
                        ))
                    except Exception as e:
                        return jsonify(create_response(
                            code=1007,
                            msg=f"创建工作空间失败: {str(e)}"
                        )), 500
                else:
                    return jsonify(create_response(
                        code=1003,
                        msg="用户取消了选择"
                    ))
            else:
                return jsonify(create_response(
                    code=1004,
                    msg=f"选择目录时出错: {result}"
                )), 500

        except queue.Empty:
            return jsonify(create_response(
                code=1005,
                msg="未能获取选择结果"
            )), 500

    except Exception as e:
        return jsonify(create_response(
            code=1006,
            msg=f"服务器错误: {str(e)}"
        )), 500
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
        card_image = current_workspace.generate_card_image(json_data)

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
            data={"image": f"data:image/png;base64,{img_str}"}
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
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
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
    error_response = check_workspace()
    if error_response:
        return error_response

    try:
        data = request.get_json()
        if not data or 'config' not in data:
            return jsonify(create_response(
                code=6002,
                msg="请提供配置数据"
            )), 400

        config = data['config']
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


if __name__ == '__main__':
    # 获取屏幕高度和宽度
    FlaskUI(app=app, server="flask", width=1500, height=800).run()
