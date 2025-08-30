import json
import os
import uuid
import random
from typing import Dict, List, Any, Optional


class TTSCardConverter:
    def __init__(self, work_directory: str):
        """
        初始化TTS卡牌转换器

        Args:
            work_directory: 工作目录路径
        """
        self.work_directory = work_directory
        self.card_type_tags = {
            "调查员": ["Investigator", "PlayerCard"],
            "调查员背面": ["Investigator", "PlayerCard"],
            "定制卡": ["PlayerCard"],
            "技能卡": ["PlayerCard"],
            "事件卡": ["PlayerCard"],
            "支援卡": ["Asset", "PlayerCard"],
            "敌人卡": ["ScenarioCard"],
            "地点卡": ["Location", "ScenarioCard"],
            "密谋卡": ["ScenarioCard"],
            "密谋卡-大画": ["ScenarioCard"],
            "场景卡": ["ScenarioCard"],
            "场景卡-大画": ["ScenarioCard"],
            "故事卡": ["ScenarioCard"],
            "冒险参考卡": ["ScenarioCard"],
        }

    def generate_guid(self) -> str:
        """生成随机GUID"""
        return ''.join(random.choices('0123456789abcdef', k=6))

    def read_json_file(self, relative_path: str) -> Dict[str, Any]:
        """读取相对路径的JSON文件"""
        full_path = os.path.join(self.work_directory, relative_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def read_card_file(self, card_path: str) -> Dict[str, Any]:
        """读取card文件，支持.card和.card.json格式"""
        base_path = os.path.join(self.work_directory, card_path)

        # 尝试读取.card.json文件
        json_path = base_path + '.json'
        if os.path.exists(json_path):
            return self.read_json_file(card_path + '.json')

        # 如果没有.json文件，尝试直接读取.card文件
        if os.path.exists(base_path):
            with open(base_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        raise FileNotFoundError(f"Card file not found: {card_path}")

    def get_card_tags(self, card_type: str) -> List[str]:
        """根据卡牌类型获取标签"""
        return self.card_type_tags.get(card_type, ["PlayerCard"])

    def create_custom_deck_entry(self, face_url: str, back_url: str,
                                 num_width: int, num_height: int,
                                 unique_back: bool = False) -> Dict[str, Any]:
        """创建CustomDeck条目"""
        return {
            "FaceURL": face_url,
            "BackURL": back_url,
            "NumWidth": num_width,
            "NumHeight": num_height,
            "BackIsHidden": True,
            "UniqueBack": unique_back,
            "Type": 0
        }

    def create_card_object_from_data(self, card_data: Dict[str, Any], card_id: int,
                                     custom_deck_id: str, face_url: str, back_url: str,
                                     num_width: int, num_height: int,
                                     back_card: Optional[Dict[str, Any]] = None,
                                     unique_back: bool = False) -> Dict[str, Any]:
        """从card数据创建卡牌对象（包含脚本）"""

        # 确定卡牌类型和标签
        card_type = card_data.get("type", "")
        tags = self.get_card_tags(card_type)

        # 获取脚本信息
        tts_script = card_data.get("tts_script", {})
        gm_notes = tts_script.get("GMNotes", "")
        lua_script = tts_script.get("LuaScript", "")

        # 如果背面也有脚本且正面没有，则使用背面的
        if back_card and not gm_notes:
            back_script = back_card.get("tts_script", {})
            gm_notes = back_script.get("GMNotes", "")

        if back_card and not lua_script:
            back_script = back_card.get("tts_script", {})
            lua_script = back_script.get("LuaScript", "")

        # 判断是否为调查员卡（需要横置）
        is_investigator = card_type in ["调查员", "Investigator"]

        return {
            "GUID": self.generate_guid(),
            "Name": "Card",
            "Transform": {
                "posX": 37.0 + random.uniform(-0.5, 0.5),
                "posY": 1.495 + random.uniform(-0.005, 0.005),
                "posZ": 37.0 + random.uniform(-0.5, 0.5),
                "rotX": random.uniform(-0.001, 0.001),
                "rotY": 270.0 + random.uniform(-0.1, 0.1),
                "rotZ": random.uniform(-0.004, 0.004),
                "scaleX": 1.15,
                "scaleY": 1.0,
                "scaleZ": 1.15
            },
            "Nickname": card_data.get("name", ""),
            "Description": card_data.get("subtitle", ""),
            "GMNotes": gm_notes,
            "AltLookAngle": {"x": 0.0, "y": 0.0, "z": 0.0},
            "ColorDiffuse": {"r": 0.713235259, "g": 0.713235259, "b": 0.713235259},
            "Tags": tags,
            "LayoutGroupSortIndex": 0,
            "Value": 0,
            "Locked": False,
            "Grid": True,
            "Snap": True,
            "IgnoreFoW": False,
            "MeasureMovement": False,
            "DragSelectable": True,
            "Autoraise": True,
            "Sticky": True,
            "Tooltip": True,
            "GridProjection": False,
            "HideWhenFaceDown": not is_investigator,
            "Hands": True,
            "CardID": card_id,
            "SidewaysCard": is_investigator,
            "CustomDeck": {
                custom_deck_id: self.create_custom_deck_entry(
                    face_url, back_url, num_width, num_height, unique_back
                )
            },
            "LuaScript": lua_script,
            "LuaScriptState": "",
            "XmlUI": ""
        }

    def create_card_object_from_image(self, image_path: str, card_id: int,
                                      custom_deck_id: str, face_url: str, back_url: str,
                                      num_width: int, num_height: int,
                                      unique_back: bool = False) -> Dict[str, Any]:
        """从image路径创建卡牌对象（不包含脚本）"""

        # 从文件名提取名称
        name = os.path.splitext(os.path.basename(image_path))[0]

        return {
            "GUID": self.generate_guid(),
            "Name": "Card",
            "Transform": {
                "posX": 37.0 + random.uniform(-0.5, 0.5),
                "posY": 1.495 + random.uniform(-0.005, 0.005),
                "posZ": 37.0 + random.uniform(-0.5, 0.5),
                "rotX": random.uniform(-0.001, 0.001),
                "rotY": 270.0 + random.uniform(-0.1, 0.1),
                "rotZ": random.uniform(-0.004, 0.004),
                "scaleX": 1.15,
                "scaleY": 1.0,
                "scaleZ": 1.15
            },
            "Nickname": name,
            "Description": "",
            "GMNotes": "",  # image类型不添加GMNotes
            "AltLookAngle": {"x": 0.0, "y": 0.0, "z": 0.0},
            "ColorDiffuse": {"r": 0.713235259, "g": 0.713235259, "b": 0.713235259},
            "Tags": ["PlayerCard"],  # 默认标签
            "LayoutGroupSortIndex": 0,
            "Value": 0,
            "Locked": False,
            "Grid": True,
            "Snap": True,
            "IgnoreFoW": False,
            "MeasureMovement": False,
            "DragSelectable": True,
            "Autoraise": True,
            "Sticky": True,
            "Tooltip": True,
            "GridProjection": False,
            "HideWhenFaceDown": True,
            "Hands": True,
            "CardID": card_id,
            "SidewaysCard": False,
            "CustomDeck": {
                custom_deck_id: self.create_custom_deck_entry(
                    face_url, back_url, num_width, num_height, unique_back
                )
            },
            "LuaScript": "",  # image类型不添加LuaScript
            "LuaScriptState": "",
            "XmlUI": ""
        }

    def convert_deck_to_tts(self, deck_config: Dict[str, Any], face_url: str,
                            back_url: str) -> Dict[str, Any]:
        """
        将牌库配置转换为TTS格式

        Args:
            deck_config: 牌库配置JSON
            face_url: 正面图片URL
            back_url: 背面图片URL

        Returns:
            TTS格式的JSON对象
        """

        print("开始转换牌库...")
        print(f"牌库名称: {deck_config.get('name', 'Unknown')}")

        # 从配置文件读取牌组尺寸
        deck_width = deck_config.get("width", 10)
        deck_height = deck_config.get("height", 7)
        max_cards_per_deck = deck_width * deck_height

        print(f"牌组尺寸: {deck_width}x{deck_height} (每个CustomDeck最多{max_cards_per_deck}张卡)")

        # 创建基础TTS对象
        tts_object = {
            "SaveName": "",
            "Date": "",
            "VersionNumber": "",
            "GameMode": "",
            "GameType": "",
            "GameComplexity": "",
            "Tags": [],
            "Gravity": 0.5,
            "PlayArea": 0.5,
            "Table": "",
            "Sky": "",
            "Note": "",
            "TabStates": {},
            "LuaScript": "",
            "LuaScriptState": "",
            "XmlUI": "",
            "ObjectStates": []
        }

        # 处理卡牌数据
        front_cards = deck_config.get("frontCards", [])
        back_cards = deck_config.get("backCards", [])

        print(f"找到 {len(front_cards)} 张正面卡牌")
        print(f"找到 {len(back_cards)} 张背面卡牌")

        # 创建背面卡牌映射（只处理card类型的背面）
        back_card_map = {}
        for back_card in back_cards:
            if back_card.get("type") == "card":
                try:
                    card_data = self.read_card_file(back_card["path"])
                    back_card_map[back_card["index"]] = card_data
                    print(f"读取背面卡牌: {back_card['path']}")
                except Exception as e:
                    print(f"无法读取背面卡牌 {back_card['path']}: {e}")

        contained_objects = []
        deck_ids = []
        custom_decks = {}

        # 使用一个统一的CustomDeck ID，从2700开始
        base_custom_deck_id = 2700
        current_custom_deck_id = str(base_custom_deck_id)
        card_position_in_deck = 0

        # 处理正面卡牌 - 现在处理所有类型
        for i, front_card in enumerate(front_cards):
            print(f"处理第 {i + 1} 张卡牌: {front_card}")

            front_card_type = front_card.get("type", "")

            try:
                # 计算卡牌在deck中的位置（根据配置的width和height）
                if card_position_in_deck >= max_cards_per_deck:
                    base_custom_deck_id += 1
                    current_custom_deck_id = str(base_custom_deck_id)
                    card_position_in_deck = 0

                # 生成CardID：CustomDeckID + 卡牌位置（从00开始）
                card_position_str = str(card_position_in_deck).zfill(2)
                card_id = int(current_custom_deck_id + card_position_str)
                print(f"生成CardID: {card_id} (position: {card_position_in_deck:02d})")

                # 根据类型处理不同的卡牌
                if front_card_type == "card":
                    # card类型：读取卡牌数据并添加脚本
                    card_data = self.read_card_file(front_card["path"])
                    print(f"成功读取card: {front_card['path']} - {card_data.get('name', 'No Name')}")

                    # 获取对应的背面卡牌（如果有）
                    back_card_data = back_card_map.get(front_card["index"])
                    if back_card_data:
                        print(f"找到对应背面卡牌: {back_card_data.get('name', 'No Name')}")

                    # 判断是否需要UniqueBack
                    card_type = card_data.get("type", "")
                    unique_back = True

                    # 如果这个CustomDeck还没有被创建，创建它
                    if current_custom_deck_id not in custom_decks:
                        custom_decks[current_custom_deck_id] = self.create_custom_deck_entry(
                            face_url, back_url, deck_width, deck_height, unique_back
                        )
                        print(f"创建CustomDeck: {current_custom_deck_id} ({deck_width}x{deck_height})")

                    # 创建卡牌对象（包含脚本）
                    card_object = self.create_card_object_from_data(
                        card_data, card_id, current_custom_deck_id,
                        face_url, back_url, deck_width, deck_height,
                        back_card_data, unique_back
                    )

                elif front_card_type == "image":
                    # image类型：创建基础卡牌对象，不添加脚本
                    print(f"处理image: {front_card['path']}")

                    # image类型通常不需要UniqueBack
                    unique_back = False

                    # 如果这个CustomDeck还没有被创建，创建它
                    if current_custom_deck_id not in custom_decks:
                        custom_decks[current_custom_deck_id] = self.create_custom_deck_entry(
                            face_url, back_url, deck_width, deck_height, unique_back
                        )
                        print(f"创建CustomDeck: {current_custom_deck_id} ({deck_width}x{deck_height})")

                    # 创建卡牌对象（不包含脚本）
                    card_object = self.create_card_object_from_image(
                        front_card["path"], card_id, current_custom_deck_id,
                        face_url, back_url, deck_width, deck_height, unique_back
                    )

                else:
                    # 其他类型：也创建基础卡牌对象
                    print(f"处理其他类型 {front_card_type}: {front_card['path']}")

                    unique_back = False

                    if current_custom_deck_id not in custom_decks:
                        custom_decks[current_custom_deck_id] = self.create_custom_deck_entry(
                            face_url, back_url, deck_width, deck_height, unique_back
                        )
                        print(f"创建CustomDeck: {current_custom_deck_id} ({deck_width}x{deck_height})")

                    # 创建基础卡牌对象
                    card_object = self.create_card_object_from_image(
                        front_card["path"], card_id, current_custom_deck_id,
                        face_url, back_url, deck_width, deck_height, unique_back
                    )

                contained_objects.append(card_object)
                deck_ids.append(card_id)
                card_position_in_deck += 1
                print(f"成功创建卡牌对象，当前总数: {len(contained_objects)}")

            except Exception as e:
                print(f"处理卡牌时出错 {front_card.get('path', 'unknown')}: {e}")
                continue

        print(f"最终生成了 {len(contained_objects)} 张卡牌")

        # *** 新增：单张卡牌特殊处理 ***
        if len(contained_objects) == 1:
            print("检测到只有1张卡牌，导出单张卡牌格式")

            # 获取唯一的卡牌对象
            single_card = contained_objects[0]

            # 调整单张卡牌的Transform位置（参考示例）
            single_card["Transform"] = {
                "posX": 32.41374 + random.uniform(-0.1, 0.1),
                "posY": 1.49510384,
                "posZ": 26.9848671 + random.uniform(-0.1, 0.1),
                "rotX": random.uniform(-1.8e-07, 1.8e-07),
                "rotY": 270.0,
                "rotZ": random.uniform(-6e-07, 6e-07),
                "scaleX": 1.0,  # 单张卡牌使用标准缩放
                "scaleY": 1.0,
                "scaleZ": 1.0
            }

            # 直接将单张卡牌添加到ObjectStates
            tts_object["ObjectStates"] = [single_card]
            print("单张卡牌格式导出完成")

            return tts_object

        # *** 原有的牌堆处理逻辑 ***
        # 如果有多张卡牌，创建牌堆
        if contained_objects:
            # 检查第一张卡牌是否为调查员卡，决定牌堆的缩放
            first_card_tags = contained_objects[0].get("Tags", [])
            is_investigator_deck = "Investigator" in first_card_tags

            # 根据第一张卡牌类型设置缩放
            if is_investigator_deck:
                # 调查员牌堆缩放
                scale_x = 1.15
                scale_y = 1.0
                scale_z = 1.15
                print("检测到调查员牌堆，使用调查员缩放 (1.15, 1.0, 1.15)")
            else:
                # 普通卡牌牌堆缩放
                scale_x = 1.0
                scale_y = 1.0
                scale_z = 1.0
                print("检测到普通卡牌牌堆，使用标准缩放 (1.0, 1.0, 1.0)")

            # 确定牌堆标签（基于第一张卡的类型）
            deck_tags = ["PlayerCard"]  # 默认标签
            if contained_objects:
                first_card_tags = contained_objects[0].get("Tags", [])
                if "Investigator" in first_card_tags:
                    deck_tags = ["Investigator", "PlayerCard"]
                elif "Asset" in first_card_tags:
                    deck_tags = ["Asset", "PlayerCard"]

            deck_object = {
                "GUID": self.generate_guid(),
                "Name": "Deck",
                "Transform": {
                    "posX": 37.0078049,
                    "posY": 1.52168572,
                    "posZ": 37.49592,
                    "rotX": -3.26525765e-07,
                    "rotY": 270.0014,
                    "rotZ": -3.29874922e-07,
                    "scaleX": scale_x,  # 使用动态缩放
                    "scaleY": scale_y,  # 使用动态缩放
                    "scaleZ": scale_z  # 使用动态缩放
                },
                "Nickname": deck_config.get("name", ""),
                "Description": "",
                "GMNotes": "",
                "AltLookAngle": {"x": 0.0, "y": 0.0, "z": 0.0},
                "ColorDiffuse": {"r": 0.713235259, "g": 0.713235259, "b": 0.713235259},
                "Tags": deck_tags,
                "LayoutGroupSortIndex": 0,
                "Value": 0,
                "Locked": False,
                "Grid": True,
                "Snap": True,
                "IgnoreFoW": False,
                "MeasureMovement": False,
                "DragSelectable": True,
                "Autoraise": True,
                "Sticky": True,
                "Tooltip": True,
                "GridProjection": False,
                "HideWhenFaceDown": True,
                "Hands": False,
                "SidewaysCard": False,
                "DeckIDs": deck_ids,
                "CustomDeck": custom_decks,
                "LuaScript": "",
                "LuaScriptState": "",
                "XmlUI": "",
                "ContainedObjects": contained_objects
            }

            tts_object["ObjectStates"].append(deck_object)
            print("成功创建牌堆对象")
        else:
            print("没有找到任何有效的卡牌，无法创建牌堆")

        return tts_object


# 使用示例
if __name__ == "__main__":
    # 初始化转换器
    converter = TTSCardConverter(r"D:\汉化文件夹\测试工作空间")

    # 读取牌库配置
    try:
        deck_config = converter.read_json_file("DeckBuilder/测试.deck")

        # 设置图片URL
        face_url = "https://raw.githubusercontent.com/xziying31/GitHubImageHost/main/images/fc0c59d3122c4edbb560e3928ea411a2.jpg"
        back_url = "https://raw.githubusercontent.com/xziying31/GitHubImageHost/main/images/a9a37751a06543b89f3b95cdb0e9b377.jpg"

        # 转换为TTS格式
        tts_result = converter.convert_deck_to_tts(deck_config, face_url, back_url)

        # 输出结果
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(tts_result, f, indent=2, ensure_ascii=False)

        print("转换完成！结果已保存到 output.json")

    except Exception as e:
        print(f"转换失败: {e}")
        import traceback

        traceback.print_exc()
