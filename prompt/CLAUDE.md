# CLAUDE.md

## Purpose
- Provide a single-layer documentation for the `prompt` module that converts natural-language card descriptions into a normalized Arkham Horror LCG JSON payload.
- Ensure consistent field names, allowed values, and normalization rules so downstream builders/renderers (backend and frontend) consume a stable schema.

## Structure
- Files
  - `player_card_picture.txt` — Source prompt/spec (Chinese). Defines required/optional fields, controlled vocabularies, and normalization rules for card JSON.
- Notes
  - No child `CLAUDE.md` files were found under this directory; this document aggregates from the current directory specification and references repo integration points.

## Components
- Prompt schema overview (core fields)
  - Required: `type`, `name`, `traits` (string[]), `body` (use `<lr>` for newlines). When `type` is `调查员卡`, `attribute` is required: four integers `[意志, 智力, 战力, 敏捷]`.
  - Common optional: `class`, `subclass` (多职阶时，可含['守护者','探求者','流浪者','潜修者','生存者']，最多2个不重复), `subtitle`, `flavor`, `level` (默认0; `-1`=无等级), `cost` (整数; 无费用填`-1`; X费用填`-2`), `submit_icon` (技能图标 list), `slots`/`slots2` (槽位枚举), `msg`, `image_prompt`。
  - Encounter/scene specific: `serial_number` (如`1a`/`2b`), `threshold` (数字或`?`或`-`), `victory` (数字或字符串), `vengeance` (若存在，将转化到`victory`说明文本，见后端处理)。
  - Location specific: `location_type`（地点卡必填：`已揭示` | `未揭示`）, `location_icon`, `location_link` (数组)。
  - Enemy specific: `enemy_damage`, `enemy_damage_horror`, `attack`, `evade`, `enemy_health`。
  - Investigator back side: `card_back` 对象：`{ size: number, option: string[], requirement: string, other: string, story: string }`；`story` 保持换行，后端会转换为`<lr>`。

- Controlled vocabularies and normalization
  - `type` allowed: `技能卡`、`支援卡`、`事件卡`、`调查员卡`、`调查员卡背`、`诡计卡`、`敌人卡`、`地点卡`、`升级卡`（定制卡）、`故事卡`、`场景卡`、`密谋卡`、`场景卡背`、`密谋卡背`。
  - `class` allowed: `守护者`、`探求者`、`流浪者`、`潜修者`、`生存者`、`中立`、`弱点`、`多职阶`。常见同义纠正：`守卫者` → `守护者`；`调查员` → `调查员卡`；`调查员背面` → `调查员卡背`；`定制卡` → `升级卡`。
  - `submit_icon` mapping（别名→标准）：`脑`→`意志`，`书`→`智力`，`拳`→`战力`，`腿/脚`→`敏捷`，`?`→`狂野`。后端会按固定顺序排序：意志→智力→战力→敏捷→狂野。
  - `slots`/`slots2` allowed: `空`、`双手`、`双法术`、`塔罗`、`手部`、`法术`、`盟友`、`身体`、`饰品`（`空`表示空图标槽位，非“无槽位”）。
  - Text handling: `body` 中换行转换为`<lr>`；`flavor` 文本保留`<lr>`作为制表符；部分全角符号将被标准化（见后端预处理）。

- Minimal example
```json
{
  "type": "支援卡",
  "class": "守护者",
  "name": "示例卡",
  "traits": ["武器"],
  "submit_icon": ["战力", "战力", "狂野"],
  "cost": 2,
  "level": 0,
  "body": "快速行动：<lr>进行一次攻击。",
  "flavor": "这把枪曾拯救过我。",
  "card_back": { "size": 0, "option": [], "requirement": "", "other": "", "story": "" }
}
```

## Dependencies
- Backend usage
  - `create_card.py:260` — Sorts `submit_icon` into canonical order and normalizes fields.
  - `create_card.py:316` — Defaults `weakness_type` to `弱点` when `class` is `弱点` and not provided.
  - `create_card.py:336` — Normalizes `card_back.story` newlines to `<lr>`.
  - `ExportHelper.py:287` — Applies bleeding for `submit_icon` to export images.
  - `ArkhamCardBuilder.py:367` — Chooses default card back type from front `type`/`class`.

- Frontend configuration
  - `arkham-app/src/config/cardTypeConfigs.ts:961` — Supports `weakness_type`.
  - `arkham-app/src/config/cardTypeConfigs.ts:844, 850, 856, 862` — `card_back.option` / `card_back.requirement` / `card_back.other` / `card_back.story` form keys.

## Integration
- Authoring workflow
  1) Compose natural-language card details in Chinese.
  2) Convert to the target JSON using this prompt schema (respect allowed values and mappings).
  3) Provide the JSON to backend renderers (e.g., `create_card.py`) to generate card images; optional bleeding and export handled by `ExportHelper.py`.
  4) For Investigator cards, include `attribute` (四维) and `card_back` details when needed.

- Key behaviors to rely on
  - Newlines in `card_back.story` are auto-converted to `<lr>` by backend (`create_card.py:336`).
  - If `class` is `弱点` and `weakness_type` omitted, backend sets `弱点` (`create_card.py:316`).
  - `submit_icon` is auto-sorted; duplicates allowed (`create_card.py:260`).
  - Some punctuation/width normalization is applied before rendering (`create_card.py` preprocessing).

## Notes
- Encoding: Use UTF-8; keep Chinese punctuation where intended. In Windows terminals, ensure UTF-8 output/input to avoid mojibake.
- Validation: Prefer controlled vocabularies exactly; when unspecified, rely on defaults (`level: 0`, `class: 中立`, etc.).
- Edge cases:
  - `cost`: `-1` for “无费用/无花费”，`-2` for “X费用”。
  - `location_type` is mandatory when `type` is `地点卡`（`已揭示` | `未揭示`）。
  - `serial_number`/`threshold` only apply to `场景卡`/`密谋卡`。
  - Use `msg` to surface upstream validation errors; backend will raise on non-empty `msg` for certain builders.

