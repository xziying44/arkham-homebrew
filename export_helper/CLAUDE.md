# export_helper

## Purpose and Scope
export_helper 模块用于批量将输入目录内的图片规范化到指定目标尺寸，面向印刷导出场景：
- 通过 `lama-cleaner` 服务执行 AI 出血（Outpainting），在服务不可用时自动降级为本地镜像延伸；
- 支持可选“角落二次修复”以优化边缘细节；
- 统一输出到输入目录下的 `output/` 子目录，保证最终尺寸与格式一致性。
本模块在更大系统中承担“导出前图像整备/扩展”职责，边界为：不生成业务数据、不承担版面排版，仅处理图像尺寸与边缘质量。

## Structure Overview
- 文件组织：
  - `main.py`：批处理驱动与参数配置（预处理 → 出血/镜像 → 二次修复 → 精确尺寸 → 保存）。
  - `LamaCleaner.py`：`lama-cleaner` HTTP 客户端封装（`/inpaint`）与镜像延伸后备实现。
  - `__init__.py`：包元信息与对外导出（`__all__ = ['LamaCleaner']`）。
- 输出约定：所有处理结果写入输入目录内 `output/`；非 PNG 源统一导出为 PNG（质量 95，`optimize=True`）。
- 子目录文档：当前无子目录 `CLAUDE.md`，无需引用。

## Key Components
### 类：LamaCleaner
- 说明：
  - `lama-cleaner` 服务的轻量客户端，封装连通性检测、`/inpaint` 调用与两类扩展（AI 出血、镜像延伸）。
- 责任：
  - 与外部服务交互；在缺省或离线场景提供无服务依赖的镜像延伸替代路径。

#### `__init__(base_url: str) -> None`
- 目的：创建客户端实例并规范化基础 URL。
- 参数：
  • `base_url` (str)：`lama-cleaner` 服务地址（如 `http://localhost:8080`）。
- 返回：(None) 构造函数无返回值。
- 抛出：`ValueError` 当 `base_url` 为空。

#### `set_base_url(base_url: str) -> None`
- 目的：动态更新服务地址。
- 参数：
  • `base_url` (str)：新服务地址。
- 返回：(None)
- 抛出：`ValueError` 当 `base_url` 为空。

#### `is_service_online(timeout: int = 5) -> bool`
- 目的：探测服务可用性（GET 根路径，`status_code < 400` 判定在线）。
- 参数：
  • `timeout` (int)：超时秒数，默认 5。
- 返回：(bool) 在线为 True，否则 False。
- 抛出：内部吞并网络异常，返回 False（记录日志）。

#### `inpaint(image: PIL.Image.Image, mask: PIL.Image.Image, **kwargs) -> PIL.Image.Image`
- 目的：调用 `/inpaint` 执行修复/出血。
- 参数：
  • `image` (PIL.Image.Image)：源图；
  • `mask` (PIL.Image.Image)：蒙版（白=需修复，黑=保留）；
  • `**kwargs`：覆盖默认表单参数（布尔需转 `'true'/'false'`）。
- 返回：(PIL.Image.Image) 修复后的图像。
- 抛出：
  - `requests.exceptions.RequestException` 网络失败；
  - `requests.exceptions.HTTPError` 非 2xx；
  - `ValueError` 服务端返回异常内容时可能抛出。
- 示例：
  ```python
  result = cleaner.inpaint(image, mask, hdStrategy='Crop', sdSteps=30)
  ```

#### `outpaint_extend(original_image: PIL.Image.Image, target_width: int, target_height: int, **kwargs) -> PIL.Image.Image`
- 目的：自动生成底图与蒙版，通过 `/inpaint` 执行“向外扩展”出血；若目标小于原图则先居中裁剪。
- 参数：
  • `original_image` (PIL.Image.Image)：原始图像；
  • `target_width` (int)：目标宽度；
  • `target_height` (int)：目标高度；
  • `**kwargs`：透传给 `inpaint` 的可选参数。
- 返回：(PIL.Image.Image) 扩展后的图像。
- 抛出：同 `inpaint`。
- 示例：
  ```python
  img2 = cleaner.outpaint_extend(img, 1000, 800, sdSteps=30)
  ```

#### `outpaint_mirror_extend(original_image: PIL.Image.Image, target_width: int, target_height: int) -> PIL.Image.Image`
- 目的：无服务依赖的镜像延伸（`numpy.pad(..., mode='reflect')`）；目标小于原图时执行居中裁剪。
- 参数：
  • `original_image` (PIL.Image.Image)：原始图像；
  • `target_width` (int)：目标宽；
  • `target_height` (int)：目标高。
- 返回：(PIL.Image.Image) 延伸/裁剪后的图像。
- 抛出：`ValueError` 不支持的图像维度（非 2/3 维）。

### 模块：main.py（对外可用的主要函数）

#### `process_images_batch(input_directory: str, target_width: int, target_height: int, lama_cleaner_url: str = 'http://localhost:8080', enable_secondary_fix: bool = True, corners_to_fix: list[str] = ['top-left'], scale_factor: float = 1.5) -> None`
- 目的：对目录内全部图片执行批处理：预处理→（AI 出血|镜像延伸）→可选角落二次修复→精确尺寸→保存。
- 参数：
  • `input_directory` (str)：输入目录（递归扫描图片）；
  • `target_width` (int)：目标宽度；
  • `target_height` (int)：目标高度；
  • `lama_cleaner_url` (str)：`lama-cleaner` 服务地址；
  • `enable_secondary_fix` (bool)：是否启用角落二次修复（需在线服务）；
  • `corners_to_fix` (list[str])：修复角落集合（'top-left'|'top-right'|'bottom-left'|'bottom-right'）；
  • `scale_factor` (float)：角落蒙版扩大倍数（基于实际出血宽高，推荐 1.2–2.0）。
- 返回：(None) 处理结果写入 `output/`，控制台输出明细日志。
- 抛出：内部逐文件捕获异常并统计，整体流程不抛出错误（便于批处理持续执行）。
- 示例：
  ```python
  from export_helper.main import process_images_batch
  process_images_batch(
      input_directory=r"D:\\图片目录",
      target_width=750,
      target_height=1050,
      lama_cleaner_url="http://localhost:8080",
      enable_secondary_fix=True,
      corners_to_fix=['top-left'],
      scale_factor=1.5
  )
  ```

（以下为关键内部工具函数，仅概述用途，非对外 API）
- `get_image_files(directory: str) -> list[str]`：递归收集图片文件（含大小写扩展名）。
- `preprocess_image_for_target_size(image, target_width, target_height) -> (Image, bool, dict)`：必要时居中裁剪，判定是否仍需出血。
- `create_corner_mask(image_size, original_size, corner='top-left', scale_factor=1.5) -> Image`：按实际出血宽高+倍数生成角落蒙版。
- `secondary_inpaint_optimization(cleaner, outpainted_image, original_size, corners_to_fix, scale_factor) -> Image`：角落二次修复循环。
- `ensure_exact_target_size(image, target_width, target_height) -> Image`：最终精确尺寸校准（局部裁剪+居中粘贴）。

## Dependencies
### Internal Dependencies
- `export_helper/LamaCleaner.py` — AI 出血与镜像后备实现（对外核心类）。
- `export_helper/main.py` — 批处理主流程与图像预/后处理。
- `export_helper/__init__.py` — 包元信息与 `LamaCleaner` 导出。

### External Dependencies
- `Pillow` — 图像加载、裁剪、粘贴与保存。
- `numpy` — 镜像延伸的高效数组填充（`reflect`）。
- `requests` — 与 `lama-cleaner` 的 HTTP 交互。
- 标准库：`os`、`glob`、`pathlib`、`io`、`typing`（类型注解，若需要）。
- 外部服务：`lama-cleaner`（默认 `http://localhost:8080`，可通过 `set_base_url` 替换）。

## Integration Points
### Public APIs
- `export_helper.LamaCleaner` — 直接实例化并调用：
  - `is_service_online(timeout: int = 5) -> bool`
  - `inpaint(image, mask, **kwargs) -> Image`
  - `outpaint_extend(original_image, target_width, target_height, **kwargs) -> Image`
  - `outpaint_mirror_extend(original_image, target_width, target_height) -> Image`
- `export_helper.main.process_images_batch(...) -> None` — 一次性批量处理入口。

### Data Flow
输入目录 → 递归收集 → 预处理（必要时居中裁剪）→
（服务在线→AI 出血｜离线→镜像延伸）→（可选角落二次修复）→ 精确尺寸校准 → 写入 `output/`。

### 扩展点
- 通过 `inpaint(**kwargs)`/`outpaint_extend(**kwargs)` 传入服务端参数，微调修复策略；
- 调整 `corners_to_fix` 与 `scale_factor` 控制二次修复范围与强度；
- 可在调用前后挂接自定义日志/指标采集（当前模块不内置回调）。

## Implementation Notes
### Design Patterns
- 适配器（Adapter）：`LamaCleaner` 统一封装外部 HTTP API；
- 备援/降级（Fallback/Graceful Degradation）：服务离线时自动切换镜像延伸；
- 函数式分解：预处理、修复、优化、校准等步骤解耦，便于测试与替换。

### Technical Decisions
- 输出格式统一为 PNG（质量 95，优化启用），减少跨格式差异；
- 目标小于原图时一律居中裁剪，避免缩放失真；
- 二次修复仅在服务在线且确实发生出血时启用；
- 镜像延伸基于 `numpy.pad(..., reflect)`，兼顾速度与边缘连续性。

### Considerations
- 性能：
  - 大图像处理消耗内存与带宽；建议分批；
  - `requests` 同步调用受网络/服务端性能影响；
  - 频繁 I/O 写入 `output/`，磁盘速度会影响总时长。
- 安全：
  - 与本地/远程 `lama-cleaner` 通信使用 HTTP，注意内网暴露与访问控制；
  - 不回传敏感元数据；异常信息避免泄露服务细节。
- 限制：
  - 未提供 CLI 参数解析与单元测试；
  - `/inpaint` 表单参数默认值依据抓包，具体最佳参数需按业务调优；
  - 镜像延伸对复杂边缘的视觉合理性不及 AI 出血；
  - 仅处理栈内图像，不涉及色彩空间/ICC 配置管理。
