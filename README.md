# 🎴 阿卡姆印牌姬

---

<p align="center">
  <a href="https://github.com/xziying44/arkham-homebrew/releases">
    <img src="https://img.shields.io/github/v/release/xziying44/arkham-homebrew?include_prereleases&label=release" alt="release" />
  </a>
  <a href="https://github.com/xziying44/arkham-homebrew/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="license: MIT" />
  </a>
  <img src="https://img.shields.io/badge/python-3.11%2B-blue?logo=python" alt="python 3.11+" />
  <img src="https://img.shields.io/badge/vue-3.x-42b883?logo=vue.js" alt="vue 3" />
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS-informational" alt="Platform: Windows | macOS" />
</p>

<p align="center">
  <strong>简体中文</strong> |
  <a href="./README_en.md">English</a>
</p>

**阿卡姆恐怖 LCG 自定义制卡工具**

一款专为《阿卡姆恐怖：卡牌版》设计的可视化制卡工具，让您轻松创建、编辑和导出自定义卡牌，打造属于自己的恐怖冒险故事。

---

## ✨ 核心特性

### 📝 可视化卡牌编辑器
- **20+ 种卡牌类型支持**：调查员、技能、支援、事件、弱点、地点、密谋、剧本、敌人等
- **所见即所得编辑**：实时预览卡牌效果，直观调整设计
- **智能表单系统**：根据卡牌类型自动显示相关字段，简化编辑流程

### 🌐 双语支持
- **界面语言**：中文/英文界面随意切换
- **字体系统**：自动适配中英文字体，支持混排
- **富文本渲染**：支持 HTML 风格标签（粗体、斜体、图标、换行等）

### 🎨 高级排版控制
- **插画变换编辑**：精确调整图片的缩放、裁剪、旋转、位移和翻转
- **文字边界编辑**：自定义文本区域位置和大小，实现复杂排版
- **模板系统**：305+ 精美卡牌模板，覆盖全系列卡牌类型

### 📦 内容包管理
- **项目组织**：基于工作区的文件管理，支持大型项目
- **遭遇组系统**：轻松管理剧本/战役中的卡组结构
- **批量操作**：支持内容包级别的批量导出和编号

### 🎲 多格式导出
- **图片导出**：PNG/JPG 格式，支持自定义 DPI 和出血
- **PDF 导出**：适合打印的拼版 PDF，支持 A4/Letter 等规格
- **TTS 导出**：一键生成 Tabletop Simulator 脚本和对象
- **ArkhamDB 导出**：导出为 ArkhamDB 格式，方便分享

### 🚀 专业功能
- **AI 出血处理**：使用 LaMa 或镜像算法自动生成出血区域
- **GitHub 图床**：集成图床功能，快速分享卡牌图片
- **牌组构建器**：支持复杂的 DeckOption 系统，构建可选牌组
- **升级卡系统**：调查员升级卡与 Power Word 脚本支持

---

## 📥 安装与启动

### Windows 系统

1. **下载应用**
   访问 [GitHub Releases](https://github.com/xziying44/arkham-homebrew/releases) 页面，下载最新版本的 `arkham-homebrew-windows-x64.zip`

2. **解压文件**
   将 ZIP 文件解压到任意目录（建议路径不包含中文）

3. **运行程序**
   双击 `Arkham Card Maker.exe` 启动应用

**目录结构说明（Windows 发行版示例）**：

```text
Arkham Card Maker/
├── Arkham Card Maker.exe   # 主程序（双击启动）
├── _internal/              # 运行时依赖与资源
│   ├── fonts/              # 字体资源
│   ├── images/             # 模板与美术资源
│   ├── templates/          # TTS 脚本等模板
│   └── ...                 # 其他内部依赖
├── logs/                   # 运行日志
├── global_config.json      # 全局配置
└── recent_directories.json # 最近使用的工作区记录
```

### macOS 系统

1. **下载应用**
   访问 [GitHub Releases](https://github.com/xziying44/arkham-homebrew/releases) 页面，根据您的 Mac 芯片类型下载：
   - **Apple Silicon（M1/M2/M3）**：下载 `Arkham-Card-Maker-macOS-arm64.dmg`
   - **Intel 芯片**：下载 `Arkham-Card-Maker-macOS-x86_64.dmg`

2. **安装应用**
   - 双击 `.dmg` 文件打开安装器
   - 将 "Arkham Card Maker" 拖入 "Applications" 文件夹

3. **首次运行**
   - 打开 "应用程序" 文件夹，找到 "Arkham Card Maker"
   - 右键点击，选择 "打开"（首次需要授权运行未签名应用）
   - 在弹出的安全提示中点击 "打开"

---

## 🚀 快速入门

### 第一步：选择工作区

首次启动后，您需要选择或创建一个工作区目录用于存储卡牌文件：

1. 点击 **"选择工作目录"** 按钮
2. 选择一个空目录或新建文件夹（建议为每个项目创建独立目录）
3. 应用会自动加载工作区文件树

### 第二步：创建第一张卡牌

1. **新建卡牌文件**
   在左侧文件树中右键点击目录，选择 **"新建文件"**，输入文件名（如 `my-card.card`）

2. **选择卡牌类型**
   在编辑面板中，从 **"卡牌类型"** 下拉菜单选择类型（如"技能"、"支援"等）

3. **填写卡牌信息**
   根据表单提示填写卡牌字段：
   - **基础信息**：卡牌名称、副标题、特质等
   - **数值属性**：费用、技能图标、生命/理智等
   - **文本内容**：卡牌描述、规则文本、引用文字等
   - **插画设置**：上传或选择插画图片

4. **实时预览**
   右侧预览面板会实时显示卡牌效果，调整满意后点击 **"保存"**

### 第三步：高级编辑（可选）

如果需要更精细的排版控制：

- **插画布局编辑**：点击 **"插画布局"** 标签页，调整图片的缩放、裁剪、旋转等参数
- **文字边界编辑**：点击 **"文字边界"** 标签页，自定义文本区域的位置和大小

### 第四步：导出卡牌

完成编辑后，您可以导出为多种格式：

1. **单卡导出**
   - 点击卡牌编辑器右上角的 **"导出"** 按钮
   - 选择格式（PNG/JPG）、规格（标准/Poker/Tarot 等）和出血选项
   - 点击确认，图片将保存到工作区对应目录

2. **批量导出**
   - 切换到 **"TTS 导出"** 页面
   - 选择内容包或遭遇组
   - 点击 **"导出 TTS"** 或 **"导出 PNP PDF"**，批量生成所有卡牌

---

## 📖 更多资源

- **用户指南**：[完整用户手册](docs/user-guide-zh.md)（详细功能说明与高级用法）
- **GitHub 仓库**：[https://github.com/xziying44/arkham-homebrew](https://github.com/xziying44/arkham-homebrew)
- **问题反馈**：[提交 Issue](https://github.com/xziying44/arkham-homebrew/issues)
- **更新日志**：[查看 Releases](https://github.com/xziying44/arkham-homebrew/releases)

---

## 🤝 贡献与反馈

如果您在使用过程中遇到问题或有改进建议，欢迎通过以下方式参与：

- 在 GitHub 提交 [Issue](https://github.com/xziying44/arkham-homebrew/issues)
- 发送邮件至项目维护者
- 参与讨论和功能建议

---

## 📄 许可证

本项目采用 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。

---

**感谢您使用阿卡姆印牌姬！祝您创作愉快！** 🎉
