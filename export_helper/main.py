import os
import glob
from pathlib import Path
from PIL import Image, ImageDraw
from LamaCleaner import LamaCleaner
import numpy as np


def get_image_files(directory):
    """
    获取指定目录下的所有图片文件

    :param directory: 目录路径
    :return: 图片文件路径列表
    """
    # 支持的图片格式
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif', '*.webp']

    image_files = []
    for extension in image_extensions:
        pattern = os.path.join(directory, '**', extension)
        image_files.extend(glob.glob(pattern, recursive=True))
        # 同时搜索大写扩展名
        pattern_upper = os.path.join(directory, '**', extension.upper())
        image_files.extend(glob.glob(pattern_upper, recursive=True))

    return sorted(list(set(image_files)))  # 去重并排序


def create_output_directory(input_directory):
    """
    在输入目录中创建output文件夹

    :param input_directory: 输入目录路径
    :return: output目录路径
    """
    output_dir = os.path.join(input_directory, 'output')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def preprocess_image_for_target_size(image, target_width, target_height):
    """
    预处理图片以适应目标尺寸：
    - 如果某边大于目标，进行居中裁剪
    - 返回处理后的图片和是否需要进一步出血的标志

    :param image: 输入图片
    :param target_width: 目标宽度
    :param target_height: 目标高度
    :return: (processed_image, needs_outpaint, crop_info)
    """
    current_width, current_height = image.size
    print(f"  预处理分析: 当前尺寸 {current_width}x{current_height} -> 目标尺寸 {target_width}x{target_height}")

    # 检查是否需要裁剪
    needs_crop_width = current_width > target_width
    needs_crop_height = current_height > target_height

    # 检查是否需要出血
    needs_extend_width = current_width < target_width
    needs_extend_height = current_height < target_height

    crop_info = {
        'cropped_width': needs_crop_width,
        'cropped_height': needs_crop_height,
        'original_size': (current_width, current_height)
    }

    processed_image = image.copy()

    # 如果需要裁剪，进行居中裁剪
    if needs_crop_width or needs_crop_height:
        # 计算裁剪后的尺寸
        crop_width = min(current_width, target_width)
        crop_height = min(current_height, target_height)

        # 计算居中裁剪的位置
        left = (current_width - crop_width) // 2
        top = (current_height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height

        processed_image = processed_image.crop((left, top, right, bottom))
        print(f"  执行居中裁剪: {current_width}x{current_height} -> {crop_width}x{crop_height}")
        print(f"  裁剪区域: left={left}, top={top}, right={right}, bottom={bottom}")

    # 检查是否还需要出血
    final_width, final_height = processed_image.size
    needs_outpaint = (final_width < target_width) or (final_height < target_height)

    if needs_outpaint:
        print(f"  仍需出血: {final_width}x{final_height} -> {target_width}x{target_height}")
    else:
        print(f"  无需出血: 已达到目标尺寸 {final_width}x{final_height}")

    return processed_image, needs_outpaint, crop_info


def create_corner_mask(image_size, original_size, corner='top-left', scale_factor=1.5):
    """
    创建角落区域的蒙版，用于二次擦除优化
    基于实际出血区域尺寸计算，并按比例扩大

    :param image_size: 出血后图片的尺寸 (width, height)
    :param original_size: 原始图片的尺寸 (width, height)
    :param corner: 角落位置 ('top-left', 'top-right', 'bottom-left', 'bottom-right')
    :param scale_factor: 蒙版扩大倍数，默认1.5倍
    :return: PIL.Image 蒙版对象 (白色=需要修复区域, 黑色=保留区域)
    """
    target_width, target_height = image_size
    orig_width, orig_height = original_size

    # 计算原图在出血图中的居中位置
    x_offset = (target_width - orig_width) // 2
    y_offset = (target_height - orig_height) // 2

    # 计算实际出血区域的尺寸
    left_bleed = x_offset  # 左侧出血宽度
    right_bleed = target_width - (x_offset + orig_width)  # 右侧出血宽度
    top_bleed = y_offset  # 顶部出血高度
    bottom_bleed = target_height - (y_offset + orig_height)  # 底部出血高度

    print(f"  出血区域分析: 左={left_bleed}px, 右={right_bleed}px, 顶={top_bleed}px, 底={bottom_bleed}px")

    # 创建黑色背景蒙版 (黑色=不修复)
    mask = Image.new('L', image_size, color=0)
    draw = ImageDraw.Draw(mask)

    if corner == 'top-left' and left_bleed > 0 and top_bleed > 0:
        # 左上角：基于实际出血区域计算蒙版尺寸并扩大
        base_mask_width = left_bleed
        base_mask_height = top_bleed

        # 按比例扩大，但不能超出图像边界
        mask_width = min(int(base_mask_width * scale_factor), target_width // 2)
        mask_height = min(int(base_mask_height * scale_factor), target_height // 2)

        # 确保蒙版不会覆盖到原图区域的核心部分
        max_allowed_width = x_offset + orig_width // 4  # 最多延伸到原图1/4处
        max_allowed_height = y_offset + orig_height // 4

        mask_width = min(mask_width, max_allowed_width)
        mask_height = min(mask_height, max_allowed_height)

        # 创建圆角矩形蒙版，圆角半径基于蒙版大小
        corner_radius = 0  # 更小的圆角，避免过度圆润

        # 绘制圆角矩形 (白色=需要修复)
        draw.rounded_rectangle(
            [0, 0, mask_width, mask_height],
            radius=corner_radius,
            fill=255
        )

        print(
            f"  创建左上角蒙版: {mask_width}x{mask_height} (基础:{base_mask_width}x{base_mask_height}, 扩大倍数:{scale_factor}x, 圆角:{corner_radius}px)")

    elif corner == 'top-right' and right_bleed > 0 and top_bleed > 0:
        # 右上角
        base_mask_width = right_bleed
        base_mask_height = top_bleed

        mask_width = min(int(base_mask_width * scale_factor), target_width // 2)
        mask_height = min(int(base_mask_height * scale_factor), target_height // 2)

        # 限制最大范围
        max_allowed_width = right_bleed + orig_width // 4
        max_allowed_height = y_offset + orig_height // 4

        mask_width = min(mask_width, max_allowed_width)
        mask_height = min(mask_height, max_allowed_height)

        corner_radius = min(mask_width, mask_height) // 6
        start_x = target_width - mask_width

        draw.rounded_rectangle(
            [start_x, 0, target_width, mask_height],
            radius=corner_radius,
            fill=255
        )

        print(
            f"  创建右上角蒙版: {mask_width}x{mask_height} (基础:{base_mask_width}x{base_mask_height}, 扩大倍数:{scale_factor}x)")

    elif corner == 'bottom-left' and left_bleed > 0 and bottom_bleed > 0:
        # 左下角
        base_mask_width = left_bleed
        base_mask_height = bottom_bleed

        mask_width = min(int(base_mask_width * scale_factor), target_width // 2)
        mask_height = min(int(base_mask_height * scale_factor), target_height // 2)

        # 限制最大范围
        max_allowed_width = x_offset + orig_width // 4
        max_allowed_height = bottom_bleed + orig_height // 4

        mask_width = min(mask_width, max_allowed_width)
        mask_height = min(mask_height, max_allowed_height)

        corner_radius = min(mask_width, mask_height) // 6
        start_y = target_height - mask_height

        draw.rounded_rectangle(
            [0, start_y, mask_width, target_height],
            radius=corner_radius,
            fill=255
        )

        print(
            f"  创建左下角蒙版: {mask_width}x{mask_height} (基础:{base_mask_width}x{base_mask_height}, 扩大倍数:{scale_factor}x)")

    elif corner == 'bottom-right' and right_bleed > 0 and bottom_bleed > 0:
        # 右下角
        base_mask_width = right_bleed
        base_mask_height = bottom_bleed

        mask_width = min(int(base_mask_width * scale_factor), target_width // 2)
        mask_height = min(int(base_mask_height * scale_factor), target_height // 2)

        # 限制最大范围
        max_allowed_width = right_bleed + orig_width // 4
        max_allowed_height = bottom_bleed + orig_height // 4

        mask_width = min(mask_width, max_allowed_width)
        mask_height = min(mask_height, max_allowed_height)

        corner_radius = min(mask_width, mask_height) // 6
        start_x = target_width - mask_width
        start_y = target_height - mask_height

        draw.rounded_rectangle(
            [start_x, start_y, target_width, target_height],
            radius=corner_radius,
            fill=255
        )

        print(
            f"  创建右下角蒙版: {mask_width}x{mask_height} (基础:{base_mask_width}x{base_mask_height}, 扩大倍数:{scale_factor}x)")

    else:
        print(f"  跳过 {corner}: 该角落无出血区域")

    return mask


def secondary_inpaint_optimization(cleaner, outpainted_image, original_size, corners_to_fix=['top-left'],
                                   scale_factor=1.5):
    """
    对出血图片的指定角落进行二次修复优化

    :param cleaner: LamaCleaner 实例
    :param outpainted_image: 出血后的图片
    :param original_size: 原始图片尺寸
    :param corners_to_fix: 需要修复的角落列表 ['top-left', 'top-right', 'bottom-left', 'bottom-right']
    :param scale_factor: 蒙版扩大倍数
    :return: 优化后的图片
    """
    current_image = outpainted_image.copy()
    image_size = current_image.size

    print(f"  开始二次修复优化，处理角落: {corners_to_fix}, 扩大倍数: {scale_factor}x")

    for corner in corners_to_fix:
        try:
            # 创建角落蒙版
            corner_mask = create_corner_mask(
                image_size=image_size,
                original_size=original_size,
                corner=corner,
                scale_factor=scale_factor
            )

            # 检查蒙版是否有有效区域（是否有白色像素）
            mask_array = np.array(corner_mask)
            white_pixels = np.sum(mask_array > 128)  # 计算白色像素数量

            if white_pixels == 0:
                print(f"  跳过 {corner}: 无出血区域需要修复")
                continue

            print(f"  {corner} 蒙版有效像素: {white_pixels} 个")

            # 保存调试蒙版（可选，用于调试）
            # corner_mask.save(f"debug_mask_{corner}.png")

            # 使用lama-cleaner进行二次修复
            print(f"  正在修复 {corner} 角落...")
            current_image = cleaner.inpaint(
                image=current_image,
                mask=corner_mask
            )
            print(f"  ✓ {corner} 角落修复完成")

        except Exception as e:
            print(f"  ❌ {corner} 角落修复失败: {e}")
            continue

    return current_image


def ensure_exact_target_size(image, target_width, target_height):
    """
    确保图片精确达到目标尺寸
    如果尺寸不匹配，进行最终调整

    :param image: 输入图片
    :param target_width: 目标宽度
    :param target_height: 目标高度
    :return: 调整后的图片
    """
    current_width, current_height = image.size

    if current_width == target_width and current_height == target_height:
        return image

    print(f"  最终尺寸调整: {current_width}x{current_height} -> {target_width}x{target_height}")

    # 如果尺寸不匹配，创建目标尺寸的画布并居中放置
    result_image = Image.new('RGB', (target_width, target_height), color='white')

    # 计算居中位置
    x_offset = (target_width - current_width) // 2
    y_offset = (target_height - current_height) // 2

    # 确保不会超出边界
    if current_width > target_width:
        # 需要裁剪宽度
        crop_left = (current_width - target_width) // 2
        image = image.crop((crop_left, 0, crop_left + target_width, current_height))
        x_offset = 0
        current_width = target_width

    if current_height > target_height:
        # 需要裁剪高度
        crop_top = (current_height - target_height) // 2
        image = image.crop((0, crop_top, current_width, crop_top + target_height))
        y_offset = 0
        current_height = target_height

    # 粘贴到目标画布
    result_image.paste(image, (x_offset, y_offset))

    return result_image


def process_images_batch(input_directory, target_width, target_height, lama_cleaner_url="http://localhost:8080",
                         enable_secondary_fix=True, corners_to_fix=['top-left'], scale_factor=1.5):
    """
    批量处理目录下的所有图片文件

    :param input_directory: 输入目录路径
    :param target_width: 目标宽度
    :param target_height: 目标高度
    :param lama_cleaner_url: lama-cleaner服务地址
    :param enable_secondary_fix: 是否启用二次修复优化
    :param corners_to_fix: 需要修复的角落列表
    :param scale_factor: 蒙版扩大倍数
    """

    print(f"=== 开始批量处理图片 ===")
    print(f"输入目录: {input_directory}")
    print(f"目标尺寸: {target_width}x{target_height}")
    print(f"Lama服务地址: {lama_cleaner_url}")
    print(f"二次修复优化: {'启用' if enable_secondary_fix else '禁用'}")
    if enable_secondary_fix:
        print(f"修复角落: {corners_to_fix}")
        print(f"蒙版扩大倍数: {scale_factor}x")

    # 1. 初始化LamaCleaner
    try:
        cleaner = LamaCleaner(lama_cleaner_url)

        # 2. 检查服务是否在线
        if not cleaner.is_service_online():
            print("警告: lama-cleaner 服务未在线，将使用镜像延伸方法")
            if enable_secondary_fix:
                print("警告: 二次修复优化需要lama-cleaner服务，已自动禁用")
                enable_secondary_fix = False
            use_lama = False
        else:
            print("✓ lama-cleaner 服务在线，将使用AI出血方法")
            use_lama = True

    except Exception as e:
        print(f"初始化LamaCleaner失败: {e}")
        print("将使用镜像延伸方法作为后备")
        cleaner = LamaCleaner("http://dummy")  # 创建一个虚拟实例用于镜像方法
        use_lama = False
        enable_secondary_fix = False

    # 3. 获取所有图片文件
    image_files = get_image_files(input_directory)

    if not image_files:
        print("❌ 在指定目录中未找到任何图片文件")
        return

    print(f"✓ 找到 {len(image_files)} 个图片文件")

    # 4. 创建输出目录
    output_dir = create_output_directory(input_directory)
    print(f"✓ 输出目录: {output_dir}")

    # 5. 批量处理图片
    success_count = 0
    error_count = 0

    for i, image_path in enumerate(image_files, 1):
        try:
            print(f"\n[{i}/{len(image_files)}] 处理: {os.path.basename(image_path)}")

            # 加载原始图片并复制到内存
            with Image.open(image_path) as img:
                original_image = img.copy()
            original_size = original_image.size
            print(f"  原始尺寸: {original_size[0]}x{original_size[1]}")

            # 步骤0：预处理 - 处理裁剪和检查是否需要出血
            preprocessed_image, needs_outpaint, crop_info = preprocess_image_for_target_size(
                original_image, target_width, target_height)

            # 更新处理后的尺寸信息
            processed_size = preprocessed_image.size
            processing_steps = []

            if crop_info['cropped_width'] or crop_info['cropped_height']:
                processing_steps.append("crop")

            # 步骤1：如果需要出血，根据服务状态选择处理方法
            if needs_outpaint:
                processing_steps.append("outpaint")

                if use_lama:
                    # 使用lama-cleaner进行出血
                    processed_image = cleaner.outpaint_extend(
                        original_image=preprocessed_image,
                        target_width=target_width,
                        target_height=target_height,
                    )
                    method_used = "lama"
                else:
                    # 使用镜像延伸方法
                    processed_image = cleaner.outpaint_mirror_extend(
                        original_image=preprocessed_image,
                        target_width=target_width,
                        target_height=target_height
                    )
                    method_used = "mirror"

                print(f"  ✓ 出血处理完成，方法: {method_used}")
            else:
                # 不需要出血，直接使用预处理的图片
                processed_image = preprocessed_image
                method_used = "direct"
                print(f"  ✓ 无需出血，直接使用预处理结果")

            # 步骤2：如果启用二次修复且使用lama方法且进行了出血，进行角落优化
            if enable_secondary_fix and use_lama and needs_outpaint:
                processing_steps.append("optimize")
                print(f"  开始二次修复优化...")
                processed_image = secondary_inpaint_optimization(
                    cleaner=cleaner,
                    outpainted_image=processed_image,
                    original_size=processed_size,  # 使用预处理后的尺寸作为原始尺寸
                    corners_to_fix=corners_to_fix,
                    scale_factor=scale_factor
                )
                method_used += "_optimized"
                print(f"  ✓ 二次修复优化完成")

            # 步骤3：确保最终尺寸精确匹配目标
            processed_image = ensure_exact_target_size(processed_image, target_width, target_height)

            # 生成输出文件名
            input_filename = Path(image_path).stem
            input_extension = Path(image_path).suffix.lower()

            # 如果原始文件不是PNG，统一输出为PNG以保证质量
            if input_extension not in ['.png']:
                output_extension = '.png'
            else:
                output_extension = input_extension

            # 添加处理步骤信息到文件名
            steps_info = "_".join(processing_steps) if processing_steps else "nochange"
            output_filename = f"{input_filename}_{method_used}_{steps_info}_{target_width}x{target_height}{output_extension}"
            output_path = os.path.join(output_dir, output_filename)

            # 保存处理后的图片
            processed_image.save(output_path, quality=95, optimize=True)

            print(f"  ✓ 成功处理并保存到: {output_filename}")
            print(f"  最终尺寸: {processed_image.size[0]}x{processed_image.size[1]}")
            print(f"  处理步骤: {' -> '.join(processing_steps) if processing_steps else '无需处理'}")
            success_count += 1

        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            error_count += 1
            continue

    # 6. 输出处理结果统计
    print(f"\n=== 批量处理完成 ===")
    print(f"成功处理: {success_count} 个文件")
    print(f"处理失败: {error_count} 个文件")
    print(f"输出目录: {output_dir}")


def main():
    """
    主函数 - 配置参数并执行批量处理
    """
    # ===========================================
    # 配置区域 - 根据需要修改以下参数
    # ===========================================

    # 1. 输入目录（包含要处理的图片文件）
    INPUT_DIRECTORY = r"C:\Users\xziyi\Desktop\出血牌框\工作区"  # 修改为您的图片目录路径

    # 2. 目标尺寸配置
    TARGET_WIDTH = 768  # 目标宽度
    TARGET_HEIGHT = 1087  # 目标高度

    # 3. lama-cleaner服务地址
    LAMA_CLEANER_URL = "http://localhost:8080"

    # 4. 二次修复优化配置
    ENABLE_SECONDARY_FIX = True  # 是否启用二次修复优化
    CORNERS_TO_FIX = ['top-left']  # 需要修复的角落，可选: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    SCALE_FACTOR = 1.5  # 蒙版扩大倍数，基于实际出血区域的倍数 (推荐 1.2-2.0)

    # ===========================================

    # 检查输入目录是否存在
    if not os.path.exists(INPUT_DIRECTORY):
        print(f"❌ 输入目录不存在: {INPUT_DIRECTORY}")
        print("请确保目录路径正确，或者创建该目录并放入图片文件")
        return

    # 执行批量处理
    try:
        process_images_batch(
            input_directory=INPUT_DIRECTORY,
            target_width=TARGET_WIDTH,
            target_height=TARGET_HEIGHT,
            lama_cleaner_url=LAMA_CLEANER_URL,
            enable_secondary_fix=ENABLE_SECONDARY_FIX,
            corners_to_fix=CORNERS_TO_FIX,
            scale_factor=SCALE_FACTOR
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了处理过程")
    except Exception as e:
        print(f"\n❌ 处理过程中发生错误: {e}")


if __name__ == "__main__":
    # 运行示例和说明
    print("LamaCleaner 批量图片处理工具 (含智能二次修复优化)")
    print("=" * 60)
    print()
    print("使用说明:")
    print("1. 确保lama-cleaner服务正在运行（如需AI出血和二次修复）")
    print("2. 修改main()函数中的配置参数")
    print("3. 运行此脚本")
    print("4. 处理后的图片将保存在输入目录下的output文件夹中")
    print()
    print("新增功能:")
    print("- 智能预处理：自动处理裁剪和出血的混合情况")
    print("- 精确尺寸控制：确保最终输出精确匹配目标尺寸")
    print("- 居中裁剪：当图片某边超出目标时，自动进行居中裁剪")
    print("- 详细处理日志：显示每个处理步骤的详细信息")
    print()
    print("二次修复优化特性:")
    print("- 基于实际出血区域计算蒙版大小")
    print("- 可配置扩大倍数（默认1.5倍）")
    print("- 智能边界限制，避免过度修复原图区域")
    print("- 详细的处理日志，便于调试和优化")
    print("- 圆角蒙版设计，避免生硬的修复边界")
    print()
    print("支持的图片格式: JPG, JPEG, PNG, BMP, TIFF, WEBP")
    print()

    # 执行主程序
    main()
