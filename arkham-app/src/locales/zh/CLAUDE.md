# Chinese Localization Module (zh)

## Purpose and Scope
提供阿卡姆印牌姬应用的中文本地化资源，覆盖应用主要功能域（主页、设置、工作空间、卡组构建、卡牌编辑、TTS 脚本/物品等）。本模块的职责是以一致的键值结构为 UI 提供中文字符串，确保与 `en/` 模块保持一一对应的键路径和组织方式。

## Structure Overview
本目录按“功能域”拆分多个本地化子模块，由 `index.ts` 聚合导出。文件组织：
- `index.ts`：聚合并默认导出 zh 语言的本地化对象
- 其余每个 `.ts` 文件对应该功能域的文案键值对象（`export default { ... }`）

子模块文件（节选）：
- `common.ts`：通用按钮/状态/消息
- `home.ts`：首页文本（最近项目、服务状态等）
- `settings.ts`：设置页面文本
- `workspace.ts` / `workspaceMain.ts`：工作空间与主视图
- `deckBuilder.ts` / `deckOptionEditor.ts`：卡组构建与选项编辑
- `cardEditor.ts`：卡牌编辑器
- `contentPackage.ts`：内容包管理
- `ttsItems.ts` / `ttsScriptEditor.ts`：TTS 物品与脚本编辑
- `about.ts`、`languageWelcome.ts`、`arkhamdbImport.ts` 等

## Key Components
### `index.ts`
- 描述：聚合当前目录下各功能子模块并默认导出一个命名空间对象
- 责任：保证键路径组织一致，供 `src/locales/index.ts` 的 `messages.zh` 使用
- 导出：
  ```ts
  export default {
    common,
    home,
    settings,
    workspace,
    workspaceMain,
    ttsItems,
    contentPackage,
    about,
    deckBuilder,
    cardEditor,
    ttsScriptEditor,
    deckOptionEditor,
    languageWelcome,
    arkhamdbImport,
  }
  ```

### 子模块（通用说明）
- 描述：各文件 `export default` 一个仅含字符串与嵌套对象的字典，键语义与 `en/` 完全一致
- 责任：为对应功能域提供 UI 文案；不包含运行时逻辑或函数导出
- 重要约束：新增键必须在 `en/` 与 `zh/` 同步创建，路径一致

## Dependencies
### Internal Dependencies
- `../en` - 英文本地化模块（需保持同构键路径，便于切换与回退）
- `../index.ts` - 语言聚合与 Vue I18n 初始化入口（使用本模块导出）

### External Dependencies
- 无直接第三方依赖（本目录仅导出常量对象）。集成时由上层通过 `vue-i18n` 消费。

## Integration Points
### Public APIs
- 默认导出：`Record<string, unknown>` 形态的命名空间对象，供 `vue-i18n` 的 `messages.zh` 使用

### Data Flow
- 输入：无（静态字典）
- 处理：上层 `createI18n({ messages: { zh, en } })` 挂载本模块
- 输出：组件通过 `$t('<domain>.<key>')` 访问对应中文字符串；缺失键根据 `fallbackLocale` 回退

## Implementation Notes
### Design Patterns
- 模块化字典：按功能域分拆，降低单文件体积与变更冲突
- 键路径一致性：与 `en/` 严格对齐，保证切换语言时键稳定

### Technical Decisions
- 仅导出常量对象，避免运行时副作用
- 通过 `index.ts` 聚合，便于在父级统一注册

### Considerations
- 性能：纯静态对象，加载开销极低；建议保持键粒度合理避免超大单文件
- 安全：不包含动态执行；注意避免在字符串中嵌入未转义的用户数据
- 限制：本目录不提供函数或类型导出；国际化占位使用 `$t` 插值（如 `{name}`）由上层处理

