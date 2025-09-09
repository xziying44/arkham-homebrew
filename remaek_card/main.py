import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
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
            code: 项目代码，用于匹配db_cards中的pack_code字段
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
        """加载db_cards.json文件"""
        db_cards_path = "db_cards.json"

        try:
            with open(db_cards_path, 'r', encoding='utf-8') as f:
                self.db_cards = json.load(f)
            print(f"成功加载 {len(self.db_cards)} 张卡牌数据")
        except json.JSONDecodeError as e:
            raise ValueError(f"db_cards.json文件格式错误: {e}")
        except Exception as e:
            raise Exception(f"读取db_cards.json文件失败: {e}")

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
        根据pack_code和position查找卡牌

        Args:
            position: 位置编号

        Returns:
            找到的卡牌数据，未找到则返回None
        """
        for card in self.db_cards:
            if (card.get('pack_code') == self.code and
                    card.get('position') == position):
                return card
        return None

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
                            f"找到匹配: {filename} -> {card_data.get('name')} (位置: {position}{'背面' if is_back else '正面'})")
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
                filename = metadata.get('filename', '')
                is_back = metadata.get('is_back', False)
                card_data = metadata.get('card_data', {})

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

                # 如果转换结果为None，跳过该卡牌
                if card_object is None:
                    print(f"跳过: {filename} - 转换结果为None")
                    skipped_count += 1
                    continue

                # 生成输出文件名 (例如: 图片/1a.png -> 卡牌/1a.card)
                # 从file_path中提取文件名部分
                path_parts = file_path.split('/')
                if len(path_parts) >= 2:
                    image_filename = path_parts[-1]  # 获取文件名部分
                    # 移除扩展名并添加.card扩展名
                    card_filename = Path(image_filename).stem + '.card'
                else:
                    # 如果路径格式不符合预期，使用原始filename
                    card_filename = filename + '.card'

                # 保存card对象到文件
                output_path = cards_dir / card_filename

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(card_object, f, ensure_ascii=False, indent=2)

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
        print(f"项目代码: {self.code}")

        metadata_list = self.scan_metadata()

        if metadata_list:
            self.save_metadata(metadata_list, output_filename)
        else:
            print("没有找到任何匹配的文件")

        return metadata_list


# 使用示例
if __name__ == "__main__":
    # 创建扫描器实例
    try:
        scanner = CardMetadataScanner(
            work_directory=r"D:\诡镇奇谈\重置玩家卡\基础游戏",  # 替换为实际的工作目录路径
            code="core"  # 替换为实际的项目代码
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

    except Exception as e:
        print(f"错误: {e}")
