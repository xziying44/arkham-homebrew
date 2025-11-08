# arkham-json-diy（根目录）

## Purpose and Scope
本仓库提供“阿卡姆恐怖 LCG”自定义制卡的完整工作流：
- 前端（arkham-app）完成卡牌编辑与管理；
- 后端（Flask 服务）提供文件/工作空间/渲染/导出等接口；
- 渲染内核（Pillow + rich_text_render）实现版式与中英混排；
- 导出助手（export_helper）支持镜像/AI 出血、PDF/JPG/PNG 等制品导出。
本文件聚焦根目录层的职责边界与对外接口：
- 汇总根级 Python 模块（server/app/main/Card 等）的公共 API；
- 描述与子模块的集成关系（bin、rich_text_render、export_helper 等）；
- 指向各子目录的 CLAUDE.md，避免内容重复。

## Structure Overview
- 子目录（均有独立文档，详见其 CLAUDE.md）：
  - `arkham-app/`（前端应用）→ arkham-app/CLAUDE.md
  - `bin/`（后端核心业务：工作空间/导出/TTS/图床）→ bin/CLAUDE.md
  - `export_helper/`（导出与出血算法封装）→ export_helper/CLAUDE.md
  - `fonts/`（字体与语言映射）→ fonts/CLAUDE.md
  - `images/`（UI 模板与美术资源）→ images/CLAUDE.md
  - `prompt/`（提示与脚本片段）→ prompt/CLAUDE.md
  - `remaek_card/`（ArkhamDB 数据转换）→ remaek_card/CLAUDE.md
  - `rich_text_render/`（富文本渲染引擎）→ rich_text_render/CLAUDE.md
  - `templates/`（TTS 模板）→ templates/CLAUDE.md
- 根级主要代码文件：
  - `server.py`：Flask Web 服务，统一对外 API 网关；
  - `app.py`：桌面端（PyWebview）启动器；
  - `main.py`：Android 端（Kivy）容器与权限/目录选取；
  - `ArkhamCardBuilder.py`：从 ArkhamDB JSON 构建卡牌文件；
  - `Card.py`：单卡绘制与版式实现；
  - `ExportHelper.py`：导出规格/出血/质量参数计算与出血实现；
  - `ResourceManager.py`：图片/字体资源与多语言配置；
  - 其他脚本：`create_card.py`、`create_pdf.py`、`macapp.py` 等。

## Key Components

### server.py（Flask 服务）
- 描述：后端服务入口，承载文件树扫描、内容读写、制图导出、GitHub 图床、TTS 导出等接口。
- 入口：`app = Flask(__name__)`
- 关键装饰器：`@app.route` 路由；`@handle_api_error` 统一异常处理。
- 公共接口（按功能分组，签名省略非关键字段，只列关键参数）：
  - 工作目录/最近记录
    - `GET /api/select-directory()`
      - Purpose: 打开目录选择（Android 原生/pywebview/tk 回退）
      - Returns: JSON{ code,msg,data:{directory?:string} }
    - `GET /api/recent-directories()` → 最近目录列表
    - `DELETE /api/recent-directories()` → 清空最近目录
    - `DELETE /api/recent-directories/<directory_path>` → 移除单条记录
    - `POST /api/open-workspace(body: {directory: string})`
      - Returns: JSON{data:{directory}}
  - 文件树与扫描
    - `GET /api/file-tree(include_hidden?: boolean, include_card_type?: boolean, mode?: 'normal'|'snapshot')`
      - Returns: JSON{data:{fileTree, scanId?, status, timestamp}}
    - `GET /api/workspace/scan-progress/<scan_id>(limit?: number=200)`
      - Returns: JSON{data:{status,progress,data[],timestamp}}
    - `POST /api/workspace/report-visible-nodes(body: {scan_id: string, visible_paths: string[]})`
    - `POST /api/workspace/refresh-cache(body: {paths?: string[]})`
  - 文件与内容
    - `POST /api/create-directory(body:{path:string,name:string})`
    - `POST /api/create-file(body:{path:string,name:string,content?:string})`
    - `PUT /api/rename-item(body:{old_path:string,new_name:string})`
    - `DELETE /api/delete-item(body:{path:string})`
    - `GET /api/file-content(path: string)` → Returns: JSON{content}
    - `PUT /api/file-content(body:{path:string,content:string})`
    - `GET /api/image-content(path: string)` → 返回图片二进制（Base64 包装见前端）
    - `GET /api/file-info(path: string)` → stat 元数据
    - `GET /api/status()` → 服务状态与工作区信息
  - 卡图生成/保存
    - `POST /api/generate-card(body:{json_data: CardJsonV1|V2})`
      - Returns: JSON{data:{image: dataURL, back_image?: dataURL, box_position: number[]}}
      - Example: 传入 V2（双面）自动生成正反面并返回 `back_image`
    - `POST /api/save-card(body:{json_data:any, filename:string, parent_path?:string, format?:'PNG'|'JPG', quality?:1..100, rotate_landscape?:boolean})`
      - Returns: JSON{data:{saved_files: string[]}}
  - 配置项
    - `GET /api/config()` → 全局或工作区配置（根据是否已打开工作区）
    - `PUT /api/config(body:{config: object})`
  - 遭遇组/内容包
    - `GET /api/encounter-groups()`
    - `POST /api/content-package/encounter-groups(body:{package_path:string})`
    - `GET /api/content-package/all-encounter-groups()`
  - 导出（牌组/PNP/TTS/ArkhamDB）
    - `POST /api/export-deck-image(body:{...})` → 图片
    - `POST /api/export-deck-pdf(body:{...})` → PDF
    - `POST /api/export-tts(body:{deck_name:string,face_url:string,back_url:string})`
    - `POST /api/content-package/export-tts(body:{package_path:string})`
    - `POST /api/content-package/export-arkhamdb(body:{...})`
    - `POST /api/content-package/generate-numbering-plan(body:{...})`
    - `POST /api/content-package/apply-numbering(body:{...})`
    - `POST /api/content-package/export-pnp(body:{...})`
    - `GET  /api/content-package/export-pnp/logs/<task_id>`
  - ArkhamDB 导入/校验
    - `POST /api/arkhamdb/import(body:{...})`
    - `GET  /api/arkhamdb/logs()`
    - `POST /api/arkhamdb/validate(body:{...})`
  - 图床（GitHub）
    - `POST /api/github/login(body:{token?:string})`
    - `POST /api/github/logout()`
    - `GET  /api/github/repositories()`
    - `POST /api/github/upload(body:{repo:string,branch:string,folder:string,images:Base64[]})`
    - `GET  /api/github/status()`
  - 单卡导出/图床检测
    - `POST /api/export-card(body:{...})`
    - `POST /api/image-host/upload(body:{...})`
    - `POST /api/image-host/check(body:{url:string})`

  返回值统一格式：`{ code:number, msg:string, data?:any }`；异常由 `@handle_api_error` 捕获并返回 `500/JSON`。

### app.py（桌面端入口）
- 描述：PyWebview 启动器，创建桌面窗口并承载 `server.app`。
- 关键方法：
  - `main()`（脚本入口）
  - `webview.create_window(title:str, app:Flask, ...)` 创建窗口并托管 Flask 应用。
- 环境：`ANDROID_ARGUMENT` 不存在时为桌面模式；`--debug/--mode` 控制调试与勘误模式。

### main.py（Android 入口，Kivy）
- 描述：Android 原生容器，申请权限、目录选择，后台线程启动 Flask，并以原生 `WebView` 加载前端。
- 公开类与方法：
  - `class AndroidWebView(url: str='http://127.0.0.1:5000')`
    - `reload(): None` — 重新加载
    - `go_back(): None` — 返回上一页
    - `can_go_back(): bool` — 是否可返回
  - `class AndroidDirectoryPicker`
    - `pick_directory(callback: Callable[[str|None], None]): None`
      - Purpose: 打开系统目录选择器并回调用户选择
    - `get_real_path_from_uri(uri: Any): str`
      - Purpose: 将 `content://` URI 解析为真实文件系统路径
  - `class ArkhamCardMakerApp(App)`
    - `start_flask_server(): None` — 后台线程启动 Flask
    - `load_webview(dt: float): None` — 初始化并加载 `WebView`
  - `def main(): None` — 应用主入口

### ArkhamCardBuilder.py（内容包 → 卡牌文件）
- 描述：从 ArkhamDB 内容包 JSON 构建卡牌对象，并按卡名/位置落盘为 `.card` 文件。
- 关键类：
  - `class ArkhamCardBuilder(content_pack_json: Dict[str,Any], work_dir: str)`
    - `validate_content_pack_structure() -> tuple[bool, list[str]]`
      - Parameters: 无
      - Returns: (是否有效, 错误信息列表)
    - `build_and_save_cards() -> int`
      - Purpose: 边构建边保存（降内存压力）
      - Returns: 成功保存数量
    - `build_cards() -> list[dict]` — 构建对象但不落盘
    - `save_cards(cards: list[dict]) -> int` — 批量保存
    - `process_content_pack() -> tuple[int, list[dict], bool, list[str]]`
      - Returns: (保存数, 空列表(兼容), 是否验证通过, 错误)
    - `get_logs() -> str` — 返回内部累计日志

### ResourceManager.py（资源/多语言）
- 描述：图片与字体资源统一入口；支持“中文名 ↔ 英文文件名”映射与多语言文案。
- 关键类与方法：
  - `class ImageManager(image_folder: str='images')`
    - `set_working_directory(directory_path: str): None`
    - `get_working_directory() -> str`
    - `get_image(image_name: str) -> Image|None` — 支持中/英文键
    - `get_image_by_src(src_path: str) -> Image` — 支持以 `@` 开头的相对工作区路径
  - `class FontManager(font_folder: str='fonts', lang: str='zh')`
    - `set_lang(lang: str): None`
    - `get_lang_font(font_type: str) -> FontInfo` — 如“标题字体/正文字体”等类型
    - `get_font(font_name: str, size: int=20) -> ImageFont|None`
    - `get_font_text(text_key: str) -> str` — 多语言文案映射（含标点适配）

### ExportHelper.py（导出规格/出血）
- 描述：定义导出枚举（格式/规格/出血/模式/模型）并计算像素尺寸、触发镜像/LaMa 出血与文字层渲染。
- 公共枚举：`ExportFormat` | `ExportSize` | `ExportBleed` | `BleedMode` | `BleedModel`
- 关键类：
  - `class ExportHelper(export_params: dict, workspace_manager: WorkspaceManager)`
    - `calculate_pixel_dimensions(dpi: int=300, bleed: ExportBleed=ExportBleed.TWO_MM, size: ExportSize=ExportSize.SIZE_61_88) -> tuple[int,int]`
    - `get_export_settings() -> dict`
    - `__str__() -> str` — 人类可读配置摘要

### Card.py（单卡绘制）
- 描述：基于 Pillow 的版式排版与贴图/文字渲染封装，供 `WorkspaceManager` 调用。
- 关键类：
  - `class Card(width:int, height:int, font_manager?:FontManager, image_manager?:ImageManager, card_type:str='default', card_class:str='default', is_back:bool=False, is_mirror:bool=False, image?:Image)`
    - `paste_image(img: Image, region: tuple[int,int,int,int], resize_mode: Literal['stretch','contain','cover']='stretch', transparent_list?: list[tuple[int,int,int]]|tuple[int,int,int]|None=None, extension:int=0) -> None`
      - Purpose: 贴图到指定区域，支持拉伸/适应/覆盖与透明圆挖空、右侧延展
    - `paste_image_with_transform(img: Image, region: tuple[int,int,int,int], transform_params: dict) -> None`
      - Parameters: `scale:number`, `crop:{top,right,bottom,left}`, `rotation:number`, `flip_horizontal?:bool`, `flip_vertical?:bool`, `offset:{x,y}`
    - `draw_centered_text(position: tuple[int,int], text:str, font_name:str, font_size:int, font_color:tuple, has_border:bool=False, border_width:int=1, border_color:tuple=(0,0,0), underline:bool=False, vertical:bool=False, max_length?:int=None, debug_line:bool=False) -> None`
    - `draw_left_text(position: tuple[int,int], text:str, font_name:str, font_size:int, font_color:tuple, has_border:bool=False, border_width:int=1, border_color:tuple=(0,0,0), max_length?:int=None, debug_line:bool=False) -> None`
    - 其他：`copy_circle_to_image(...)` 等内部工具；`last_render_list: list` 暴露最近一次渲染项用于前端交互。

## Dependencies
### Internal Dependencies
- `bin/`：
  - `workspace_manager`（核心渲染与文件系统编排、配置读写、导出实现）
  - `file_manager.QuickStart`（最近目录记录）
  - `config_directory_manager`（跨平台可写配置目录）
  - `gitHub_image.GitHubImageHost`（图床）
  - 其他：扫描/进度追踪、导出/PNP、TTS、ArkhamDB 转换工具
- `export_helper/`：LaMa/mirror 出血与文字层叠加、PDF 导出辅助
- `rich_text_render/`：富文本解析与排版（统一文本绘制入口）
- `fonts/`、`images/`：资源文件与映射配置

### External Dependencies
- Web/服务：`Flask`（3.x），`pywebview`（桌面），`requests`
- 图像：`Pillow`（>=10），`numpy`
- 桌面/移动：`Kivy`、`jnius`（Android 原生交互）
- PDF：`reportlab`
- 其他：`tqdm`、`psutil` 等（详见 `requirements*.txt`）

## Integration Points
### Public APIs
- Web API：见 “server.py（Flask 服务）” 小节完整列表，统一响应 `{code,msg,data}`。
- 桌面端：`app.py` 创建 Webview 承载同一套 Flask 路由。
- Android：`main.py` 后台启动 Flask，并以 `WebView` 加载前端，目录选择通过 `AndroidDirectoryPicker` 回调传回 `server.py`。

### Data Flow
- 前端（arkham-app）→ HTTP → `server.py` 路由 → `bin.workspace_manager` 编排 → `Card/ResourceManager/export_helper` → 产物（JPG/PNG/PDF/TTS）。
- 内容包（.pack/ArkhamDB JSON）→ `ArkhamCardBuilder`/`ContentPackageManager` → 生成 `.card` 文件或导出 TTS/PNP。

### Extension Points
- 出血方式：`ExportHelper.BleedModel`（`MIRROR` / `LAMA`）与 `BleedMode`（`CROP` / `STRETCH`）。
- 图床：`GitHubImageHost`，支持静默登录与仓库/分支/目录选择。
- 多语言：`FontManager.set_lang` 与 `language_config.json` 驱动字体/文案。

## Implementation Notes
### Design Patterns
- Facade：`server.py` 统一封装工作区/渲染/导出能力为 REST 接口。
- Builder：`ArkhamCardBuilder` 分步构建（索引→正/背面→图片/TTS 元数据→写盘）。
- Strategy：出血（镜像/LaMa）、导出规格/DPI、语言字体选择。

### Technical Decisions
- 平台适配：
  - 桌面（PyWebview）与 Android（Kivy+jnius）复用同一 Flask 服务；
  - Android 11+ 使用 `Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION` 申请“管理所有文件”权限；
  - 目录选择在 Android 使用原生 Intent，在桌面使用 pywebview/tk 回退。
- 扫描优化：文件树“结构快返 + 后台异步扫描”，前端通过 `scanId` 轮询增量。
- 统一错误处理：`@handle_api_error` 捕获并回传详细错误类型与栈信息（安全脱敏）。

### Considerations
- 性能：
  - 图片操作尽量复用对象与缓存（字体缓存、资源映射）；
  - 大型内容包采用“边构建边保存”避免占用峰值内存。
- 安全：
  - 路径校验仅允许工作区内的相对路径；
  - GitHub Token 仅用于图床相关接口，错误信息脱敏；
  - Android URI → 路径转换包含健壮性回退。
- 限制：
  - LaMa 出血依赖外部服务 `lama_baseurl`；
  - 移动端 WebView 能力受系统版本限制（混合内容/缓存策略已按需放开）。

