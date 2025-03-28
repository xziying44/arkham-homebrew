# 生成OCR训练数据
# 读取cards.json
import json
import os
import random
import sys
from PIL import ImageDraw
from Card import FontManager, ImageManager
from batch_build import batch_build_card

with open('cards_en.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# 修改数据路径配置为PaddleOCR格式
data_root_dir = r'D:\OCR_DATA\train_data'

# 创建目录结构
os.makedirs(os.path.join(data_root_dir, 'det/train'), exist_ok=True)
os.makedirs(os.path.join(data_root_dir, 'det/test'), exist_ok=True)
os.makedirs(os.path.join(data_root_dir, 'rec/train'), exist_ok=True)
os.makedirs(os.path.join(data_root_dir, 'rec/test'), exist_ok=True)

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
    '💙'
]


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
        card = batch_build_card(
            card_json=card_json,
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
                icon_exist = False
                for icon in icon_list:
                    if icon in mark_info["text"]:
                        icon_exist = True
                        break
                if not icon_exist:
                    continue
                if mark_info["text"] in icon_list:
                    continue
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


def generate():
    random.shuffle(cards)

    split_idx = int(0.8 * len(cards))

    # 训练集生成
    train_total = split_idx
    print(f"\n开始生成训练集（共 {train_total} 张）...")
    for i, card in enumerate(cards[:train_total], 1):
        try:
            generate_card_image(card, generate_type='train')
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
            generate_card_image(card, generate_type='test')
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


def test_generate_card_image():
    card = batch_build_card(
        card_json=cards[14],
        font_manager=font_manager,
        image_manager=image_manager
    )
    draw = ImageDraw.Draw(card.image)
    for mark in card.text_mark:
        points = mark['points']
        # Draw quadrilateral (assuming points are in order)
        draw.polygon(points, outline="red")
        # Add text label near the box
        draw.text((points[0][0], points[0][1] - 15), mark['text'], fill="red")
    card.image.show()


if __name__ == '__main__':
    font_manager = FontManager('../fonts', lang='en')
    image_manager = ImageManager('../images')

    # 清空已有的标注文件
    for gt_file in ['det/det_gt_train.txt', 'det/det_gt_test.txt',
                    'rec/rec_gt_train.txt', 'rec/rec_gt_test.txt']:
        if os.path.exists(os.path.join(data_root_dir, gt_file)):
            os.remove(os.path.join(data_root_dir, gt_file))

    generate()
    # test_generate_card_image()
