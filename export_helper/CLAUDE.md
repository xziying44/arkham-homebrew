[根目录](../CLAUDE.md) > **export_helper**

## Purpose
- 高级导出助手模块，提供图片尺寸规范化与智能出血（Outpainting）能力，用于阿卡姆印牌姬项目的高质量打印导出场景。
- 通过 lama-cleaner 服务进行 AI 出血，并在服务不可用时自动降级为镜像延伸；可选二次角落修复以优化边缘细节。

## Structure
- 入口文件：`main.py` — 批量处理驱动与参数配置（预处理 → 出血/镜像 → 二次修复 → 尺寸校准 → 保存）。
- AI 适配：`LamaCleaner.py` — HTTP 客户端封装 `/inpaint`，以及本地镜像延伸备用实现。
- 包初始化：`__init__.py` — 导出 `LamaCleaner`，提供版本/作者元信息。
- 输出目录：处理结果统一写入输入目录下的 `output/` 子目录，非 PNG 源统一输出为 PNG（质量 95，优化开启）。

## Components
- 函数（`main.py`）：
  - `get_image_files(directory)` — 递归收集支持格式图片。
  - `create_output_directory(input_directory)` — 创建 `output/` 目录。
  - `preprocess_image_for_target_size(image, w, h)` — 大边裁剪+是否需出血判断。
  - `create_corner_mask(image_size, original_size, corner, scale_factor)` — 基于实际出血区域的角落蒙版。
  - `secondary_inpaint_optimization(cleaner, img, original_size, corners_to_fix, scale_factor)` — 二次角落修复。
  - `ensure_exact_target_size(image, w, h)` — 精确对齐到目标尺寸（必要时局部裁剪+居中粘贴）。
  - `process_images_batch(input_directory, w, h, lama_cleaner_url, enable_secondary_fix, corners_to_fix, scale_factor)` — 批处理主流程。
- 类（`LamaCleaner.py`）：
  - `LamaCleaner`：
    - `is_service_online()` — 探测服务可用性。
    - `set_base_url(base_url)` — 动态切换服务地址。
    - `inpaint(image, mask, **kwargs)` — 调用 `/inpaint` 完成修复/出血。
    - `outpaint_extend(original_image, target_width, target_height, **kwargs)` — 自动生成源/蒙版并调用 API 扩展。
    - `outpaint_mirror_extend(original_image, target_width, target_height)` — 不依赖服务的镜像延伸备用方案。

## Dependencies
- Python 库：`Pillow`（图像处理）、`numpy`（数组/镜像填充）、`requests`（HTTP 调用）、`glob`、`pathlib`。
- 外部服务：`lama-cleaner`（默认 `http://localhost:8080`）。
- 支持格式：JPG/JPEG、PNG、BMP、TIFF/TIF、WEBP（大小写扩展名均识别）。

## Integration
- 直接运行：
  - `cd export_helper && python main.py`
  - 在 `main()` 中配置：`INPUT_DIRECTORY`、`TARGET_WIDTH/TARGET_HEIGHT`、`LAMA_CLEANER_URL`、`ENABLE_SECONDARY_FIX`、`CORNERS_TO_FIX`、`SCALE_FACTOR`。
- 作为库调用示例：
  ```python
  from export_helper.main import process_images_batch
  process_images_batch(
      input_directory=r"D:\图片目录",
      target_width=750,
      target_height=1050,
      lama_cleaner_url="http://localhost:8080",
      enable_secondary_fix=True,
      corners_to_fix=['top-left'],
      scale_factor=1.5
  )
  ```
- 服务降级：若 `lama-cleaner` 不可用，自动改用 `outpaint_mirror_extend`，并关闭二次修复（该步骤依赖 API 修复能力）。
- 输出规范：若源非 PNG，统一导出 PNG 以保证质量与一致性；输出命名包含处理方法与步骤标记，便于追踪。

## Notes
- 尺寸策略：当目标尺寸小于原图时，优先执行居中裁剪；最终通过 `ensure_exact_target_size` 严格对齐画布尺寸。
- 二次修复：角落蒙版大小基于实际出血宽高并按倍数放大，包含边界限制以避免“过修复”。
- 性能与稳定性：逐文件异常隔离；详细日志辅助定位；大批量处理建议分批并确保服务端 GPU 资源充足。
- 兼容性：未发现下级子目录 `CLAUDE.md` 文档，当前文档为本目录单层聚合版（来源：代码与配置）。
