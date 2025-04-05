# 生成OCR训练数据
# 读取cards.json
import json
import os
import random
import sys
from PIL import ImageDraw, Image, ImageFilter
from Card import FontManager, ImageManager
from batch_build import batch_build_card
from yolo_arkham_icon import YoloArkhamIcon

with open('cards_en.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# 修改数据路径配置为PaddleOCR格式
data_root_dir = r'D:\OCR_DATA\train_data'
data_root_dir_yolov5 = r'D:\OCR_DATA\train_data_yolov5'

# 创建目录结构
os.makedirs(os.path.join(data_root_dir, 'det/train'), exist_ok=True)
os.makedirs(os.path.join(data_root_dir, 'det/test'), exist_ok=True)
os.makedirs(os.path.join(data_root_dir, 'rec/train'), exist_ok=True)
os.makedirs(os.path.join(data_root_dir, 'rec/test'), exist_ok=True)
os.makedirs(os.path.join(data_root_dir_yolov5, 'train'), exist_ok=True)
os.makedirs(os.path.join(data_root_dir_yolov5, 'train', 'images'), exist_ok=True)
os.makedirs(os.path.join(data_root_dir_yolov5, 'train', 'labels'), exist_ok=True)
os.makedirs(os.path.join(data_root_dir_yolov5, 'test', 'images'), exist_ok=True)
os.makedirs(os.path.join(data_root_dir_yolov5, 'test', 'labels'), exist_ok=True)

# 初始化索引数据
index_data = {
    'det_index': 1,
    'rec_index': 1
}

icon_list = [
    '🏅',
    '⭕',
    '➡️',
    '⚡',
    '💀',
    '👤',
    '📜',
    '👹',
    '🐙',
    '⭐',
    '👊',
    '📚',
    '🦶',
    '🧠',
    '❓',
    '🔵',
    '🌑',
    '🌟',
    '❄️',
    '🕵️',
    '🚶',
    '🏕️',
    '🛡️',
    '🧘',
    '🔍',
    '🫀',
    '💙',
    '🌸'
]

icon_dict = {
    '🏅': '<独特>',
    '⭕': '<反应>',
    '➡️': '<启动>',
    '⚡': '<免费>',
    '💀': '<骷髅>',
    '👤': '<异教徒>',
    '📜': '<石板>',
    '👹': '<古神>',
    '🐙': '<触手>',
    '⭐': '<旧印>',
    '👊': '<拳>',
    '📚': '<书>',
    '🦶': '<脚>',
    '🧠': '<脑>',
    '❓': '<?>',
    '🔵': '<点>',
    '🌑': '<诅咒>',
    '🌟': '<祝福>',
    '❄️': '<雪花>',
    '🕵️': '<调查员>',
    '🚶': '<流浪者>',
    '🏕️': '<生存者>',
    '🛡️': '<守护者>',
    '🧘': '<潜修者>',
    '🔍': '<探求者>',
    '🌸': '<花>'
}

yolov5_dict = [
    '🏅',
    '⭕',
    '➡️',
    '⚡',
    '💀',
    '👤',
    '📜',
    '👹',
    '🐙',
    '⭐',
    '👊',
    '📚',
    '🦶',
    '🧠',
    '❓',
    '🔵',
    '🌑',
    '🌟',
    '❄️',
    '🕵️',
    '🚶',
    '🏕️',
    '🛡️',
    '🧘',
    '🔍',
    '🫀',
    '💙',
    '➖',
    '🌸',
    '投入-意志',
    '投入-战力',
    '投入-敏捷',
    '投入-智力',
    '投入-狂野',
    '槽位-双手',
    '槽位-双法术',
    '槽位-塔罗',
    '槽位-手部',
    '槽位-法术',
    '槽位-盟友',
    '槽位-身体',
    '槽位-饰品',
    '多职阶-守护者',
    '多职阶-探求者',
    '多职阶-流浪者',
    '多职阶-潜修者',
    '多职阶-生存者',
    '地点标识-暗红漏斗',
    '地点标识-标识底',
    '地点标识-橙心',
    '地点标识-浅褐水滴',
    '地点标识-深紫星',
    '地点标识-深绿斜二',
    '地点标识-深蓝T',
    '地点标识-紫月',
    '地点标识-红十',
    '地点标识-红方',
    '地点标识-绿菱',
    '地点标识-蓝三角',
    '地点标识-褐扭',
    '地点标识-青花',
    '地点标识-黄圆',
    '地点标识-粉桃',
    '地点标识-粉心',
    '地点标识-绿星',
    '地点标识-橙圆',
    '地点标识-红扭',
    '地点标识-红斜二',
    '地点标识-黄漏斗',
    '地点标识-黄三角',
    '地点标识-蓝菱',
    '地点标识-蓝月',
    '地点标识-绿T',
    '地点标识-斜十字',
    '地点标识-紫方',
    '数字-?',
    '数字-X',
    '数字-无',
    '数字-0',
    '数字-1',
    '数字-2',
    '数字-3',
    '数字-4',
    '数字-5',
    '数字-6',
    '数字-7',
    '数字-8',
    '数字-9',
    '数字-10',
    '数字-11',
    '数字-12',
    '数字-13',
    '数字-14',
    '数字-15',
    '等级-无',
    '等级-0',
    '等级-1',
    '等级-2',
    '等级-3',
    '等级-4',
    '等级-5',
]


# 定义一个异常类
class NoDictError(Exception):

    def __init__(self, message, img=None) -> None:
        super().__init__(message)
        if img:
            img.show()


def get_mark_index(mark_text, img=None):
    for i, icon in enumerate(yolov5_dict):
        if mark_text in icon:
            return i
    raise NoDictError(f"找不到对应的标注：{mark_text}", img)


# yolo_arkham_icon = YoloArkhamIcon()
yolo_arkham_icon = None


def generate_card_image(generate_card, generate_type='train'):
    """
    生成卡牌图片并保存为PaddleOCR格式
    :param generate_card: 卡牌数据
    :param generate_type: 数据类型，train/test
    :return:
    """
    # 确定是训练集还是测试集
    det_img_dir = os.path.join(data_root_dir, f'det/{generate_type}')
    rec_img_dir = os.path.join(data_root_dir, f'rec/{generate_type}')

    # 创建图片目录
    os.makedirs(det_img_dir, exist_ok=True)
    os.makedirs(rec_img_dir, exist_ok=True)

    def build_card(card_json, is_back=False):
        # 从random_pictures目录下随机取一张图片
        random_picture_path = os.path.join('random_pictures',
                                           random.choice(os.listdir(os.path.join('random_pictures'))))
        card_data = rand_add_icon(card_json)
        card = batch_build_card(
            card_json=card_data,
            font_manager=font_manager,
            image_manager=image_manager,
            is_back=is_back,
            picture_path=random_picture_path
        )
        if card:
            # 保存检测模型图片和标注
            det_img_path = os.path.join(det_img_dir, f'{index_data["det_index"]:06d}.jpg')
            # 转为RGB模式
            card.image = card.image.convert('RGB')
            filtered_detections = yolo_arkham_icon.detect(card.image)
            card.image = yolo_arkham_icon.arkham_icon_to_text(card.image, filtered_detections)

            card.image.save(det_img_path, quality=95)

            # 准备检测模型的标注数据
            det_annotations = []
            for mark_info in card.text_mark:
                annotation = {
                    "transcription": mark_info["text"],
                    "points": mark_info["points"]
                }
                det_annotations.append(annotation)

            # 保存识别模型图片和标注
            for i, mark_info in enumerate(card.text_mark, 1):
                # 筛选只有图标的标注
                # icon_exist = False
                # for icon in icon_list:
                #     if icon in mark_info["text"]:
                #         icon_exist = True
                #         break
                # if not icon_exist:
                #     continue
                # if mark_info["text"] in icon_list:
                #     continue
                # 裁剪文本区域
                points = mark_info["points"]
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                text_img = card.image.crop((x_min, y_min, x_max, y_max))

                # 保存识别模型图片
                rec_img_path = os.path.join(rec_img_dir, f'{index_data["det_index"]:06d}-{i:02d}.jpg')
                text_img.save(rec_img_path, quality=95)

                # 准备识别模型的标注数据
                rec_annotation = f'{os.path.basename(rec_img_path)}\t{mark_info["text"]}\n'
                with open(os.path.join(data_root_dir, f'rec/rec_gt_{generate_type}.txt'), 'a', encoding='utf-8') as f:
                    f.write(rec_annotation)

            # 保存检测模型的标注数据
            det_annotation = f'{os.path.basename(det_img_path)}\t{json.dumps(det_annotations, ensure_ascii=False)}\n'
            with open(os.path.join(data_root_dir, f'det/det_gt_{generate_type}.txt'), 'a', encoding='utf-8') as f:
                f.write(det_annotation)

            index_data["det_index"] += 1

    build_card(generate_card)
    if generate_card.get('type_code', None) == 'location':
        build_card(generate_card, is_back=True)


def generate(generate_type='ocr'):
    random.shuffle(cards)

    split_idx = int(0.8 * len(cards))

    # 训练集生成
    train_total = split_idx
    print(f"\n开始生成训练集（共 {train_total} 张）...")
    for i, card in enumerate(cards[:train_total], 1):
        try:
            if generate_type == 'ocr':
                generate_card_image(card, generate_type='train')
            else:
                generate_card_image_yolov5(card, generate_type='train')
        except NoDictError as e:
            raise e
        except Exception as e:
            print(f"生成训练集时出现错误：{e}")
        progress = int(20 * i / train_total)
        sys.stdout.write(
            f"\r训练集进度: {i}/{train_total} "
            f"[{'▉' * progress}{' ' * (20 - progress)}] {i / train_total:.1%}"
        )
        sys.stdout.flush()

    # 验证集生成
    val_total = len(cards) - split_idx
    print(f"\n开始生成验证集（共 {val_total} 张）...")
    for i, card in enumerate(cards[train_total:train_total + val_total], 1):
        try:
            if generate_type == 'ocr':
                generate_card_image(card, generate_type='test')
            else:
                generate_card_image_yolov5(card, generate_type='test')
        except NoDictError as e:
            raise e
        except Exception as e:
            print(f"生成训练集时出现错误：{e}")
        progress = int(20 * i / val_total)
        sys.stdout.write(
            f"\r验证集进度: {i}/{val_total} "
            f"[{'▉' * progress}{' ' * (20 - progress)}] {i / val_total:.1%}"
        )
        sys.stdout.flush()
    print("\n验证集生成完成！")

    print("\n训练集生成完成！")


def conversion_card_img_to_yolov5(card, size=640):
    """将图片和坐标转化为640图片"""
    # 调整图片尺寸并填充
    img = card.image
    # 计算缩放比例
    ratio = size / max(img.width, img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)

    # 缩放图片
    resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 创建新图片并粘贴
    new_img = Image.new('RGB', (size, size), (0, 0, 0))
    pad_w = (size - new_w) // 2
    pad_h = (size - new_h) // 2
    new_img.paste(resized_img, (pad_w, pad_h))

    # 调整标注坐标
    adjusted_annotations = []
    for mark_info in card.icon_mark:
        points = mark_info["points"]
        # 将原始坐标转换为新图片坐标
        for i, point in enumerate(points):
            x, y = point
            x = x * ratio + pad_w
            y = y * ratio + pad_h
            points[i] = (x, y)
        mark_info["points"] = points
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        width = x_max - x_min
        height = y_max - y_min
        adjusted_annotations.append(
            f'{get_mark_index(mark_text=mark_info["text"], img=new_img)} {x_center / new_img.width} {y_center / new_img.height} '
            f'{width / new_img.width} {height / new_img.height}\n'
        )

    return new_img, adjusted_annotations


def rand_add_icon(card_data):
    """随机增加数据"""
    if card_data.get('text', None) and len(card_data['text']) > 10:
        text = card_data['text']
        text_line = text.split('\n')
        # 随机插入1-5个图标
        for _ in range(random.randint(1, 5)):
            ramdom_icon = icon_dict.get(random.choice(icon_list), '')
            # 随机插在某一行的开始或结尾
            text_line_index = random.randint(0, len(text_line) - 1)
            if random.random() < 0.5:
                text_line[text_line_index] = f'{ramdom_icon}{text_line[text_line_index]}'
            else:
                text_line[text_line_index] = f'{text_line[text_line_index]}{ramdom_icon}'

        # 汇总为text
        card_data['text'] = '\n'.join(text_line)
    return card_data


def generate_card_image_yolov5(generate_card, generate_type='train'):
    """生成卡牌图片并保存为YOLOv5格式"""
    # 确定是训练集还是测试集
    img_dir = os.path.join(data_root_dir_yolov5, f'{generate_type}/images')
    label_dir = os.path.join(data_root_dir_yolov5, f'{generate_type}/labels')

    # 创建图片目录
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(label_dir, exist_ok=True)

    def build_card(card_json, is_back=False):
        # 从random_pictures目录下随机取一张图片
        random_picture_path = os.path.join('random_pictures',
                                           random.choice(os.listdir(os.path.join('random_pictures'))))
        card_data = rand_add_icon(card_json)
        card_data = card_data_enhancement(card_data)
        card = batch_build_card(
            card_json=card_data,
            font_manager=font_manager,
            image_manager=image_manager,
            is_back=is_back,
            picture_path=random_picture_path
        )
        card.final_processing()
        if card and len(card.icon_mark) > 0:
            # 生成YOLOv5格式的图片和标注
            new_img, annotations = conversion_card_img_to_yolov5(card)
            # 保存图片
            img_path = os.path.join(img_dir, f'{index_data["det_index"]:06d}.jpg')
            new_img = augment_image(new_img)
            new_img.save(img_path, quality=95)
            # 保存标注数据
            label_path = os.path.join(label_dir, f'{index_data["det_index"]:06d}.txt')
            with open(label_path, 'w', encoding='utf-8') as f:
                f.writelines(annotations)

            index_data["det_index"] += 1

    build_card(generate_card)
    if generate_card.get('type_code', None) == 'location':
        build_card(generate_card, is_back=True)


def augment_image(img):
    """
    随机对PIL图像添加噪点或模糊，不改变图像大小
    参数:
        img (PIL.Image.Image): 输入的图像对象
    返回:
        PIL.Image.Image: 处理后的图像对象
    """
    if random.random() < 0.2:
        # 20%的概率不做处理
        return img
    # 统一转换为RGB模式以简化处理
    img = img.convert('RGB')

    if random.random() < 0.5:
        # 添加随机强度的高斯噪声
        sigma = random.uniform(10, 50)
        alpha = random.uniform(0.05, 0.15)

        # 生成RGB三通道独立噪声
        r = Image.effect_noise(img.size, sigma).convert('L')
        g = Image.effect_noise(img.size, sigma).convert('L')
        b = Image.effect_noise(img.size, sigma).convert('L')
        noise_img = Image.merge('RGB', (r, g, b))

        return Image.blend(img, noise_img, alpha)
    else:
        # 添加随机强度的模糊效果
        return img.filter(
            ImageFilter.GaussianBlur(
                radius=random.uniform(0.5, 1.0)
            )
        )


def card_data_enhancement(card_data):
    """对卡牌数据进行增强"""
    # 随机经验
    card_data['xp'] = random.randint(-1, 5)
    # 随机费用
    card_data['cost'] = random.randint(-2, 15)
    if card_data.get('type_code', None) == 'asset':
        # 增加随机血量和san 随机 0到15
        card_data['health'] = random.randint(0, 15)
        card_data['horror'] = random.randint(0, 15)
    if card_data.get('type_code', None) == 'enemy':
        # 增加随机属性
        random_list = ['?', 'X', '-', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        card_data['enemy_fight'] = random.choice(random_list)
        card_data['health'] = random.choice(random_list)
        card_data['enemy_evade'] = random.choice(random_list)
        # 随机True/False
        if card_data['health'] not in ['?', 'X', '-']:
            card_data['health_per_investigator'] = random.choice([True, False])

    print(card_data)
    return card_data


def test_generate_card_image():
    card_data = rand_add_icon(cards[1265])
    card_data = card_data_enhancement(card_data)
    card = batch_build_card(
        card_json=card_data,
        font_manager=font_manager,
        image_manager=image_manager
    )
    if card:
        card.final_processing()

    card.image = augment_image(card.image)
    new_img, mark_list = conversion_card_img_to_yolov5(card)
    draw = ImageDraw.Draw(new_img)
    for mark in card.icon_mark:
        points = mark['points']
        # Draw quadrilateral (assuming points are in order)
        draw.polygon(points, outline="red")
        # Add text label near the box
        draw.text((points[0][0], points[0][1] - 15), mark['text'], fill="red")

    new_img.show()
    print(mark_list)


if __name__ == '__main__':
    font_manager = FontManager('../fonts', lang='en')
    image_manager = ImageManager('../images')
    # 设置环境变量 设置训练数据
    os.environ['CARD_TRAIN_DATA'] = '1'

    generate(generate_type='yolov5')
    # generate()
    # test_generate_card_image()
