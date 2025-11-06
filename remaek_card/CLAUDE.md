**remaek_card** — Single-layer module documentation

## Purpose
- 负责将 ArkhamDB 数据与本地图片/翻译进行整合，生成标准化的卡牌元数据与卡牌对象用于前端或外部工具。
- 提供两种运行模式：单文件夹处理与批量处理；支持中英混合数据（以 `translation_data.json` 为增量覆盖）。
- 转换结果遵循前端 cardTypeConfigs.ts 约定（参见 `ArkhamDBConverter` 类注释）。

## Structure
- 代码文件
  - `main.py`：元数据扫描与批处理入口（类 `CardMetadataScanner`）。
  - `arkhamdb2card.py`：ArkhamDB → 统一卡牌对象转换器（类 `ArkhamDBConverter`）。
  - `remaek_player_card.py`：玩家卡牌生成与图片下载/裁切（类 `RemakeCardsTranslationTask`，可选集成）。
- 数据文件
  - `db_cards_en.json`：ArkhamDB 英文原始数据库（必需）。
  - `translation_data.json`：翻译映射（可选，按 `code` 精准覆盖主库与 `linked_card`）。
  - `location_icons_mapping.json`：地点图标映射（可选，供地点图标提取与渲染）。
  - `gmnotes_index.json`：GM notes 索引（可选，供场景/地点等定制信息提取）。
- 文档
  - `批量处理使用说明.md`：运行方式与目录结构说明（配合批量模式）。

## Components
- `CardMetadataScanner`（`main.py`）
  - `__init__(work_directory, code)`：初始化工作目录与 code 前缀；加载并应用翻译到 `db_cards_en.json`。
  - `scan_metadata()`：扫描图片文件，解析位置/是否背面，匹配数据库并产出元数据列表。
  - `save_metadata(metadata, output_filename='metadata.json')`：保存扫描结果。
  - `convert_and_save_cards(metadata_filename='card_metadata.json')`：调用 `ArkhamDBConverter` 将元数据转为统一卡牌对象，输出至目标目录（如 `卡牌/`）。
  - `run_scan_and_save(output_filename='metadata.json')`：一体化扫描并保存。
  - `batch_process_all_folders(base_directory, folder_type='重置玩家卡')`：批量处理指定根目录下的子目录（如 01_基础游戏 …），生成汇总报告。

- `ArkhamDBConverter`（`arkhamdb2card.py`）
  - 常量映射：`FACTION_MAP`、`TYPE_MAP_FRONT`、`TYPE_MAP_BACK`、`SLOT_MAP`、`TEXT_FORMAT_MAP`、`SPAN_ICON_MAP`、`ENCOUNTER_GROUP_MAP`、`COPYRIGHT_DICT`。
  - 初始化与通用：`__init__(arkhamdb_json)`、`_format_text()`、`_format_flavor_text()`、`_extract_common_player_card_properties()`、`_apply_special_card_handling()`。
  - 前后面转换：`convert_front()`、`convert_back()` 以及分类型实现（如 `_convert_asset_front()`、`_convert_enemy_front()`、`_convert_location_back()` 等）。
  - 扩展数据：`load_gmnotes_index()`、`load_location_icons_mapping()`、`get_location_icon_mapping()`、`_extract_location_icons_from_gmnotes()`。
  - 关系/统计：`set_full_database()`、`find_card_by_linked_to_code()`、`calculate_encounter_group_statistics()`、`set_encounter_group_index()`、`get_encounter_group_info()`。

- `RemakeCardsTranslationTask`（`remaek_player_card.py`）
  - 额外工具链（可选）：从对象 JSON 中抽取卡牌、下载与裁切图片、批量生成卡牌；依赖外部 `ResourceManager`, `create_card` 等上层项目组件。

## Dependencies
- 运行环境
  - Python 3.7+（建议 3.8+）。
- 第三方库
  - `Pillow`（`PIL.Image`）：图片处理与编码。
  - `requests`：图片下载（仅 `remaek_player_card.py` 可选使用）。
- 标准库（核心使用）
  - `json`、`os`、`re`、`base64`、`pathlib.Path`、`typing`。
- 数据与资源
  - `db_cards_en.json`（必需）、`translation_data.json`（可选）、`location_icons_mapping.json`（可选）、`gmnotes_index.json`（可选）。
- 外部/上游对接
  - 前端配置 `cardTypeConfigs.ts`（转换产物字段契约）。
  - 上层渲染/制卡工具（如 `ResourceManager`、`CardCreator`）。

## Integration
- 单文件夹处理
  ```bash
  python main.py
  ```
  - 默认示例使用 Windows 路径（可在 `main.py` 内修改 `work_directory` 与 `code`）。
  - 产物：`metadata.json` / `card_metadata.json` 与 `卡牌/` 目录中的 `.card` 文件。

- 批量处理
  ```bash
  python main.py batch [文件夹类型] [基础目录]
  # 例：python main.py batch 重置玩家卡 "D:\\诡镇奇谈"
  ```
  - 目录要求与更多示例详见 `批量处理使用说明.md`。
  - 输出包含批量报告（如 `batch_processing_results_重置玩家卡.json`）。

- 转换与前端/工具的契约
  - `ArkhamDBConverter` 产物字段与前端 `cardTypeConfigs.ts` 保持一致。
  - 地点图标与 GM notes 可通过加载 `location_icons_mapping.json`、`gmnotes_index.json` 丰富产物。
  - 遭遇组索引通过 `calculate_encounter_group_statistics()` 与 `set_encounter_group_index()` 统一统计和查询。

## Notes
- 文件命名与匹配
  - 图片文件名需包含位置数字；背面以 `b` 结尾以便识别。
  - `code` 前缀用于在数据库中快速定位卡牌（如 `01`）。
- 翻译覆盖
  - `translation_data.json` 以 `code` 为键对主卡与 `linked_card` 做非空字段的增量覆盖；`duplicated_by` 会级联同步。
- 性能与稳定性
  - 批处理按文件夹顺序运行；单个失败不影响全局，错误会在控制台与报告中记录。
  - 遭遇组统计较耗时，建议在批量模式中一次性计算并复用。
- 可选组件
  - `remaek_player_card.py` 涉及下载与图片裁切，需配置网络代理（如使用）与外部依赖；不影响核心扫描与转换流程。
- 故障排查
  - 确保路径/权限/磁盘空间正确；校验 `db_cards_en.json` 存在且可解析。
  - 详情用法、目录结构、示例输出参见 `批量处理使用说明.md`。
