# CryptoSift Android 应用构建指南

本文档提供了在Windows系统上使用WSL (Windows Subsystem for Linux)将CryptoSift打包成Android应用的详细步骤。

## 项目准备情况

我们已经完成了以下准备工作：

1. 创建了完整的`buildozer.spec`配置文件
2. 添加了应用图标(`icon.svg`)和启动画面(`presplash.svg`)
3. 创建了`assets`目录用于存放资源文件
4. 确保了所有必要的依赖项都已在配置文件中列出

## 构建步骤

### 1. 安装WSL

在Windows上，buildozer需要在Linux环境中运行，因此我们需要使用WSL：

1. 以管理员身份打开PowerShell并运行：
   ```
   wsl --install
   ```

2. 重启电脑并完成Ubuntu设置

### 2. 在WSL中设置环境

1. 打开WSL终端并安装必要的依赖：
   ```bash
   sudo apt update
   sudo apt upgrade -y
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-setuptools python3-wheel build-essential libssl-dev libffi-dev python3-dev
   ```

2. 安装buildozer：
   ```bash
   pip3 install --user buildozer
   ```

3. 安装Android依赖：
   ```bash
   sudo apt install -y libltdl-dev libffi-dev libssl-dev autoconf automake libtool
   sudo apt install -y zlib1g-dev
   ```

### 3. 将项目复制到WSL

1. 在WSL中，创建一个工作目录：
   ```bash
   mkdir -p ~/projects/cryptosift
   ```

2. 从Windows复制文件到WSL（在WSL终端中执行）：
   ```bash
   cp -r /mnt/d/work/CryptoSift/* ~/projects/cryptosift/
   ```

### 4. 构建APK

1. 进入项目目录：
   ```bash
   cd ~/projects/cryptosift
   ```

2. 构建APK：
   ```bash
   buildozer -v android debug
   ```
   首次构建会下载Android SDK和NDK，可能需要较长时间。

3. 构建完成后，APK文件将位于：
   ```
   ~/projects/cryptosift/bin/cryptosift-0.1-arm64-v8a_armeabi-v7a-debug.apk
   ```

4. 将APK复制回Windows：
   ```bash
   cp ~/projects/cryptosift/bin/*.apk /mnt/d/work/CryptoSift/
   ```

## 安装到Android设备

1. 通过USB连接Android设备到电脑
2. 在Android设备上启用开发者选项和USB调试
3. 使用adb安装APK：
   ```
   adb install cryptosift-0.1-arm64-v8a_armeabi-v7a-debug.apk
   ```
   或者直接将APK传输到设备并手动安装

## 应用功能

- **加密货币选择**：应用支持多种加密货币选择，包括BTC、ETH、SOL等
- **预测时间设置**：可以自定义预测未来多少小时的价格走势
- **分析结果展示**：显示每种加密货币的涨跌概率和主要趋势

## 故障排除

如果在构建过程中遇到问题：

1. **缺少依赖项**：检查buildozer日志并安装缺少的依赖
   ```bash
   cat .buildozer/logs/buildozer-*.log
   ```

2. **Python模块问题**：确保所有必要的Python模块都已在`buildozer.spec`的`requirements`部分列出

3. **权限问题**：确保WSL有足够的权限访问项目文件

4. **内存不足**：如果构建过程中出现内存不足错误，可以尝试增加WSL的内存限制

## 注意事项

- 该应用需要互联网连接才能获取最新的加密货币价格和美股数据
- 首次分析可能需要较长时间，请耐心等待
- 预测结果仅供参考，不构成投资建议
- 如果API密钥过期，请在`CryptoSift.py`文件中更新相关密钥