import glob
import json
import os
import re
import shutil

import polib
import requests
from PIL import Image

from Card import FontManager, ImageManager
from batch_build import batch_build_card

# 准备工作 ----
working_directory = r'D:\working_directory'

cards_json_name = 'All Player Cards.json'
picture_source = 'source'
picture_processing = 'processing'
picture_output = 'output'
replace_the_directory = r'D:\working_directory\替换'
# 加载必要文件 ----
all_player_cards = []
# with open(os.path.join(working_directory, cards_json_name), 'r', encoding='utf-8') as f:
#     temp = json.load(f)
#     all_player_cards = temp['ObjectStates'][0]['ContainedObjects']
source_dir = os.path.join(working_directory, picture_source)
source_files = os.listdir(source_dir)


# -------------------------------------------------------------

def find_card_objects(directory, result_array):
    """
    扫描指定目录下所有JSON文件，查找包含"name": "Card"的对象

    :param directory: 要扫描的目录路径
    :param result_array: 用于存储结果的数组（会被原地修改）
    :return: 包含所有找到的Card对象的数组
    """

    def check_object(obj):
        """ 递归检查JSON对象 """
        if isinstance(obj, dict):
            # 检查当前字典是否符合条件
            try:
                if obj.get('Name') == 'Card' or obj.get('Name') == 'CardCustom':
                    card_id = str(obj['CardID'])
                    card_deck_id = card_id[:-2]
                    if 'CustomDeck' not in obj:
                        return
                    if 'GMNotes' not in obj or obj['GMNotes'] == '':
                        return
                    if card_deck_id not in obj['CustomDeck']:
                        # 获取obj第一个key
                        key = list(obj['CustomDeck'].keys())[0]
                        obj['CustomDeck'][card_deck_id] = obj['CustomDeck'][key]
                    result_array.append(obj)
            finally:
                # 继续递归检查所有值
                for value in obj.values():
                    check_object(value)
        elif isinstance(obj, list):
            # 递归检查列表中的每个元素
            for item in obj:
                check_object(item)

    # 遍历目录及子目录中的所有json文件
    for json_path in glob.glob(os.path.join(directory, '**/*.json'), recursive=True):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                check_object(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"⚠️ 解析失败: {json_path}")
        except Exception as e:
            print(f"🚨 读取文件异常 [{json_path}]: {str(e)}")

    return result_array


# 写一个方法，传入str，取出str中的所有字母和数字并组成新的str返回
def get_alnum_str(s):
    return ''.join([c for c in s if c.isalnum()])


def split_image_by_index(cols, rows, index, image_path=None, image=None):
    """将图片按指定行列数切割并返回指定序号的子图"""
    # 打开原始图片
    img = image if image is not None else Image.open(image_path)
    width, height = img.size

    # 计算每个子图的尺寸
    block_width = width // cols
    block_height = height // rows

    # 计算裁剪区域坐标
    i = index // cols
    j = index % cols
    left = j * block_width
    upper = i * block_height
    right = (j + 1) * block_width
    lower = (i + 1) * block_height

    # 截取子图并返回
    return img.crop((left, upper, right, lower))


def split_image(image_path, output_dir, cols, rows):
    """
    将图片按指定行列数切割并保存到目标目录
    :param image_path: 原始图片路径
    :param output_dir: 输出目录路径
    :param cols: 水平分割数（列数）
    :param rows: 垂直分割数（行数）
    """
    # 打开原始图片
    file_suffix = image_path.split('.')[-1]
    img = Image.open(image_path)
    width, height = img.size

    # 计算每个子图的尺寸
    block_width = width // cols
    block_height = height // rows

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 遍历所有行列进行切割
    for i in range(rows):
        for j in range(cols):
            # 计算裁剪区域坐标
            left = j * block_width
            upper = i * block_height
            right = (j + 1) * block_width
            lower = (i + 1) * block_height

            # 截取子图并保存
            crop_img = img.crop((left, upper, right, lower))
            index = i * cols + j  # 计算序号
            crop_img.save(os.path.join(output_dir, f"{index:02d}.{file_suffix}"))
            pass
        pass
    pass


def merge_images(metadata, input_dir, output_dir, source_dir):
    """
    将分割后的卡牌图片合并为完整图片
    :param metadata: 元数据
    :param input_dir: 分割后的图片目录
    :param output_dir: 合并后的输出路径
    """
    cols = metadata['width']
    rows = metadata['height']

    # 打开第一个图片获取尺寸
    block_width, block_height = None, None
    for card in metadata['cards']:
        if 'output_file_name' in card:
            with Image.open(os.path.join(input_dir, card['output_file_name'])) as img:
                block_width, block_height = img.size
            break
    if block_width is None or block_height is None:
        print('无法获取图片尺寸')
        return

    # 创建新画布
    merged = Image.new('RGB', (cols * block_width, rows * block_height), color=(0, 0, 0))

    # 逐个粘贴图片
    for i in range(rows):
        for j in range(cols):
            index = i * cols + j
            # 查找id的文件
            b = False
            for card in metadata['cards']:
                if card['id'] == index:
                    if 'output_file_name' in card:
                        file_path = os.path.join(input_dir, card['output_file_name'])
                        b = True
                        with Image.open(file_path) as img:
                            # 计算粘贴位置
                            x = j * block_width
                            y = i * block_height
                            img = img.resize((block_width, block_height))
                            merged.paste(img, (x, y))
                        break
                    else:
                        file_path = os.path.join(source_dir, card['file_name'])
                        b = True
                        # 使用源的图片
                        with Image.open(file_path) as img:
                            # 计算粘贴位置
                            x = j * block_width
                            y = i * block_height
                            img = img.resize((block_width, block_height))
                            merged.paste(img, (x, y))
                        break
            if b is False:
                # 使用源的图片
                try:
                    file_path = os.path.join(source_dir, f"{index:02d}.jpg")
                    if not os.path.exists(file_path):
                        file_path = os.path.join(source_dir, f"{index:02d}.png")
                    with Image.open(file_path) as img:
                        # 计算粘贴位置
                        x = j * block_width
                        y = i * block_height
                        img = img.resize((block_width, block_height))
                        merged.paste(img, (x, y))
                except:
                    print('未找到图片')
                pass

    # 检测metadata['file_name']后缀名，统一生成出jpg
    file_suffix = metadata['file_name'].split('.')[-1]
    if file_suffix == 'png':
        metadata['file_name'] = metadata['file_name'].replace('.png', '.jpg')
    # 保存合并后的图片
    merged.save(os.path.join(output_dir, metadata['file_name']))


def sorting_images_by_id():
    """额外分拣所有图片到特定文件夹并以ID命名"""
    sorting_images_output_dir = os.path.join(working_directory, 'sorting_images_output')
    # 如果文件夹不存在则创建
    if not os.path.exists(sorting_images_output_dir):
        os.mkdir(sorting_images_output_dir)
        pass
    # 查找加工文件夹下的所有文件夹，除去未查找到信息的文件
    processing_folders = [folder for folder in os.listdir(os.path.join(working_directory, picture_processing))
                          if folder != '未查找到信息的文件']
    processing_folders_len = len(processing_folders)
    for index, folder in enumerate(processing_folders):
        print(f'正在分拣第{index + 1}/{processing_folders_len}个文件夹')
        # 读取metadata.json
        with open(os.path.join(working_directory, picture_processing, folder, 'metadata.json'), 'r',
                  encoding='utf-8') as f:
            metadata = json.load(f)
            pass
        # 将metadata['cards']按id从小到大排序
        metadata['cards'].sort(key=lambda x: x['id'])
        for card in metadata['cards']:
            card_id = card['GMNotes']['id']
            file_name = card['file_name']
            # 读取file_name图片，转成jpg后保存到sorting_images_output_dir，以card_id命名
            # 读取图片
            with Image.open(os.path.join(working_directory, picture_processing, folder, file_name)) as img:
                # 如果图片不是jpg格式，转成jpg
                if img.format != 'JPEG':
                    img = img.convert('RGB')
                # 将图片向左旋转90度
                # img = img.transpose(Image.ROTATE_90)
                # 保存图片
                img.save(os.path.join(sorting_images_output_dir, f"{card_id}-{'a' if card['is_back'] else 'b'}.jpg"))


def sorting_images():
    """分拣图片"""
    print('正在清理文件夹...')
    # 清理加工文件夹内容以及子文件夹
    try:
        for folder in [picture_processing, picture_output]:
            for file in os.listdir(os.path.join(working_directory, folder)):
                shutil.rmtree(os.path.join(working_directory, folder, file))
    except Exception:
        pass
    # 在加工文件夹创建一个文件夹叫“未查找到信息的文件”
    if not os.path.exists(os.path.join(working_directory, picture_processing, '未查找到信息的文件')):
        os.mkdir(os.path.join(working_directory, picture_processing, '未查找到信息的文件'))
    # 清理'未查找到信息的文件'的文件
    for file in os.listdir(os.path.join(working_directory, picture_processing, '未查找到信息的文件')):
        os.remove(os.path.join(working_directory, picture_processing, '未查找到信息的文件', file))
    # 将all_player_cards的地址转化为缓存文件名
    for card in all_player_cards:
        card_id = str(card['CardID'])
        card_deck_id = card_id[:-2]
        custom_deck = card['CustomDeck'][card_deck_id]
        custom_deck['FaceURL'] = get_alnum_str(custom_deck['FaceURL'])
        custom_deck['BackURL'] = get_alnum_str(custom_deck['BackURL'])
    # 查找source文件夹下的所有文件
    print('开始分拣图片...')
    source_files_len = len(source_files)
    for index, file in enumerate(source_files):
        print(f'正在处理第{index + 1}/{source_files_len}张图片')
        # if 'httpssteamusercontentaakamaihdnetugc1684870715280867313BFD2AF968EAC917D3B838DCB8B1656941CD8' not in file:
        #     continue
        # 取file文件名不包含后缀
        file_name = file.split('.')[0]
        # 取file文件名后缀
        file_suffix = file.split('.')[-1]
        # 查找图片对应的json
        # 生成图片元数据
        deck_metadata = {
            'file_name': file,
            'width': 0,
            'height': 0,
            'cards': []
        }
        for card in all_player_cards:
            card_id = str(card['CardID'])
            card_deck_id = card_id[:-2]
            card_deck_num = int(card_id[-2:])
            custom_deck = card['CustomDeck'][card_deck_id]
            if custom_deck['FaceURL'] == file_name or custom_deck['BackURL'] == file_name:
                deck_metadata['cards'].append({
                    'id': card_deck_num,
                    'file_name': card_id[-2:] + '.' + file_suffix,
                    'GMNotes': json.loads(card['GMNotes']),
                    'is_back': custom_deck['BackURL'] == file_name
                })
                deck_metadata['width'] = custom_deck['NumWidth']
                deck_metadata['height'] = custom_deck['NumHeight']
            pass
        if len(deck_metadata['cards']) > 0 and deck_metadata['width'] > 0 and deck_metadata['height'] > 0:
            # 将deck_metadata['cards']按id从小到大排序
            deck_metadata['cards'].sort(key=lambda x: x['id'])
            # 清除重复id的对象
            temp = []
            for card in deck_metadata['cards']:
                if card['id'] not in [t['id'] for t in temp]:
                    temp.append(card)
            deck_metadata['cards'] = temp
            # 创建index文件夹
            index_dir = os.path.join(working_directory, picture_processing, file_name)
            os.makedirs(index_dir, exist_ok=True)
            # 写入元数据
            with open(os.path.join(index_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
                json.dump(deck_metadata, f, ensure_ascii=False, indent=4)
                pass
            # 分割图片
            split_image(
                image_path=os.path.join(source_dir, file),
                output_dir=index_dir,
                cols=deck_metadata['width'],
                rows=deck_metadata['height']
            )
            pass
        else:
            # 将图片复制到未查找到信息的文件夹
            shutil.copy2(os.path.join(source_dir, file),
                         os.path.join(working_directory, picture_processing, '未查找到信息的文件', file))
            pass
        pass
    print('分拣完成！')


def find_db_player_card_by_id(card_id, player_cards):
    find_db_player_card = None
    for db_player_card in player_cards:
        if db_player_card['code'] == card_id:
            find_db_player_card = db_player_card
            break
        # 查找taboo
        if '-t' in card_id:
            if db_player_card['code'] == card_id.replace('-t', ''):
                find_db_player_card = replace_taboo_card(db_player_card)
                break
            pass
        pass
    return find_db_player_card


temp_taboo_list = {}


def remake_player_cards(additional_exports=False, replace_investigators=False):
    """汉化玩家卡"""
    font_manager = FontManager()
    image_manager = ImageManager()
    # 读取player_cards.json
    with open(os.path.join(working_directory, 'player_cards.json'), 'r', encoding='utf-8') as f:
        player_cards = json.load(f)
    # 遍历player_cards，替换text内容
    for db_player_card in player_cards:
        if 'text' in db_player_card:
            db_player_card['text'] = db_player_card['text'].replace('.', '。')
    # 查找加工文件夹下的所有文件夹，除去未查找到信息的文件
    processing_folders = [folder for folder in os.listdir(os.path.join(working_directory, picture_processing))
                          if folder != '未查找到信息的文件']
    processing_folders_len = len(processing_folders)
    # 统计遭遇组
    encounter_groups = count_encounter_groups()
    for index, folder in enumerate(processing_folders):
        print(f'正在制作第{index + 1}/{processing_folders_len}个文件夹')
        # 读取metadata.json
        with open(os.path.join(working_directory, picture_processing, folder, 'metadata.json'), 'r',
                  encoding='utf-8') as f:
            metadata = json.load(f)
            pass
        # # # 临时测试第一个文件夹
        # if index != 51:
        #     continue
        if folder != 'httpssteamusercontentaakamaihdnetugc2424696374430578395F97B770FB90EA18B46F58614CCE0016406E3E777':
            continue

        print('folder', folder)
        print(metadata)
        # 在目录下创建临时的output目录
        output_dir = os.path.join(working_directory, picture_processing, folder, 'output')
        os.makedirs(output_dir, exist_ok=True)
        # 读取所有卡片
        # 将metadata['cards']按id从小到大排序
        metadata['cards'].sort(key=lambda x: x['id'])
        for card in metadata['cards']:
            # 读取卡片元数据
            card_id = card['GMNotes']['id']
            find_db_player_card = find_db_player_card_by_id(card_id, player_cards)
            if find_db_player_card is not None:
                # 构建卡牌
                print("构建卡牌", find_db_player_card['code'], find_db_player_card['name'])
                output_card = batch_build_card(
                    card_json=find_db_player_card,
                    font_manager=font_manager,
                    image_manager=image_manager,
                    picture_path=os.path.join(working_directory, picture_processing, folder, card['file_name']),
                    encounter_count=encounter_groups.get(find_db_player_card.get('encounter_code', ''), -1),
                    is_back=card.get('is_back', False)
                )
                # 保存卡牌
                card['output_file_name'] = card['file_name'].split('.')[0] + '.png'
                print('正在保存卡牌', card['output_file_name'])
                if output_card is not None:
                    if additional_exports:
                        # 额外导出，按code命名
                        if find_db_player_card['type_name'] in ['支援', '事件', '技能'] or \
                                (find_db_player_card.get('subtype_code', '') == 'weakness' or
                                 find_db_player_card.get('subtype_code', '') == 'basicweakness'):
                            # 转成RGB
                            temp = output_card.image.convert('RGB')
                            # 将图片长宽缩小一半
                            temp = temp.resize((int(temp.width / 1.5), int(temp.height / 1.5)))
                            temp.save(
                                os.path.join(working_directory, 'additional_exports',
                                             f'{find_db_player_card["code"]}-t.jpg'),
                                quality=75)
                            temp_taboo_list[find_db_player_card["code"]] = find_db_player_card
                            pass

                    output_card.image.save(os.path.join(output_dir, card['output_file_name']), quality=95)
                else:
                    print('不支持的卡牌类型', find_db_player_card['type_name'])
                    # 在替换目录中查找代替翻译图
                    replace_file_name = os.path.join(replace_the_directory, metadata['file_name'])
                    if os.path.exists(replace_file_name):
                        # 粘贴替换图
                        print("替换翻译图")
                        im = split_image_by_index(
                            image_path=replace_file_name,
                            cols=metadata['width'],
                            rows=metadata['height'],
                            index=card['id']
                        )
                        print(os.path.join(output_dir, card['output_file_name']))
                        im.save(os.path.join(output_dir, card['output_file_name']), quality=95)
                    else:
                        print("替换原图")
                        # 粘贴原图
                        shutil.copy2(
                            os.path.join(working_directory, picture_processing, folder, card['file_name']),
                            os.path.join(output_dir, card['output_file_name'])
                        )
            pass
        # 合并卡牌
        print('合并卡牌', json.dumps(metadata))
        merge_images(
            metadata=metadata,
            input_dir=output_dir,
            output_dir=os.path.join(working_directory, picture_output),
            source_dir=os.path.join(working_directory, picture_processing, folder)
        )
        pass


# 读取 taboo.json
with open(os.path.join(working_directory, 'taboos.json'), 'r', encoding='utf-8') as f:
    taboos = json.load(f)


def load_translations(po_file):
    """加载 PO 文件并保留原始换行符"""
    po = polib.pofile(po_file)
    translations = {}
    for entry in po:
        if entry.msgid and entry.msgstr:
            # 保留原始换行符
            msgid = entry.msgid
            msgstr = entry.msgstr
            translations[msgid] = msgstr
    return translations


def translate(text, translations):
    """翻译文本并保留换行结构"""
    # 标准化换行符为 \n 并去除首尾空格
    normalized = text.strip().replace('\r\n', '\n').replace('\r', '\n')
    return translations.get(normalized, text)


sys_translations = load_translations(os.path.join(working_directory, 'translations', 'taboos.po'))


def replace_taboo_card(player_card):
    """替换Taboo卡牌"""
    taboo_date = '2024-10-23'
    find_taboo_card = None
    print(player_card['name'], json.dumps(player_card))
    for taboo in taboos:
        if taboo['date_start'] == taboo_date:
            for taboo_card in taboo['cards']:
                if player_card['code'] == taboo_card['code']:
                    find_taboo_card = taboo_card
                    break
            break
        pass
    print('替换Taboo卡牌', find_taboo_card)
    if find_taboo_card is None:
        print('未找到Taboo卡牌')
        return player_card
    # 替换player_card的内容
    if 'replacement_text' in find_taboo_card:
        original_text = find_taboo_card['replacement_text']
        print(player_card['name'], 'original_text', original_text)
        player_card['text'] = translate(original_text, sys_translations)
        player_card['text'] = player_card['text'].replace('\\', '')
    if 'xp' in find_taboo_card:
        print(player_card['name'], find_taboo_card['xp'])
        if find_taboo_card['xp'] > 0:
            player_card['text'] = f"束缚(+{find_taboo_card['xp']}经验)。" + player_card['text']
        elif find_taboo_card['xp'] < 0:
            player_card['text'] = f"释放({find_taboo_card['xp']}经验)。" + player_card['text']
    print('替换后', json.dumps(player_card))
    print('-------------')
    # 不改变上面部分继续续写，根据taboo_card的内容替换player_card的内容

    return player_card


def download_cards(download_all=False):
    """下载卡图图片"""
    # 读取player_cards.json
    with open(os.path.join(working_directory, 'player_cards.json'), 'r', encoding='utf-8') as f:
        player_cards = json.load(f)
    FaceURL = set()
    for card in all_player_cards:
        card_id = str(card['CardID'])
        card_deck_id = card_id[:-2]

        custom_deck = card['CustomDeck'][card_deck_id]
        GMNotes = json.loads(card['GMNotes'])
        if download_all is False:
            for db_player_card in player_cards:
                if db_player_card['code'] == GMNotes['id']:
                    if 'The Drowned City Investigator Expansion' == db_player_card['pack_name']:
                        continue
                    if db_player_card['type_name'] in ['调查员', '剧本', '密谋', '场景']:
                        continue
                    # 下载图片
                    FaceURL.add(custom_deck['FaceURL'])
                    # 下载背面
                    if 'UniqueBack' in custom_deck and custom_deck['UniqueBack'] is True:
                        FaceURL.add(custom_deck['BackURL'])
                    pass
        else:
            # 下载所有
            FaceURL.add(custom_deck['FaceURL'])
            # 下载背面
            if 'UniqueBack' in custom_deck and custom_deck['UniqueBack'] is True:
                FaceURL.add(custom_deck['BackURL'])
            pass
    # 下载图片
    print(len(FaceURL))
    count = 1
    # 下载所有唯一图片
    for url in FaceURL:
        try:
            # 格式化文件名
            filename = get_alnum_str(url)
            # 检测文件是否存在 jpg或png都检查
            if os.path.exists(os.path.join(working_directory, picture_source, f"{filename}.jpg")) or os.path.exists(
                    os.path.join(working_directory, picture_source, f"{filename}.png")):
                print(f'已存在 {filename}')
                continue
            # 下载图片 使用代理
            proxies = {
                'http': 'http://127.0.0.1:7890',
                'https': 'http://127.0.0.1:7890',
            }
            response = requests.get(url, stream=True, timeout=30, proxies=proxies)
            response.raise_for_status()  # 检查HTTP状态码

            save_path = os.path.join(working_directory, picture_source, filename)

            # 保存图片文件
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # 判断图片是PNG还是JPG
            file_suffix = ''
            with Image.open(save_path) as img:
                image_format = img.format.upper()
                if image_format == 'JPEG':
                    file_suffix = 'jpg'
                elif image_format == 'PNG':
                    file_suffix = 'png'
                else:
                    print(f'未知图片格式 {image_format}')
                    continue
            # 重命名文件
            os.rename(save_path, os.path.join(working_directory, picture_source, f"{filename}.{file_suffix}"))

            print(f'成功下载 {filename}')

        except Exception as e:
            print(f'下载失败 {url}，错误：{str(e)}')
            continue


def replace_translations():
    """替换翻译"""
    # 读取player_cards.json
    with open(os.path.join(working_directory, 'player_cards.json'), 'r', encoding='utf-8') as f:
        player_cards = json.load(f)
    # 搜索工作目录下的translations文件夹的所有json文件，包括子文件夹
    translations = []
    for root, dirs, files in os.walk(os.path.join(working_directory, 'translations', 'pack')):
        for file in files:
            if file.endswith('.json'):
                translations.append(os.path.join(root, file))
    # 遍历读取每个json
    for translation in translations:
        with open(translation, 'r', encoding='utf-8') as f:
            temp_card_json = json.load(f)
            for temp_card in temp_card_json:
                for db_player_card in player_cards:
                    if temp_card['code'] == db_player_card['code']:
                        # 获取temp_card所有的key
                        temp_card_keys = temp_card.keys()
                        for key in temp_card_keys:
                            # 替换db_player_card的key
                            db_player_card[key] = temp_card[key]
                        break
                    pass
                pass
    # 保存player_cards.json
    with open(os.path.join(working_directory, 'player_cards.json'), 'w', encoding='utf-8') as f:
        json.dump(player_cards, f, ensure_ascii=False, indent=4)


def count_encounter_groups():
    # 读取player_cards.json
    with open(os.path.join(working_directory, 'player_cards.json'), 'r', encoding='utf-8') as f:
        player_cards = json.load(f)
    encounter_count = dict()
    card_repetition = set()
    for card in all_player_cards:
        if 'GMNotes' not in card:
            continue
        GMNotes = json.loads(card['GMNotes'])
        if 'id' not in GMNotes:
            continue
        find_db_player_card = find_db_player_card_by_id(GMNotes['id'], player_cards)
        if find_db_player_card is not None \
                and find_db_player_card['code'] not in card_repetition and 'encounter_code' in find_db_player_card:
            card_repetition.add(find_db_player_card['code'])
            encounter_code = find_db_player_card['encounter_code']
            if encounter_code in encounter_count:
                encounter_count[encounter_code] += find_db_player_card['quantity']
            else:
                encounter_count[encounter_code] = find_db_player_card['quantity']
    return encounter_count


def test1():
    """测试1"""
    # 随机从all_player_cards数组取200张卡
    import random
    # 读取player_cards.json
    with open(os.path.join(working_directory, 'player_cards.json'), 'r', encoding='utf-8') as f:
        def replace_bold(match):
            content = match.group(1)
            if "设计" in content:
                return f""  # 如果包含“设计”，删除
            else:
                return f"【{content}】"  # 否则用【】包裹

        def replace_italic(match):
            content = match.group(1)
            if "FAQ" in content:
                return f""  # 如果包含“设计”，删除
            else:
                return f"{content}"

        text = f.read()
        text = re.sub(r'<b>(.*?)</b>', replace_bold, text)
        text = re.sub(r'<i>(.*?)</i>', replace_italic, text)
        text = re.sub(r'\[\[(.*?)]]', r"{\1}", text)
        text = re.sub(r'\[action]', r"<启动>", text)
        text = re.sub(r'\[Action]', r"<启动>", text)
        text = re.sub(r'\[reaction]', r"<反应>", text)
        text = re.sub(r'\[free]', r"<免费>", text)
        text = re.sub(r'\[fast]', r"<免费>", text)

        text = re.sub(r'\[combat]', r"<拳>", text)
        text = re.sub(r'\[intellect]', r"<书>", text)
        text = re.sub(r'\[willpower]', r"<脑>", text)
        text = re.sub(r'\[agility]', r"<脚>", text)
        text = re.sub(r'\[wild]', r"<?>", text)

        text = re.sub(r'\[skull]', r"<骷髅>", text)
        text = re.sub(r'\[cultist]', r"<异教徒>", text)
        text = re.sub(r'\[elder_thing]', r"<古神>", text)
        text = re.sub(r'\[tablet]', r"<石板>", text)
        text = re.sub(r'\[auto_fail]', r"<触手>", text)
        text = re.sub(r'\[elder_sign]', r"<旧印>", text)
        text = re.sub(r'\[bless]', r"<祝福>", text)
        text = re.sub(r'\[curse]', r"<诅咒>", text)

        text = re.sub(r'\[per_investigator]', r"<调查员>", text)
        text = re.sub(r'\[guardian]', r"<守护者>", text)
        text = re.sub(r'\[seeker]', r"<探求者>", text)
        text = re.sub(r'\[rogue]', r"<流浪者>", text)
        text = re.sub(r'\[mystic]', r"<潜修者>", text)
        text = re.sub(r'\[survivor]', r"<生存者>", text)
        player_cards = json.loads(text)
    random.shuffle(all_player_cards)
    random_player_cards = all_player_cards[:200]
    random_output_cards = []
    for item in all_player_cards:
        card_id = str(item['CardID'])
        card_deck_id = card_id[:-2]
        custom_deck = item['CustomDeck'][card_deck_id]
        GMNotes = json.loads(item['GMNotes'])
        find_db_player_card = find_db_player_card_by_id(GMNotes['id'], player_cards)
        if find_db_player_card is not None:
            if 'text' in find_db_player_card:
                random_output_cards.append({
                    'real_text': find_db_player_card['real_text'],
                    'translate_text': find_db_player_card['text']
                })
            print('------------------')
        pass

    # 写出到random_player_cards
    with open(os.path.join(working_directory, 'random_player_cards.json'), 'w', encoding='utf-8') as f:
        json.dump(random_output_cards, f, ensure_ascii=False, indent=4)


def remake_investigators_cards():
    """充值调查员卡"""
    # 读取player_cards.json
    with open(os.path.join(working_directory, 'player_cards.json'), 'r', encoding='utf-8') as f:
        player_cards = json.load(f)
    # 遍历player_cards，筛选type_code=investigator的对象
    investigators_cards = []
    for card in player_cards:
        if card['type_code'] == 'investigator':
            investigators_cards.append(card)
    # 重置调查员卡
    font_manager = FontManager()
    image_manager = ImageManager()
    for investigator_card in investigators_cards:
        if 'encounter_name' in investigator_card:
            continue
        if investigator_card['code'][:2] == '90':
            continue
        picture_path = os.path.join(working_directory, 'investigators', 'sorting_images_output',
                                    f"{investigator_card['code']}-b.jpg")
        if not os.path.exists(picture_path):
            continue
        # 构建卡牌
        output_card = batch_build_card(
            card_json=investigator_card,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path,
            encounter_count=-1,
            is_back=False
        )
        # 保存卡牌
        if output_card is not None:
            print('正在保存卡牌', investigator_card)
            output_card.image.save(
                os.path.join(working_directory, 'investigators', f"{investigator_card['code']}-a.png"),
                quality=95)
            # # 转成RGB
            # temp_p = output_card.image.convert('RGB')
            # # 将图片长宽缩小一半
            # temp_p = temp_p.resize((int(temp_p.width / 1.5), int(temp_p.height / 1.5)))
            # temp_p.save(
            #     os.path.join(working_directory, 'investigators', f"{investigator_card['code']}-a.jpg"),
            #     quality=75)
        #
        picture_path_2 = os.path.join(working_directory, 'investigators', 'sorting_images_output',
                                      f"{investigator_card['code']}-a.jpg")
        if not os.path.exists(picture_path):
            continue
        # 构建卡牌
        output_card_2 = batch_build_card(
            card_json=investigator_card,
            font_manager=font_manager,
            image_manager=image_manager,
            picture_path=picture_path_2,
            encounter_count=-1,
            is_back=True
        )
        # 保存卡牌
        if output_card_2 is not None:
            print('正在保存卡牌', investigator_card)
            output_card_2.image.save(
                os.path.join(working_directory, 'investigators', f"{investigator_card['code']}-b.png"),
                quality=95)

            # # 转成RGB
            # temp_p = output_card_2.image.convert('RGB')
            # # 将图片长宽缩小一半
            # temp_p = temp_p.resize((int(temp_p.width / 1.5), int(temp_p.height / 1.5)))
            # temp_p.save(
            #     os.path.join(working_directory, 'investigators', f"{investigator_card['code']}-b.jpg"),
            #     quality=75)


if __name__ == '__main__':
    # 所有玩家卡
    # with open(os.path.join(working_directory, cards_json_name), 'r', encoding='utf-8') as f:
    #     temp = json.load(f)
    #     all_player_cards = temp['ObjectStates'][0]['ContainedObjects']
    # 搜索JSON卡牌对象
    find_card_objects(os.path.join(working_directory, 'source_json'), all_player_cards)
    # print(json.dumps(all_player_cards))
    # test1()
    # 下载卡图
    # download_cards(download_all=True)
    # 分拣卡图
    sorting_images()
    # 额外分拣成ID文件名
    # sorting_images_by_id()
    # 替换翻译
    # replace_translations()
    # 制作卡牌
    remake_player_cards(additional_exports=False, replace_investigators=True)
    # print(json.dumps(temp_taboo_list, ensure_ascii=False, indent=4))

    # 制作调查员卡
    # remake_investigators_cards()
    pass
