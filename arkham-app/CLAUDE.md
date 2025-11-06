[根目录](../../CLAUDE.md) > [arkham-app](../) > **arkham-app**

## 变更记录 (Changelog)

- **2025-10-12**: 初始化模块文档，更新组件结构说明
- **2025-10-12**: 已存在基础文档，本次更新添加了更详细的组件说明

## 模块职责

arkham-app是阿卡姆印牌姬项目的前端模块，基于Vue 3 + TypeScript + Vite构建。它提供了现代化的用户界面，用于卡牌设计、编辑、管理和导出。该模块通过RESTful API与Python后端通信，实现完整的卡牌生成工作流。

## 入口与启动

### 主入口文件
- **src/main.ts**: 应用程序入口点，负责Vue应用初始化、多语言配置和全局设置

### 开发命令
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 应用配置
- **vite.config.ts**: Vite构建配置，包括开发服务器代理设置
- **tsconfig.json**: TypeScript编译配置
- **package.json**: 项目依赖和脚本定义

## 对外接口

### API服务层 (src/api/)

该模块包含了与后端通信的所有API接口：

- **http-client.ts**: HTTP客户端封装，提供统一的请求处理
- **endpoints.ts**: API端点定义
- **types.ts**: TypeScript类型定义
- **index.ts**: API服务统一导出

#### 主要服务模块
1. **directory-service.ts**: 目录选择和管理
2. **workspace-service.ts**: 工作空间操作
3. **config-service.ts**: 配置管理
4. **card-service.ts**: 卡牌生成和管理
5. **tts-export-service.ts**: TTS导出功能
6. **ai-service.ts**: AI相关服务
7. **github-service.ts**: GitHub集成

### 组件接口

所有Vue组件都遵循以下接口规范：
- 使用`<script setup>`语法
- 通过props接收父组件数据
- 通过emit向父组件发送事件
- 支持TypeScript类型检查

## 关键依赖与配置

### 核心依赖
- **Vue 3.5.18**: 前端框架
- **Naive UI 2.42.0**: UI组件库
- **Vue I18n 9.14.5**: 国际化支持
- **Axios 1.11.0**: HTTP客户端
- **date-fns-tz 3.2.0**: 日期时区处理
- **uuid 11.1.0**: 唯一ID生成

### 开发依赖
- **Vite 7.1.2**: 构建工具
- **TypeScript 5.8.3**: 类型系统
- **Vue TSC 3.0.5**: Vue TypeScript编译器
- **@vitejs/plugin-vue 6.0.1**: Vue插件

### 配置文件
- **src/config/cardTypeConfigs.ts**: 中文卡牌类型配置
- **src/config/cardTypeConfigsEn.ts**: 英文卡牌类型配置
- **src/config/ttsScriptGenerator.ts**: TTS脚本生成器
- **src/config/upgrade-script-generator.ts**: 升级脚本生成器

## 数据模型

### 卡牌数据结构
```typescript
interface CardData {
  id: string;
  type: CardType; // 调查员、技能、支援、事件、弱点、升级
  name: string;
  text: string;
  // ...其他卡牌属性
}
```

### 工作空间数据结构
```typescript
interface Workspace {
  path: string;
  name: string;
  cards: CardData[];
  settings: WorkspaceSettings;
}
```

详细类型定义请参考 `src/api/types.ts`

## 测试与质量

### 测试策略
- 组件单元测试 (待实现)
- API接口测试 (待实现)
- E2E测试 (待实现)

### 代码质量工具
- **ESLint**: 代码风格检查 (配置待添加)
- **Prettier**: 代码格式化 (配置待添加)
- **TypeScript**: 类型检查

## 常见问题 (FAQ)

### Q: 如何添加新的卡牌类型？
A: 需要同时修改以下文件：
1. 更新 `src/api/types.ts` 中的类型定义
2. 在 `src/config/` 中添加新的配置
3. 创建对应的Vue组件
4. 更新API服务

### Q: 如何添加新的语言支持？
A:
1. 在 `src/locales/` 下创建新的语言文件夹
2. 添加对应的翻译文件
3. 更新 `src/locales/index.ts` 配置

### Q: 前端如何与后端通信？
A: 通过 `src/api/` 中的服务模块，所有API调用都经过统一的HTTP客户端处理。

## 相关文件清单

### 核心文件
- `src/main.ts` - 应用入口
- `src/App.vue` - 根组件
- `src/style.css` - 全局样式

### 页面组件 (src/pages/)
- `HomePage.vue` - 首页
- `WorkspacePage.vue` - 工作空间页面
- `workspace/WorkspaceMain.vue` - 主工作区
- `workspace/DeckBuilder.vue` - 卡组构建器
- `workspace/TTSItems.vue` - TTS项目管理
- `workspace/Settings.vue` - 设置页面
- `workspace/About.vue` - 关于页面

### 功能组件 (src/components/)
- `FileTreePanel.vue` - 文件树面板
- `FormEditPanel.vue` - 表单编辑面板
- `ImagePreviewPanel.vue` - 图片预览面板
- `IllustrationLayoutEditor.vue` - 插图布局编辑器
- `DeckEditor.vue` - 卡组编辑器
- `TtsScriptEditor.vue` - TTS脚本编辑器
- `TTSExportGuide.vue` - TTS导出指南
- `ResizeSplitter.vue` - 可调整大小的分割器
- `WorkspaceSidebar.vue` - 工作空间侧边栏
- `FormField.vue` - 表单字段组件

### 资源文件
- `src/assets/cardbacks/` - 卡背图片
- `public/` - 公共静态资源

### 配置文件
- `vite.config.ts` - Vite配置
- `tsconfig.json` - TypeScript配置
- `tsconfig.app.json` - 应用TypeScript配置
- `tsconfig.node.json` - Node.js TypeScript配置

## 开发注意事项

1. **API调用**: 所有后端API调用都应通过 `src/api/` 中的服务模块进行
2. **类型安全**: 充分利用TypeScript的类型系统，避免使用 `any`
3. **组件复用**: 优先使用Naive UI组件，自定义组件应该具有良好的复用性
4. **国际化**: 所有用户可见的文本都应该通过i18n系统处理
5. **性能优化**: 大量数据渲染时考虑使用虚拟滚动或分页