# GitHub Actions 工作流

## 目的和范围

该目录包含GitHub Actions自动化工作流配置，用于构建和发布应用程序。主要职责包括为macOS平台编译应用、生成可分发的二进制文件，以及支持多种架构的构建。这些工作流作为项目的CI/CD管道，确保代码质量和发布流程的自动化。

## 结构概览

```
.github/workflows/
├── build-macos.yml              - macOS基础构建工作流
├── build-macos-multi-arch.yml   - macOS多架构构建工作流（ARM64和x86_64）
└── build-macos-pyinstaller.yml  - 使用PyInstaller的macOS构建工作流
```

## 主要组件

### build-macos.yml
- **描述**: 基础的macOS构建工作流
- **职责**: 为macOS平台编译应用，生成初始的可执行文件
- **触发条件**: 代码提交或手动触发
- **关键步骤**:
  - 设置Python环境
  - 安装依赖项
  - 构建应用
  - 上传构建产物

### build-macos-multi-arch.yml
- **描述**: 支持多种CPU架构的构建工作流
- **职责**: 为ARM64（Apple Silicon）和x86_64（Intel）架构分别编译应用
- **关键特性**:
  - 并行构建不同架构
  - 生成架构特定的二进制文件
  - 支持通用二进制（Universal Binary）

### build-macos-pyinstaller.yml
- **描述**: 使用PyInstaller工具的高级构建工作流
- **职责**: 将Python应用打包成独立的macOS可执行文件
- **关键步骤**:
  - PyInstaller配置和编译
  - 代码签名和公证（Notarization）
  - 生成DMG安装包
  - 发布到GitHub Releases

## 依赖项

### 内部依赖
- `app.py` - 主应用程序入口
- `requirements.txt` - Python依赖列表
- `arkham-app/` - 前端应用（需要编译）

### 外部依赖
- **GitHub Actions** - 工作流执行环境
- **Python** - 运行时环境（3.9+）
- **PyInstaller** - Python应用打包工具
- **Node.js** - 前端资源构建（npm）
- **macOS SDK** - 系统级编译工具链

## 集成点

### 触发事件
- 代码推送（push）到主分支
- GitHub Release发布
- 手动工作流触发（workflow_dispatch）

### 输出产物
- 编译后的可执行文件
- DMG安装包
- 构建日志和产物
- 发布到GitHub Releases

### 上游依赖
- arkham-app前端构建完成
- 所有Python依赖可用

## 实现说明

### 设计模式
- **管道模式**: 多个构建阶段顺序执行
- **矩阵构建**: build-macos-multi-arch.yml使用strategy矩阵实现多架构并行构建

### 技术决策
- **PyInstaller选择**: 相比其他打包工具，PyInstaller对包含C扩展和外部依赖的项目支持更好
- **多架构支持**: 同时支持Intel和Apple Silicon架构，提升用户体验
- **自动化发布**: 工作流直接发布到GitHub Releases，简化发布流程

### 重要配置
- Python版本: 3.9+（应与本地开发环境匹配）
- macOS最低版本: 10.13+（根据PyInstaller要求）
- 代码签名: 使用GitHub提供的证书（如需代码签名）

### 性能考虑
- 多架构构建会增加总体构建时间（约2倍）
- 建议使用缓存加速依赖安装
- 构建产物大小: ~100-200MB（因包含完整Python运行时）

### 安全考虑
- 不在工作流中存储密钥或令牌（使用GitHub Secrets）
- 若需发布到外部服务，使用GitHub提供的加密Secrets
- 构建产物应在签名后公证，确保macOS认可

### 已知限制
- 仅支持macOS构建（不支持Linux/Windows构建）
- 构建机器需要充足的存储空间（至少10GB可用空间）
- 跨架构编译可能增加构建时间和复杂性
