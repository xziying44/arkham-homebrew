[根目录](../../../CLAUDE.md) > [arkham-app](../..) > [src](..) > **config**

## 变更记录 (Changelog)

- 2025-11-06: 首次创建本模块文档，梳理配置结构与生成器API
- 2025-11-10: 新增“调查员小卡”卡牌类型（纯图片）；字段：正/背选择、滤镜样式(normal/grayscale)、背面共享正面插画与设置；中文/英文配置同步；默认背面类型映射；小卡不提供外部图片替换。
- 2025-11-22: 新增“规则小卡”类型，字段限定为标题/正文/页码，双语配置同步，页码提示 1-999。

## 模块职责 (Scope)

config 子模块提供前端配置数据与脚本生成工具：
- 卡牌类型配置映射：驱动表单字段、联动显示、选项与默认值
- 中英双语配置：与 UI 国际化配合的字段文案与展示名称
- TTS 脚本生成器：生成/解析带相位按钮的 Lua 脚本
- 自定义升级表脚本生成器：基于坐标生成 Power Word 升级表 Lua 脚本

## 架构与文件 (Architecture)

- cardTypeConfigs.ts：中文卡牌类型配置与类型定义
- cardTypeConfigsEn.ts：英文卡牌类型配置与类型定义（含 `field_type_en`）
- ttsScriptGenerator.ts：TTS 相位侧边按钮脚本生成/解析
- upgrade-script-generator.ts：Power Word 升级表脚本生成

两份配置文件均导出同名 `cardTypeConfigs` 映射，结构一致；英文字段文件在展示文案上做本地化扩展。

## 数据结构 (Data Model)

类型定义（两份配置文件顶部一致，英文版额外含 `field_type_en`）：

```ts
export interface FieldOption {
  label: string
  value: string | number | null
}

export interface ShowCondition {
  field: string                  // 依赖的字段名
  value: any                     // 匹配值
  operator?: 'equals' | 'not-equals' | 'includes' | 'not-includes'
}

export interface FormField {
  key: string                    // 字段键（可复用，配合 index 表示同组多项）
  name: string                   // 字段显示名（本地化）
  type: 'text' | 'textarea' | 'number' | 'select' | 'multi-select' | 'string-array' | 'image' | 'encounter-group-select'
  layout?: 'full' | 'half' | 'third' | 'quarter' // 表单栅格宽度
  min?: number
  max?: number
  rows?: number
  maxlength?: number
  options?: FieldOption[]        // 选项（select/multi-select）
  showCondition?: ShowCondition  // 条件显示
  index?: number                 // 同 key 分组下的序号（如 subclass[0..2], attribute[0..3]）
  maxSize?: number               // image 最大字节数（如 50MB）
  defaultValue?: any
  helpText?: string
}

export interface CardTypeConfig {
  fields: FormField[]
  field_type_display?: string            // 展示名（含 emoji）
  card_category?: 'player' | 'encounter' // 卡牌分类
  // 英文版额外：field_type_en?: string
}
```

表单布局与复用约定：
- 栅格宽度：`full`=1列、`half`=1/2、`third`=1/3、`quarter`=1/4。
- 复用字段：相同 `key` 搭配 `index` 表示同字段组的第 N 项，例如：
  - `subclass` 索引 0/1/2 → 第一/第二/第三职阶
  - `attribute` 索引 0..3 → 意志/智力/战力/敏捷
- 条件显示：`showCondition` 控制字段可见性（如仅当 `class=多职阶` 时展示 `subclass`）。

取值约定（常见哨兵值）：
- `level`: `-2`=定制标, `-1`=无等级, `0..5`=正式等级
- `cost`: `-2`=X 费用, `-1`=无费用, `0..99`=费用值
- `health`/`horror`: `-2`=无限, `-1`=无, `0..99`=具体数值

特殊字段类型：
- `string-array`：字符串数组（如特性列表）；
- `image`：图片上传，含 `maxSize` 校验；
- `encounter-group-select`：遭遇组选择器（用于中立遭遇卡）；
- 条件外部图：`use_external_image`(0/1) + `external_image`(image)，通过 `showCondition` 组合展示。

帮助文本与标记语法（片段源自配置内置 `helpText`）：
- 文本加粗：`【粗体】` 或 `{{粗体}}`
- 特性标签：`{盟友}`
- 风味文本：`[这是风味文本]` 或 `<flavor ...>...</flavor>` 高级风味块
- `<upg>`/`<升级>`：定制卡中用于自动生成 TTS 复选框脚本
- 卡名插值：`<fullname>`
- 图标标签：提供多种图标别名（如 `<骷髅>`、`<触手>`、`<书>`、`<拳>`、`<祝福>`、`<诅咒>`、`<frost>` 等），亦可直接使用 Emoji
- 结构标签：`<br>` 换行、`<hr>` 横线、`<center>...</center>` 居中

## 配置映射 (cardTypeConfigs)

导出：`export const cardTypeConfigs: Record<string, CardTypeConfig>`

键为卡牌类型（中文），值为对应的字段集合与分类信息。常见类型示例：
- 玩家卡：`支援卡`、`事件卡`、`技能卡`、`调查员`、`调查员背面` 等
- 遭遇卡：若 `card_category = 'encounter'`，可含 `encounter_group`（`encounter-group-select`）

动态字段示例模式：
- 多职阶：当 `class = 多职阶` 时展示 `subclass[0..2]`
- 弱点类型：当 `class = 弱点` 时展示 `weakness_type`
- 遭遇组：当 `class = 中立` 时展示 `encounter_group`

中英文对应：
- 中文配置：`cardTypeConfigs.ts`（`field_type_display` 使用中文与 emoji）
- 英文配置：`cardTypeConfigsEn.ts`（增加 `field_type_en`，字段 `name` 文案为英文）

## 生成器 (Generators)

### TTS 相位按钮脚本 (ttsScriptGenerator.ts)

导出类型与常量：

```ts
export interface PhaseButton { id: string; label: string; color: string }
export interface PhaseButtonConfig { buttons: PhaseButton[] }

export const buttonLabelOptions: { value: string; label: string; emoji: string }[]
export const colorOptions: { value: string; label: string }[]
export const defaultPhaseButtons: PhaseButton[]
```

生成与解析：

```ts
export function generateButtonParams(config: PhaseButtonConfig): string
// 生成 Lua 中的 buttonParams 片段

export function generatePhaseButtonScript(config: PhaseButtonConfig): string
// 生成完整可用的相位按钮 Lua 脚本（替换占位符：buttonParams、按钮索引映射、按钮数量）

export function parsePhaseButtonConfig(luaScript: string): PhaseButtonConfig | null
// 从既有 Lua 脚本中解析出 PhaseButtonConfig（基于正则，失败返回 null）
```

使用示例：

```ts
import { defaultPhaseButtons, generatePhaseButtonScript } from './ttsScriptGenerator'

const script = generatePhaseButtonScript({ buttons: defaultPhaseButtons })
// 将 script 复制到 TTS 的对象 Lua 脚本中
```

注意：`parsePhaseButtonConfig` 依赖脚本结构与正则匹配，若手工改动脚本结构或缩进，可能解析失败。

### 升级表脚本 (upgrade-script-generator.ts)

公开 API：

```ts
export function generateUpgradePowerWordScript(checkboxCoordinates: [number, number][]): string
```

功能：
- 输入为复选框的像素坐标点数组（`[x, y]`），内部按 `y` 聚类为行；
- 基于 `CALIBRATION_DATA` 参考点计算像素→逻辑坐标的线性变换（scale/offset）；
- 推导 `xInitial/xOffset` 与每行 `posZ`、`count`，插入到模板 Lua 中的 `customizations` 表；
- 输出完整可用的 Lua 脚本（保留原库代码与调用约定）。

使用示例：

```ts
import { generateUpgradePowerWordScript } from './upgrade-script-generator'

const coords: [number, number][] = [
  [68, 206], [108, 206], [148, 206],
  [68, 260], [108, 260]
]

const lua = generateUpgradePowerWordScript(coords)
```

校准说明：
- `CALIBRATION_DATA` 提供两组像素/逻辑参考点用于估算线性变换；
- 若模板或图片 DPI 变化，请更新参考点以保证 `posZ` 与 `xInitial/xOffset` 精度；
- 行内列距通过首个可测的相邻 `x` 差估算，必要时可在代码中调整推导常数。

## 公共 API 参考 (API Reference)

### 配置类型与映射

```ts
// 类型
export interface FieldOption { label: string; value: string | number | null }
export interface ShowCondition { field: string; value: any; operator?: 'equals' | 'not-equals' | 'includes' | 'not-includes' }
export interface FormField { /* 见“数据结构”章节 */ }
export interface CardTypeConfig { /* 见“数据结构”章节 */ }

// 映射
export const cardTypeConfigs: Record<string, CardTypeConfig>
// 中文与英文版本各自导出，键（中文类型名）一致，文案/展示名本地化
```

字段类型语义：
- `text`/`textarea`/`number`：基础输入；
- `select`：单选，下拉选项来自 `options`；
- `multi-select`：多选；
- `string-array`：以数组形式存入（如特性）；
- `image`：图片文件，遵循 `maxSize` 限制；
- `encounter-group-select`：自定义组件，选择遭遇组。

条件显示：
- `equals`（默认）：当前表单值等于 `value` 时显示；
- `not-equals`：不等于时显示；
- `includes`/`not-includes`：用于数组或多选型值的包含判断。

哨兵值（常见）：
- 等级：`-2`=定制，`-1`=无，`0..5`=普通等级
- 费用：`-2`=X，`-1`=无，`0..99`=费用
- 生命/理智：`-2`=无限，`-1`=无，`0..`=数值

### TTS 相位按钮

```ts
export interface PhaseButton { id: string; label: string; color: string }
export interface PhaseButtonConfig { buttons: PhaseButton[] }

export const buttonLabelOptions: { value: string; label: string; emoji: string }[]
export const colorOptions: { value: string; label: string }[]
export const defaultPhaseButtons: PhaseButton[]

export function generateButtonParams(config: PhaseButtonConfig): string
export function generatePhaseButtonScript(config: PhaseButtonConfig): string
export function parsePhaseButtonConfig(luaScript: string): PhaseButtonConfig | null
```

注意：`label` 使用预设的单字符代号（见 `buttonLabelOptions.value`），对应 Arkham 图标字体。

### 升级表脚本

```ts
export function generateUpgradePowerWordScript(checkboxCoordinates: [number, number][]): string
```

输入：像素坐标数组；输出：完整 Lua 脚本字符串。

## 使用建议 (Guidelines)

- 新增卡牌类型：按现有类型模式添加 `fields`，复用 `showCondition`、`index` 组织多项字段；
- 本地化：中文/英文文件需保持键与结构一致，仅变更展示文案与 `field_type_en`；
- 校验与默认值：优先使用 `select` 枚举与哨兵值约定，减少前端校验复杂度；
- 生成器：在 TTS 中验证脚本后再固化为默认配置，避免正则解析失败；
- 图片字段：注意 `maxSize`（如 50MB）与外部图的条件显示逻辑。

