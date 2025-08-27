**简体中文** | [English](./README_en.md)

# 阿卡姆印牌姬

一个基于Flask的自动化卡牌生成工具，支持通过OpenAI生成卡牌JSON数据并转换为精美卡牌图像。

## 功能特性

- 🖼️ 可视化卡牌设计界面
- 🤖 集成OpenAI智能生成卡牌内容
- 🎨 支持自定义字体、图片资源和样式模板
- 📦 提供多种卡牌类型支持：
    - 调查员卡
    - 技能卡
    - 支援卡
    - 事件卡
    - 弱点卡
    - 升级卡
- 🌐 基于Web的桌面应用程序（使用Pywebview）

## 快速开始

### 免安装运行（Windows系统）

1. 访问 [Releases页面](https://github.com/xziying44/arkham-homebrew/releases)
2. 下载最新版本的 `arkham-homebrew-windows-x64.zip`
3. 解压到任意目录
4. 双击运行 `Arkham Card Maker.exe`

#### 目录结构说明

```
.
├── app.exe     # 主程序
├── _internal/             # 运行时依赖（请勿修改）
├── fonts/                 # 字体资源（必需）
├── images/                # 卡牌模板（必需）
├── prompt/                # 提示词目录（必需）
└── config.json            # 配置文件（首次运行自动生成）
```

### 环境要求

- Python 3.9+
- [要求字体文件](fonts/)
- [必要图片资源](images/)

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/xziying44/arkham-homebrew.git

# 安装依赖
pip install -r requirements.txt
```

### 启动应用

```bash
python app.py
```

## 项目结构

```
.
├── app.py                 # 主程序入口
├── Card.py                # 卡牌渲染核心逻辑
├── create_card.py         # 卡牌生成处理器
├── requirements.txt       # 依赖列表
├── config.json            # 配置文件
├── fonts/                 # 字体资源
├── images/                # 图片模板
├── static/                # 静态资源
└── templates/             # HTML模板
```

## 开发指南

### 扩展卡牌类型

1. 在`create_card.py`中添加新的处理函数
2. 在`Card.py`中扩展`Card`类的渲染方法
3. 添加对应的图片模板到`images/`目录

## 贡献方式

欢迎通过Issue和PR参与贡献！请遵循以下流程：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/your-feature`)
3. 提交修改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建Pull Request

## License

And of course:

MIT: [https://rem.mit-license.org](https://rem.mit-license.org/)
