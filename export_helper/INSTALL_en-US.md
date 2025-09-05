[简体中文](./INSTALL_zh-CN.md) | **English**

# 🎨 Lama Cleaner Installation Guide

This guide will walk you through the installation process for Lama Cleaner, a powerful, free and open-source inpainting tool.

## Step 1: Install Python Environment

Lama Cleaner requires a Python environment to run.

- **Supported Versions:** Python 3.7 ~ 3.10
- **Official Download Page:** [https://www.python.org/downloads/](https://www.python.org/downloads/)

> **Note:** Based on community testing, Python 3.11 also works correctly at the moment.

Please download and install a suitable Python version for your operating system from the official website. Ensure that the `python` and `pip` commands are added to your system's PATH.

## Step 2: Install Lama Cleaner

You can choose to install the GPU-accelerated version or the CPU-only version based on your hardware.

### 🚀 GPU Accelerated Version (Recommended)

If you have a CUDA-compatible NVIDIA GPU, it is highly recommended to install this version for the best performance.

1.  **Install PyTorch with CUDA Support**

    First, you need to install a version of PyTorch that matches your CUDA version. Visit the following link to generate the correct installation command for your system:
    - **Official PyTorch Get Started Page:** [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)

    **Example Command (Windows & Linux, for CUDA 12.1):**
    ```bash
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    ```
    > **Attention:** Please replace `cu121` in the command with your own CUDA version (e.g., `cu118`). If you are unsure about your CUDA version, you can check it by running `nvidia-smi` in your terminal.

2.  **Install Lama Cleaner**

    After PyTorch is installed, execute the following command to install Lama Cleaner:
    ```bash
    pip install lama-cleaner
    ```

### 💻 CPU-Only Version

If you do not have an NVIDIA GPU or prefer not to set up the CUDA environment, you can opt for the CPU-only version.

Simply run the following command in your terminal or command prompt:
```bash
pip install lama-cleaner
```
*pip will automatically install the CPU version of PyTorch for you.*

## Step 3: Launch the Application

Once the installation is complete, use the following commands to start the Lama Cleaner service.

- **To launch with GPU support:**
  ```bash
  lama-cleaner --model=lama --device=cuda --port=8080
  ```

- **To launch with CPU support:**
  ```bash
  lama-cleaner --model=lama --device=cpu --port=8080
  ```

> #### Parameter Explanation:
> - `--model=lama`: Specifies the inpainting model to use. `lama` is one of the default and best-performing models.
> - `--device=cuda`: Specifies that the computation should be done on the **GPU**.
> - `--device=cpu`: Specifies that the computation should be done on the **CPU**.
> - `--port=8080`: Specifies the port on which the service will run. You can change this to any other available port.

## Step 4: Verify the Installation

After the service starts successfully, you will see an output in your terminal similar to `Uvicorn running on http://0.0.0.0:8080`.

Now, open your web browser and navigate to the following address:

**[http://localhost:8080](http://localhost:8080)**

If you can see the Lama Cleaner web interface, it means the installation and launch were successful! 🎉