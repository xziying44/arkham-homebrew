import io

import numpy as np  # 导入 numpy 用于高效的数组操作
import requests
from PIL import Image


class LamaCleaner:
    """
    一个用于与 lama-cleaner HTTP API 交互的 Python 客户端。
    """

    def __init__(self, base_url: str):
        """
        初始化客户端。

        :param base_url: lama-cleaner 服务器的 HTTP 地址, 例如: http://localhost:8080
        """
        if not base_url:
            raise ValueError("base_url 不能为空")

        # 如果 URL 以斜杠结尾，则移除它
        self.base_url = base_url.rstrip('/')
        self.inpaint_url = f"{self.base_url}/inpaint"

    def set_base_url(self, base_url: str):
        """
        设置新的 base_url 并更新相关的 URL 端点。

        :param base_url: 新的 lama-cleaner 服务器的 HTTP 地址
        :raises ValueError: 如果 base_url 为空
        """
        if not base_url:
            raise ValueError("base_url 不能为空")

        # 如果 URL 以斜杠结尾，则移除它
        self.base_url = base_url.rstrip('/')
        self.inpaint_url = f"{self.base_url}/inpaint"
        print(f"Base URL 已更新为: {self.base_url}")

    def is_service_online(self, timeout: int = 5) -> bool:
        """
        检查 lama-cleaner 服务是否在线。

        :param timeout: 请求超时时间（秒），默认为5秒
        :return: 如果服务在线返回 True，否则返回 False
        """
        try:
            # 尝试访问服务器根路径
            response = requests.get(self.base_url, timeout=timeout)
            # 如果状态码是 200-299 范围内，认为服务在线
            if response.status_code < 400:
                print(f"✓ lama-cleaner 服务在线 (状态码: {response.status_code})")
                return True
            else:
                print(f"✗ lama-cleaner 服务响应异常 (状态码: {response.status_code})")
                return False

        except requests.exceptions.ConnectionError:
            print(f"✗ 无法连接到 lama-cleaner 服务: {self.base_url}")
            return False
        except requests.exceptions.Timeout:
            print(f"✗ 连接 lama-cleaner 服务超时 (超过 {timeout} 秒)")
            return False
        except Exception as e:
            print(f"✗ 检查服务状态时发生错误: {e}")
            return False

    def inpaint(self, image: Image.Image, mask: Image.Image, **kwargs) -> Image.Image:
        """
        调用 lama-cleaner 的 /inpaint 接口进行图像修复。

        :param image: PIL.Image 对象，表示原始图像。
        :param mask: PIL.Image 对象，表示蒙版。白色区域为需要修复的部分。
        :param kwargs: 其他可选的 API 参数，用于覆盖默认值。
                       例如: hdStrategy="Crop", ldmSteps=30 等。
        :return: PIL.Image 对象，表示修复后的图像。
        :raises: requests.exceptions.RequestException: 如果网络请求失败。
                 ValueError: 如果服务器返回错误。
        """
        # 将 PIL Image 对象转换为内存中的二进制数据
        image_buffer = io.BytesIO()
        image.save(image_buffer, format='PNG')
        image_buffer.seek(0)  # 重置指针到文件开头

        mask_buffer = io.BytesIO()
        # lama-cleaner 需要一个单通道的灰度图作为mask
        mask.convert('L').save(mask_buffer, format='PNG')
        mask_buffer.seek(0)

        # 准备 multipart/form-data
        files = {
            'image': ('image.png', image_buffer, 'image/png'),
            'mask': ('mask.png', mask_buffer, 'image/png')
        }

        # 从浏览器抓包获得的默认参数
        # 您可以在调用 inpaint 方法时通过 kwargs 来覆盖它们
        form_data = {
            'ldmSteps': 25,
            'ldmSampler': 'plms',
            'zitsWireframe': 'true',  # bools需要转为字符串 'true'/'false'
            'hdStrategy': 'Crop',
            'hdStrategyCropMargin': 196,
            'hdStrategyCropTrigerSize': 800,
            'hdStrategyResizeLimit': 2048,
            'prompt': '',
            'negativePrompt': '',
            'croperX': 0,  # 默认值可能需要根据实际情况调整，这里设为0
            'croperY': 0,
            'croperHeight': 512,
            'croperWidth': 512,
            'useCroper': 'false',
            'sdMaskBlur': 5,
            'sdStrength': 0.75,
            'sdSteps': 50,
            'sdGuidanceScale': 7.5,
            'sdSampler': 'uni_pc',
            'sdSeed': -1,
            'sdMatchHistograms': 'false',
            'sdScale': 1,
            'cv2Radius': 5,
            'cv2Flag': 'INPAINT_NS',
            'paintByExampleSteps': 50,
            'paintByExampleGuidanceScale': 7.5,
            'paintByExampleSeed': -1,
            'paintByExampleMaskBlur': 5,
            'paintByExampleMatchHistograms': 'false',
            'p2pSteps': 50,
            'p2pImageGuidanceScale': 1.5,
            'p2pGuidanceScale': 7.5,
            'controlnet_conditioning_scale': 0.4,
            'controlnet_method': 'control_v11p_sd15_canny',
        }

        # 使用用户传入的参数更新默认值
        # 注意：所有值都需要是字符串类型，特别是布尔值要转为 'true'/'false'
        for key, value in kwargs.items():
            if isinstance(value, bool):
                form_data[key] = str(value).lower()
            else:
                form_data[key] = str(value)

        try:
            response = requests.post(self.inpaint_url, files=files, data=form_data)
            # 确认请求是否成功
            response.raise_for_status()

            # 将返回的二进制图像数据转换为 PIL Image 对象
            result_image = Image.open(io.BytesIO(response.content))
            return result_image

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP 错误: {http_err}")
            print(f"服务器响应内容: {response.text}")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"网络请求错误: {req_err}")
            raise

    def outpaint_extend(self, original_image: Image.Image, target_width: int, target_height: int,
                        **kwargs) -> Image.Image:
        """
        扩展方法：使用 lama-cleaner API 自动创建源图和mask图进行出血处理。

        :param original_image: PIL.Image 对象，表示原始图像。
        :param target_width: 目标图像的宽度。
        :param target_height: 目标图像的高度。
        :param kwargs: 其他可选的 API 参数，传递给 inpaint 方法。
        :return: PIL.Image 对象，表示扩展后的图像。
        :raises: ValueError: 如果目标尺寸小于原图尺寸。
        """
        # 获取原图尺寸
        orig_width, orig_height = original_image.size

        # 验证目标尺寸
        if target_width < orig_width or target_height < orig_height:
            raise ValueError(f"目标尺寸 ({target_width}x{target_height}) 不能小于原图尺寸 ({orig_width}x{orig_height})")

        # 如果尺寸相同，直接返回原图
        if target_width == orig_width and target_height == orig_height:
            print("目标尺寸与原图相同，无需处理。")
            return original_image.copy()

        # 计算居中位置坐标（如果差值为奇数，忽略小数点）
        x_offset = (target_width - orig_width) // 2
        y_offset = (target_height - orig_height) // 2

        # 1. 创建黑色背景底图
        base_image = Image.new('RGB', (target_width, target_height), color=(0, 0, 0))

        # 2. 将原图粘贴到底图的居中位置
        base_image.paste(original_image, (x_offset, y_offset))

        # 3. 创建mask图像
        # 创建一个白色背景的mask（白色区域将被修复）
        mask_image = Image.new('L', (target_width, target_height), color=255)  # 白色背景

        # 在mask上创建黑色区域，对应原图的位置（黑色区域不会被修复）
        mask_black_region = Image.new('L', (orig_width, orig_height), color=0)  # 黑色区域
        mask_image.paste(mask_black_region, (x_offset, y_offset))

        # 4. 调用inpaint方法进行出血处理
        print("正在使用 lama-cleaner API进行扩展...")
        result = self.inpaint(base_image, mask_image, **kwargs)
        return result

    # --- 新增方法开始 ---
    @staticmethod
    def outpaint_mirror_extend(original_image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        使用镜像延伸的方式扩展图像，不调用 lama-cleaner API。
        此方法通过反射图像边缘的像素来填充扩展区域。

        :param original_image: PIL.Image 对象，表示原始图像。
        :param target_width: 目标图像的宽度。
        :param target_height: 目标图像的高度。
        :return: PIL.Image 对象，表示扩展后的图像。
        :raises: ValueError: 如果目标尺寸小于原图尺寸。
        """
        # 获取原图尺寸
        orig_width, orig_height = original_image.size

        # 验证目标尺寸
        if target_width < orig_width or target_height < orig_height:
            raise ValueError(f"目标尺寸 ({target_width}x{target_height}) 不能小于原图尺寸 ({orig_width}x{orig_height})")

        # 如果尺寸相同，直接返回原图
        if target_width == orig_width and target_height == orig_height:
            print("目标尺寸与原图相同，无需处理。")
            return original_image.copy()

        # 计算需要填充的边距
        pad_width_total = target_width - orig_width
        pad_height_total = target_height - orig_height

        # 将边距分配到两侧，处理奇数边距的情况
        pad_left = pad_width_total // 2
        pad_right = pad_width_total - pad_left
        pad_top = pad_height_total // 2
        pad_bottom = pad_height_total - pad_top

        # 将 PIL Image 转换为 numpy 数组以便进行高效处理
        image_array = np.array(original_image)

        # 定义填充规则。对于彩色图(3维)和灰度图(2维)分别处理
        if image_array.ndim == 3:  # 彩色图 (height, width, channels)
            pad_spec = ((pad_top, pad_bottom), (pad_left, pad_right), (0, 0))
        elif image_array.ndim == 2:  # 灰度图 (height, width)
            pad_spec = ((pad_top, pad_bottom), (pad_left, pad_right))
        else:
            raise ValueError(f"不支持的图像维度: {image_array.ndim}。只支持彩色和灰度图。")

        # 使用 numpy.pad 进行镜像填充 ('reflect' 模式)
        print("正在使用镜像延伸方式进行扩展...")
        padded_array = np.pad(image_array, pad_width=pad_spec, mode='reflect')

        # 将处理后的 numpy 数组转换回 PIL Image
        result_image = Image.fromarray(padded_array)

        return result_image
    # --- 新增方法结束 ---


if __name__ == "__main__":
    # --- 准备工作 ---
    LAMA_CLEANER_URL = "http://localhost:8080"

    try:
        # 1. 初始化客户端
        cleaner = LamaCleaner(LAMA_CLEANER_URL)

        # 2. 检查服务是否在线 (lama-cleaner出血时需要)
        is_online = cleaner.is_service_online()
        if not is_online:
            print("提示：lama-cleaner 服务未在线，outpaint_extend 方法将无法使用。")

        # 3. 示例：更改服务地址（如果需要）
        # cleaner.set_base_url("http://192.168.1.100:8080")
        # cleaner.is_service_online()  # 检查新地址是否可用

        # --- 加载原始图片 ---
        try:
            original_image = Image.open('000174-raw.jpg')
        except FileNotFoundError:
            print("错误: 未找到 '000174-raw.jpg'。请确保当前目录下有此文件。")
            print("将创建一个 200x300 的示例图片用于测试。")
            original_image = Image.new('RGB', (200, 300), color='blue')
            original_image.paste(Image.new('RGB', (100, 150), color='red'), (50, 75))
            original_image.save("000174-raw.jpg")

        target_w, target_h = 821, 1121

        # --- 4. 测试 lama-cleaner 的扩展方法 (如果服务在线) ---
        if is_online:
            print(f"\n--- 测试 lama-cleaner 扩展方法 (目标尺寸: {target_w}x{target_h}) ---")
            lama_result = cleaner.outpaint_extend(
                original_image=original_image,
                target_width=target_w,
                target_height=target_h
            )
            if lama_result:
                lama_result.save("outpaint_lama_result.png")
                print("Lama 扩展成功！结果已保存为 'outpaint_lama_result.png'")
        else:
            print("\n--- 跳过 lama-cleaner 扩展测试 (服务离线) ---")

        # --- 5. 测试新的镜像延伸方法 ---
        print(f"\n--- 测试镜像延伸方法 (目标尺寸: {target_w}x{target_h}) ---")
        mirror_result = cleaner.outpaint_mirror_extend(
            original_image=original_image,
            target_width=target_w,
            target_height=target_h
        )
        if mirror_result:
            mirror_result.save("outpaint_mirror_result.png")
            print("镜像延伸成功！结果已保存为 'outpaint_mirror_result.png'")


    except requests.exceptions.ConnectionError:
        print(f"连接失败: 无法连接到 {LAMA_CLEANER_URL}。请确保 lama-cleaner 服务正在运行。")
    except Exception as e:
        print(f"发生了一个未知错误: {e}")
