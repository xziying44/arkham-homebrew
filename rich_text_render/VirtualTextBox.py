from typing import List, Tuple, Union, Optional
from dataclasses import dataclass
from PIL import Image
from PIL.ImageFont import FreeTypeFont


@dataclass
class TextObject:
    """文本对象"""
    text: str
    font: FreeTypeFont
    height: int
    width: int


@dataclass
class ImageObject:
    """图片对象"""
    image: Image.Image
    height: int
    width: int


@dataclass
class RenderItem:
    """渲染项，包含对象和其左上角坐标"""
    obj: Union[TextObject, ImageObject]
    x: int
    y: int


DrawObject = Union[TextObject, ImageObject]


class VirtualTextBox:
    """虚拟文本框盒子类，用于处理多边形区域内的文本布局"""

    def __init__(
            self,
            polygon_vertices: List[Tuple[int, int]],
            default_line_spacing: int, padding: int = 0,
            paragraph_spacing: Optional[int] = None
    ):
        """
        初始化虚拟文本框

        Args:
            polygon_vertices: 多边形顶点坐标列表
            default_line_spacing: 默认行间距
            padding: 内边距
            paragraph_spacing: 段落间距，默认为行间距的一半
        """
        self.polygon_vertices: List[Tuple[int, int]] = polygon_vertices
        self.default_line_spacing: int = default_line_spacing
        self.padding: int = padding
        # 新增段落间距属性
        if paragraph_spacing is None:
            self.paragraph_spacing: int = default_line_spacing // 3
        else:
            self.paragraph_spacing: int = paragraph_spacing

        # 计算多边形边界
        self.min_y = min(v[1] for v in polygon_vertices)
        self.max_y = max(v[1] for v in polygon_vertices)

        self.cursor_y: int = self.min_y + padding
        line_start_x, _ = self._calculate_horizontal_bounds(
            polygon_vertices,
            self.cursor_y,
            self.cursor_y + default_line_spacing,
            padding)
        self.cursor_x: int = line_start_x
        self.render_list: List[RenderItem] = []

        # 当前行的边界缓存
        self.current_line_left: int = 0
        self.current_line_right: int = 0
        self.current_line_height: int = 0

        # 自定义行边距设置
        self.custom_line_margins: Optional[Tuple[int, int]] = None  # (left_margin, right_margin)
        self.use_custom_margins: bool = False

        # 标点符号规则
        self.cannot_be_line_start = {'。', '，', '！', '？', '；', '：', ')', '）',
                                     '}', '】', '>', '》', '"', "'", '.', '!', '?'}
        self.cannot_be_line_end = {'(', '（', '{', '【', '<', '《', '"', "'"}

        # 初始化第一行边界
        self._update_line_bounds()

    def _update_line_bounds(self) -> None:
        """更新当前行的左右边界"""
        if self.cursor_y >= self.max_y - self.padding:
            self.current_line_left = 0
            self.current_line_right = 0
            return

        # 如果使用自定义边距，直接应用
        if self.use_custom_margins and self.custom_line_margins:
            self.current_line_left = self.custom_line_margins[0]
            self.current_line_right = self.custom_line_margins[1]
            return

        line_height = max(self.current_line_height, self.default_line_spacing)
        self.current_line_left, self.current_line_right = self._calculate_horizontal_bounds(
            self.polygon_vertices,
            self.cursor_y,
            self.cursor_y + line_height,
            self.padding
        )

    def _can_fit_in_current_line(self, obj_width: int) -> bool:
        """检查对象是否能放入当前行"""
        return self.cursor_x + obj_width <= self.current_line_right

    def _can_fit_vertically(self, obj_height: int) -> bool:
        """检查对象是否能在垂直方向放入当前位置"""
        return self.cursor_y + obj_height <= self.max_y - self.padding

    def _can_fit_next_line(self, obj_height: int) -> bool:
        """检查下一行是否能容纳指定高度的对象"""
        next_line_height = max(obj_height, self.default_line_spacing)
        next_y = self.cursor_y + max(self.current_line_height, self.default_line_spacing)
        return next_y + next_line_height <= self.max_y - self.padding

    def _move_to_next_line(self, obj_height: int = 0, extra_spacing: int = 0) -> bool:  # <-- 新增参数
        """移动到下一行，返回是否成功"""
        # 计算基础的Y轴位移（行高 + 行距）
        base_y_jump = max(self.current_line_height, self.default_line_spacing)

        # 加上额外的间距（例如段落间距）
        total_y_jump = base_y_jump + extra_spacing

        next_y = self.cursor_y + total_y_jump
        next_line_height = max(obj_height, self.default_line_spacing)

        # 检查下一行是否能容纳对象
        if next_y + next_line_height > self.max_y - self.padding:
            return False

        self.cursor_y = next_y
        self.current_line_height = 0
        # 换行时重置自定义边距
        self.use_custom_margins = False
        self.custom_line_margins = None
        self._update_line_bounds()
        self.cursor_x = self.current_line_left
        return True

    def newline(self) -> bool:
        """
        强制换行到下一行

        Returns:
            bool: 成功换行返回True，无法换行（已到边界）返回False
        """
        return self._move_to_next_line()

    def new_paragraph(self, spacing: Optional[int] = None) -> bool:
        """
        强制换行并开始一个新段落，会额外增加一段垂直间距。

        Args:
            spacing (Optional[int]): 本次换段的特定间距。如果为 None，则使用默认的段落间距。

        Returns:
            bool: 成功换段返回True，如果空间不足则返回False。
        """
        # 如果用户为本次换段指定了特定间距，则使用它；否则使用类实例的默认值
        para_spacing = spacing if spacing is not None else self.paragraph_spacing

        # 调用我们增强后的核心方法，并传入额外的段落间距
        return self._move_to_next_line(extra_spacing=para_spacing)

    def set_current_line_margins(self, left_margin: int, right_margin: int) -> bool:
        """
        设置当前行的左右边距

        Args:
            left_margin: 左边距（绝对坐标）
            right_margin: 右边距（绝对坐标）

        Returns:
            bool: 设置成功返回True，边距无效返回False
        """
        # 验证边距的有效性
        if left_margin >= right_margin:
            return False

        # 检查边距是否在多边形范围内
        min_x = min(vertex[0] for vertex in self.polygon_vertices)
        max_x = max(vertex[0] for vertex in self.polygon_vertices)

        if left_margin < min_x or right_margin > max_x:
            return False

        # 检查当前光标位置是否还在新的边距范围内
        if self.cursor_x > right_margin:
            return False

        # 应用新的边距设置
        self.custom_line_margins = (left_margin, right_margin)
        self.use_custom_margins = True

        # 更新当前行边界
        self.current_line_left = left_margin
        self.current_line_right = right_margin

        # 如果当前光标位置小于左边距，移动到左边距位置
        if self.cursor_x < left_margin:
            self.cursor_x = left_margin

        return True

    def reset_line_margins(self) -> None:
        """
        重置当前行边距，恢复使用多边形计算的边界
        """
        self.use_custom_margins = False
        self.custom_line_margins = None
        self._update_line_bounds()

        # 确保光标位置在有效范围内
        if self.cursor_x < self.current_line_left:
            self.cursor_x = self.current_line_left
        elif self.cursor_x > self.current_line_right:
            self.cursor_x = self.current_line_right

    def get_current_line_info(self) -> dict:
        """
        获取当前行的信息

        Returns:
            dict: 包含当前行信息的字典
        """
        return {
            'cursor_x': self.cursor_x,
            'cursor_y': self.cursor_y,
            'line_left': self.current_line_left,
            'line_right': self.current_line_right,
            'line_height': self.current_line_height,
            'available_width': self.current_line_right - self.cursor_x,
            'using_custom_margins': self.use_custom_margins,
            'custom_margins': self.custom_line_margins
        }

    def _handle_line_start_punctuation(self, obj: TextObject) -> bool:
        """
        处理不能在行首的标点符号。
        此函数被调用时，光标已经移动到了新行的开头。
        它的任务是从上一行的末尾“借”一个或多个字符到当前行。
        """
        if not self.render_list:
            # 渲染列表为空，无法回溯，让其正常放置
            return False

        # 1. 识别需要从上一行末尾移动到当前行的字符
        items_to_move = []
        last_line_y = self.render_list[-1].y

        # 从后往前遍历渲染列表
        for i in range(len(self.render_list) - 1, -1, -1):
            item_on_prev_line = self.render_list[i]

            # 如果已经不是上一行的内容，停止回溯
            if item_on_prev_line.y != last_line_y:
                break

            # 如果对象不是文本，也停止回溯
            if not isinstance(item_on_prev_line.obj, TextObject):
                break

            # 将上一行的这个字符项弹出，并准备移动
            self.render_list.pop()
            items_to_move.insert(0, item_on_prev_line.obj)  # 插入到开头以保持顺序

            # 检查这个字符是否是“可以作为行末”的字符（例如，不是'('）
            # 如果是，那么我们找到了一个合适的回溯断点，停止回溯
            if item_on_prev_line.obj.text not in self.cannot_be_line_end:
                break

        # 2. 如果没有找到可以移动的字符（比如上一行末尾也是'('），则放弃特殊处理
        if not items_to_move:
            # 恢复被弹出的项（如果有的话），虽然在这种逻辑下items_to_move为空，这里是为了代码健壮性
            # 但因为没找到，所以什么都不用做。就让标点符号留在行首。
            return False

        # 3. 将“借”来的字符和当前的标点符号，重新在当前行进行布局
        all_objects_to_re_push = items_to_move + [obj]

        for item_obj in all_objects_to_re_push:
            # 注意：这里我们直接调用push。由于重新push的字符已经不是在行首了
            # （第一个字符被放上去后，光标就移动了），所以不会导致无限递归。
            if not self.push(item_obj):
                # 如果重新 push 失败，说明空间不足。这是一个需要处理的复杂情况。
                # 简单起见，我们假设它总能成功。
                # 实际项目中可能需要一个更健壮的回滚机制。
                return False

                # 5. 因为我们已经手动处理了obj的push，所以告诉外部的push函数不要再处理了
        return True

    def _handle_line_end_punctuation(self, obj: TextObject) -> bool:
        """处理不能在行末的标点符号"""
        # 直接换行到下一行
        if not self._move_to_next_line(obj.height):
            return False
        return self.push(obj)

    def push(self, obj: DrawObject) -> bool:
        """
        添加绘画对象（重构版，正确处理标点符号规则）

        Args:
            obj: 文本对象或图片对象

        Returns:
            bool: 成功返回True，超过边界返回False
        """
        # 1. 初始垂直空间检查
        if not self._can_fit_vertically(obj.height):
            return False

        # 2. 预更新当前行的高度
        self.current_line_height = max(self.current_line_height, obj.height)

        # 3. 检查是否需要换行
        if not self._can_fit_in_current_line(obj.width):

            # 【关键逻辑】在换行前，检查上一行末尾是否有不应在行末的标点
            dangling_objects = self._pop_dangling_punctuation_from_line_end()

            # 换行
            if not self._can_fit_next_line(obj.height):
                return False  # 下一行也容不下
            if not self._move_to_next_line(obj.height):
                return False

            # 更新换行后的行高
            new_line_height = obj.height
            for d_obj in dangling_objects:
                new_line_height = max(new_line_height, d_obj.height)
            self.current_line_height = max(self.current_line_height, new_line_height)

            # 将“悬挂”的标点符号重新推入到新行
            for d_obj in dangling_objects:
                if not self.push(d_obj):
                    # 如果这里失败，说明逻辑有严重问题，可能需要回滚所有操作
                    return False

        # 4. 【关键逻辑】对象即将被放置，此时检查它是否是“不应在行首”的标点
        # 只有在光标确实在行首时，这个检查才有意义
        if isinstance(obj,
                      TextObject) and obj.text in self.cannot_be_line_start and self.cursor_x == self.current_line_left:
            # 调用行首处理函数，如果它成功处理了，就直接返回True
            if self._handle_line_start_punctuation(obj):
                return True
            # 如果处理失败（比如上一行没东西可借），则按正常流程让它留在行首

        # 5. 放置对象
        # 再次检查垂直空间，因为行首处理可能移动了光标
        if not self._can_fit_vertically(obj.height):
            return False

        render_item = RenderItem(obj, self.cursor_x, self.cursor_y)
        self.render_list.append(render_item)
        self.cursor_x += obj.width

        return True

    def _pop_dangling_punctuation_from_line_end(self) -> List[DrawObject]:
        """
        检查当前行的末尾是否有不应在行末的标点。
        如果有，将它们从render_list中弹出，并返回这些对象。
        同时会正确回退self.cursor_x的位置。
        """
        if not self.render_list:
            return []

        objects_to_move = []
        # 确保我们只检查当前光标所在视觉行
        last_item_y = self.render_list[-1].y
        if self.cursor_y != last_item_y:
            return []

        # 从后往前遍历，寻找所有连续的、不应在行末的标点
        for i in range(len(self.render_list) - 1, -1, -1):
            item = self.render_list[i]
            if item.y != self.cursor_y:
                break  # 已经不是当前行了

            if isinstance(item.obj, TextObject) and item.obj.text in self.cannot_be_line_end:
                # 找到了，弹出它
                popped_item = self.render_list.pop()
                # 插入到列表开头，以保持原始顺序
                objects_to_move.insert(0, popped_item.obj)
                # 【非常重要】光标位置必须回退
                self.cursor_x -= popped_item.obj.width
            else:
                # 碰到一个正常字符，停止寻找
                break

        return objects_to_move

    def get_render_list(self) -> List[RenderItem]:
        """
        获取完整的渲染列表

        Returns:
            List[RenderItem]: 包含所有渲染项的列表
        """
        return self.render_list.copy()

    def _calculate_horizontal_bounds(self, vertices: List[Tuple[int, int]],
                                     start_y: float, end_y: float,
                                     padding: int) -> Tuple[int, int]:
        """
        计算给定Y轴区间内多边形的水平边界（忽略水平边）

        Args:
            vertices: 多边形顶点坐标列表
            start_y: Y轴起始位置
            end_y: Y轴结束位置
            padding: 内边距

        Returns:
            Tuple[int, int]: (左边界x坐标, 右边界x坐标)
        """
        y_min = min(start_y, end_y)
        y_max = max(start_y, end_y)
        intersection_x_coords = []
        valid_edges = []

        # 筛选在有效高度范围内的边
        vertex_count = len(vertices)
        for i in range(vertex_count):
            _, y1 = vertices[i]
            _, y2 = vertices[(i + 1) % vertex_count]
            edge_y_min = min(y1, y2)
            edge_y_max = max(y1, y2)

            # 检查边是否与Y轴区间有交集
            if (y_min <= edge_y_min <= y_max or y_min <= edge_y_max <= y_max or
                    (edge_y_min <= y_min and edge_y_max >= y_max)):
                valid_edges.append((vertices[i], vertices[(i + 1) % vertex_count]))

        # 计算所有有效边与Y轴区间的交点
        for edge in valid_edges:
            point1, point2 = edge
            x1, y1 = point1
            x2, y2 = point2
            edge_y_min = min(y1, y2)
            edge_y_max = max(y1, y2)

            # 跳过水平线段
            if y1 == y2:
                continue

            # 计算交点x坐标
            for y in range(int(start_y), int(end_y), 3):
                if edge_y_min < y < edge_y_max:
                    intersection_x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                    intersection_x_coords.append(intersection_x)

        # 处理无交点的情况
        if not intersection_x_coords:
            min_x = min(vertex[0] for vertex in vertices)
            max_x = max(vertex[0] for vertex in vertices)
            return min_x + padding, max_x - padding

        # 找到最大宽度的区间
        intersection_x_coords.sort()
        left_bound = 0
        right_bound = 0
        max_width = 0

        for i in range(len(intersection_x_coords) - 1):
            current_width = intersection_x_coords[i + 1] - intersection_x_coords[i]
            if current_width > max_width:
                max_width = current_width
                left_bound = intersection_x_coords[i]
                right_bound = intersection_x_coords[i + 1]

        # 如果没有找到有效区间，使用边界值
        if left_bound == 0 and right_bound == 0:
            left_bound = min(intersection_x_coords)
            right_bound = max(intersection_x_coords)

        # 应用内边距
        final_left = left_bound + padding
        final_right = right_bound - padding

        # 处理内边距过大的情况
        if final_left > final_right:
            min_x = min(vertex[0] for vertex in vertices)
            max_x = max(vertex[0] for vertex in vertices)
            return min_x, max_x

        return round(final_left), round(final_right)
