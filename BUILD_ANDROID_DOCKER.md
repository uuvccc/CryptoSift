# 使用Docker在Windows上构建CryptoSift Android应用

本文档提供了如何使用Docker在Windows上构建CryptoSift Android应用的详细步骤，无需安装WSL。

## 前提条件

1. 安装Docker Desktop for Windows
   - 从[Docker官网](https://www.docker.com/products/docker-desktop/)下载并安装Docker Desktop
   - 确保Docker服务正常运行

2. 确保已安装以下软件：
   - Git for Windows
   - Android SDK Platform Tools（用于adb命令）

## 构建步骤

### 1. 准备Docker环境

1. 创建一个名为`Dockerfile`的文件，放在项目根目录下：

```dockerfile
FROM python:3.9-slim

# 安装必要的依赖
RUN apt-get update && apt-get install -y \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libltdl-dev \
    autoconf \
    automake \
    libtool \
    zlib1g-dev

# 安装buildozer
RUN pip3 install --upgrade buildozer

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV USER=root

# 默认命令
CMD ["buildozer", "-v", "android", "debug"]
```

2. 打开命令提示符或PowerShell，导航到项目目录并构建Docker镜像：

```bash
cd d:\work\CryptoSift
docker build -t cryptosift-builder .
```

### 2. 使用Docker构建APK

1. 在项目目录中运行Docker容器，将当前目录挂载到容器的`/app`目录：

```bash
# 在Windows命令提示符(CMD)中使用绝对路径（使用反斜杠）
docker run --rm -e BUILDOZER_WARN_ON_ROOT=0 -v "D:\work\CryptoSift":/app cryptosift-builder

# 在Windows命令提示符(CMD)中使用绝对路径（使用正斜杠）
docker run --rm -e BUILDOZER_WARN_ON_ROOT=0 -v "D:/work/CryptoSift":/app cryptosift-builder
```

```powershell
# 在PowerShell中使用绝对路径
docker run --rm -e BUILDOZER_WARN_ON_ROOT=0 -v "D:/work/CryptoSift:/app" cryptosift-builder

# 在PowerShell中使用${PWD}变量
docker run --rm -e BUILDOZER_WARN_ON_ROOT=0 -v "${PWD}:/app" cryptosift-builder
```

> **注意**: 
> 1. 在Windows中，`%cd%`可能无法正确解析为绝对路径。请使用完整的绝对路径或在PowerShell中使用`${PWD}`。
> 2. 在PowerShell中使用`${PWD}`时，整个路径映射（`${PWD}:/app`）需要放在一对双引号内。
> 3. Docker支持使用正斜杠（/）或反斜杠（\）作为路径分隔符，但使用反斜杠时需要转义（双反斜杠）。
> 4. **重要**：路径映射的左侧必须是项目根目录（包含buildozer.spec文件的目录），不要在路径末尾添加`/app`。例如，使用`D:/work/CryptoSift`而不是`D:/work/CryptoSift/app`。
> 5. 添加`-e BUILDOZER_WARN_ON_ROOT=0`参数可以避免buildozer的root用户确认提示。

2. 构建过程将开始，首次构建会下载Android SDK和NDK，可能需要较长时间。

3. 构建完成后，APK文件将位于项目目录的`bin`文件夹中：

```
d:\work\CryptoSift\bin\cryptosift-0.1-arm64-v8a_armeabi-v7a-debug.apk
```

## 安装到Android设备

1. 通过USB连接Android设备到电脑

2. 在Android设备上启用开发者选项和USB调试

3. 使用adb安装APK：

```bash
adb install bin\cryptosift-0.1-arm64-v8a_armeabi-v7a-debug.apk
```

或者直接将APK传输到设备并手动安装

## 故障排除

如果在构建过程中遇到问题：

1. **网络连接问题**：
   - 如果出现无法下载基础镜像的错误，可能是网络连接问题
   - 请参考[Docker故障排除指南](DOCKER_TROUBLESHOOTING.md)中的网络连接问题解决方案
   - 我们已更新Dockerfile使用Ubuntu基础镜像，这可能有助于解决某些网络问题

2. **Docker容器权限问题**：确保Docker Desktop有足够的权限访问项目目录

3. **内存不足**：在Docker Desktop设置中增加分配给Docker的内存

4. **构建失败**：查看构建日志以获取详细错误信息

5. **APK安装失败**：确保Android设备已启用USB调试和未知来源应用安装权限

详细的故障排除步骤请参考[Docker故障排除指南](DOCKER_TROUBLESHOOTING.md)。

## 优势与注意事项

### 优势

- 无需安装WSL或Linux虚拟机
- 构建环境完全隔离，不会影响Windows系统
- 可以在任何支持Docker的系统上重现相同的构建环境
- 避免了WSL与Windows之间的文件系统兼容性问题

### 注意事项

- Docker镜像首次下载和构建可能需要较长时间
- 需要为Docker分配足够的系统资源（CPU、内存、存储）
- 构建过程中会下载大量文件，确保网络连接稳定
- 该应用需要互联网连接才能获取最新的加密货币价格和美股数据