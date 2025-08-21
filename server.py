from flask import Flask, jsonify, request, send_from_directory
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import os
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
