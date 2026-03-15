# GitHub Actions 构建修复 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复 Fedora Linux 与 Intel macOS 的 GitHub Actions 构建失败问题。

**Architecture:** 仅调整工作流运行环境，不改应用代码与依赖版本。通过固定 Fedora 主版本避免 Python 3.14 触发源码编译失败，通过替换 Intel macOS runner 恢复 GitHub 支持的构建节点。

**Tech Stack:** GitHub Actions YAML、Fedora 容器、macOS Intel runner、PyInstaller

---

### Task 1: 记录设计与锁定修改点

**Files:**
- Create: `docs/plans/2026-03-15-github-actions-build-fixes-design.md`
- Create: `docs/plans/2026-03-15-github-actions-build-fixes.md`
- Modify: `.github/workflows/build-macos-multi-arch.yml`

**Step 1: 确认失败根因**

- Linux Fedora 构建失败根因：`fedora:latest` 提供 Python 3.14，`pydantic_core==2.27.2` 依赖的 PyO3 不支持 3.14。
- Intel macOS 构建失败根因：`macos-13` runner 已不可用。

**Step 2: 选择最小变更方案**

- Intel runner 改为 `macos-15-intel`
- Fedora 容器改为 `fedora:41`

### Task 2: 修改工作流配置

**Files:**
- Modify: `.github/workflows/build-macos-multi-arch.yml`

**Step 1: 修改 Intel macOS runner**

将矩阵中的：

```yaml
- runner: macos-13
```

改为：

```yaml
- runner: macos-15-intel
```

**Step 2: 修改 Fedora 容器镜像**

将 job 级别容器配置中的：

```yaml
container: ${{ matrix.distro == 'fedora' && 'fedora:latest' || null }}
```

改为：

```yaml
container: ${{ matrix.distro == 'fedora' && 'fedora:41' || null }}
```

**Step 3: 保持其他逻辑不变**

- 不调整 Python 3.11 配置
- 不升级 `requirements-linux.txt`
- 不修改打包脚本

### Task 3: 本地验证

**Files:**
- Modify: `.github/workflows/build-macos-multi-arch.yml`

**Step 1: 校验关键替换**

Run: `rg -n "macos-15-intel|fedora:41|macos-13|fedora:latest" .github/workflows/build-macos-multi-arch.yml`

Expected:

- 能看到 `macos-15-intel`
- 能看到 `fedora:41`
- 不再看到 `macos-13`
- 不再看到 `fedora:latest`

**Step 2: 进行 YAML 语法校验**

Run: `python3 - <<'PY'\nimport sys\nfrom pathlib import Path\nimport yaml\npath = Path('.github/workflows/build-macos-multi-arch.yml')\nwith path.open('r', encoding='utf-8') as f:\n    yaml.safe_load(f)\nprint('YAML OK')\nPY`

Expected:

- 输出 `YAML OK`

**Step 3: 检查最终差异**

Run: `git diff -- .github/workflows/build-macos-multi-arch.yml docs/plans/2026-03-15-github-actions-build-fixes-design.md docs/plans/2026-03-15-github-actions-build-fixes.md`

Expected:

- 仅包含本次工作流修复与文档新增内容
