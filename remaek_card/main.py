import json
import os
import re
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
from arkhamdb2card import ArkhamDBConverter


class CardMetadataScanner:
    """
    卡牌元数据扫描器
    用于扫描工作目录下的图片文件，并根据db_cards.json生成元数据
    """

    def __init__(self, work_directory: str, code: str):
        """
        初始化扫描器

        Args:
            work_directory: 工作目录路径
            code: 项目代码，用于匹配db_cards中的card code前N位
        """
        self.work_directory = Path(work_directory)
        self.code = code
        self.db_cards = []

        # 检查工作目录是否存在
        if not self.work_directory.exists():
            raise FileNotFoundError(f"工作目录不存在: {work_directory}")

        # 读取db_cards.json文件
        self._load_db_cards()

    def _load_db_cards(self):
        """加载db_cards.json文件并应用翻译数据"""
        db_cards_path = "db_cards_en.json"
        translation_path = "translation_data.json"

        try:
            # 1. 加载英文数据库
            with open(db_cards_path, 'r', encoding='utf-8') as f:
                self.db_cards = json.load(f)
            print(f"成功加载 {len(self.db_cards)} 张英文卡牌数据")

            # 2. 加载并应用翻译数据
            if os.path.exists(translation_path):
                with open(translation_path, 'r', encoding='utf-8') as f:
                    translations = json.load(f)

                # 创建code到翻译数据的映射
                translation_map = {trans.get('code'): trans for trans in translations if 'code' in trans}
                print(f"成功加载 {len(translation_map)} 张翻译数据")

                # 应用翻译
                translated_count = 0
                total_fields_replaced = 0

                for card in self.db_cards:
                    card_code = card.get('code', '')
                    if card_code in translation_map:
                        translation = translation_map[card_code]
                        fields_replaced = 0

                        # 遍历翻译数据中的所有字段（除了code）
                        for field_name, trans_value in translation.items():
                            if field_name != 'code' and trans_value is not None and trans_value != '':
                                # 只替换非空的翻译值
                                card[field_name] = trans_value
                                fields_replaced += 1

                        if fields_replaced > 0:
                            translated_count += 1
                            total_fields_replaced += fields_replaced

                    # 处理linked_card字段的翻译
                    linked_card = card.get('linked_card')
                    if linked_card and isinstance(linked_card, dict):
                        linked_card_code = linked_card.get('code', '')
                        if linked_card_code in translation_map:
                            linked_translation = translation_map[linked_card_code]
                            linked_fields_replaced = 0

                            # 遍历翻译数据中的所有字段（除了code）
                            for field_name, trans_value in linked_translation.items():
                                if field_name != 'code' and trans_value is not None and trans_value != '':
                                    # 只替换非空的翻译值
                                    linked_card[field_name] = trans_value
                                    linked_fields_replaced += 1

                            if linked_fields_replaced > 0:
                                translated_count += 1
                                total_fields_replaced += linked_fields_replaced
                                print(
                                    f"应用linked_card翻译: {linked_card_code} ({linked_card.get('name', 'Unknown')}) - 替换 {linked_fields_replaced} 个字段")

                # 处理duplicated_by字段的翻译
                duplicated_translation_count = 0
                for card in self.db_cards:
                    duplicated_by = card.get('duplicated_by')
                    if duplicated_by and isinstance(duplicated_by, list):
                        card_code = card.get('code', '')
                        if card_code in translation_map:
                            # 如果当前卡牌有翻译，则为其所有复制品应用相同的翻译
                            translation = translation_map[card_code]

                            for duplicated_code in duplicated_by:
                                # 查找被复制的卡牌
                                duplicated_card = None
                                for target_card in self.db_cards:
                                    if target_card.get('code') == duplicated_code:
                                        duplicated_card = target_card
                                        break

                                if duplicated_card:
                                    duplicated_fields_replaced = 0
                                    # 应用翻译到被复制的卡牌
                                    for field_name, trans_value in translation.items():
                                        if field_name != 'code' and trans_value is not None and trans_value != '':
                                            duplicated_card[field_name] = trans_value
                                            duplicated_fields_replaced += 1

                                    if duplicated_fields_replaced > 0:
                                        duplicated_translation_count += 1
                                        total_fields_replaced += duplicated_fields_replaced
                                        print(
                                            f"应用duplicated_by翻译: {duplicated_code} ({duplicated_card.get('name', 'Unknown')}) - 替换 {duplicated_fields_replaced} 个字段")

                print(f"成功应用翻译: {translated_count}/{len(self.db_cards)} 张卡牌")
                print(f"duplicated_by翻译: {duplicated_translation_count} 张卡牌")
                print(f"总计替换字段: {total_fields_replaced} 个")

                # 显示未找到翻译的卡牌数量
                untranslated_count = len(self.db_cards) - translated_count
                if untranslated_count > 0:
                    print(f"未找到翻译: {untranslated_count} 张卡牌")
            else:
                print(f"警告: 翻译文件不存在 {translation_path}，将使用原始英文数据")

        except json.JSONDecodeError as e:
            raise ValueError(f"JSON文件格式错误: {e}")
        except Exception as e:
            raise Exception(f"加载数据失败: {e}")

        # 计算遭遇组统计信息并设置到ArkhamDBConverter中
        print("正在计算遭遇组统计信息...")
        try:
            encounter_group_index = ArkhamDBConverter.calculate_encounter_group_statistics(self.db_cards)
            ArkhamDBConverter.set_encounter_group_index(encounter_group_index)
            print(f"成功计算遭遇组信息: {len(encounter_group_index)} 张卡牌")
            
            # 显示一些统计信息
            encounter_groups = {}
            for card_code, group_info in encounter_group_index.items():
                group_name = group_info.split('/')[-1]  # 获取总数部分
                if group_name not in encounter_groups:
                    encounter_groups[group_name] = 0
                encounter_groups[group_name] += 1
            
            print(f"遭遇组统计: {len(encounter_groups)} 个不同的遭遇组")
            for group_size, count in sorted(encounter_groups.items()):
                print(f"  总数 {group_size}: {count} 张卡牌")
                
        except Exception as e:
            print(f"警告: 计算遭遇组信息失败: {e}")
            print("将继续处理，但卡牌可能缺少遭遇组编号信息")

        # 设置完整数据库引用，用于linked_to_code查找
        print("正在设置完整数据库引用...")
        ArkhamDBConverter.set_full_database(self.db_cards)
        print(f"成功设置完整数据库引用: {len(self.db_cards)} 张卡牌")

        # 加载地点图标映射数据
        print("正在加载地点图标映射数据...")
        try:
            ArkhamDBConverter.load_location_icons_mapping("location_icons_mapping.json")
            ArkhamDBConverter.load_gmnotes_index("gmnotes_index.json")
        except Exception as e:
            print(f"警告: 加载地点图标映射数据失败: {e}")
            print("将继续处理，但地点卡可能缺少图标信息")

    def _extract_position_from_filename(self, filename: str) -> tuple[Optional[int], bool]:
        """
        从文件名中提取位置数字和是否为背面

        Args:
            filename: 文件名(不含扩展名)

        Returns:
            tuple: (position数字, 是否为背面)
        """
        # 检查是否为背面(文件名包含'b')
        is_back = filename.lower().endswith('b')

        # 移除可能的'b'后缀
        clean_filename = filename.lower().rstrip('b')

        # 提取数字部分
        numbers = re.findall(r'\d+', clean_filename)
        if numbers:
            try:
                position = int(numbers[-1])  # 取最后一个数字
                return position, is_back
            except ValueError:
                pass

        return None, is_back

    def _find_card_by_position(self, position: int) -> Optional[Dict[str, Any]]:
        """
        根据code前N位和position查找卡牌

        Args:
            position: 位置编号

        Returns:
            找到的卡牌数据，未找到则返回None
        """
        # 计算要比较的前N位长度
        code_length = len(self.code)

        for card in self.db_cards:
            card_code = card.get('code', '')

            # 检查卡牌code的前N位是否匹配
            if (len(card_code) >= code_length and
                    card_code[:code_length] == self.code and
                    card.get('position') == position):
                return card

        return None

    def _find_card_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        根据code查找卡牌

        Args:
            code: 具体编号

        Returns:
            找到的卡牌数据，未找到则返回None
        """
        for card in self.db_cards:
            card_code = card.get('code', '')

            # 检查卡牌code的前N位是否匹配
            if card_code == code:
                return card

        return None

    def _process_image_to_base64(self, image_path: Path, type_code: str, is_back: bool = False) -> str:
        """
        处理图片并转换为base64字符串

        Args:
            image_path: 图片文件路径
            type_code: 卡牌类型代码
            is_back: 是否为背面

        Returns:
            处理后的图片base64字符串
        """
        try:
            # 打开图片
            with Image.open(image_path) as img:
                # 获取原图尺寸
                original_width, original_height = img.size

                # 目标尺寸
                target_width, target_height = 739, 1049

                # 计算裁剪的左上角坐标（居中裁剪）
                left = int((original_width - target_width) / 2)
                top = int((original_height - target_height) / 2)

                # 确保坐标不为负数
                left = max(0, left)
                top = max(0, top)

                # 计算右下角坐标
                right = min(original_width, left + target_width)
                bottom = min(original_height, top + target_height)

                # 裁剪图片
                cropped_img = img.crop((left, top, right, bottom))

                # 如果裁剪后的尺寸不足目标尺寸，则进行缩放
                if cropped_img.size != (target_width, target_height):
                    cropped_img = cropped_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

                # 如果是调查员卡牌，根据正面/背面进行不同的旋转
                if type_code in ["investigator", 'act', 'agenda']:
                    if is_back:
                        # 背面：逆时针90度旋转
                        cropped_img = cropped_img.rotate(90, expand=True)
                    else:
                        # 正面：顺时针90度旋转
                        cropped_img = cropped_img.rotate(-90, expand=True)

                # 转换为RGB模式（确保没有透明通道）
                if cropped_img.mode != 'RGB':
                    cropped_img = cropped_img.convert('RGB')

                # 转换为base64
                from io import BytesIO
                buffer = BytesIO()
                cropped_img.save(buffer, format='JPEG', quality=95)
                img_bytes = buffer.getvalue()
                base64_string = base64.b64encode(img_bytes).decode('utf-8')

                return base64_string

        except Exception as e:
            raise Exception(f"处理图片失败 {image_path}: {e}")

    def scan_metadata(self) -> List[Dict[str, Any]]:
        """
        扫描元数据

        Returns:
            扫描到的元数据列表
        """
        images_dir = self.work_directory / "图片"

        if not images_dir.exists():
            raise FileNotFoundError(f"图片目录不存在: {images_dir}")

        metadata_list = []

        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

        # 扫描图片目录下的所有文件
        for file_path in images_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                # 获取相对于工作目录的路径
                relative_path = file_path.relative_to(self.work_directory)

                # 获取文件名(不含扩展名)
                filename = file_path.stem

                # 提取位置和背面信息
                position, is_back = self._extract_position_from_filename(filename)

                if position is not None:
                    # 查找对应的卡牌数据
                    card_data = self._find_card_by_position(position)

                    if not card_data and self.code == '01':
                        card_data = self._find_card_by_code(self.code + filename.zfill(3))
                        pass

                    if card_data:
                        # 构建元数据
                        metadata = {
                            'file_path': str(relative_path).replace('\\', '/'),  # 统一使用正斜杠
                            'filename': filename,
                            'position': position,
                            'is_back': is_back,
                            'pack_code': card_data.get('pack_code'),
                            'card_code': card_data.get('code'),
                            'card_name': card_data.get('name'),
                            'card_real_name': card_data.get('real_name'),
                            'type_code': card_data.get('type_code'),
                            'type_name': card_data.get('type_name'),
                            'faction_code': card_data.get('faction_code'),
                            'faction_name': card_data.get('faction_name'),
                            'card_data': card_data  # 完整的卡牌数据
                        }
                        metadata_list.append(metadata)
                        print(
                            f"找到匹配: {filename} -> {card_data.get('name')} (位置: {position}{'背面' if is_back else '正面'}) [code: {card_data.get('code')}]")
                    else:
                        print(f"警告: 未找到位置 {position} 对应的卡牌数据 - 文件: {filename}")
                else:
                    print(f"警告: 无法从文件名提取位置信息 - 文件: {filename}")

        print(f"扫描完成，共找到 {len(metadata_list)} 个匹配的文件")
        return metadata_list

    def save_metadata(self, metadata_list: List[Dict[str, Any]], output_filename: str = 'metadata.json'):
        """
        保存元数据到JSON文件

        Args:
            metadata_list: 元数据列表
            output_filename: 输出文件名
        """
        output_path = self.work_directory / output_filename

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_list, f, ensure_ascii=False, indent=2)
            print(f"元数据已保存到: {output_path}")
        except Exception as e:
            raise Exception(f"保存元数据文件失败: {e}")

    def convert_and_save_cards(self, metadata_filename: str = 'card_metadata.json'):
        """
        读取元数据并将卡牌转化为card对象，保存到"卡牌"目录

        Args:
            metadata_filename: 元数据文件名，默认为'card_metadata.json'
        """
        print("开始转换卡牌数据...")

        # 读取元数据文件
        metadata_path = self.work_directory / metadata_filename
        if not metadata_path.exists():
            raise FileNotFoundError(f"元数据文件不存在: {metadata_path}")

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata_list = json.load(f)
        except Exception as e:
            raise Exception(f"读取元数据文件失败: {e}")

        # 创建"卡牌"目录
        cards_dir = self.work_directory / "卡牌"
        cards_dir.mkdir(exist_ok=True)

        converted_count = 0
        skipped_count = 0

        for metadata in metadata_list:
            try:
                # 获取文件路径信息
                file_path = metadata.get('file_path', '')
                filename = metadata.get('card_code', '')
                is_back = metadata.get('is_back', False)
                card_data = metadata.get('card_data', {})
                type_code = metadata.get('type_code', '')
                if is_back and not card_data.get('double_sided') and 'linked_card' in card_data:
                    type_code = card_data['linked_card'].get('type_code', '')
                    pass
                if is_back:
                    filename += '_b'
                else:
                    filename += '_a'

                if not card_data:
                    print(f"警告: 元数据中缺少卡牌数据 - 文件: {filename}")
                    skipped_count += 1
                    continue

                # 创建ArkhamDBConverter实例
                converter = ArkhamDBConverter(card_data)

                # 根据是否为背面调用不同的转换方法
                if is_back:
                    card_object = converter.convert_back()
                else:
                    card_object = converter.convert_front()

                # 检测是否有定制卡
                customization_text = card_data.get('customization_text', '')
                customization_card = None
                if customization_text and customization_text != '':
                    print(f"正在处理定制卡: {filename}")
                    # 转化定制卡
                    customization_card = converter.convert_customization()

                # 如果转换结果为None，跳过该卡牌
                if card_object is None:
                    print(f"跳过: {filename} - 转换结果为None")
                    skipped_count += 1
                    continue

                # 处理图片并转换为base64
                image_full_path = self.work_directory / file_path
                if not image_full_path.exists():
                    print(f"警告: 图片文件不存在 - {image_full_path}")
                    skipped_count += 1
                    continue

                try:
                    # 处理图片并转换为base64，传递is_back参数
                    picture_base64 = self._process_image_to_base64(image_full_path, type_code, is_back)

                    # 添加新字段到card对象
                    card_object['picture_base64'] = 'data:image/png;base64,' + picture_base64
                    card_object['image_mode'] = 1

                    rotation_info = ""
                    if type_code in ["investigator", 'act', 'agenda']:
                        rotation_info = f" - {'逆时针90°' if is_back else '顺时针90°'}旋转"

                    print(
                        f"图片处理完成: {filename} ({'调查员' if type_code == 'investigator' else '普通卡牌'}){rotation_info}")

                except Exception as e:
                    print(f"图片处理失败: {filename} - 错误: {e}")
                    skipped_count += 1
                    continue

                # 生成输出文件名 (例如: 图片/1a.png -> 卡牌/1a.card)
                card_filename = filename + '.card'

                # 保存card对象到文件
                output_path = cards_dir / card_filename

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(card_object, f, ensure_ascii=False, indent=2)

                if customization_card:
                    # 保存定制卡
                    customization_filename = filename + '-c.card'
                    with open(cards_dir / customization_filename, 'w', encoding='utf-8') as f:
                        json.dump(customization_card, f, ensure_ascii=False, indent=2)
                    print(f"定制卡保存成功: {filename} -> {customization_filename}")

                converted_count += 1
                print(f"转换成功: {filename} -> {card_filename} ({'背面' if is_back else '正面'})")

            except Exception as e:
                print(f"转换失败: {filename} - 错误: {e}")
                skipped_count += 1
                continue

        print(f"\n转换完成!")
        print(f"成功转换: {converted_count} 个文件")
        print(f"跳过: {skipped_count} 个文件")
        print(f"卡牌文件保存在: {cards_dir}")

    def run_scan_and_save(self, output_filename: str = 'metadata.json') -> List[Dict[str, Any]]:
        """
        执行扫描并保存元数据

        Args:
            output_filename: 输出文件名

        Returns:
            扫描到的元数据列表
        """
        print(f"开始扫描工作目录: {self.work_directory}")
        print(f"项目代码: {self.code} (匹配卡牌code的前{len(self.code)}位)")

        metadata_list = self.scan_metadata()

        if metadata_list:
            self.save_metadata(metadata_list, output_filename)
        else:
            print("没有找到任何匹配的文件")

        return metadata_list

    @staticmethod
    def batch_process_all_folders(base_directory: str, folder_type: str = "重置玩家卡"):
        """
        批量处理01-54所有文件夹
        
        Args:
            base_directory: 基础目录路径 (例如: "D:\诡镇奇谈")
            folder_type: 文件夹类型 ("重置玩家卡" 或 "重置剧本卡")
        """
        # 定义文件夹映射关系
        folder_mapping = {
            "01": "01_基础游戏",
            "02": "02_敦威治遗产",
            "03": "03_卡尔克萨之路",
            "04": "04_失落的时代",
            "05": "05_万象无终",
            "06": "06_食梦者",
            "07": "07_印斯茅斯的阴谋",
            "08": "08_暗与地球之界",
            "09": "09_绯红密钥",
            "10": "10_铁杉谷盛宴",
            "11": "11_沉没之城",
            "50": "50_重返基础",
            "51": "51_重返敦威治遗产",
            "52": "52_重返卡尔克萨之路",
            "53": "53_重返失落的时代",
            "54": "54_重返万象无终"
        }

        # 按数字顺序排序
        sorted_codes = sorted(folder_mapping.keys(), key=lambda x: int(x))

        print("=" * 80)
        print(f"开始批量处理所有文件夹")
        print(f"基础目录: {base_directory}")
        print(f"文件夹类型: {folder_type}")
        print(f"总共需要处理: {len(sorted_codes)} 个文件夹")
        print("=" * 80)

        success_count = 0
        error_count = 0
        total_cards_processed = 0

        # 处理结果统计
        processing_results = []

        for i, code in enumerate(sorted_codes, 1):
            folder_name = folder_mapping[code]
            work_directory = os.path.join(base_directory, folder_type, folder_name)

            print(f"\n[{i}/{len(sorted_codes)}] 正在处理: {folder_name} (代码: {code})")
            print(f"路径: {work_directory}")
            print("-" * 60)

            try:
                # 检查目录是否存在
                if not os.path.exists(work_directory):
                    print(f"警告: 目录不存在，跳过 - {work_directory}")
                    error_count += 1
                    processing_results.append({
                        'code': code,
                        'folder_name': folder_name,
                        'status': 'skipped',
                        'reason': '目录不存在',
                        'cards_count': 0
                    })
                    continue

                # 创建扫描器实例
                scanner = CardMetadataScanner(
                    work_directory=work_directory,
                    code=code
                )

                # 执行扫描并保存元数据
                metadata = scanner.run_scan_and_save("card_metadata.json")

                cards_count = len(metadata) if metadata else 0

                if cards_count > 0:
                    # 输出统计信息
                    back_count = sum(1 for item in metadata if item['is_back'])
                    front_count = cards_count - back_count
                    print(f"统计信息: 正面 {front_count} 张, 背面 {back_count} 张, 总计 {cards_count} 张")

                    # 转换卡牌数据并保存到"卡牌"目录
                    scanner.convert_and_save_cards("card_metadata.json")

                    print(f"✅ {folder_name} 处理完成 - 共 {cards_count} 张卡牌")
                    success_count += 1
                    total_cards_processed += cards_count
                    processing_results.append({
                        'code': code,
                        'folder_name': folder_name,
                        'status': 'success',
                        'cards_count': cards_count,
                        'front_count': front_count,
                        'back_count': back_count
                    })
                else:
                    print(f"⚠️ {folder_name} 没有找到匹配的卡牌文件")
                    processing_results.append({
                        'code': code,
                        'folder_name': folder_name,
                        'status': 'no_cards',
                        'cards_count': 0
                    })

            except Exception as e:
                print(f"❌ {folder_name} 处理失败: {e}")
                error_count += 1
                processing_results.append({
                    'code': code,
                    'folder_name': folder_name,
                    'status': 'error',
                    'reason': str(e),
                    'cards_count': 0
                })
                continue

        # 输出最终统计结果
        print("\n" + "=" * 80)
        print("批量处理完成!")
        print("=" * 80)
        print(f"成功处理: {success_count} 个文件夹")
        print(f"处理失败: {error_count} 个文件夹")
        print(f"总计处理卡牌: {total_cards_processed} 张")

        # 保存处理结果到文件
        results_file = os.path.join(base_directory, f"batch_processing_results_{folder_type}.json")
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'summary': {
                        'total_folders': len(sorted_codes),
                        'success_count': success_count,
                        'error_count': error_count,
                        'total_cards_processed': total_cards_processed,
                        'base_directory': base_directory,
                        'folder_type': folder_type,
                        'processing_time': None  # 可以添加时间戳
                    },
                    'details': processing_results
                }, f, ensure_ascii=False, indent=2)
            print(f"处理结果已保存到: {results_file}")
        except Exception as e:
            print(f"保存处理结果失败: {e}")

        # 显示详细结果
        print("\n详细处理结果:")
        for result in processing_results:
            status_icon = {
                'success': '✅',
                'error': '❌',
                'skipped': '⏭️',
                'no_cards': '⚠️'
            }.get(result['status'], '❓')

            print(f"{status_icon} {result['folder_name']} ({result['code']}) - {result['status']}")
            if result['status'] == 'success':
                print(
                    f"    卡牌数量: {result['cards_count']} (正面: {result['front_count']}, 背面: {result['back_count']})")
            elif result['status'] in ['error', 'skipped']:
                print(f"    原因: {result.get('reason', '未知')}")

        return processing_results


# 使用示例
if __name__ == "__main__":
    import sys

    try:
        # 检查命令行参数
        if len(sys.argv) > 1 and sys.argv[1].lower() == "batch":
            # 批量处理模式
            print("=" * 60)
            print("批量处理模式")
            print("=" * 60)

            # 获取基础目录和文件夹类型
            base_directory = r"D:\诡镇奇谈"  # 默认基础目录
            folder_type = "重置玩家卡"  # 默认处理玩家卡

            if len(sys.argv) > 2:
                folder_type = sys.argv[2]

            if len(sys.argv) > 3:
                base_directory = sys.argv[3]

            print(f"基础目录: {base_directory}")
            print(f"文件夹类型: {folder_type}")
            print("开始批量处理...")

            # 执行批量处理
            results = CardMetadataScanner.batch_process_all_folders(base_directory, folder_type)

        else:
            # 单个文件夹处理模式（原有逻辑）
            print("=" * 60)
            print("单个文件夹处理模式")
            print("=" * 60)

            # 文件夹映射关系说明
            print("支持的文件夹代码:")
            print("01_基础游戏 -> 01")
            print("02_敦威治遗产 -> 02")
            print("03_卡尔克萨之路 -> 03")
            print("04_失落的时代 -> 04")
            print("05_万象无终 -> 05")
            print("06_食梦者 -> 06")
            print("07_印斯茅斯的阴谋 -> 07")
            print("08_暗与地球之界 -> 08")
            print("09_绯红密钥 -> 09")
            print("10_铁杉谷盛宴 -> 10")
            print("11_沉没之城 -> 11")
            print("50_重返基础 -> 50")
            print("51_重返敦威治遗产 -> 51")
            print("52_重返卡尔克萨之路 -> 52")
            print("53_重返失落的时代 -> 53")
            print("54_重返万象无终 -> 54")
            print()

            # 创建扫描器实例
            # scanner = CardMetadataScanner(
            #     work_directory=r"D:\诡镇奇谈\重置玩家卡\01_基础游戏",  # 替换为实际的工作目录路径
            #     code="01"  # 使用code前缀，匹配前2位
            # )

            # 如果需要处理剧本卡，取消下面的注释并注释上面的代码
            scanner = CardMetadataScanner(
                work_directory=r"D:\诡镇奇谈\重置剧本卡\03_卡尔克萨之路",  # 替换为实际的工作目录路径
                code="03"  # 使用code前缀，匹配前2位
            )

            # 执行扫描并保存元数据
            metadata = scanner.run_scan_and_save("card_metadata.json")

            # 输出一些统计信息
            if metadata:
                back_count = sum(1 for item in metadata if item['is_back'])
                front_count = len(metadata) - back_count
                print(f"\n统计信息:")
                print(f"正面图片: {front_count} 张")
                print(f"背面图片: {back_count} 张")
                print(f"总计: {len(metadata)} 张")

            # 转换卡牌数据并保存到"卡牌"目录
            scanner.convert_and_save_cards("card_metadata.json")

            print("\n" + "=" * 60)
            print("使用说明:")
            print("单个文件夹处理: python main.py")
            print("批量处理所有文件夹: python main.py batch [文件夹类型] [基础目录]")
            print("示例:")
            print("  python main.py batch 重置玩家卡")
            print("  python main.py batch 重置剧本卡 \"D:\\诡镇奇谈\"")
            print("=" * 60)

    except Exception as e:
        print(f"错误: {e}")
        import traceback

        traceback.print_exc()
