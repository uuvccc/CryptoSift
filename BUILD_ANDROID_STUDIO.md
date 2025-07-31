# 使用Android Studio构建CryptoSift Android应用

本文档提供了如何使用Android Studio在Windows上构建CryptoSift Android应用的基本步骤。这是一种替代方案，适用于熟悉Android开发的用户。

## 前提条件

1. 安装Android Studio
   - 从[Android开发者网站](https://developer.android.com/studio)下载并安装最新版本的Android Studio
   - 确保已安装Android SDK和必要的构建工具

2. 安装Python环境
   - 确保已安装Python 3.8或更高版本
   - 安装必要的Python依赖项

## 构建步骤

### 1. 使用python-for-android生成Android项目

首先，我们需要使用python-for-android工具生成一个Android Studio可以识别的项目结构。这一步可以在WSL或Docker环境中完成：

```bash
# 安装python-for-android
pip install python-for-android

# 生成Android项目
p4a create --dist_name=cryptosift --bootstrap=sdl2 --requirements=python3,kivy,requests,yfinance

# 构建项目
p4a apk --private=. --package=org.cryptosift --name=CryptoSift --version=0.1 --bootstrap=sdl2 --requirements=python3,kivy,requests,yfinance --sdk-dir=/path/to/android-sdk --ndk-dir=/path/to/android-ndk --dist-name=cryptosift
```

### 2. 导入到Android Studio

1. 打开Android Studio

2. 选择「Open an Existing Project」

3. 导航到python-for-android生成的项目目录（通常在`.p4a/dist/cryptosift/build/outputs/apk`）

4. 等待Android Studio完成项目导入和Gradle同步

### 3. 修改项目配置

1. 在Android Studio中，打开`build.gradle`文件，确保SDK版本和构建工具版本正确

2. 如果需要，更新应用图标和启动画面：
   - 将`icon.svg`转换为PNG格式并放入`res/drawable`目录
   - 将`presplash.svg`转换为PNG格式并放入`res/drawable`目录

3. 更新`AndroidManifest.xml`文件，确保权限设置正确：

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### 4. 构建APK

1. 在Android Studio中，选择「Build」>「Build Bundle(s) / APK(s)」>「Build APK(s)」

2. 等待构建完成

3. 构建完成后，APK文件将位于`app/build/outputs/apk/debug/`目录中

## 安装到Android设备

1. 通过USB连接Android设备到电脑

2. 在Android Studio中，选择「Run」>「Run 'app'」

3. 选择已连接的设备，点击「OK」

或者手动安装APK：

```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

## 优势与注意事项

### 优势

- 完全在Windows环境中工作，无需WSL或Docker
- 可以利用Android Studio强大的调试和分析工具
- 可以直接添加原生Android功能和UI元素
- 便于发布到Google Play商店

### 注意事项

- 需要对Android开发有一定了解
- 配置过程较为复杂
- 可能需要手动解决Python和Java/Kotlin代码之间的集成问题
- 对原始Kivy应用可能需要进行一些修改

## 参考资源

- [Kivy官方文档：Android打包](https://kivy.org/doc/stable/guide/packaging-android.html)
- [python-for-android文档](https://python-for-android.readthedocs.io/)
- [Android开发者文档](https://developer.android.com/docs)