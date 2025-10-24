import json
import re
import os
import base64
import logging
import requests
import io
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path

from bin.arkhamdb2card import ArkhamDBConverter


class ArkhamCardBuilder:
    """
    从ArkhamDB JSON内容包构建卡牌对象并保存到工作目录的类
    使用ArkhamDBConverter进行卡牌转换
    """

    def __init__(self, content_pack_json: Dict[str, Any], work_dir: str):
        """
        初始化卡牌构建器

        Args:
            content_pack_json: ArkhamDB内容包的JSON数据
            work_dir: 工作目录路径，用于保存生成的卡牌文件
        """
        self.content_pack = content_pack_json
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)

        # 从meta获取语言设置
        self.language = self._get_content_pack_language()

        # 日志系统
        self.log_messages = []
        self._setup_logging()

        # 卡牌索引
        self.cards_by_code = {}
        self.double_sided_pairs = set()
        self.linked_card_relations = {}

        # 设置完整数据库引用
        self._setup_full_database()

    def _get_content_pack_language(self) -> str:
        """
        从内容包meta中获取语言设置

        Returns:
            语言代码字符串
        """
        meta = self.content_pack.get('meta', {})
        language = meta.get('language', 'en')  # 默认为英文
        return language

    def _setup_logging(self):
        """设置日志系统"""
        self.logger = logging.getLogger('ArkhamCardBuilder')
        self.logger.setLevel(logging.INFO)

        # 创建字符串处理器用于收集日志
        self.log_capture_string = io.StringIO()
        ch = logging.StreamHandler(self.log_capture_string)
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def get_logs(self) -> str:
        """获取日志信息字符串"""
        return self.log_capture_string.getvalue()

    def _setup_full_database(self):
        """设置完整数据库引用，用于查找linked_to_code"""
        if 'cards' in self.content_pack.get('data', {}):
            ArkhamDBConverter.set_full_database(self.content_pack['data']['cards'])

    def validate_content_pack_structure(self) -> Tuple[bool, List[str]]:
        """
        验证内容包结构是否符合要求

        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []

        # 检查meta字段
        if 'meta' not in self.content_pack:
            errors.append("缺少meta字段")
        else:
            meta = self.content_pack['meta']
            if not isinstance(meta, dict):
                errors.append("meta字段必须是对象类型")

        # 检查data字段
        if 'data' not in self.content_pack:
            errors.append("缺少data字段")
        else:
            data = self.content_pack['data']
            if not isinstance(data, dict):
                errors.append("data字段必须是对象类型")
            else:
                # 检查cards字段
                if 'cards' not in data:
                    errors.append("data字段中缺少cards")
                else:
                    cards = data['cards']
                    if not isinstance(cards, list):
                        errors.append("data.cards字段必须是数组类型")
                    elif len(cards) == 0:
                        errors.append("data.cards数组不能为空")

                # 检查packs字段
                if 'packs' not in data:
                    errors.append("data字段中缺少packs")
                else:
                    packs = data['packs']
                    if not isinstance(packs, list):
                        errors.append("data.packs字段必须是数组类型")

        is_valid = len(errors) == 0
        if is_valid:
            self.logger.info("内容包结构验证通过")
        else:
            self.logger.error(f"内容包结构验证失败: {', '.join(errors)}")

        return is_valid, errors

    def _sanitize_filename(self, name: str, position: int) -> str:
        """
        清理文件名，移除标点符号

        Args:
            name: 卡牌名称
            position: 卡牌位置

        Returns:
            清理后的文件名
        """
        # 移除所有非字母数字字符（保留空格）
        cleaned_name = re.sub(r'[^\w\s]', '', name)
        # 移除多余空格并用点连接
        cleaned_name = re.sub(r'\s+', '', cleaned_name)
        return f"{position:03d}.{cleaned_name}.card"

    def _download_image_to_base64(self, url: str, max_retries: int = 2) -> Optional[str]:
        """
        下载图片并转换为base64编码，包含data URL格式的元数据
        根据实际的content-type判断图片格式，非图片格式默认为PNG

        Args:
            url: 图片URL
            max_retries: 最大重试次数

        Returns:
            完整的data URL格式的base64字符串，失败返回None
        """
        for attempt in range(max_retries + 1):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # 获取响应的content-type
                content_type = response.headers.get('content-type', '').lower()

                # 判断是否为图片格式
                if self._is_image_content_type(content_type):
                    # 使用实际的图片格式
                    mime_type = content_type.split(';')[0].strip()  # 移除可能的参数部分
                    self.logger.debug(f"检测到图片格式: {mime_type} for URL: {url}")
                else:
                    # 非图片格式，默认使用PNG
                    mime_type = 'image/png'
                    self.logger.warning(f"非图片格式或未知格式 ({content_type})，默认使用 PNG: {url}")

                # 转换为base64
                image_data = base64.b64encode(response.content).decode('utf-8')

                # 构建完整的data URL
                data_url = f"data:{mime_type};base64,{image_data}"

                self.logger.info(f"成功下载图片 ({mime_type}): {url}")
                return data_url

            except requests.RequestException as e:
                self.logger.warning(f"网络请求失败 (尝试 {attempt + 1}/{max_retries + 1}): {url} - {str(e)}")
                if attempt == max_retries:
                    return None
            except Exception as e:
                self.logger.warning(f"图片处理失败 (尝试 {attempt + 1}/{max_retries + 1}): {url} - {str(e)}")
                if attempt == max_retries:
                    return None

    def _is_image_content_type(self, content_type: str) -> bool:
        """
        判断content-type是否为图片格式

        Args:
            content_type: HTTP响应的content-type头

        Returns:
            是否为图片格式
        """
        if not content_type:
            return False

        # 常见的图片MIME类型
        image_mime_types = {
            'image/png',
            'image/jpeg',
            'image/jpg',
            'image/gif',
            'image/webp',
            'image/bmp',
            'image/tiff',
            'image/svg+xml',
            'image/x-icon',
            'image/ico'
        }

        # 提取主要的MIME类型（移除参数部分）
        main_type = content_type.split(';')[0].strip().lower()

        # 检查是否在已知的图片类型中
        if main_type in image_mime_types:
            return True

        # 检查是否以 'image/' 开头（兼容未列出的图片格式）
        if main_type.startswith('image/'):
            return True

        return False

    def _build_card_index(self):
        """构建卡牌索引，处理linked_card关系"""
        if 'cards' not in self.content_pack.get('data', {}):
            self.logger.error("内容包中没有找到cards数据")
            return

        # 首先构建code到卡牌的映射
        for card in self.content_pack['data']['cards']:
            card_code = card.get('code')
            if card_code:
                self.cards_by_code[card_code] = card

                # 记录linked_card关系
                linked_card = card.get('linked_card')
                if linked_card and isinstance(linked_card, dict):
                    linked_code = linked_card.get('code')
                    if linked_code:
                        self.linked_card_relations[card_code] = linked_code
                        self.linked_card_relations[linked_code] = card_code

        # 标记双面卡对
        for card in self.content_pack['data']['cards']:
            card_code = card.get('code')
            if not card_code:
                continue

            # 检查是否是双面卡
            if card.get('double_sided', False):
                # 双面卡自身包含正反面
                self.double_sided_pairs.add(card_code)

            elif card_code in self.linked_card_relations:
                # 通过linked_card关联的双面卡
                linked_code = self.linked_card_relations[card_code]
                self.double_sided_pairs.add(card_code)
                self.double_sided_pairs.add(linked_code)

        self.logger.info(
            f"构建卡牌索引完成: 共{len(self.cards_by_code)}张卡牌, {len(self.double_sided_pairs) // 2}对双面卡")

    def _convert_card_with_arkhamdb_converter(self, card_data: Dict[str, Any], is_back: bool = False) -> Optional[
        Dict[str, Any]]:
        """
        使用ArkhamDBConverter转换卡牌

        Args:
            card_data: 原始卡牌数据
            is_back: 是否是背面

        Returns:
            转换后的卡牌对象，或None
        """
        try:
            converter = ArkhamDBConverter(card_data)

            if is_back:
                converted_card = converter.convert_back()
            else:
                converted_card = converter.convert_front()

            return converted_card

        except Exception as e:
            self.logger.error(f"ArkhamDBConverter转换失败: {card_data.get('name', 'unknown')} - {str(e)}")
            return None

    def _add_image_data_to_card(self, card_obj: Dict[str, Any], card_data: Dict[str, Any], is_front: bool = True):
        """
        为卡牌对象添加图片数据

        Args:
            card_obj: 转换后的卡牌对象
            card_data: 原始卡牌数据
            is_front: 是否是正面
        """
        image_field = 'image_url' if is_front else 'back_image_url'
        image_url = card_data.get(image_field)

        if image_url:
            base64_data = self._download_image_to_base64(image_url)
            if base64_data:
                card_obj['picture_base64'] = base64_data
                card_obj['image_mode'] = 1
                self.logger.info(f"成功下载并转换图片: {image_url}")
            else:
                card_obj['image_mode'] = 0
                self.logger.warning(f"图片下载失败: {image_url}")
        else:
            card_obj['image_mode'] = 0

    def _add_tts_script_metadata(self, card_obj: Dict[str, Any], card_code: str):
        """
        为卡牌正面添加TTS脚本元数据

        Args:
            card_obj: 卡牌对象
            card_code: 卡牌代码
        """
        if card_code:
            # 构建TTS脚本元数据
            gm_notes = json.dumps({"id": card_code})
            card_obj['tts_script'] = {
                "GMNotes": gm_notes
            }
            self.logger.debug(f"添加TTS脚本元数据: {card_code}")

    def _add_language_and_version(self, card_obj: Dict[str, Any]):
        """
        为卡牌对象添加语言和版本信息

        Args:
            card_obj: 卡牌对象
        """
        # 添加语言设置
        card_obj['language'] = self.language

        # 添加版本信息
        card_obj['version'] = "2.0"

        # 递归处理背面（如果存在）
        if 'back' in card_obj and isinstance(card_obj['back'], dict):
            card_obj['back']['language'] = self.language
            card_obj['back']['version'] = "2.0"

    def _get_default_card_back_type(self, front_card_obj: Dict[str, Any]) -> str:
        """
        根据正面卡牌的type和class获取默认卡背类型

        Args:
            front_card_obj: 转换后的正面卡牌对象

        Returns:
            卡背类型字符串
        """
        card_type = front_card_obj.get('type', '')
        card_class = front_card_obj.get('class', '')

        # 如果class为"弱点"，则使用玩家卡背
        if card_class == '弱点':
            return '玩家卡背'

        # 根据type判断卡背类型
        if card_type in ['支援卡', '事件卡', '技能卡']:
            return '玩家卡背'
        elif card_type == '定制卡':
            return '定制卡背'
        else:
            # 剩下的所有类型都使用遭遇卡背
            return '遭遇卡背'

    def _handle_double_sided_card(self, card: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理双面卡牌

        Args:
            card: 卡牌数据

        Returns:
            包含正反面的完整卡牌对象，或None
        """
        card_code = card.get('code')
        if not card_code:
            return None

        self.logger.info(f"处理双面卡牌: {card.get('name', 'unknown')}")

        # 使用ArkhamDBConverter转换正面
        front_obj = self._convert_card_with_arkhamdb_converter(card, is_back=False)
        if not front_obj:
            return None

        # 添加正面图片数据
        self._add_image_data_to_card(front_obj, card, is_front=True)

        # 添加TTS脚本元数据到正面
        self._add_tts_script_metadata(front_obj, card_code)

        # 处理背面
        back_obj = None

        if card.get('double_sided', False):
            # 自身包含背面信息
            back_obj = self._convert_card_with_arkhamdb_converter(card, is_back=True)
            if back_obj:
                self._add_image_data_to_card(back_obj, card, is_front=False)

        elif card_code in self.linked_card_relations:
            # 通过linked_card关联
            linked_code = self.linked_card_relations[card_code]
            linked_card = self.cards_by_code.get(linked_code)
            if linked_card:
                back_obj = self._convert_card_with_arkhamdb_converter(linked_card, is_back=False)
                if back_obj:
                    self._add_image_data_to_card(back_obj, linked_card, is_front=True)

        # 如果背面转换失败，创建默认背面
        if back_obj is None:
            # 根据正面卡牌类型获取默认卡背
            default_back_type = self._get_default_card_back_type(front_obj)
            back_obj = {
                'type': default_back_type,
                'name': card.get('name', '') + ' (背面)',
                'image_mode': 0
            }
            self.logger.warning(f"无法获取背面信息，使用默认背面 ({default_back_type}): {card.get('name', 'unknown')}")

        # 将背面对象添加到正面
        front_obj['back'] = back_obj

        # 添加原始数据中的位置信息
        front_obj['position'] = card.get('position', 0)
        front_obj['code'] = card.get('code', '')

        # 添加语言和版本信息
        self._add_language_and_version(front_obj)

        return front_obj

    def _handle_single_sided_card(self, card: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理单面卡牌

        Args:
            card: 卡牌数据

        Returns:
            单面卡牌对象，或None
        """
        card_code = card.get('code')
        if not card_code:
            return None

        # 检查是否应该被识别为双面卡的一部分
        if card_code in self.double_sided_pairs:
            self.logger.debug(f"跳过单面处理，卡牌 {card_code} 是双面卡的一部分")
            return None

        self.logger.info(f"处理单面卡牌: {card.get('name', 'unknown')}")

        # 使用ArkhamDBConverter转换正面
        card_obj = self._convert_card_with_arkhamdb_converter(card, is_back=False)
        if not card_obj:
            return None

        # 添加正面图片数据
        self._add_image_data_to_card(card_obj, card, is_front=True)

        # 添加TTS脚本元数据到正面
        self._add_tts_script_metadata(card_obj, card_code)

        # 根据正面卡牌类型获取默认卡背
        default_back_type = self._get_default_card_back_type(card_obj)

        # 添加默认背面
        card_obj['back'] = {
            'type': default_back_type,
            'name': card.get('name', '') + ' (背面)',
            'image_mode': 0
        }

        self.logger.info(f"使用默认卡背 ({default_back_type}): {card.get('name', 'unknown')}")

        # 添加原始数据中的位置信息
        card_obj['position'] = card.get('position', 0)
        card_obj['code'] = card.get('code', '')

        # 添加语言和版本信息
        self._add_language_and_version(card_obj)

        return card_obj

    def _save_single_card(self, card: Dict[str, Any]) -> bool:
        """
        保存单张卡牌到文件

        Args:
            card: 卡牌对象

        Returns:
            是否保存成功
        """
        try:
            # 生成文件名
            filename = self._sanitize_filename(
                card.get('name', 'unknown'),
                card.get('position', 0)
            )

            file_path = self.work_dir / filename

            # 保存为JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(card, f, ensure_ascii=False, indent=2)

            self.logger.info(f"保存卡牌: {filename}")
            return True

        except Exception as e:
            self.logger.error(f"保存卡牌失败: {card.get('name', 'unknown')} - {str(e)}")
            return False

    def build_and_save_cards(self) -> int:
        """
        构建并保存所有卡牌对象（边构建边保存，避免内存溢出）

        Returns:
            成功保存的卡牌数量
        """
        self.logger.info("开始构建并保存卡牌对象...")
        self.logger.info(f"内容包语言: {self.language}")

        # 构建索引
        self._build_card_index()

        saved_count = 0
        processed_codes = set()

        for card in self.content_pack['data']['cards']:
            card_code = card.get('code')
            if not card_code or card_code in processed_codes:
                continue

            card_obj = None

            # 检查是否是双面卡
            if card_code in self.double_sided_pairs:
                card_obj = self._handle_double_sided_card(card)
            else:
                card_obj = self._handle_single_sided_card(card)

            # 立即保存构建的卡牌
            if card_obj:
                if self._save_single_card(card_obj):
                    saved_count += 1

                processed_codes.add(card_code)

                # 如果是双面卡，也标记关联卡牌为已处理
                if card_code in self.linked_card_relations:
                    linked_code = self.linked_card_relations[card_code]
                    processed_codes.add(linked_code)

        self.logger.info(f"卡牌构建并保存完成: 共成功保存{saved_count}张卡牌")
        return saved_count

    def build_cards(self) -> List[Dict[str, Any]]:
        """
        构建所有卡牌对象（保留原有方法以兼容性）

        Returns:
            卡牌对象列表
        """
        self.logger.info("开始构建卡牌对象...")
        self.logger.info(f"内容包语言: {self.language}")

        # 构建索引
        self._build_card_index()

        built_cards = []
        processed_codes = set()

        for card in self.content_pack['data']['cards']:
            card_code = card.get('code')
            if not card_code or card_code in processed_codes:
                continue

            card_obj = None

            # 检查是否是双面卡
            if card_code in self.double_sided_pairs:
                card_obj = self._handle_double_sided_card(card)
            else:
                card_obj = self._handle_single_sided_card(card)

            if card_obj:
                built_cards.append(card_obj)
                processed_codes.add(card_code)

                # 如果是双面卡，也标记关联卡牌为已处理
                if card_code in self.linked_card_relations:
                    linked_code = self.linked_card_relations[card_code]
                    processed_codes.add(linked_code)

        self.logger.info(f"卡牌构建完成: 共构建{len(built_cards)}张卡牌")
        return built_cards

    def save_cards(self, cards: List[Dict[str, Any]]) -> int:
        """
        保存卡牌对象到文件（保留原有方法以兼容性）

        Args:
            cards: 卡牌对象列表

        Returns:
            成功保存的卡牌数量
        """
        saved_count = 0

        for card in cards:
            if self._save_single_card(card):
                saved_count += 1

        self.logger.info(f"卡牌保存完成: 成功保存{saved_count}张卡牌")
        return saved_count

    def process_content_pack(self) -> Tuple[int, List[Dict[str, Any]], bool, List[str]]:
        """
        处理整个内容包（使用边构建边保存的方式）

        Returns:
            (成功保存的卡牌数量, 空卡牌列表, 是否验证通过, 错误信息列表)
        """
        self.logger.info("开始处理内容包...")

        try:
            # 首先验证内容包结构
            is_valid, errors = self.validate_content_pack_structure()
            if not is_valid:
                self.logger.error("内容包结构验证失败，停止处理")
                return 0, [], False, errors

            # 构建并保存卡牌对象（边构建边保存）
            saved_count = self.build_and_save_cards()

            return saved_count, [], True, []

        except Exception as e:
            self.logger.error(f"处理内容包时发生错误: {str(e)}")
            return 0, [], False, [f"处理内容包时发生错误: {str(e)}"]


# 使用示例
def main():
    # 读取JSON文件
    with open(r"C:\Users\xziyi\Downloads\ordinary_citizens (2).json", 'r', encoding='utf-8') as f:
        content_pack = json.load(f)

    # 创建构建器实例
    builder = ArkhamCardBuilder(content_pack, r'D:\汉化文件夹\测试导出空间')

    # 处理内容包
    saved_count, _, is_valid, errors = builder.process_content_pack()

    # 输出日志
    print("处理完成!")
    print(f"成功保存 {saved_count} 张卡牌")
    print(f"内容包语言: {builder.language}")
    if not is_valid:
        print(f"验证错误: {errors}")
    print("\n处理日志:")
    print(builder.get_logs())


if __name__ == "__main__":
    main()
