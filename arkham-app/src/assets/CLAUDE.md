[根目录](../../../CLAUDE.md) > [arkham-app](../../) > [src](../) > **assets**

## Purpose and Scope

作为 arkham-app 前端模块的静态资源集合（Memory: Part of arkham-app frontend module providing static assets），本目录提供应用运行所需的图片与图标文件：
- 卡牌背面图像（玩家卡、遭遇卡）
- 通用示例图标（`vue.svg` 作为占位图标）

资源用于：前端 UI 渲染、卡牌预览、卡组编辑与导出（含 TTS）。

## Structure Overview

纯资源目录，按类别分层组织。当前结构：

```
assets/
├── vue.svg                      (0.50 KB) - Vue 标志（示例/占位）
└── cardbacks/                   - 卡牌背面图像子模块
    ├── player-back.jpg          (156.78 KB) - 玩家卡背面
    ├── encounter-back.jpg       (128.66 KB) - 遭遇卡背面
    └── CLAUDE.md                - 子目录文档（详细说明与集成点）
```

组织约定：
- 同类资源集中在子目录（如 `cardbacks/`）。
- 文件名使用短横线连接的语义化命名（`player-back.jpg`）。
- 采用浏览器原生支持的图片格式（JPG、SVG）。

## Key Components

### 资源分类
- 图像（JPG）
  - `cardbacks/player-back.jpg`：玩家卡标准背面图像
  - `cardbacks/encounter-back.jpg`：遭遇卡标准背面图像
- 图标（SVG）
  - `vue.svg`：示例/占位图标（当前无强绑定使用场景）

### 命名与组织模式
1. 目录即语义：按用途分目录（`cardbacks/`）。
2. 名称即角色：`{type}-{variant}.{ext}`（如 `player-back.jpg`）。
3. 文档伴随：子目录配套 `CLAUDE.md` 说明（参见 `cardbacks/CLAUDE.md`）。

### 资产清单（Inventory）
- `src/assets/vue.svg` — SVG 图标，占位/示例；当前未在代码中直接引用
- `src/assets/cardbacks/player-back.jpg` — 玩家卡背面（DeckEditor 预览/选择、导出流程）
- `src/assets/cardbacks/encounter-back.jpg` — 遭遇卡背面（DeckEditor 预览/选择、导出流程）

## Dependencies

### Internal
- 前端构建与静态资源管线：Vite（原样拷贝与哈希处理）
- 使用组件：`src/components/DeckEditor.vue`（卡背选择与预览）
- 参考文档：`src/assets/cardbacks/CLAUDE.md`（子模块详细说明）

### External
- 浏览器对 JPG/SVG 的原生渲染支持
- 后端导出工具链（如 Pillow 等）在后端侧引用图像文件（详情见子模块文档）

## Integration Points

前端通过相对路径或模块导入方式使用资源：

- 模板直接引用（预览图）：
  - `src/components/DeckEditor.vue:230` → `../assets/cardbacks/player-back.jpg`
  - `src/components/DeckEditor.vue:240` → `../assets/cardbacks/encounter-back.jpg`

- 模块化导入（编译期处理与按需打包）：
  - `src/components/DeckEditor.vue:341` → `import playerBack from '@/assets/cardbacks/player-back.jpg'`
  - `src/components/DeckEditor.vue:342` → `import encounterBack from '@/assets/cardbacks/encounter-back.jpg'`

资源加载说明：
- 前端：由 Vite 处理静态资源，路径别名 `@` 指向 `src/`。
- 后端/脚本：如需组合导出，按相对路径读取 `arkham-app/src/assets/...`（具体流程见子模块文档）。

## Implementation Notes

### 设计与维护
1. 资源外部化：静态资源与业务代码分离，替换升级不影响逻辑层。
2. 可替换性：如需更新背面设计，直接替换同名 JPG（保持尺寸/格式一致）。
3. 可扩展性：新增类别时创建语义化子目录并补充 `CLAUDE.md`。

### 性能与构建
- JPG 文件大小控制在百 KB 量级，满足预览与导出平衡。
- Vite 对静态资源进行指纹与缓存优化；SVG 体积小，渲染开销低。

### 已知限制
- 当前仅包含两种标准卡背与一个示例 SVG，未提供变体/主题化方案。
- `vue.svg` 作为占位图标，暂未在代码中发现直接引用。
