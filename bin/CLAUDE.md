# bin 模块

## Purpose and Scope
本目录为后端核心业务逻辑层，负责：
- 工作空间/文件系统访问与受控写入（安全边界在工作目录内）
- 卡图生成与导出（图片、PDF、PNP、TTS 对象）
- 图床上传（Cloudinary、ImgBB、GitHub 仓库）
- 内容包导出（ArkhamDB、TTS 物品）、自动编号与资料整合
- 统一日志记录与全局配置目录管理

该层通过公开类与函数为上层 API/GUI 提供稳定的服务接口；不直接承担路由，仅实现领域逻辑。

## Structure Overview
文件组织（导入/导出关键点）：
- 导出 API（通过 `bin/__init__.py` 导出）：`QuickStart`、`DeckExporter`、`TTSCardConverter`、`ContentPackageManager`、`ConfigDirectoryManager`（__init__.py:23）
- 工作空间与扫描：`workspace_manager.py`（WorkspaceManager/Scanner/Progress/Cache）
- 导出实现：`deck_exporter.py`（图片/PDF）、`pnp_exporter.py`（PNP PDF）
- 内容包与格式转换：`content_package_manager.py`、`card2arkhamdb.py`、`arkhamdb2card.py`、`card_numbering.py`
- 图床与上传：`image_uploader.py`（Cloudinary/ImgBB/工厂）、`gitHub_image.py`（GitHub 图床）
- 基础设施：`logger.py`（单例日志）、`config_directory_manager.py`（单例配置目录）

## Key Components
（以下优先覆盖公开/导出 API；内部重要组件附摘要）

### QuickStart（file_manager.py:7）
- 描述：最近目录记录与快速启动的小型工具类。
- 职责：读写 `recent_directories.json`，维护最多 20 条最近访问记录。
- 关键方法：
  #### `__init__(config_file: str = "recent_directories.json")`
  - Purpose: 设置记录文件路径与上限。
  - Parameters:
    • config_file (str): 记录文件名；默认 `recent_directories.json`。
  - Returns: (None)

  #### `add_recent_directory(directory_path: str) -> bool`（file_manager.py:32）
  - Purpose: 添加/置顶一条最近目录记录，自动去重并截断到 20 条。
  - Parameters:
    • directory_path (str): 绝对或相对路径；必须存在且为目录。
  - Returns: (bool) 成功/失败。
  - Throws: I/O 异常内部捕获并打印，返回 False。

  #### `get_recent_directories() -> List[Dict[str, Any]]`（file_manager.py:64）
  - Purpose: 读取并过滤无效路径，必要时回写清理后的列表。
  - Returns: (List[Dict]) 最近目录列表（含 path/name/timestamp/formatted_time）。

  #### `remove_recent_directory(directory_path: str) -> bool`（file_manager.py:80）
  - Purpose: 移除指定路径记录。
  - Returns: (bool) 是否实际删除。

  #### `clear_recent_directories() -> bool`（file_manager.py:95）
  - Purpose: 清空所有记录。
  - Returns: (bool) 成功/失败。

### DeckExporter（deck_exporter.py:10）
- 描述：将 DeckBuilder 配置导出为图片或 PDF（按正反顺序处理，横图统一旋转）。
- 职责：拼接大图（或逐页 PDF），对共享背面与独立背面做差异处理。
- 关键方法：
  #### `__init__(workspace_manager: WorkspaceManager)`
  - Purpose: 注入工作空间以读取/生成卡图。
  - Parameters:
    • workspace_manager (WorkspaceManager): 文件/卡图服务提供者。
  - Returns: (None)

  #### `export_deck_image(deck_name: str, export_format: str = 'PNG', quality: int = 95) -> bool`（deck_exporter.py:22）
  - Purpose: 依据 DeckBuilder/<deck_name> 生成正反拼图。
  - Parameters:
    • deck_name (str): DeckBuilder 下 JSON 文件名。
    • export_format (str): 'PNG' 或 'JPG'；默认 'PNG'。
    • quality (int): JPG 质量 1–100；默认 95。
  - Returns: (bool) 导出是否成功。
  - Throws: I/O 错误与 JSON 解析错误内部捕获，返回 False。
  - Example:
    • `DeckExporter(ws).export_deck_image('mydeck.json', 'JPG', 90)`

  #### `export_deck_pdf(deck_name: str, pdf_filename: Optional[str] = None) -> bool`（deck_exporter.py:143）
  - Purpose: 生成逐页 PDF（正面→背面），带文本层元数据。
  - Parameters:
    • deck_name (str): DeckBuilder JSON 文件名。
    • pdf_filename (str, optional): 输出文件名；默认与 deck 同名。
  - Returns: (bool) 是否成功。

### TTSCardConverter（tts_card_converter.py:7）
- 描述：将 DeckBuilder 配置转换为 TTS 存档 JSON（可区分调查员/其他牌堆）。
- 职责：读取 .card/.card.json，拼装 CustomDeck 与对象状态。
- 关键方法：
  #### `__init__(work_directory: str)`
  - Purpose: 设置工作目录做相对路径解析。
  - Parameters:
    • work_directory (str): 工作根路径。
  - Returns: (None)

  #### `convert_deck_to_tts(deck_config: Dict[str, Any], face_url: str, back_url: str) -> Dict[str, Any]`（tts_card_converter.py:260）
  - Purpose: 生成符合 TTS 的完整对象 JSON（ObjectStates）。
  - Parameters:
    • deck_config (Dict): DeckBuilder JSON 内容。
    • face_url (str): 正面图片 URL。
    • back_url (str): 背面图片 URL（共享或独立）。
  - Returns: (Dict) TTS 存档对象。
  - Throws: 文件缺失/解析异常内部捕获并打印。

  #### `read_card_file(card_path: str) -> Dict[str, Any]`（tts_card_converter.py:43）
  - Purpose: 读取 `.card` 或 `.card.json` 并解析。
  - Parameters:
    • card_path (str): 相对工作目录路径（不含 `.json` 后缀）。
  - Returns: (Dict) 卡牌 JSON。

### ContentPackageManager（content_package_manager.py:13）
- 描述：内容包导出总管，支持 TTS 盒子与 ArkhamDB 数据，同时提供遭遇组资产收集。
- 职责：统一记录日志、读取模板、整合图片 URL、调用转换器/导出器。
- 关键方法：
  #### `__init__(content_package_data: Dict[str, Any], workspace_manager)`
  - Purpose: 注入内容包与工作空间。
  - Parameters:
    • content_package_data (Dict): 内容包 JSON（meta、cards 等）。
    • workspace_manager (WorkspaceManager): 依赖文件/卡图/配置。
  - Returns: (None)

  #### `export_to_tts() -> Dict[str, Any]`（content_package_manager.py:101）
  - Purpose: 生成包含 `ObjectStates` 的 TTS 盒子 JSON 与过程日志。
  - Returns: (Dict) `{ success, box_json?, logs, error? }`。

  #### V2 改造要点（TTS 脚本生成与解析）
  - 统一使用 `TtsScriptGenerator(workspace_manager)` 生成 GMNotes/LuaScript（导出与预览一致）。
  - `_extract_gmnotes_id(card)` / `_parse_gmnotes(card)`：V2 优先（用生成器结果），旧数据回退解析 `tts_script.GMNotes`。
  - 签名卡：V2 使用 `tts_config.signatures = [{ path, count }]`，生成器按相对路径解析卡文件获得稳定脚本 ID；路径不存在则跳过该条。

  #### `export_to_arkhamdb(output_path: str = None) -> Dict[str, Any]`（content_package_manager.py:270）
  - Purpose: 依据卡牌数据与编号生成 ArkhamDB 导出文件。
  - Parameters:
    • output_path (str, optional): 指定输出路径；默认生成到工作空间 `ContentPackage/`。
  - Returns: (Dict) 导出结果与日志。

  #### `get_encounter_groups_from_package() -> List[Dict[str, Any]]`（content_package_manager.py:498）
  - Purpose: 聚合内容包引用到的遭遇组图片为 base64 资源条目。
  - Returns: (List[Dict]) `[ {name, base64, relative_path}, ... ]`。
  - Example:
    • 用于“一键打包”时，将遭遇组图片同步到目标目录或上传。

### ConfigDirectoryManager（config_directory_manager.py:8）
- 描述：平台/打包感知的全局配置目录定位工具（单例）。
- 职责：提供应用级配置、日志与 TTS 保存目录位置。
- 关键方法：
  #### `get_global_config_dir() -> str`（config_directory_manager.py:73）
  - Purpose: 返回全局配置目录（便携模式优先当前目录）。

  #### `get_logs_dir() -> str`（config_directory_manager.py:81）
  - Purpose: 返回日志目录路径。

  #### `get_tts_save_directory() -> Optional[str]`（config_directory_manager.py:89）
  - Purpose: Windows 下解析“我的文档/Tabletop Simulator/.../Saved Objects/阿卡姆姬制作”，并确保存在。
  - Returns: (str|None) 目录或 None（非 Windows 或创建失败）。

### WorkspaceManager（workspace_manager.py:642）
- 描述：工作空间读写与卡图生成中枢；含目录树扫描、类型缓存、文件/图片 I/O、卡图生成与保存。
- 关键方法（对外常用）：
  #### `get_file_tree(include_hidden: bool = False) -> Dict[str, Any]`（workspace_manager.py:1049）
  - Purpose: 返回可直接渲染的树结构（含类型/排序/部分 card_type）。

  #### `create_directory(dir_name: str, parent_path: Optional[str] = None) -> bool`（workspace_manager.py:1074）
  #### `create_file(file_name: str, content: str = "", parent_path: Optional[str] = None) -> bool`（workspace_manager.py:1101）
  #### `rename_item(old_path: str, new_name: str) -> bool`（workspace_manager.py:1138）
  #### `delete_item(item_path: str) -> bool`（workspace_manager.py:1176）
  - Purpose: 受控文件系统操作（路径必须在工作空间内；自动维护 `.cache/card_types.json`）。

  #### `get_file_content(file_path: str) -> Optional[str]`（workspace_manager.py:1204）
  #### `get_image_as_base64(image_path: str) -> Optional[str]`（workspace_manager.py:1244）
  #### `get_file_info(file_path: str) -> Optional[Dict[str, Any]]`（workspace_manager.py:1286）
  #### `save_file_content(file_path: str, content: str) -> bool`（workspace_manager.py:1323）

  #### `generate_card_image(json_data: Dict[str, Any], silence: bool = False)`（workspace_manager.py:1435）
  - Purpose: 调用渲染管线（CardCreator / FontManager / ImageManager）生成卡图或底图层。
  - Returns: (Card|None) 生成的卡对象。

  #### `save_card_image(json_data: Dict[str, Any], filename: str, parent_path: Optional[str] = None) -> bool`（workspace_manager.py:1719）
  #### `save_card_image_enhanced(json_data: Dict[str, Any], filename: str, parent_path: Optional[str] = None, export_format: str = 'JPG', quality: int = 95, rotate_landscape: bool = False) -> Dict[str, Any]`（workspace_manager.py:1768）
  - Purpose: 保存（可选横图旋转/生成缩略图/双面卡）并返回各资源路径。

（内部支撑类：WorkspaceScanner、ScanProgressTracker、CacheManager 提供分层扫描、后台并发、基于 mtime 的类型缓存与优先级队列调整。）

### 图床与上传
- GitHubImageHost（gitHub_image.py:9）：登录（login/silent_login）、列仓库、上传图片并返回直链（login:40, list:116, upload:166, get_status:252）。
- ImageUploader 抽象 + CloudinaryUploader（image_uploader.py:32）/ImgBBUploader（image_uploader.py:88），统一 `check_file_exists / upload_file` 接口；工厂 `create_uploader(config)`（image_uploader.py:142）。

### 导出与转换（内部）
- PNPExporter（pnp_exporter.py:26）：基于 ExportHelper 生成 PNP PDF，支持日志回调、临时目录与双面导出（_create_temp_directory:139, _export_card_images:157）。
- Card2ArkhamDBConverter（card2arkhamdb.py:15）：将自定义卡数据转 ArkhamDB 结构（支持多职阶/背面拆分/图片 URL 互换）。
- ArkhamDBConverter（arkhamdb2card.py:7）：ArkhamDB → 内部卡对象（文本与图标清洗、遭遇组映射）。
- card_numbering.py：按遭遇组与类型排序生成编号方案，并可回填到卡牌数据。

## Dependencies
### Internal Dependencies
- `workspace_manager.py` - 工作空间与生成中枢
- `deck_exporter.py` - 牌库图片/PDF导出
- `pnp_exporter.py` - PNP PDF 导出
- `content_package_manager.py` - 内容包导出
- `card2arkhamdb.py` / `arkhamdb2card.py` - 互转
- `card_numbering.py` - 自动编号
- `image_uploader.py` / `gitHub_image.py` - 图床上传
- `logger.py` - 日志单例
- `config_directory_manager.py` - 配置目录单例

### External Dependencies
- `Pillow (PIL)` - 图片处理与缩放/裁剪/旋转
- `requests` - HTTP 调用（GitHub/ImgBB 等）
- `cloudinary` - Cloudinary SDK 上传
- `reportlab` - PDF 矢量绘制
- `concurrent.futures` - 线程池并发（扫描）

## Integration Points
### Public APIs
- `QuickStart`（file_manager.py:7）
- `DeckExporter`（deck_exporter.py:10）
- `TTSCardConverter`（tts_card_converter.py:7）
- `ContentPackageManager`（content_package_manager.py:13）
- `ConfigDirectoryManager`（config_directory_manager.py:8）

### 数据流（示意）
- 导出图片/PDF：DeckBuilder JSON → DeckExporter → WorkspaceManager.generate_card_image → 输出文件
- TTS 导出：DeckBuilder JSON/图片 URL → TTSCardConverter → TTS ObjectStates JSON
- ArkhamDB 导出：内容包(JSON) → ContentPackageManager → Card2ArkhamDBConverter/card_numbering → 输出 JSON
- 图床上传：本地文件 → ImageUploader/GitHubImageHost → 直链 URL

### 回调与扩展点
- 扫描进度回调：`ScanProgressTracker.start_scan(..., progress_callback)`（workspace_manager.py 内部）
- 日志回调：`PNPExporter(..., log_callback=...)`（pnp_exporter.py:36）
- 图床工厂：`create_uploader(config)`（image_uploader.py:142）支持切换后端

## Implementation Notes
### 设计模式
- 单例：`LoggerManager`、`ConfigDirectoryManager`（集中化配置与日志路径管理）
- 工厂：`create_uploader(config)`（按配置选择 Cloudinary/ImgBB）
- 缓存：`CacheManager` 基于 mtime 的文件类型缓存；WorkspaceManager 的 `.cache/card_types.json`
- 任务调度：`ScanProgressTracker` 使用线程池与优先队列重排

### 技术决策
- 目录树构建使用 `os.scandir` 与一次性 `stat`，降低 I/O 开销（workspace_manager.py:400 起）
- 解析 card 类型仅读取文件前 4KB 并正则匹配 `"type": "..."`（workspace_manager.py:560 附近）
- 横向卡图统一旋转以保证导出一致性（deck_exporter.py:292 `_process_card_image_for_export`）

### 配置与环境
- `APP_MODE` 影响图像处理模式（workspace_manager.py:1550 附近）
- 全局/工作空间配置按字段白名单分别保存（workspace_manager.py:2100 起）
- Windows 下 TTS 保存目录自动定位（config_directory_manager.py:89）

### 性能
- 扫描分层/分批推进，并在 200 项粒度做节流与让出 CPU
- 基于 mtime 的轻量缓存避免重复解析大型 JSON（5MB 上限）

### 安全
- GitHub Token 只存内存 headers，不写日志；避免输出敏感配置
- 文件写入前校验路径在工作空间内，防止目录逃逸

### 限制
- 超过 5MB 的 JSON 文件跳过类型解析（WorkspaceScanner.MAX_JSON_SIZE）
- 依赖外部渲染栈（FontManager/ImageManager/CardCreator）可用性；缺失时仅返回卡背或报警告
### TtsScriptGenerator（tts_script_generator.py）
- 描述：统一 GMNotes/LuaScript 生成器，权威生成源，导出与预览一致。
- 入口：`generate(card_data) -> { GMNotes, LuaScript }`
- 行为（V2 专用）：
  - 优先级：
    1) 升级表脚本（`tts_config.upgrade.coordinates`）→ `templates/upgrade_sheet.lua`
    2) 封印脚本（`tts_config.seal`）→ `templates/seal.lua`
    3) 调查员阶段按钮（仅调查员）→ `templates/phase_buttons.lua`
  - 封印脚本配置结构：
    ```jsonc
    tts_config: {
      seal?: {
        enabled: boolean;            // 开关
        allTokens: boolean;          // 允许所有 Token（与 INVALID_TOKENS 协同）
        tokens: string[];            // 指定允许的 Token 名称（Elder Sign, Skull, …）
        max?: number | null;         // 最大封印数；空/0 表示不限制（库默认 99）
      },
      language?: string;             // 'zh' | 'zh-CHT' | 'zh-cn' | 'zh-tw' → 中文菜单；其他 → 英文
    }
    ```
  - 模板占位符：注入 VALID_TOKENS / INVALID_TOKENS / UPDATE_ON_HOVER / MAX_SEALED / RESOLVE_TOKEN；并注入菜单 i18n（Release/Resolve/Seal/Return/…）与 TOKEN_DISPLAY（标记名汉化）。
  - 直达菜单：当只配置一种可封印类型时，自动显示“释放 <Token> / 结算 <Token>”。
  - 地点/场景/密谋等 GMNotes：保持原有解析（线索/毁灭阈值、参考卡 token 修饰解析）。
- 行为（非 V2）：回退读取 `card_data.tts_script` 并兼容地点卡旧数据结构。
