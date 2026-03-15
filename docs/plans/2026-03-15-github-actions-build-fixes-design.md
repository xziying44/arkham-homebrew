# GitHub Actions 构建修复设计

## 背景

当前仓库的 GitHub Actions 存在两个独立但都由外部环境变化引发的构建故障：

1. `Fedora/RHEL/CentOS` Linux 构建使用 `fedora:latest` 容器，当前已升级到 Python 3.14，导致 `pydantic_core==2.27.2` 依赖的 PyO3 构建失败，同时 `pillow==11.1.0` 缺少预编译 wheel 后退回源码编译并要求系统 `zlib` 头文件。
2. Intel macOS 构建仍使用 `macos-13` runner，GitHub 已停止支持该配置，工作流会直接因 runner 不可用而失败。

## 目标

以最小改动修复这两个工作流问题，恢复现有发布流程，不扩散到应用代码和依赖版本升级。

## 方案对比

### 方案一：固定外部运行环境版本

- Intel macOS runner 从 `macos-13` 切换到 `macos-15-intel`
- Fedora 容器从 `fedora:latest` 固定到 `fedora:41`

优点：

- 改动范围最小
- 不需要升级项目依赖
- 继续沿用当前系统 Python 与系统 PyQt 的打包方式

缺点：

- 后续仍需关注 GitHub runner 与 Fedora 版本生命周期

### 方案二：保留最新 Fedora，补齐源码编译链

- 给 Fedora 安装 Rust、Cargo、`zlib-devel`
- 对 PyO3 配置前向 ABI 兼容

优点：

- 可以继续跟随最新 Fedora 镜像

缺点：

- 构建时间更长
- 依赖源码编译更脆弱
- 未来仍可能被其他 Python 3.14 兼容问题击穿

### 方案三：整体升级 Python 依赖

- 更新 `pydantic_core`、`pillow` 等依赖到明确支持 Python 3.14 的版本

优点：

- 理论上可以适配最新解释器

缺点：

- 影响面大
- 需要回归应用打包兼容性
- 不适合当前仅修复 CI 的目标

## 选定方案

采用方案一。

## 详细设计

### Intel macOS runner

- 修改文件：`.github/workflows/build-macos-multi-arch.yml`
- 将 Intel 架构矩阵项的 `runner` 从 `macos-13` 改为 `macos-15-intel`
- 保留 Apple Silicon 的 `macos-latest`
- 保留 Python 3.11，不扩大变更面

### Fedora 容器版本

- 修改文件：`.github/workflows/build-macos-multi-arch.yml`
- 将 Linux 构建 job 的容器条件表达式中 Fedora 镜像从 `fedora:latest` 改为 `fedora:41`
- 保持现有 `dnf install` 和虚拟环境逻辑不变
- 通过固定 Fedora 主版本，确保系统 Python 不漂移到 3.14

## 风险与回退

### 风险

- GitHub 后续如果再次调整 Intel runner 标签，需要再次更新
- Fedora 41 未来退役时仍需维护

### 回退

- 两处改动均集中在同一个工作流文件，必要时可单独回退该文件中的对应行

## 验证策略

1. 本地检查工作流文件中关键 runner 和容器标签是否已替换。
2. 使用本地 YAML 解析工具做语法校验；如果环境缺少工具，则至少执行 GitHub Actions 关键片段检查。
3. 提醒用户重新触发 GitHub Actions 进行最终远端验证。
