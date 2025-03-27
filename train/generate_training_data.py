# 生成OCR训练数据
# 读取cards.json
import json
import os
import random
import sys  # 新增sys模块用于强制刷新

from PIL import ImageDraw

from Card import FontManager, ImageManager
from batch_build import batch_build_card

with open('cards_en.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)
# 数据路径
data_root_dir = r'D:\BaiduSyncdisk\PycharmProjects\arkham-ocr-craft\data_root_dir'

index_data = {
    'file_index': 1
}


def generate_card_image(generate_card, generate_type='train'):
    """
    生成卡牌图片
    :param generate_card: 卡牌数据
    :param generate_type: 数据类型，train/test
    :return:
    """
    dir_images = os.path.join(data_root_dir, 'ch4_training_images')
    dir_transcription_gt = os.path.join(data_root_dir, 'ch4_training_localization_transcription_gt')
    if generate_type == 'test':
        dir_images = os.path.join(data_root_dir, 'ch4_test_images')
        dir_transcription_gt = os.path.join(data_root_dir, 'ch4_test_localization_transcription_gt')
    # 如果不存在目录则创建
    if not os.path.exists(dir_images):
        os.makedirs(dir_images)
    if not os.path.exists(dir_transcription_gt):
        os.makedirs(dir_transcription_gt)

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
            card.image = card.image.convert('RGB')
            card.image.save(os.path.join(dir_images, f'{index_data["file_index"]:06d}.jpg'), quality=95)
            # 保存元数数据
            with open(os.path.join(dir_transcription_gt, f'gt_{index_data["file_index"]:06d}.txt'), 'w',
                      encoding='utf-8') as f:
                for mark_info in card.text_mark:
                    for point in mark_info['points']:
                        f.write(f'{point[0]},{point[1]},')
                    f.write(f'{mark_info["text"]}\n')
            index_data["file_index"] += 1

    build_card(generate_card)
    if generate_card.get('type_code', None) == 'location':
        build_card(generate_card, is_back=True)

    pass


def generate():
    random.shuffle(cards)

    split_idx = int(0.8 * len(cards))

    # 训练集生成
    train_total = split_idx
    # train_total = 20
    print(f"\n开始生成训练集（共 {train_total} 张）...")
    for i, card in enumerate(cards[:train_total], 1):
        try:
            generate_card_image(card, generate_type='train')
        except Exception as e:
            print(f"生成训练集时出现错误：{e}")
        # 添加flush=True强制立即输出，并增加sys.stdout.write保证显示
        progress = int(20 * i / train_total)
        sys.stdout.write(
            f"\r训练集进度: {i}/{train_total} "
            f"[{'▉' * progress}{' ' * (20 - progress)}] {i / train_total:.1%}"
        )
        sys.stdout.flush()

    # 验证集生成（保持相同逻辑）
    val_total = len(cards) - split_idx
    # val_total = 2
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

    print("\n训练集生成完成！")  # 换行确保最终进度可见


def test_generate_card_image():
    card = batch_build_card(
        card_json=cards[14],
        font_manager=font_manager,
        image_manager=image_manager
    )
    draw = ImageDraw.Draw(card.image)
    card.image.show()
    for mark in card.text_mark:
        points = mark['points']
        # Draw quadrilateral (assuming points are in order)
        draw.polygon(points, outline="red")
        # Add text label near the box
        draw.text((points[0][0], points[0][1] - 15), mark['text'], fill="red")
    # card.image.show()


if __name__ == '__main__':
    font_manager = FontManager('../fonts', lang='en')
    image_manager = ImageManager('../images')

    # generate()
    test_generate_card_image()
