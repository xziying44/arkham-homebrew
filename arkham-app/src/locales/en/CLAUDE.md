# English Localization Module (en)

## Purpose and Scope

提供阿卡姆印牌姬应用的英文本地化字符串和内容。本模块包含所有UI界面、对话、提示信息的英文翻译，支持国际化功能。包括卡牌编辑、卡牌组管理、TTS脚本编辑等各个功能模块的本地化字符串。

## Structure Overview

本模块是一个TypeScript/JavaScript本地化资源集合，包含15个导出文件，每个文件对应应用的一个功能模块：

```
en/
├── index.ts                   (878 B) - 导出所有本地化字符串的入口
├── common.ts                  (754 B) - 通用术语和常用短语
├── about.ts                   (2658 B) - 关于页面内容
├── arkhamdbImport.ts          (2602 B) - ArkhamDB导入功能
├── cardEditor.ts              (7188 B) - 卡牌编辑器UI文本
├── deckBuilder.ts             (9132 B) - 卡牌组构建器UI文本
├── deckOptionEditor.ts        (5449 B) - 卡牌组选项编辑器UI文本
├── contentPackage.ts          (19785 B) - 内容包管理UI文本
├── home.ts                    (2474 B) - 主页UI文本
├── languageWelcome.ts         (579 B) - 语言选择欢迎文本
├── settings.ts                (2427 B) - 设置页面UI文本
├── ttsItems.ts                (2451 B) - TTS物品管理UI文本
├── ttsScriptEditor.ts         (4728 B) - TTS脚本编辑器UI文本
├── workspace.ts               (379 B) - 工作空间UI文本
└── workspaceMain.ts           (10902 B) - 工作空间主模块UI文本
```

## Key Components

### 核心导出文件

#### `index.ts`
- **用途**: 聚合并导出所有英文本地化字符串
- **导出**: 统一的本地化对象，包含所有子模块的字符串
- **结构**:
  ```typescript
  export default {
    common: {...},
    about: {...},
    arkhamdbImport: {...},
    // ... 其他模块
  }
  ```

### 功能性本地化模块

#### `common.ts`
- **用途**: 提供通用术语、按钮标签、通用操作文本
- **典型内容**: "确定", "取消", "保存", "删除", "编辑"等通用文本
- **使用场景**: 跨多个模块共享的UI元素

#### `cardEditor.ts`
- **用途**: 卡牌编辑功能的UI文本
- **包含**: 卡牌属性标签、编辑提示、验证消息
- **关键字符串**: 卡牌类型、属性名称、编辑说明

#### `deckBuilder.ts`
- **用途**: 卡牌组构建界面的本地化字符串
- **包含**: 卡牌选择、数量调整、费用计算相关文本
- **规模**: 9.1 KB，包含详细的UI文本

#### `contentPackage.ts`
- **用途**: 内容包管理功能的UI文本（最大的本地化文件）
- **包含**: 内容包导入、导出、管理、验证等相关字符串
- **规模**: 19.3 KB，包含广泛的内容管理相关术语

#### `ttsScriptEditor.ts`
- **用途**: TTS（Tabletop Simulator）脚本编辑器的UI文本
- **包含**: 脚本编辑提示、语法帮助、操作指南

#### `workspaceMain.ts`
- **用途**: 工作空间主模块的核心UI文本（第二大文件）
- **规模**: 10.7 KB
- **包含**: 工作空间操作、文件管理、状态提示

### 其他模块化文件

#### `arkhamdbImport.ts`
- **用途**: ArkhamDB卡牌库导入功能文本
- **包含**: 导入步骤说明、数据映射提示、导入结果消息

#### `deckOptionEditor.ts`
- **用途**: 卡牌组选项编辑界面文本
- **包含**: 选项标签、配置说明、约束条件文本

#### `about.ts`
- **用途**: 应用程序关于页面信息
- **包含**: 版本号、开发者信息、致谢等

#### `home.ts`
- **用途**: 应用主页面文本
- **包含**: 欢迎信息、快速开始指南

#### `languageWelcome.ts`
- **用途**: 语言选择界面欢迎文本
- **包含**: 多语言支持的初始提示

#### `settings.ts`
- **用途**: 应用设置页面的配置选项文本
- **包含**: 首选项名称、说明、提示信息

#### `ttsItems.ts`
- **用途**: TTS物品列表管理的UI文本
- **包含**: 物品操作、分类标签

#### `workspace.ts`
- **用途**: 工作空间基础操作文本
- **包含**: 工作空间管理的基本术语

## Dependencies

### Internal Dependencies
- `arkham-app/src/locales/index.ts` - 母模块，聚合所有语言
- `arkham-app/src/locales/zh` - 中文本地化对应模块，应保持结构一致

### External Dependencies
- **Vue I18n** (`vue-i18n`) - 国际化框架，提供本地化字符串管理
- **TypeScript** - 类型检查，确保本地化字符串的一致性

## Integration Points

### Public APIs
- **导出对象**: 默认导出包含所有英文本地化字符串的对象
  ```typescript
  export default {
    common: { /* common.ts content */ },
    about: { /* about.ts content */ },
    // ... other modules
  }
  ```

### Data Flow
1. **初始化流程**:
   - Vue应用启动时，Vue I18n加载本地化模块
   - 用户选择语言或根据系统设置自动选择英文

2. **字符串使用流程**:
   - 前端组件通过`$t()`函数或`useI18n()`钩子访问本地化字符串
   - 动态更新UI显示内容

3. **字符串查询路径**:
   - `$t('en.common.ok')` - 访问common模块的"ok"字符串
   - `$t('en.cardEditor.title')` - 访问cardEditor模块的"title"字符串

### 集成约束
- 每个组件的本地化字符串通过`$t()`键值查询
- 遵循模块化的字符串组织，确保易于维护

## Implementation Notes

### Design Patterns
- **模块化本地化**: 按功能模块组织字符串，降低复杂度
- **单一责任**: 每个文件对应一个功能域

### 技术决策
1. **TypeScript格式**: 使用TypeScript提供类型安全和IDE支持
2. **按功能模块组织**: 便于维护和本地化协作
3. **统一导出**: 通过index.ts聚合，简化集成

### 本地化维护
- 为保持一致性，所有新的UI文本应在此模块中添加
- 应与zh模块同步更新，保持两种语言的特性一致

### 与中文模块的关系
- 结构必须完全相同，便于翻译维护
- 如在en中添加新字符串，必须同时在zh中添加相应翻译
- 使用对齐的键值，确保本地化键的一致性

### 性能考虑
- 本地化字符串延迟加载，不会显著影响应用启动时间
- 字符串使用键值查询，性能开销极小

### 已知限制
- 仅支持en和zh两种语言（由zh模块同步维护）
- 不支持动态加载额外语言
- 字符串中的变量需要通过I18n的插值机制处理
