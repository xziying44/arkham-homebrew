from PIL import Image, ImageDraw, ImageFont
import torch
import pandas as pd


class YoloArkhamIcon:
    """诡镇奇谈找图模型"""

    def __init__(self) -> None:
        # 加载模型
        self.model = torch.hub.load("ultralytics/yolov5", "custom", path="model/arkham-icon.pt")
        self.icon_list = {
            '🏅': '特',
            '⭕': '反',
            '➡️': '启',
            '⚡': '速',
            '💀': '骷',
            '👤': '徒',
            '📜': '板',
            '👹': '神',
            '🐙': '败',
            '⭐': '成',
            '👊': '拳',
            '📚': '书',
            '🦶': '脚',
            '🧠': '脑',
            '❓': '问',
            '🔵': '点',
            '🌑': '诅',
            '🌟': '祝',
            '❄️': '雪',
            '🕵️': '人',
            '🚶': '流',
            '🏕️': '求',
            '🛡️': '守',
            '🧘': '潜',
            '🔍': '探',
        }
        self.font = ImageFont.truetype("simfang.ttf", 20)

    def detect(self, image: Image.Image | str) -> pd.DataFrame:
        """检测图片中的图标"""
        if isinstance(image, str):
            image = Image.open(image)

        # 推理
        results = self.model(image)

        # 获取检测结果
        detections = results.pandas().xyxy[0]

        # --- 冲突处理逻辑 ---
        # 按置信度降序排序
        sorted_detections = detections.sort_values('confidence', ascending=False)
        filtered_rows = []

        for _, row in sorted_detections.iterrows():
            current_class = row['class']
            conflict = False

            # 检测冲突区域超过80%的区域，使用置信度较高的忽略置信度较低的
            for existing_row in filtered_rows:
                # 计算当前检测框与已保留框的交集面积
                x_min_exist = existing_row['xmin']
                x_max_exist = existing_row['xmax']
                y_min_exist = existing_row['ymin']
                y_max_exist = existing_row['ymax']

                # 计算交集区域
                x_left = max(x_min_exist, row['xmin'])
                y_top = max(y_min_exist, row['ymin'])
                x_right = min(x_max_exist, row['xmax'])
                y_bottom = min(y_max_exist, row['ymax'])

                # 如果有交集
                if x_right > x_left and y_bottom > y_top:
                    intersection_area = (x_right - x_left) * (y_bottom - y_top)
                    current_area = (row['xmax'] - row['xmin']) * (row['ymax'] - row['ymin'])
                    exist_area = (x_max_exist - x_min_exist) * (y_max_exist - y_min_exist)

                    # 计算重叠比例（相对于较小框的面积）
                    overlap_ratio = intersection_area / min(current_area, exist_area)

                    # 如果重叠超过80%，则标记为冲突
                    if overlap_ratio > 0.5:
                        conflict = True
                        break

            # 无冲突时保留当前框且置信度大于30%
            if not conflict and row['confidence'] > 0.3:
                filtered_rows.append(row)

        # 转换为新的DataFrame
        filtered_detections = pd.DataFrame(filtered_rows)

        return filtered_detections

    def arkham_icon_to_text(self, image: Image.Image | str, filtered_detections: pd.DataFrame) -> Image.Image:
        """将检测到的图标转为文本"""
        if isinstance(image, str):
            image = Image.open(image)
        # 转为RGB

        for index, row in filtered_detections.iterrows():
            # 获取图标区域
            name = row['name']
            if name not in self.icon_list:
                continue
            # 截取图标区域
            icon_box = (int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax']))
            icon = image.crop(icon_box)
            # 寻找icon最浅色
            max_pixel = max(icon.getdata())  # 获取最大像素值
            # 生成文本
            text = self.icon_list[name]
            bbox = self.font.getbbox(text)
            # 创建一个bbox大小的透明图片
            text_image = Image.new('RGB',
                                   (int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1]) + 2),
                                   max_pixel)
            # 绘制文本
            draw = ImageDraw.Draw(text_image)
            # 外边框
            draw.text((0, 0), text, font=self.font, fill='black')
            # 将图片缩放到
            text_image = text_image.resize((icon_box[2] - icon_box[0], icon_box[3] - icon_box[1]))

            # 覆盖回原图
            image.paste(text_image, icon_box)
        return image
