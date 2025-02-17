import json
import os
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory, render_template
from openai import OpenAI

from Card import FontManager, ImageManager
from create_card import process_card_json, create_investigators_card, create_investigators_card_back

app = Flask(__name__, static_folder='static', static_url_path='/static')

basedir = os.path.dirname(__file__)

# 初始化配置
CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    "openai": {
        "base_url": "https://api.deepseek.com",
        "api_key": "",
        "model": "deepseek-chat"
    }
}

# 全局对象
openai_client = None
font_manager = FontManager('fonts')
image_manager = ImageManager('images')


def create_response(code=0, msg="成功", data=None, status=200):
    """创建标准响应"""
    return jsonify({
        "code": code,
        "msg": msg,
        "data": data
    }), status


def load_config():
    """加载配置文件"""
    try:
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"配置文件加载失败: {str(e)}")


def save_config(new_config):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(new_config, f, indent=2)
    except Exception as e:
        raise RuntimeError(f"配置文件保存失败: {str(e)}")


def init_openai():
    """初始化OpenAI客户端"""
    global openai_client
    try:
        config = load_config()
        openai_config = config['openai']
        openai_client = OpenAI(
            base_url=openai_config['base_url'],
            api_key=openai_config['api_key']
        )
    except Exception as e:
        raise RuntimeError(f"OpenAI初始化失败: {str(e)}")


# 初始化服务
try:
    init_openai()
except Exception as e:
    app.logger.error(f"服务初始化失败: {str(e)}")


@app.route('/favicon.ico')  # 设置icon
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),  # 对于当前文件所在路径,比如这里是static下的favicon.ico
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/api/config', methods=['GET'])
def get_openai_config():
    """获取当前OpenAI配置"""
    try:
        config = load_config()
        return create_response(data=config['openai'])
    except Exception as e:
        return create_response(500, str(e), None, 500)


@app.route('/api/config', methods=['POST'])
def update_openai_config():
    """更新OpenAI配置"""
    try:
        new_config = request.json
        if not new_config or not all(key in new_config for key in ['base_url', 'api_key', 'model']):
            return create_response(400, "缺少必要参数", None, 400)

        config = load_config()
        config['openai'] = new_config
        save_config(config)
        init_openai()  # 重新初始化客户端
        return create_response()
    except Exception as e:
        return create_response(500, str(e), None, 500)


# 新增生成JSON的接口
@app.route('/api/generate-json', methods=['POST'])
def generate_json():
    """生成卡牌JSON"""
    try:
        # 参数校验
        if 'text' not in request.json:
            return create_response(400, "缺少text参数", None, 400)
        user_input = request.json['text']

        # 读取提示词文件
        with open('prompt/player_card.txt', encoding='utf-8') as f:
            prompt = f.read()

        # 调用OpenAI接口
        response = openai_client.chat.completions.create(
            model=load_config()['openai']['model'],
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
            stream=False
        )

        # 解析返回的JSON
        card_json = json.loads(response.choices[0].message.content)
        return create_response(data=card_json)

    except Exception as e:
        app.logger.exception(f"JSON生成失败: {str(e)}")
        app.logger.error(f"JSON生成失败: {str(e)}")
        return create_response(500, "JSON生成失败：" + str(e), str(e), 500)


# 新增生成图片的接口
@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """根据JSON生成卡牌图片"""
    picture_path = None
    try:
        # 参数校验
        if 'json' not in request.form:
            return create_response(400, "缺少json参数", None, 400)

        # 解析JSON
        card_json = json.loads(request.form['json'])

        # 处理图片上传
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                # 创建临时目录
                temp_dir = os.path.join(app.root_path, 'temp')
                os.makedirs(temp_dir, exist_ok=True)

                # 生成唯一文件名
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                ext = os.path.splitext(image_file.filename)[1]
                filename = f"upload_{timestamp}{ext}"
                filepath = os.path.join(temp_dir, filename)

                # 保存文件
                image_file.save(filepath)
                picture_path = filepath

        # 创建输出目录
        today = datetime.now().strftime("%Y-%m-%d")
        output_dir = os.path.join(os.path.join(basedir, 'output'), today)
        os.makedirs(output_dir, exist_ok=True)
        # 生成卡牌图片
        if 'type' in card_json and card_json['type'] == '调查员卡':
            # 调查员卡特殊处理
            data = {}
            # 生成正面
            card = create_investigators_card(
                card_json,
                font_manager=font_manager,
                image_manager=image_manager,
                picture_path=picture_path
            )
            # 生成自增文件名
            existing = [f for f in os.listdir(output_dir) if f.endswith('.png')]
            next_num = len(existing) + 1
            filename = f"{next_num:04d}.png"
            filepath = os.path.join(output_dir, filename)

            # 保存图片
            card.image.save(filepath, quality=95)
            data['url'] = f"/images/{today}/{filename}"

            # 生成背面，如果有的话
            if 'card_back' in card_json and len(card_json['card_back']['option']) > 0:
                card_back = create_investigators_card_back(
                    card_json,
                    font_manager=font_manager,
                    image_manager=image_manager,
                    picture_path=picture_path
                )
                # 生成自增文件名
                existing = [f for f in os.listdir(output_dir) if f.endswith('.png')]
                next_num = len(existing) + 1
                filename = f"{next_num:04d}.png"
                filepath = os.path.join(output_dir, filename)

                # 保存图片
                card_back.image.save(filepath, quality=95)
                data['back_url'] = f"/images/{today}/{filename}"

            return create_response(data=data)
        else:
            card = process_card_json(
                card_json,
                font_manager=font_manager,
                image_manager=image_manager,
                picture_path=picture_path
            )
            # 生成自增文件名
            existing = [f for f in os.listdir(output_dir) if f.endswith('.png')]
            next_num = len(existing) + 1
            filename = f"{next_num:04d}.png"
            filepath = os.path.join(output_dir, filename)

            # 保存图片
            card.image.save(filepath, quality=95)

            return create_response(data={"url": f"/images/{today}/{filename}"})

    except json.JSONDecodeError:
        return create_response(400, "JSON格式错误", None, 400)
    except Exception as e:
        app.logger.exception(e)
        app.logger.error(f"图片生成失败: {str(e)}")
        return create_response(500, "图片生成失败", str(e), 500)
    finally:
        # 清理picture_path
        if picture_path is not None and os.path.exists(picture_path):
            os.remove(picture_path)


@app.route('/images/<path:path>')
def serve_image(path):
    """提供生成的图片访问"""
    try:
        return send_from_directory('output', path)
    except FileNotFoundError:
        return create_response(404, "图片未找到", None, 404)
    except Exception as e:
        return create_response(500, "图片获取失败", str(e), 500)


@app.errorhandler(404)
def handle_404(e):
    return create_response(404, "资源未找到", None, 404)


@app.errorhandler(500)
def handle_500(e):
    return create_response(500, "服务器内部错误", None, 500)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
