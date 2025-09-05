**简体中文** | [English](./INSTALL_en-US.md)

# 🎨 Lama Cleaner 安装指南

本指南将引导您完成 Lama Cleaner 的安装过程。Lama Cleaner 是一款强大的、免费且开源的图像修复工具。

## 步骤 1: 安装 Python 环境

Lama Cleaner 需要 Python 环境才能运行。

- **支持版本:** Python 3.7 ~ 3.10
- **官方下载地址:** [https://www.python.org/downloads/](https://www.python.org/downloads/)

> **提示:** 根据社区测试，Python 3.11 版本目前也可以正常工作。

请先从官网下载并安装适合您操作系统的 Python 版本，并确保 `python` 和 `pip` 命令已正确添加到系统环境变量中。

## 步骤 2: 安装 Lama Cleaner

您可以根据自己的硬件情况选择安装 GPU 加速版或仅 CPU 版。

### 🚀 GPU 加速版 (推荐)

如果您拥有兼容 CUDA 的 NVIDIA 显卡，强烈建议安装此版本以获得最佳性能。

1.  **安装支持 CUDA 的 PyTorch**

    首先，您需要根据您的 CUDA 版本安装对应的 PyTorch。请访问以下地址，生成适合您系统的安装命令：
    - **PyTorch 官方安装向导:** [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)

    **安装示例 (Windows & Linux, CUDA 12.1):**
    ```bash
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    ```
    > **注意:** 请将命令中的 `cu121` 替换为您自己的 CUDA 版本 (例如 `cu118`)。如果您不确定自己的 CUDA 版本，可以在终端中运行 `nvidia-smi` 命令查看。

2.  **安装 Lama Cleaner**

    安装完 PyTorch后，执行以下命令安装 Lama Cleaner：
    ```bash
    pip install lama-cleaner
    ```

### 💻 CPU 版

如果您的电脑没有 NVIDIA 显卡，或者不想配置 CUDA 环境，可以选择安装 CPU 版本。

直接在您的终端或命令提示符中运行以下命令即可：
```bash
pip install lama-cleaner
```
*pip 会自动为您安装 CPU 版本的 PyTorch。*

## 步骤 3: 启动服务

安装完成后，使用以下命令启动 Lama Cleaner 服务。

- **使用 GPU 启动:**
  ```bash
  lama-cleaner --model=lama --device=cuda --port=8080
  ```

- **使用 CPU 启动:**
  ```bash
  lama-cleaner --model=lama --device=cpu --port=8080
  ```

> #### 参数说明:
> - `--model=lama`: 指定使用的修复模型，`lama` 是默认且效果最好的模型之一。
> - `--device=cuda`: 指定使用 **GPU** 进行计算。
> - `--device=cpu`: 指定使用 **CPU** 进行计算。
> - `--port=8080`: 指定服务运行的端口，您可以更改为其他未被占用的端口。

## 步骤 4: 验证运行

服务启动成功后，您会在终端看到类似 `Uvicorn running on http://0.0.0.0:8080` 的输出。

此时，打开您的浏览器并访问以下地址：

**[http://localhost:8080](http://localhost:8080)**

如果能看到 Lama Cleaner 的界面，则说明安装和启动都已成功！🎉