import json
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

import requests
from PIL import Image

from ResourceManager import FontManager, ImageManager
from create_card import CardCreator
from remaek_card.arkhamdb2card import ArkhamDBConverter

# 在现有导入语句后添加

location_icon = {
    'Circle': '地点标识-黄圆',
    'Hourglass': '地点标识-暗红漏斗',
    'Tilde': '地点标识-褐扭',
    'Square': '地点标识-红方',
    'Tee': '地点标识-深蓝T',
    'Diamond': '地点标识-绿菱',
    'Triangle': '地点标识-蓝三角',
    'Crescent': '地点标识-紫月',
    'Plus': '地点标识-红十',
    'SlantedEquals': '地点标识-深绿斜二',
}


class RemakeCardsTranslationTask:
    """重置卡牌任务"""

    def __init__(
            self,
            work_dir: str
    ) -> None:
        # 构建work_dir的绝对路径
        self.work_dir = os.path.abspath(work_dir)

        # 查询目录下的objects文件夹，搜索所有json文件
        object_files = []
        for root, dirs, files in os.walk(os.path.join(self.work_dir, 'objects')):
            for file in files:
                if file.endswith('.json'):
                    object_files.append(os.path.join(root, file))
        self.result_array = []
        for file in object_files:
            with open(file, 'r', encoding='utf-8') as f:
                self.result_array.extend(self._find_cards_in_json(json.load(f)))

        # 加载检查db_cards.json是否存在，存在则读取db_cards.json为对象
        self.db_cards = []
        db_cards_path = 'db_cards.json'
        if os.path.exists(db_cards_path):
            try:
                with open(db_cards_path, 'r', encoding='utf-8') as f:
                    self.db_cards = json.load(f)
                print(f"成功加载 db_cards.json，包含 {len(self.db_cards)} 条记录")
            except json.JSONDecodeError as e:
                print(f"读取 db_cards.json 时发生JSON解析错误: {e}")
                self.db_cards = []
            except Exception as e:
                print(f"读取 db_cards.json 时发生错误: {e}")
                self.db_cards = []
        else:
            print("db_cards.json 文件不存在，将创建新的数据库")

        # 在初始化时读取metadata.json
        self.metadata = {}
        metadata_file = os.path.join(self.work_dir, 'metadata.json')
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f"成功加载 metadata.json，包含 {len(self.metadata)} 条记录")
            except json.JSONDecodeError as e:
                print(f"读取 metadata.json 时发生JSON解析错误: {e}")
                self.metadata = {}
            except Exception as e:
                print(f"读取 metadata.json 时发生错误: {e}")
                self.metadata = {}
        else:
            print("metadata.json 文件不存在，请先运行 arrange_metadata() 方法")

    @staticmethod
    def _get_alnum_str(s):
        return ''.join([c for c in s if c.isalnum()])

    def _find_cards_in_json(self, object_json):
        result_array = []

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
                        if card_deck_id not in obj['CustomDeck']:
                            # 获取obj第一个key
                            key = list(obj['CustomDeck'].keys())[0]
                            obj['CustomDeck'][card_deck_id] = obj['CustomDeck'][key]
                        obj['FormatFaceURL'] = self._get_alnum_str(obj['CustomDeck'][card_deck_id]['FaceURL'])
                        obj['FormatBackURL'] = self._get_alnum_str(obj['CustomDeck'][card_deck_id]['BackURL'])
                        obj['UniqueBack'] = obj['CustomDeck'][card_deck_id]['UniqueBack']
                        result_array.append(obj)
                finally:
                    # 继续递归检查所有值
                    for value in obj.values():
                        check_object(value)
            elif isinstance(obj, list):
                # 递归检查列表中的每个元素
                for item in obj:
                    check_object(item)

        check_object(object_json)
        return result_array

    @staticmethod
    def _print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
        """
        打印进度条
        :param iteration: 当前迭代次数
        :param total: 总迭代次数
        :param prefix: 前缀字符串
        :param suffix: 后缀字符串
        :param length: 进度条长度
        :param fill: 进度条填充字符
        """
        percent = "{0:.1f}".format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
        sys.stdout.flush()
        if iteration == total:
            print()

    def download_cards(self):
        """下载卡牌"""
        download_cache_path = os.path.join(self.work_dir, 'download')
        if not os.path.exists(download_cache_path):
            os.mkdir(download_cache_path)
        FaceURL = set()
        for card in self.result_array:
            card_id = str(card['CardID'])
            card_deck_id = card_id[:-2]

            custom_deck = card['CustomDeck'][card_deck_id]
            # # 格式化URL
            # match = re.search(r'https?://\S+', custom_deck['FaceURL'])
            # if match:
            #     FaceURL.add(match.group(0))
            #     match = re.search(r'https?://\S+', custom_deck['BackURL'])
            # if match:
            #     FaceURL.add(match.group(0))
            FaceURL.add(custom_deck['FaceURL'])
            FaceURL.add(custom_deck['BackURL'])

        # 下载图片 使用代理
        proxies = {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890',
        }

        # 下载图片
        def download_image(download_url: str, max_retries: int = 3) -> bool:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            }

            for attempt in range(max_retries):
                try:
                    # 格式化文件名
                    filename = self._get_alnum_str(download_url)
                    # 检测文件是否存在 jpg或png都检查
                    if os.path.exists(os.path.join(download_cache_path, f"{filename}.jpg")):
                        return True

                    response = requests.get(
                        download_url,
                        stream=True,
                        timeout=30,
                        proxies=proxies,
                        headers=headers
                    )
                    response.raise_for_status()  # 检查HTTP状态码

                    save_path = os.path.join(download_cache_path, filename)

                    # 保存图片文件
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    # 统一把图片转为jpg格式
                    with Image.open(save_path) as img:
                        # 转为RGB模式
                        img = img.convert('RGB')
                        # 保存为jpg格式
                        img.save(save_path + '.jpg', quality=95)

                    # 删除原始文件
                    os.remove(save_path)
                    return True

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        wait_time = (attempt + 1) * 5  # 指数退避
                        print(f'\n遇到429错误，等待{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})')
                        sleep(wait_time)
                        continue
                    print(f'\n下载失败 {download_url}，HTTP错误：{str(e)}')
                    return False
                except Exception as e:
                    print(f'\n下载失败 {download_url}，错误：{str(e)}')
                    return False

            print(f'\n下载失败 {download_url}，达到最大重试次数')
            return False

        total_urls = len(FaceURL)
        print(f"开始下载 {total_urls} 张卡牌图片...")

        success_count = 0
        for i, url in enumerate(FaceURL, 1):
            # 更新进度条
            self._print_progress_bar(i, total_urls, prefix='进度:', suffix=f'完成 {i}/{total_urls}', length=30)

            # 如果失败最多重试3次
            for retry in range(3):
                if download_image(url):
                    success_count += 1
                    break
                if retry == 2:  # 最后一次重试失败
                    print(f'\n下载失败: {url} (尝试3次后仍然失败)')

        print(f"\n下载完成! 成功下载 {success_count}/{total_urls} 张图片")

    @staticmethod
    def _get_custom_deck(card_object: dict):
        """获取自定义牌组"""
        card_id = str(card_object['CardID'])
        card_deck_id = card_id[:-2]

        custom_deck = card_object['CustomDeck'][card_deck_id]
        custom_deck['index'] = int(card_id[-2:])
        return custom_deck

    def get_card_by_code(self, code: str) -> dict | None:
        """
        根据code查询db_cards中的卡牌数据

        :param code: 卡牌代码
        :return: 找到返回卡牌对象，没找到返回None
        """
        if not self.db_cards or not isinstance(self.db_cards, list):
            return None

        # 使用next()和生成器表达式查找匹配的卡牌
        return next((card for card in self.db_cards if card.get('code') == code), None)

    @staticmethod
    def cutting_pictures(image: Image.Image, num_width: int, num_height: int, index: int):
        """从原图中切割出卡牌"""
        # 计算一张卡的大小
        card_width = image.width // num_width
        card_height = image.height // num_height

        # 切割指定位置的卡牌
        j = index % num_width
        i = index // num_width

        if i >= num_height or j >= num_width:
            print(f"警告: 卡牌索引超出范围")
            return None

        left = j * card_width
        top = i * card_height
        right = left + card_width
        bottom = top + card_height

        return image.crop((left, top, right, bottom))

    def arrange_metadata(self):
        """整理元数据"""
        download_cache_path = os.path.join(self.work_dir, 'download')
        if not os.path.exists(download_cache_path):
            raise FileNotFoundError(f"未找到下载目录: {download_cache_path}")
        factory_dir = os.path.join(self.work_dir, 'factory')
        if not os.path.exists(factory_dir):
            os.makedirs(factory_dir)

        # 图片缓存字典
        image_cache = {}

        def get_cached_image(image_path: str) -> Image.Image:
            """获取缓存的图片，如果不存在则加载并缓存（复制到内存）"""
            if image_path not in image_cache:
                try:
                    with Image.open(image_path) as img:
                        image_cache[image_path] = img.copy()  # 复制到内存并缓存
                except Exception as e:
                    raise
            return image_cache[image_path]

        # 定义元数据对象
        metadata = {}
        card_len = len(self.result_array)
        for i, card in enumerate(self.result_array):
            custom_card = self._get_custom_deck(card)
            try:
                GMNotes = card.get('GMNotes', '')
                GMNotes = json.loads(GMNotes)
            except:
                print(f"警告: 无法解析GMNotes: {card}")
                continue
            card_id = GMNotes['id']
            db_card = self.get_card_by_code(card_id)
            if not db_card:
                print(f"警告: 未找到卡牌: {card_id}")
                continue

            face_path = os.path.join(self.work_dir, 'download', self._get_alnum_str(custom_card['FaceURL']) + '.jpg')
            back_path = os.path.join(self.work_dir, 'download', self._get_alnum_str(custom_card['BackURL']) + '.jpg')
            with Image.open(face_path) as face_img:
                face_image = self.cutting_pictures(
                    image=face_img.copy(),
                    num_width=custom_card['NumWidth'],
                    num_height=custom_card['NumHeight'],
                    index=custom_card['index']
                )
            if custom_card['UniqueBack']:
                # 独特卡背
                back_image = self.cutting_pictures(
                    image=get_cached_image(back_path),
                    num_width=custom_card['NumWidth'],
                    num_height=custom_card['NumHeight'],
                    index=custom_card['index']
                )
            else:
                # 忽略通用卡背
                if 'httpssteamusercontentaakamaihdnetugc2342503777940352139A2D42E7E5C43D045D72CE5CFC907E4F886C8C690' in back_path:
                    back_image = '玩家卡背'
                elif 'httpssteamusercontentaakamaihdnetugc2342503777940351785F64D8EFB75A9E15446D24343DA0A6EEF5B3E43DB' in back_path:
                    back_image = '遭遇卡背'
                else:
                    back_image = get_cached_image(back_path)
            save_path_a = os.path.join(factory_dir, f"{card_id}-a.jpg")
            save_path_b = os.path.join(factory_dir, f"{card_id}-b.jpg")
            # 保存元数据
            metadata[card_id] = {
                'id': card_id,
                'GMNotes': GMNotes,
                'db_card': db_card,
                'custom_card': custom_card,
                'face_path': save_path_a
            }
            if isinstance(back_image, Image.Image):
                metadata[card_id]['back_path'] = save_path_b
            else:
                metadata[card_id]['back_path'] = back_image
            if os.path.exists(save_path_a) and os.path.exists(save_path_b):
                # 如果存在则跳过
                continue
            # 保存图片到factory目录
            face_image.save(save_path_a, quality=95)
            if isinstance(back_image, Image.Image):
                back_image.save(save_path_b, quality=95)
            # 打印进度条
            self._print_progress_bar(i, card_len, prefix='进度:', suffix='完成', length=50)
            pass
        # 保存元数据
        metadata_file = os.path.join(self.work_dir, 'metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

        # 更新实例的metadata
        self.metadata = metadata

    @staticmethod
    def extract_location_icons(json_data):
        """
        从JSON数据中提取所有地点图标的名字

        Args:
            json_data: JSON数据（字典格式或JSON字符串）

        Returns:
            set: 包含所有地点图标名字的集合
        """
        # 如果输入是字符串，先解析为字典
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        icons_set = set()

        # 遍历所有卡牌数据
        for card_id, card_data in data.items():
            # 检查是否有GMNotes字段
            if "GMNotes" in card_data:
                gm_notes = card_data["GMNotes"]

                # 检查是否是地点类型
                if gm_notes.get("type") == "Location":
                    # 提取locationFront中的图标
                    if "locationFront" in gm_notes and "icons" in gm_notes["locationFront"]:
                        front_icons = gm_notes["locationFront"]["icons"]
                        # 按"|"分割图标名称
                        for icon in front_icons.split("|"):
                            if icon.strip():  # 去除空白字符并检查是否为空
                                icons_set.add(icon.strip())

                    # 提取locationBack中的图标
                    if "locationBack" in gm_notes and "icons" in gm_notes["locationBack"]:
                        back_icons = gm_notes["locationBack"]["icons"]
                        # 按"|"分割图标名称
                        for icon in back_icons.split("|"):
                            if icon.strip():  # 去除空白字符并检查是否为空
                                icons_set.add(icon.strip())

        return icons_set

    def remake_card(self, card_id: str) -> dict:
        """
        重新制作指定卡牌的数据

        :param card_id: 卡牌ID
        :return: 包含转换后卡牌数据的字典
        """
        # 从实例变量中读取metadata
        if not self.metadata:
            raise FileNotFoundError(f"metadata 为空，请确保已正确初始化或运行 arrange_metadata() 方法")

        # 检查card_id是否存在
        if card_id not in self.metadata:
            raise ValueError(f"未找到卡牌ID: {card_id}")

        card_metadata = self.metadata[card_id]
        db_card = card_metadata.get('db_card')

        if not db_card:
            raise ValueError(f"卡牌 {card_id} 缺少数据库卡牌数据")

        # 创建ArkhamDBConverter实例
        converter = ArkhamDBConverter(db_card)

        # 初始化结果字典
        result = {
            'card_id': card_id,
            'metadata': card_metadata,
            'converted_data': {}
        }

        # 转换正面数据
        front_data = converter.convert_front()
        if front_data:
            result['converted_data']['front'] = front_data.copy()
            # 如果有正面图片路径，添加到数据中
            if 'face_path' in card_metadata and os.path.exists(card_metadata['face_path']):
                # 这里可以选择添加图片路径或转换为base64
                result['converted_data']['front']['picture_path'] = card_metadata['face_path']

            print(f"✓ 成功转换正面数据: {card_id} -> {result['converted_data']['front'].get('name')}")
        else:
            print(f"✗ 正面数据转换失败: {card_id}")

        # 转换背面数据（如果存在）
        back_path = card_metadata.get('back_path')

        # 检查是否有独特背面（不是预设的卡背字符串）
        has_unique_back = (back_path and
                           isinstance(back_path, str) and
                           back_path not in ['玩家卡背', '遭遇卡背'] and
                           os.path.exists(back_path))

        if has_unique_back or db_card.get('double_sided'):
            back_data = converter.convert_back()
            if back_data:
                result['converted_data']['back'] = back_data.copy()
                # 如果有背面图片路径，添加到数据中
                if has_unique_back:
                    result['converted_data']['back']['picture_path'] = back_path

                print(f"✓ 成功转换背面数据: {card_id} -> {result['converted_data']['back'].get('name')}")
            else:
                print(f"✗ 背面数据转换失败: {card_id}")
        else:
            print(f"- 无需转换背面数据: {card_id} (使用标准卡背: {back_path})")

        return result

    def batch_remake_cards(self, card_creator: CardCreator, output_dir: str = None, thread_count: int = 4) -> dict:
        """
        批量重置卡牌功能

        :param card_creator: CardCreator 实例
        :param output_dir: 输出目录，默认为工作目录下的 remade_cards 目录
        :param thread_count: 线程数量，默认为4
        :return: 包含成功和失败信息的字典
        """
        if not self.metadata:
            raise ValueError("metadata为空，请确保已正确初始化")

        # 设置输出目录
        if output_dir is None:
            output_dir = os.path.join(self.work_dir, 'remade_cards')

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建输出目录: {output_dir}")

        # 统计信息
        total_cards = len(self.metadata)
        success_count = 0
        error_count = 0
        success_cards = []
        error_cards = []

        print(f"开始批量重置 {total_cards} 张卡牌...")

        def process_single_card(card_id: str, index: int) -> tuple:
            """处理单张卡牌的函数"""
            try:
                # 重制卡牌数据
                remake_result = self.remake_card(card_id)
                converted_data = remake_result['converted_data']

                # 处理正面
                front_saved = False
                if 'front' in converted_data and converted_data['front'] is not None:
                    if converted_data['front'].get('is_encounter'):
                        creator.transparent_encounter = True
                    else:
                        creator.transparent_encounter = False
                    front_card = card_creator.create_card(converted_data['front'])
                    if front_card and front_card.image:
                        front_filename = f"{card_id}-a.jpg"
                        front_output_path = os.path.join(output_dir, front_filename)
                        # 转为RGB
                        front_card.image = front_card.image.convert('RGB')
                        front_card.image.save(front_output_path, quality=95)
                        front_saved = True

                # 处理背面
                back_saved = False
                if 'back' in converted_data and converted_data['back'] is not None:
                    if converted_data['back'].get('is_encounter'):
                        creator.transparent_encounter = True
                    else:
                        creator.transparent_encounter = False
                    back_card = card_creator.create_card(converted_data['back'])
                    if back_card and back_card.image:
                        back_filename = f"{card_id}-b.jpg"
                        back_output_path = os.path.join(output_dir, back_filename)
                        # 转为RGB
                        back_card.image = back_card.image.convert('RGB')
                        back_card.image.save(back_output_path, quality=95)
                        back_saved = True

                # 更新进度条
                self._print_progress_bar(
                    index + 1, total_cards,
                    prefix='进度:',
                    suffix=f'完成 {index + 1}/{total_cards} - {card_id}',
                    length=30
                )

                return ('success', card_id, front_saved, back_saved, None)

            except Exception as e:
                error_msg = f"处理卡牌 {card_id} 时出错: {str(e)}"
                print(f"\n{error_msg}")
                return ('error', card_id, False, False, str(e))

        # 使用线程池处理卡牌
        card_ids = list(self.metadata.keys())

        # 单线程处理（因为进度条显示问题）
        if thread_count == 1:
            for i, card_id in enumerate(card_ids):
                result = process_single_card(card_id, i)
                status, card_id, front_saved, back_saved, error = result

                if status == 'success':
                    success_count += 1
                    success_cards.append({
                        'card_id': card_id,
                        'front_saved': front_saved,
                        'back_saved': back_saved
                    })
                else:
                    error_count += 1
                    error_cards.append({
                        'card_id': card_id,
                        'error': error
                    })
        else:
            # 多线程处理
            print("使用多线程处理可能会影响进度条显示...")
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                # 提交所有任务
                future_to_card = {
                    executor.submit(process_single_card, card_id, i): (card_id, i)
                    for i, card_id in enumerate(card_ids)
                }

                # 收集结果
                for future in as_completed(future_to_card):
                    result = future.result()
                    status, card_id, front_saved, back_saved, error = result

                    if status == 'success':
                        success_count += 1
                        success_cards.append({
                            'card_id': card_id,
                            'front_saved': front_saved,
                            'back_saved': back_saved
                        })
                    else:
                        error_count += 1
                        error_cards.append({
                            'card_id': card_id,
                            'error': error
                        })

        # 打印统计结果
        print(f"\n批量重置完成!")
        print(f"总计: {total_cards} 张卡牌")
        print(f"成功: {success_count} 张")
        print(f"失败: {error_count} 张")
        print(f"输出目录: {output_dir}")

        # 保存处理日志
        log_data = {
            'timestamp': str(json.dumps(None, default=str)),  # 当前时间
            'total_cards': total_cards,
            'success_count': success_count,
            'error_count': error_count,
            'output_directory': output_dir,
            'success_cards': success_cards,
            'error_cards': error_cards
        }

        log_file = os.path.join(output_dir, 'batch_remake_log.json')
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=4)
        print(f"处理日志已保存到: {log_file}")

        return log_data

    def batch_remake_specific_cards(self, card_ids: list, card_creator: CardCreator, output_dir: str = None) -> dict:
        """
        重置指定的卡牌

        :param card_ids: 要重置的卡牌ID列表
        :param card_creator: CardCreator 实例
        :param output_dir: 输出目录，默认为工作目录下的 remade_cards 目录
        :return: 包含成功和失败信息的字典
        """
        if not self.metadata:
            raise ValueError("metadata为空，请确保已正确初始化")

        # 检查卡牌ID是否存在
        valid_card_ids = []
        invalid_card_ids = []
        for card_id in card_ids:
            if card_id in self.metadata:
                valid_card_ids.append(card_id)
            else:
                invalid_card_ids.append(card_id)

        if invalid_card_ids:
            print(f"警告: 以下卡牌ID不存在: {invalid_card_ids}")

        if not valid_card_ids:
            print("错误: 没有有效的卡牌ID")
            return {'error': 'No valid card IDs'}

        # 设置输出目录
        if output_dir is None:
            output_dir = os.path.join(self.work_dir, 'remade_cards')

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建输出目录: {output_dir}")

        # 统计信息
        total_cards = len(valid_card_ids)
        success_count = 0
        error_count = 0
        success_cards = []
        error_cards = []

        print(f"开始重置指定的 {total_cards} 张卡牌...")

        for i, card_id in enumerate(valid_card_ids):
            try:
                # 重制卡牌数据
                remake_result = self.remake_card(card_id)
                converted_data = remake_result['converted_data']

                # 处理正面
                front_saved = False
                if 'front' in converted_data and converted_data['front'] is not None:
                    front_card = card_creator.create_card(converted_data['front'])
                    if front_card and front_card.image:
                        front_filename = f"{card_id}-a.jpg"
                        front_output_path = os.path.join(output_dir, front_filename)
                        # 转为JPEG
                        front_card.image = front_card.image.convert('RGB')
                        front_card.image.save(front_output_path, quality=95)
                        front_saved = True

                # 处理背面
                back_saved = False
                if 'back' in converted_data and converted_data['back'] is not None:
                    back_card = card_creator.create_card(converted_data['back'])
                    if back_card and back_card.image:
                        back_filename = f"{card_id}-b.jpg"
                        back_output_path = os.path.join(output_dir, back_filename)
                        back_card.image = back_card.image.convert('RGB')
                        back_card.image.save(back_output_path, quality=95)
                        back_saved = True

                success_count += 1
                success_cards.append({
                    'card_id': card_id,
                    'front_saved': front_saved,
                    'back_saved': back_saved
                })

                # 更新进度条
                self._print_progress_bar(
                    i + 1, total_cards,
                    prefix='进度:',
                    suffix=f'完成 {i + 1}/{total_cards} - {card_id}',
                    length=30
                )

            except Exception as e:
                error_count += 1
                error_msg = f"处理卡牌 {card_id} 时出错: {str(e)}"
                print(f"\n{error_msg}")
                error_cards.append({
                    'card_id': card_id,
                    'error': str(e)
                })

        # 打印统计结果
        print(f"\n指定卡牌重置完成!")
        print(f"总计: {total_cards} 张卡牌")
        print(f"成功: {success_count} 张")
        print(f"失败: {error_count} 张")
        print(f"输出目录: {output_dir}")

        # 返回结果
        return {
            'total_cards': total_cards,
            'success_count': success_count,
            'error_count': error_count,
            'output_directory': output_dir,
            'success_cards': success_cards,
            'error_cards': error_cards,
            'invalid_card_ids': invalid_card_ids
        }


if __name__ == '__main__':
    # 创建任务实例
    task = RemakeCardsTranslationTask('官方卡重置/所有玩家卡')

    # 步骤一：下载卡牌图片
    # task.download_cards()
    # 步骤二：整理元数据
    # task.arrange_metadata()
    # 步骤三：检查地点图标是否有新增
    # task.read_metadata_and_extract_icons()

    # 创建字体和图片管理器
    fm = FontManager('../fonts')
    im = ImageManager('../images')
    creator = CardCreator(
        font_manager=fm,
        image_manager=im,
        image_mode=1,
        transparent_encounter=False,
        transparent_background=False
    )

    # 批量重置所有卡牌
    # result = task.batch_remake_cards(creator, thread_count=1)
    # print(f"批量重置结果: {result}")

    # 或者重置指定卡牌
    specific_cards = ['01014', '06030']  # 替换为您要重置的卡牌ID
    result = task.batch_remake_specific_cards(specific_cards, creator)
    print(f"指定卡牌重置结果: {result}")

# if __name__ == '__main__':
#     task = RemakeCardsTranslationTask('官方卡重置/所有玩家卡')
#     # 步骤一：下载卡牌图片
#     # task.download_cards()
#     # 步骤二：整理元数据
#     # task.arrange_metadata()
#     # 步骤三：检查地点图标是否有新增
#     # task.read_metadata_and_extract_icons()
#
#     test_data = task.remake_card('08728')
#     print(json.dumps(test_data['converted_data'], ensure_ascii=False, indent=4))
#
#     # 创建卡牌创建器
#     # 创建字体和图片管理器
#     fm = FontManager('../fonts')
#     im = ImageManager('../images')
#     creator = CardCreator(
#         font_manager=fm,
#         image_manager=im,
#         image_mode=1,
#         transparent_encounter=True,
#         transparent_background=False
#     )
#     # encounter_icon = test_data.get('encounter_icon', {})
#     if test_data['converted_data']['front'].get('is_encounter'):
#         creator.transparent_encounter = True
#     else:
#         creator.transparent_encounter = False
#     card = creator.create_card(test_data['converted_data']['front'])
#     # if 'front' in encounter_icon:
#     #     card.set_encounter_icon(encounter_icon['front'])
#     card.image.show()
#     # back_card = creator.create_card(test_data['converted_data']['back'])
#     # if 'back' in encounter_icon:
#     #     card.set_encounter_icon(encounter_icon['back'])
#     # back_card.image.show()
