# arkham-app/src

## Purpose and Scope
本目录为前端应用的源码根目录（Vue 3 + TypeScript）。负责应用启动、全局配置、页面与组件装配、服务层对接、国际化资源与类型定义的统一组织，是前端开发的主要工作区。

- 主要职责：
  - 应用初始化与挂载
  - 页面切换与全局主题管理
  - 组件装配与 UI 渲染
  - 服务层（api/）统一接入
  - 多语言（locales/）加载与使用
  - 类型与配置集中管理（types/、config/）

## Structure Overview
```
src/
├── main.ts                  应用入口与初始化
├── App.vue                  根组件（主题/导航/消息）
├── style.css                全局样式
├── vite-env.d.ts            Vite 类型声明
├── api/                     后端通信与服务封装（详见 ./api/CLAUDE.md）
├── assets/                  静态资源（详见 ./assets/CLAUDE.md）
├── components/              可复用组件（详见 ./components/CLAUDE.md）
├── config/                  配置与生成器（详见 ./config/CLAUDE.md）
├── locales/                 国际化（详见 ./locales/CLAUDE.md）
├── pages/                   页面与工作区（详见 ./pages/CLAUDE.md）
└── types/                   类型定义（详见 ./types/CLAUDE.md）
```

## Key Components
### main.ts
- 描述：应用入口与初始化逻辑。
- 职责：
  - 创建并挂载 Vue 应用实例
  - 注册 i18n 插件
  - 全局右键菜单管控（允许输入/可编辑元素保留）
  - 引入全局字体与样式
- 公开 API：无（不导出任何成员）。

### App.vue
- 描述：根组件，提供全局主题、消息与页面装配。
- 职责：
  - 通过 Naive UI 的 `NConfigProvider`、`NMessageProvider` 提供全局配置/消息
  - 基于本地状态管理简易页面切换（Home ↔ Workspace）
  - 统一处理“深浅色主题”切换
- 关键状态：
  - `theme: GlobalTheme | null` — 当前主题（null=亮色，darkTheme=暗色）
  - `currentPage: 'home' | 'workspace'` — 当前页面
  - `workspaceParams: { mode: 'file'|'folder'; projectPath: string; projectName: string }`
- 关键方法（内部）：
  #### `toggleTheme(): void`
  - 作用：切换全局主题（亮/暗）。
  - 参数：无
  - 返回：(void)
  - Throws：不抛出

  #### `navigateToWorkspace(params: { mode: 'file' | 'folder'; projectPath: string; projectName: string }): void`
  - 作用：设置工作区参数并切换到工作区页面。
  - 参数：
    • params.mode ('file'|'folder')：打开模式；
    • params.projectPath (string)：项目路径；
    • params.projectName (string)：项目名称；
  - 返回：(void)
  - Throws：不抛出

  #### `navigateToHome(): void`
  - 作用：切换回首页。
  - 参数：无
  - 返回：(void)
  - Throws：不抛出

### style.css
- 描述：全局样式与桌面应用容器布局约束。
- 职责：
  - 统一字体、色彩与交互控件基础样式
  - 调整 `#app` 占满可视区域，禁用页面层滚动

### vite-env.d.ts
- 描述：Vite 的类型提示与环境声明。
- 公开 API：无。

## Dependencies
### Internal Dependencies
- `./api/` — 服务层封装（HTTP 客户端、领域服务、类型），详见 `api/CLAUDE.md`
- `./components/` — 复用组件与编辑器模块，详见 `components/CLAUDE.md`
- `./config/` — 卡牌类型配置与脚本生成器，详见 `config/CLAUDE.md`
- `./locales/` — 中英文本地化资源与初始化，详见 `locales/CLAUDE.md`
- `./pages/` — 顶层页面与工作区子页面，详见 `pages/CLAUDE.md`
- `./types/` — 全局共享类型，详见 `types/CLAUDE.md`

### External Dependencies
- `vue` — 应用框架与 `<script setup>` 组合式 API
- `naive-ui` — UI 组件库（主题、全局样式、消息容器等）
- `vue-i18n` — 国际化插件
- `vfonts` — 全局字体（Lato、FiraCode）
- 其他（由子模块直接依赖）：`axios`、`date-fns-tz`、`uuid` 等（详见对应子目录文档）

## Integration Points
### Public APIs
- 本目录不对外导出公共函数/类。对外交互能力由子模块（`api/`、`components/`、`pages/` 等）各自暴露；请参阅相应子目录的 `CLAUDE.md`。

### Data Flow
- 启动流程：
  1) `main.ts` 创建应用 → 注册 `i18n` → 绑定右键管控；
  2) 挂载到 `#app`；
  3) `App.vue` 提供全局主题/消息 → 按 `currentPage` 渲染页面；
- 页面导航：
  - HomePage 通过事件请求进入 Workspace（详见 `pages/CLAUDE.md`）；
  - WorkspacePage 通过事件请求返回 Home（详见 `pages/CLAUDE.md`）。
- 主题传递：
  - `App.vue` 作为单一主题源，通过 Props 将 `isDark` 传递至页面/组件树。

## Implementation Notes
### Design Patterns
- Provider（配置提供者）：使用 `NConfigProvider` 与 `NMessageProvider` 提供全局主题与消息能力。
- Service Layer（服务分层）：后端交互统一经 `api/` 服务模块完成。
- Composition API：统一采用 Vue 3 `<script setup>` 语法组织逻辑。

### Technical Decisions
- 简化路由：不引入 Vue Router，使用本地状态管理页面切换，贴合桌面应用使用场景。
- 右键行为：默认禁用页面级右键，仅保留输入类/可编辑元素右键，提高一致性与误触防护。
- 字体引入：在入口统一引入 Lato 与 FiraCode，确保渲染一致性。

### Considerations
- 性能：
  - 页面按需渲染；建议对大列表采用虚拟滚动（由具体组件实现）。
  - 可在页面/组件层引入懒加载进行代码分割（当前未实现）。
- 安全：
  - 服务层需进行响应校验与错误兜底；
  - 路径与用户输入必须在调用服务前进行基本清洗；
  - 禁止在 UI 中泄漏底层错误细节（统一转为用户可读提示）。
- 配置/环境：
  - Vite 开发代理见项目根的 `vite.config.ts`；
  - TypeScript 配置见项目根的 `tsconfig.json`。
- 限制：
  - 无浏览器历史/深链支持；
  - 页面右键全局禁用策略在某些浏览器扩展下可能受影响。

---
子目录文档引用（不重复内容）：
- `./api/CLAUDE.md`
- `./assets/CLAUDE.md`
- `./components/CLAUDE.md`
- `./config/CLAUDE.md`
- `./locales/CLAUDE.md`
- `./pages/CLAUDE.md`
- `./types/CLAUDE.md`
