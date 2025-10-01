import json
import os
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

    def process_location_gm_notes(self, gm_notes: str, front_card_type: str,
                                 back_card: Optional[Dict[str, Any]] = None) -> str:
        """
        处理地点卡的GMNotes字段
        
        Args:
            gm_notes: 正面卡牌的GMNotes
            front_card_type: 正面卡牌类型
            back_card: 背面卡牌数据
            
        Returns:
            处理后的GMNotes字符串
        """
        try:
            # 解析正面GMNotes
            front_gm_data = {}
            if gm_notes:
                front_gm_data = json.loads(gm_notes)
            
            # 处理正面为地点卡的情况
            if front_card_type == "地点卡" and front_gm_data.get("type") == "Location":
                if "location" in front_gm_data:
                    front_gm_data["locationFront"] = front_gm_data.pop("location")
                    print(f"正面地点卡：将location字段改为locationFront")
            
            # 处理背面为地点卡的情况
            if back_card:
                back_card_type = back_card.get("type", "")
                back_tts_script = back_card.get("tts_script", {})
                back_gm_notes = back_tts_script.get("GMNotes", "")
                
                if back_gm_notes:
                    back_gm_data = json.loads(back_gm_notes)
                    
                    # 如果背面是地点卡
                    if back_card_type == "地点卡" and back_gm_data.get("type") == "Location":
                        if "location" in back_gm_data:
                            # 将背面的location改为locationBack并合并到正面
                            front_gm_data["locationBack"] = back_gm_data["location"]
                            print(f"背面地点卡：将location字段改为locationBack并合并到正面")
            
            # 返回处理后的JSON字符串
            return json.dumps(front_gm_data, ensure_ascii=False) if front_gm_data else ""
            
        except json.JSONDecodeError as e:
            print(f"解析GMNotes JSON时出错: {e}")
            return gm_notes
        except Exception as e:
            print(f"处理地点卡GMNotes时出错: {e}")
            return gm_notes

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

        # 特殊处理地点卡的GMNotes
        gm_notes = self.process_location_gm_notes(gm_notes, card_type, back_card)

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
        将牌库配置转换为TTS格式，将调查员卡和其他卡分成两个牌堆

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

        # 读取共享背面配置
        is_shared_back = deck_config.get('isSharedBack', False)
        shared_back_card = deck_config.get('sharedBackCard', {})

        print(f"共享背面: {'是' if is_shared_back else '否'}")
        if is_shared_back and shared_back_card:
            print(f"共享背面类型: {shared_back_card.get('type', 'unknown')}")

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

        # 创建背面卡牌映射
        back_card_map = {}
        shared_back_data = None

        if is_shared_back and shared_back_card:
            # 使用共享背面
            if shared_back_card.get("type") == "card":
                try:
                    shared_back_data = self.read_card_file(shared_back_card["path"])
                    print(f"读取共享背面卡牌: {shared_back_card['path']}")
                    # 为所有正面卡牌位置设置相同的共享背面
                    for front_card in front_cards:
                        back_card_map[front_card["index"]] = shared_back_data
                except Exception as e:
                    print(f"无法读取共享背面卡牌 {shared_back_card['path']}: {e}")
        else:
            # 使用位置对应的背面卡牌
            for back_card in back_cards:
                if back_card.get("type") == "card":
                    try:
                        card_data = self.read_card_file(back_card["path"])
                        back_card_map[back_card["index"]] = card_data
                        print(f"读取背面卡牌: {back_card['path']}")
                    except Exception as e:
                        print(f"无法读取背面卡牌 {back_card['path']}: {e}")

        # 分别处理调查员卡和其他卡牌
        investigator_cards = []  # 调查员卡牌列表
        other_cards = []  # 其他卡牌列表

        # 使用统一的CustomDeck ID，从2700开始
        base_custom_deck_id = 2700
        current_custom_deck_id = str(base_custom_deck_id)
        card_position_in_deck = 0

        # 处理正面卡牌，按类型分组
        for i, front_card in enumerate(front_cards):
            print(f"处理第 {i + 1} 张卡牌: {front_card}")

            front_card_type = front_card.get("type", "")
            front_index = front_card.get("index", 0)

            try:
                # 计算卡牌在deck中的位置
                if card_position_in_deck >= max_cards_per_deck:
                    base_custom_deck_id += 1
                    current_custom_deck_id = str(base_custom_deck_id)
                    card_position_in_deck = 0

                # 生成CardID
                card_position_str = str(front_index).zfill(2)
                card_id = int(current_custom_deck_id + card_position_str)
                print(f"生成CardID: {card_id} (position: {card_position_in_deck:02d})")

                # 设置UniqueBack
                unique_back = not is_shared_back

                # 判断是否为调查员卡
                is_investigator_card = False
                if front_card_type == "card":
                    try:
                        card_data = self.read_card_file(front_card["path"])
                        card_type = card_data.get("type", "")
                        is_investigator_card = card_type in ["调查员", "Investigator"]
                    except Exception as e:
                        print(f"无法读取卡牌数据判断类型: {e}")

                # 根据类型处理不同的卡牌
                if front_card_type == "card":
                    # card类型：读取卡牌数据并添加脚本
                    card_data = self.read_card_file(front_card["path"])
                    print(f"成功读取card: {front_card['path']} - {card_data.get('name', 'No Name')}")

                    # 获取对应的背面卡牌
                    back_card_data = back_card_map.get(front_card["index"])
                    if back_card_data:
                        if is_shared_back:
                            print(f"使用共享背面: {back_card_data.get('name', 'No Name')}")
                        else:
                            print(f"找到对应背面卡牌: {back_card_data.get('name', 'No Name')}")

                    # 创建卡牌对象
                    card_object = self.create_card_object_from_data(
                        card_data, card_id, current_custom_deck_id,
                        face_url, back_url, deck_width, deck_height,
                        back_card_data, unique_back
                    )

                elif front_card_type == "image":
                    # image类型：创建基础卡牌对象，不添加脚本
                    print(f"处理image: {front_card['path']}")
                    unique_back = False

                    card_object = self.create_card_object_from_image(
                        front_card["path"], card_id, current_custom_deck_id,
                        face_url, back_url, deck_width, deck_height, unique_back
                    )

                else:
                    # 其他类型：也创建基础卡牌对象
                    print(f"处理其他类型 {front_card_type}: {front_card['path']}")
                    unique_back = False

                    card_object = self.create_card_object_from_image(
                        front_card["path"], card_id, current_custom_deck_id,
                        face_url, back_url, deck_width, deck_height, unique_back
                    )

                # 根据是否为调查员卡分组
                if is_investigator_card:
                    investigator_cards.append({
                        'card_object': card_object,
                        'card_id': card_id,
                        'custom_deck_id': current_custom_deck_id
                    })
                    print(f"添加到调查员卡组: {card_object.get('Nickname', 'Unknown')}")
                else:
                    other_cards.append({
                        'card_object': card_object,
                        'card_id': card_id,
                        'custom_deck_id': current_custom_deck_id
                    })
                    print(f"添加到其他卡组: {card_object.get('Nickname', 'Unknown')}")

                card_position_in_deck += 1

            except Exception as e:
                print(f"处理卡牌时出错 {front_card.get('path', 'unknown')}: {e}")
                continue

        print(f"调查员卡数量: {len(investigator_cards)}")
        print(f"其他卡牌数量: {len(other_cards)}")

        # 处理调查员卡 (左边)
        if investigator_cards:
            if len(investigator_cards) == 1:
                # 单张调查员卡
                single_card = investigator_cards[0]['card_object']
                single_card["Transform"] = {
                    "posX": -13.253087 + random.uniform(-0.1, 0.1),
                    "posY": 0.973604739,
                    "posZ": 5.63178 + random.uniform(-0.1, 0.1),
                    "rotX": random.uniform(-4.13e-08, 4.13e-08),
                    "rotY": 89.9999847,
                    "rotZ": random.uniform(-1.92e-07, 1.92e-07),
                    "scaleX": 1.15,
                    "scaleY": 1.0,
                    "scaleZ": 1.15
                }
                tts_object["ObjectStates"].append(single_card)
                print("创建单张调查员卡（左边）")
            else:
                # 多张调查员卡，创建牌堆
                investigator_deck_ids = [card['card_id'] for card in investigator_cards]
                investigator_contained_objects = [card['card_object'] for card in investigator_cards]

                # 收集所有CustomDeck
                investigator_custom_decks = {}
                for card in investigator_cards:
                    deck_id = card['custom_deck_id']
                    if deck_id not in investigator_custom_decks:
                        investigator_custom_decks[deck_id] = self.create_custom_deck_entry(
                            face_url, back_url, deck_width, deck_height, not is_shared_back
                        )

                investigator_deck_object = {
                    "GUID": self.generate_guid(),
                    "Name": "Deck",
                    "Transform": {
                        "posX": -13.253087 + random.uniform(-0.1, 0.1),
                        "posY": 0.973604739,
                        "posZ": 5.63178 + random.uniform(-0.1, 0.1),
                        "rotX": random.uniform(-7.78e-07, 7.78e-07),
                        "rotY": 89.9999847,
                        "rotZ": random.uniform(-3.26e-07, 3.26e-07),
                        "scaleX": 1.15,
                        "scaleY": 1.0,
                        "scaleZ": 1.15
                    },
                    "Nickname": "调查员卡堆",
                    "Description": "",
                    "GMNotes": "",
                    "AltLookAngle": {"x": 0.0, "y": 0.0, "z": 0.0},
                    "ColorDiffuse": {"r": 0.713235259, "g": 0.713235259, "b": 0.713235259},
                    "Tags": ["Investigator", "PlayerCard"],
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
                    "HideWhenFaceDown": False,  # 调查员卡牌堆不隐藏
                    "Hands": False,
                    "SidewaysCard": True,  # 调查员牌堆横置
                    "DeckIDs": investigator_deck_ids,
                    "CustomDeck": investigator_custom_decks,
                    "LuaScript": "",
                    "LuaScriptState": "",
                    "XmlUI": "",
                    "ContainedObjects": investigator_contained_objects
                }
                tts_object["ObjectStates"].append(investigator_deck_object)
                print("创建调查员牌堆（左边）")

        # 处理其他卡牌 (右边)
        if other_cards:
            if len(other_cards) == 1:
                # 单张其他卡牌
                single_card = other_cards[0]['card_object']
                single_card["Transform"] = {
                    "posX": 3.71505737 + random.uniform(-0.1, 0.1),
                    "posY": 0.973604739,  # 使用与调查员卡相同的高度
                    "posZ": -0.104532719 + random.uniform(-0.1, 0.1),
                    "rotX": random.uniform(-7.78e-07, 7.78e-07),
                    "rotY": 179.999817,
                    "rotZ": random.uniform(-3.26e-07, 3.26e-07),
                    "scaleX": 1.0,  # 普通卡牌使用标准缩放
                    "scaleY": 1.0,
                    "scaleZ": 1.0
                }
                tts_object["ObjectStates"].append(single_card)
                print("创建单张其他卡牌（右边）")
            else:
                # 多张其他卡牌，创建牌堆
                other_deck_ids = [card['card_id'] for card in other_cards]
                other_contained_objects = [card['card_object'] for card in other_cards]

                # 收集所有CustomDeck
                other_custom_decks = {}
                for card in other_cards:
                    deck_id = card['custom_deck_id']
                    if deck_id not in other_custom_decks:
                        other_custom_decks[deck_id] = self.create_custom_deck_entry(
                            face_url, back_url, deck_width, deck_height, not is_shared_back
                        )

                # 确定牌堆标签（基于第一张卡的类型）
                deck_tags = ["PlayerCard"]  # 默认标签
                if other_contained_objects:
                    first_card_tags = other_contained_objects[0].get("Tags", [])
                    if "Asset" in first_card_tags:
                        deck_tags = ["Asset", "PlayerCard"]

                other_deck_object = {
                    "GUID": self.generate_guid(),
                    "Name": "Deck",
                    "Transform": {
                        "posX": 3.71505737 + random.uniform(-0.1, 0.1),
                        "posY": 0.026581943,
                        "posZ": -0.104532719 + random.uniform(-0.1, 0.1),
                        "rotX": random.uniform(-7.78e-07, 7.78e-07),
                        "rotY": 179.999817,
                        "rotZ": random.uniform(-3.26e-07, 3.26e-07),
                        "scaleX": 1.0,  # 普通卡牌牌堆使用标准缩放
                        "scaleY": 1.0,
                        "scaleZ": 1.0
                    },
                    "Nickname": deck_config.get("name", "其他卡牌"),
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
                    "DeckIDs": other_deck_ids,
                    "CustomDeck": other_custom_decks,
                    "LuaScript": "",
                    "LuaScriptState": "",
                    "XmlUI": "",
                    "ContainedObjects": other_contained_objects
                }
                tts_object["ObjectStates"].append(other_deck_object)
                print("创建其他卡牌牌堆（右边）")

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
