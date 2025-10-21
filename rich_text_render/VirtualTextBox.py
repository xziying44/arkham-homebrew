# VirtualTextBox.py
from dataclasses import dataclass
from typing import List, Tuple, Union, Optional

from PIL import Image
from PIL.ImageFont import FreeTypeFont


@dataclass
class TextObject:
    """文本对象"""
    text: str
    font: FreeTypeFont
    font_name: str
    font_size: float
    height: int
    width: int
    color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]
    border_width: int = 0
    border_color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = "#000000"
    offset_x: int = 0
    offset_y: int = 0

    def __post_init__(self):
        self.color = self._convert_color(self.color)
        self.border_color = self._convert_color(self.border_color)

    @staticmethod
    def _convert_color(color) -> str:
        """将颜色转换为十六进制字符串格式"""
        if isinstance(color, (tuple, list)):
            if len(color) == 3:  # RGB
                r, g, b = color
                return f"#{r:02x}{g:02x}{b:02x}"
            elif len(color) == 4:  # RGBA
                r, g, b, a = color
                return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
        return color  # 如果已经是字符串格式，直接返回


@dataclass
class ImageObject:
    """图片对象"""
    image: Image.Image
    height: int
    width: int


@dataclass
class FlexObject:
    """动态flex对象，用于占用剩余空间"""
    y: int = 0  # 在get_render_list时会被重新计算


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
            padding: 全局内边距
            paragraph_spacing: 段落间距，默认为行间距的三分之一
        """
        self.polygon_vertices: List[Tuple[int, int]] = polygon_vertices
        self.default_line_spacing: int = default_line_spacing
        self.padding: int = padding
        if paragraph_spacing is None:
            self.paragraph_spacing: int = default_line_spacing // 3
        else:
            self.paragraph_spacing: int = paragraph_spacing

        self.min_y = min(v[1] for v in polygon_vertices)
        self.max_y = max(v[1] for v in polygon_vertices)

        self.cursor_y: int = self.min_y + padding
        self.cursor_x: int = 0
        self.render_list: List[RenderItem] = []
        self.flex_list: List[FlexObject] = []
        self.drawn_lines: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []

        self.current_line_left: int = 0
        self.current_line_right: int = 0
        self.current_line_height: int = 0

        # --- 用于行居中状态的属性 ---
        self._is_line_centering_enabled: bool = False

        # --- 用于辅助线状态的属性 ---
        self._guide_lines_active: bool = False
        self._guide_line_segments: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []

        self.line_padding: int = 0
        self.use_line_padding: bool = False

        self.cannot_be_line_start = {'。', '，', '！', '？', '；', '：', ')', '）', '、',
                                     '}', '】', '>', '》', '.', '!', '?', ',', '”'}
        self.cannot_be_line_end = {'(', '（', '{', '【', '<', '《', '“'}

        self._update_line_bounds()
        self.cursor_x = self.current_line_left

    # --- 设置行居中方法 ---
    def set_line_center(self) -> None:
        """
        启用行居中模式。
        启用后，当一行因内容超出而自动换行时，该行的所有对象将被水平居中。
        此设置会持续生效，直到调用 cancel_line_center。
        """
        self._is_line_centering_enabled = True

    # --- 取消行居中方法 ---
    def cancel_line_center(self) -> None:
        """
        取消行居中模式。
        调用此方法会立即对当前行（光标所在的行）的内容进行居中处理，
        并将光标移动到居中后最后一个对象的右侧。
        后续添加的对象将不再居中。
        """
        if self._is_line_centering_enabled:
            # 在关闭标志之前，对当前行执行一次居中操作
            self._recenter_current_line()
        self._is_line_centering_enabled = False

    # --- 辅助线方法 ---
    def _add_guide_segment_for_line(self, line_y: int, line_left: int, line_height: int):
        """
        内部辅助方法，用于为给定行的属性计算并添加辅助线段。
        """
        # 计算用于绘制的行高，确保空行也有最小高度
        line_height_for_calc = max(line_height, self.default_line_spacing)
        # 垂直延伸量，确保线条无缝连接
        vertical_extension = 0
        # 辅助线的水平位置，位于内容区域左侧10像素处
        guide_x = line_left - 18

        # 创建第一条垂直线段
        p1_start = (guide_x, line_y - vertical_extension)
        p1_end = (guide_x, line_y + line_height_for_calc + vertical_extension)
        self._guide_line_segments.append((p1_start, p1_end))

        # 创建第二条垂直线段（在第一条右侧6像素处）
        p2_start = (guide_x + 6, line_y - vertical_extension)
        p2_end = (guide_x + 6, line_y + line_height_for_calc + vertical_extension)
        self._guide_line_segments.append((p2_start, p2_end))

    def set_guide_lines(self) -> None:
        """
        设置辅助线。

        启用后，系统将为每一新行文本生成两条垂直的辅助线，从当前行开始，
        位置在文本边界左侧10像素处。这将清除任何先前生成的辅助线。
        一行的辅助线是在该行完成时（即发生换行或调用 `cancel_guide_lines` 时）生成的。
        """
        self._guide_lines_active = True

    def cancel_guide_lines(self) -> None:
        """
        取消辅助线，并最终确定当前行的辅助线。

        如果辅助线处于激活状态，此方法将为当前行生成辅助线段，
        从而结束辅助线的绘制过程。后续的新行将不再有辅助线。
        """
        if self._guide_lines_active:
            # 为请求取消的当前行添加最后的线段
            self._add_guide_segment_for_line(
                self.cursor_y, self.current_line_left, self.current_line_height
            )
        self._guide_lines_active = False

    def get_guide_line_segments(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        返回已生成的辅助线线段列表。

        列表中的每一项都是一个 `((x1, y1), (x2, y2))` 元组，用于绘制一条线。
        注意：如果辅助线仍处于活动状态，此方法不会包含当前未最终确定的行的线段。
        在调用此方法之前，请调用 `cancel_guide_lines` 以最终确定最后一个线段。
        """
        # ==================== BUG修复 ====================
        return self._guide_line_segments
        # ===============================================

    def get_drawn_lines(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        返回通过 `draw_line_to_end` 方法添加的所有用户绘制线条的列表。

        列表中的每一项都是一个 ((x1, y1), (x2, y2)) 元组，代表一条线段。
        """
        return self.drawn_lines

    # --- 实际执行居中操作的私有方法 ---
    def _recenter_current_line(self) -> None:
        """
        将当前行的所有对象（RenderItem）在其可用空间内水平居中。
        同时更新光标x坐标到行尾。
        """
        items_on_line = []
        if not self.render_list:
            return  # 如果没有渲染项，则无需操作

        # 当前行的y坐标就是光标的y坐标
        line_y = self.cursor_y

        # 从后向前遍历render_list，收集所有在当前行的项
        for i in range(len(self.render_list) - 1, -1, -1):
            item = self.render_list[i]
            if item.y == line_y:
                # 插入到列表开头以保持原始顺序
                items_on_line.insert(0, item)
            else:
                # 已经遍历到上一行，停止搜索
                break

        if not items_on_line:
            return  # 当前行没有对象，无需操作

        # 计算行内所有对象的总宽度
        total_content_width = sum(item.obj.width for item in items_on_line)
        # 获取当前行的可用宽度
        available_width = self.current_line_right - self.current_line_left

        # 计算居中所需的左边距
        if available_width > total_content_width:
            offset = (available_width - total_content_width) / 2
            current_x = self.current_line_left + offset
        else:
            # 如果内容本身比可用空间还宽（不太可能，但作为保护），则左对齐
            current_x = self.current_line_left

        # 重新定位该行上的每一个对象
        for item in items_on_line:
            item.x = round(current_x)
            current_x += item.obj.width

        # 更新光标位置到最后一个对象之后
        self.cursor_x = round(current_x)

    def _update_line_bounds(self) -> None:
        if self.cursor_y >= self.max_y - self.padding:
            self.current_line_left = 0
            self.current_line_right = 0
            return

        line_height = max(self.current_line_height, self.default_line_spacing)

        base_left, base_right = self._calculate_horizontal_bounds(
            self.polygon_vertices,
            self.cursor_y,
            self.cursor_y + line_height,
            self.padding
        )

        if self.use_line_padding:
            final_left = base_left + self.line_padding
            final_right = base_right - self.line_padding
            if final_left >= final_right:
                self.current_line_left = base_left
                self.current_line_right = base_right
            else:
                self.current_line_left = final_left
                self.current_line_right = final_right
        else:
            self.current_line_left = base_left
            self.current_line_right = base_right

    def _move_to_next_line(self, obj_height: int = 0, extra_spacing: int = 0) -> bool:
        """移动到下一行，返回是否成功"""
        # 在移动到下一行之前，检查是否需要居中当前行
        if self._is_line_centering_enabled:
            self._recenter_current_line()

        # 如果辅助线功能已激活，为即将离开的行记录线段
        if self._guide_lines_active:
            self._add_guide_segment_for_line(
                self.cursor_y, self.current_line_left, self.current_line_height
            )

        base_y_jump = max(self.current_line_height, self.default_line_spacing)
        total_y_jump = base_y_jump + extra_spacing
        next_y = self.cursor_y + total_y_jump
        next_line_height = max(obj_height, self.default_line_spacing)

        if next_y + next_line_height > self.max_y - self.padding:
            return False

        self.cursor_y = next_y
        self.current_line_height = 0

        self._update_line_bounds()
        self.cursor_x = self.current_line_left
        return True

    def set_line_padding(self, padding: int) -> bool:
        if padding < 0:
            return False
        self.line_padding = padding
        self.use_line_padding = True
        self._update_line_bounds()
        if self.current_line_left >= self.current_line_right:
            self.use_line_padding = False
            self.line_padding = 0
            self._update_line_bounds()
            return False
        if self.cursor_x < self.current_line_left:
            self.cursor_x = self.current_line_left
        return True

    def cancel_line_padding(self) -> None:
        self.use_line_padding = False
        self.line_padding = 0

    def _can_fit_in_current_line(self, obj_width: int) -> bool:
        return self.cursor_x + obj_width <= self.current_line_right

    def _can_fit_vertically(self, obj_height: int) -> bool:
        return self.cursor_y + obj_height <= self.max_y - self.padding

    def _can_fit_next_line(self, obj_height: int) -> bool:
        next_line_height = max(obj_height, self.default_line_spacing)
        next_y = self.cursor_y + max(self.current_line_height, self.default_line_spacing)
        return next_y + next_line_height <= self.max_y - self.padding

    def newline(self) -> bool:
        return self._move_to_next_line()

    def new_paragraph(self, spacing: Optional[int] = None) -> bool:
        para_spacing = spacing if spacing is not None else self.paragraph_spacing
        return self._move_to_next_line(extra_spacing=para_spacing)

    def draw_line_to_end(self, v_align: str = 'center') -> bool:
        """
        从当前光标位置绘制一条线到行尾，不换行。

        这条线是一个装饰性元素，它会消耗掉当前行剩余的水平空间，
        但不会影响行高或参与对象流式布局。
        线条被添加到单独的列表中，可以通过 `get_drawn_lines` 获取。

        Args:
            v_align (str): 线条在当前行框内的垂直对齐方式。
                           可选值为 'top', 'center', 'bottom'。
                           'top': 线条位于行框顶部。
                           'center': 线条位于行框中部。
                           'bottom': 线条位于行框底部。

        Returns:
            bool: 如果成功添加线条，返回 True；如果当前行没有剩余空间，返回 False。
        """
        start_x = self.cursor_x
        end_x = self.current_line_right

        # 如果光标已在行尾或超出，则没有空间绘制
        if start_x >= end_x:
            return False

        # 计算当前行的有效高度，用于垂直对齐
        # 如果行内已有内容，使用 current_line_height，否则使用默认行距
        line_box_height = self.current_line_height or self.default_line_spacing

        # 根据对齐方式计算线条的垂直位置 (y-coordinate)
        y_pos = 0.0
        if v_align == 'top':
            y_pos = self.cursor_y
        elif v_align == 'bottom':
            y_pos = self.cursor_y + line_box_height
        else:  # 默认为 'center'
            y_pos = self.cursor_y + line_box_height / 2

        y_pos = round(y_pos)

        # 创建线段并添加到列表中
        line_segment = ((start_x, y_pos), (end_x, y_pos))
        self.drawn_lines.append(line_segment)

        # 此操作消耗了行内剩余空间，将光标移动到行尾
        self.cursor_x = end_x

        return True

    def get_current_line_info(self) -> dict:
        return {
            'cursor_x': self.cursor_x,
            'cursor_y': self.cursor_y,
            'line_left': self.current_line_left,
            'line_right': self.current_line_right,
            'line_height': self.current_line_height,
            'available_width': self.current_line_right - self.cursor_x,
            'using_line_padding': self.use_line_padding,
            'line_padding_value': self.line_padding if self.use_line_padding else 0,
            'is_line_centering': self._is_line_centering_enabled,
            'is_guide_lines_active': self._guide_lines_active,
        }

    def _handle_line_start_punctuation(self, obj: TextObject) -> bool:
        if not self.render_list: return False
        items_to_move = []
        last_line_y = self.render_list[-1].y
        for i in range(len(self.render_list) - 1, -1, -1):
            item_on_prev_line = self.render_list[i]
            if item_on_prev_line.y != last_line_y: break
            if not isinstance(item_on_prev_line.obj, TextObject): break
            self.render_list.pop()
            items_to_move.insert(0, item_on_prev_line.obj)
            if item_on_prev_line.obj.text not in self.cannot_be_line_end: break
        if not items_to_move: return False
        all_objects_to_re_push = items_to_move + [obj]
        for item_obj in all_objects_to_re_push:
            if not self.push(item_obj): return False
        return True

    def _handle_line_end_punctuation(self, obj: TextObject) -> bool:
        if not self._move_to_next_line(obj.height): return False
        return self.push(obj)

    def push(self, obj: DrawObject) -> bool:
        if not self._can_fit_vertically(obj.height):
            return False

        self.current_line_height = max(self.current_line_height, obj.height)

        if not self._can_fit_in_current_line(obj.width):
            dangling_objects = self._pop_dangling_punctuation_from_line_end()
            if not self._can_fit_next_line(obj.height):
                return False
            if not self._move_to_next_line(obj.height):
                return False
            new_line_height = obj.height
            for d_obj in dangling_objects:
                new_line_height = max(new_line_height, d_obj.height)
            self.current_line_height = max(self.current_line_height, new_line_height)
            for d_obj in dangling_objects:
                if not self.push(d_obj):
                    return False

        # 检查是否是行首的空格（TextObject且内容为空格且光标在行首）
        if isinstance(obj, TextObject) and self.cursor_x == self.current_line_left:
            # 如果是纯空格文本，直接跳过不渲染
            if obj.text.strip() == '':
                return True

        if isinstance(obj,
                      TextObject) and obj.text in self.cannot_be_line_start and self.cursor_x == self.current_line_left:
            if self._handle_line_start_punctuation(obj):
                return True

        if not self._can_fit_vertically(obj.height):
            return False

        render_item = RenderItem(obj, self.cursor_x + obj.offset_x, self.cursor_y + obj.offset_y)
        self.render_list.append(render_item)
        self.cursor_x += obj.width
        return True

    def _pop_dangling_punctuation_from_line_end(self) -> List[DrawObject]:
        if not self.render_list: return []
        objects_to_move = []
        last_item_y = self.render_list[-1].y
        if self.cursor_y != last_item_y: return []
        for i in range(len(self.render_list) - 1, -1, -1):
            item = self.render_list[i]
            if item.y != self.cursor_y: break
            if isinstance(item.obj, TextObject) and item.obj.text in self.cannot_be_line_end:
                popped_item = self.render_list.pop()
                objects_to_move.insert(0, popped_item.obj)
                self.cursor_x -= popped_item.obj.width
            else:
                break
        return objects_to_move

    def get_render_list(self) -> List[RenderItem]:
        # --- 修改：如果调用时居中是开启的，需要先居中当前未满的行 ---
        # 这是一个重要的行为决策：当获取最终渲染列表时，是否要居中最后一行？
        # 根据您的需求，居中发生在换行或取消时。所以 get_render_list 前应调用
        # newline() 或 cancel_line_center() 来确保最后一行也被处理。
        # 如果希望 get_render_list() 自动处理，可以取消下面的注释。
        # if self._is_line_centering_enabled:
        #     self._recenter_current_line()

        render_list = self.render_list.copy()
        remaining_vertical_distance = self.get_remaining_vertical_distance()
        # 赋予剩余的垂直距离给 flex
        if len(self.flex_list) > 0 and remaining_vertical_distance > 0:
            flex_height = int(remaining_vertical_distance / (len(self.flex_list) + 1))
            for flex in self.flex_list:
                for item_render in render_list:
                    if item_render.y >= flex.y:
                        item_render.y += flex_height
        return render_list

    # ==================== 新增方法 ====================
    def get_remaining_vertical_distance(self) -> int:
        """
        返回最后一行的底部，距离最底部边界线（考虑内边距）的距离，最低为0。

        如果文本框为空，则返回从当前光标位置开始的整个可用高度。
        如果最后一行内容已超出或接触到底部边界，则返回0。

        Returns:
            int: 剩余的垂直距离，最低为0。
        """
        # 计算考虑内边距后的有效底部边界 Y 坐标
        box_bottom_boundary = self.max_y - self.padding

        # 情况1：文本框内没有任何内容
        if not self.render_list:
            # 返回从当前光标（也就是起始位置）到盒子底部的完整距离
            remaining_space = box_bottom_boundary - self.cursor_y
            return max(0, round(remaining_space))

        # 情况2：文本框内有内容
        # 获取最后一行的 Y 坐标（所有在同一行的 RenderItem y值相同）
        last_line_y = self.render_list[-1].y
        max_height_on_last_line = 0

        # 从后向前遍历渲染列表，找到最后一行的所有元素，并计算该行的最大高度
        for item in reversed(self.render_list):
            if item.y == last_line_y:
                max_height_on_last_line = max(max_height_on_last_line, item.obj.height)
            else:
                # 已经遍历到上一行的数据，可以停止搜索
                break

        # 计算最后一行的底部 Y 坐标
        last_line_bottom = last_line_y + max_height_on_last_line

        # 计算最后一行底部到盒子底部的距离
        distance = box_bottom_boundary - last_line_bottom

        # 确保返回值不小于0
        return max(0, round(distance))

    # ==================== 新增方法结束 ====================

    def _calculate_horizontal_bounds(self, vertices: List[Tuple[int, int]],
                                     start_y: float, end_y: float,
                                     padding: int) -> Tuple[int, int]:
        y_min = min(start_y, end_y)
        y_max = max(start_y, end_y)
        intersection_x_coords = []
        valid_edges = []
        vertex_count = len(vertices)
        for i in range(vertex_count):
            _, y1 = vertices[i]
            _, y2 = vertices[(i + 1) % vertex_count]
            edge_y_min = min(y1, y2)
            edge_y_max = max(y1, y2)
            if (y_min <= edge_y_min <= y_max or y_min <= edge_y_max <= y_max or
                    (edge_y_min <= y_min and edge_y_max >= y_max)):
                valid_edges.append((vertices[i], vertices[(i + 1) % vertex_count]))
        for edge in valid_edges:
            point1, point2 = edge
            x1, y1 = point1
            x2, y2 = point2
            edge_y_min = min(y1, y2)
            edge_y_max = max(y1, y2)
            if y1 == y2: continue
            for y in range(int(start_y), int(end_y), 3):
                if edge_y_min < y < edge_y_max:
                    intersection_x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                    intersection_x_coords.append(intersection_x)
        if not intersection_x_coords:
            min_x = min(vertex[0] for vertex in vertices)
            max_x = max(vertex[0] for vertex in vertices)
            return min_x + padding, max_x - padding
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
        if left_bound == 0 and right_bound == 0:
            left_bound = min(intersection_x_coords)
            right_bound = max(intersection_x_coords)
        final_left = left_bound + padding
        final_right = right_bound - padding
        if final_left > final_right:
            min_x = min(vertex[0] for vertex in vertices)
            max_x = max(vertex[0] for vertex in vertices)
            return min_x, max_x
        return round(final_left), round(final_right)

    def add_flex(self):
        """
        添加动态虚拟块
        """
        # 检测指针是否在行首，如果不在立即换行
        if self.cursor_x != self.current_line_left:
            self.newline()
        # 重置当前行指针
        flex_obj = FlexObject(y=self.cursor_y)
        self.flex_list.insert(0, flex_obj)
