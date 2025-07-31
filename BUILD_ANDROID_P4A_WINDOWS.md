# 使用预编译Python-for-Android在Windows上构建CryptoSift

本文档提供了如何在Windows上直接使用预编译的Python-for-Android工具包构建CryptoSift Android应用的方法，无需WSL或Docker。

> **注意**：这种方法处于实验阶段，可能不如Docker或WSL方法稳定。

## 前提条件

1. 安装Python 3.8或更高版本

2. 安装Java JDK 8或更高版本，并设置JAVA_HOME环境变量

3. 下载并安装Android SDK和NDK
   - 可以通过Android Studio安装，或直接下载命令行工具
   - 设置ANDROID_SDK_HOME和ANDROID_NDK_HOME环境变量

4. 安装Git for Windows

## 构建步骤

### 1. 安装预编译的Python-for-Android

1. 打开命令提示符或PowerShell，安装python-for-android：

```bash
pip install python-for-android
```

2. 安装必要的Python依赖：

```bash
pip install kivy buildozer cython
```

### 2. 准备构建环境

1. 创建一个p4a_recipes目录用于存放自定义配方：

```bash
mkdir %USERPROFILE%\.p4a\recipes
```

2. 设置必要的环境变量：

```bash
setx ANDROIDSDK %ANDROID_SDK_HOME%
setx ANDROIDNDK %ANDROID_NDK_HOME%
setx ANDROIDAPI "29"
setx ANDROIDNDKVER "r21e"
```

### 3. 构建APK

1. 导航到项目目录：

```bash
cd d:\work\CryptoSift
```

2. 使用python-for-android构建APK：

```bash
p4a apk --private=. --package=org.cryptosift --name="CryptoSift" --version=0.1 --bootstrap=sdl2 --requirements=python3,kivy,requests,yfinance,numpy,pandas --permission=INTERNET
```

3. 构建过程可能需要一些时间，完成后APK将位于当前目录中。

## 安装到Android设备

1. 通过USB连接Android设备到电脑

2. 在Android设备上启用开发者选项和USB调试

3. 使用adb安装APK：

```bash
adb install CryptoSift-0.1-debug.apk
```

## 故障排除

如果在构建过程中遇到问题：

1. **缺少工具或依赖**：确保已安装所有必要的工具和依赖

2. **路径问题**：确保环境变量正确设置，特别是JAVA_HOME、ANDROID_SDK_HOME和ANDROID_NDK_HOME

3. **构建失败**：
   - 检查Python版本兼容性
   - 确保Android SDK和NDK版本兼容
   - 尝试使用--debug选项获取更详细的错误信息：
     ```bash
     p4a apk --debug --private=. ...
     ```

4. **Windows特定问题**：
   - 路径长度限制：确保项目路径不要太长
   - 权限问题：尝试以管理员身份运行命令提示符

## 优势与注意事项

### 优势

- 无需安装WSL或Docker
- 直接在Windows环境中工作
- 可以利用已有的Windows Python环境

### 注意事项

- 这种方法在Windows上的支持有限，可能遇到兼容性问题
- 构建过程可能不如在Linux环境中稳定
- 某些Python库在Windows上的交叉编译可能存在问题
- 可能需要手动解决依赖冲突

## 替代方案

如果这种方法在您的环境中不起作用，请考虑：

1. 使用[Docker构建方法](BUILD_ANDROID_DOCKER.md)（推荐）
2. 使用[WSL构建方法](BUILD_ANDROID.md)
3. 使用[Android Studio方法](BUILD_ANDROID_STUDIO.md)