@echo off
echo ===== CryptoSift Android 构建脚本 =====
echo.

REM Check if Docker is installed
docker --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker not found. Please install Docker Desktop for Windows.
    echo Download: https://www.docker.com/products/docker-desktop/
    exit /b 1
)

REM Check if Docker service is running
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker service not running. Please start Docker Desktop.
    echo 1. Open Docker Desktop from Start Menu
    echo 2. Wait until the whale icon shows "Docker Desktop is running"
    exit /b 1
)

REM 检查网络连接
ping -n 1 registry-1.docker.io > nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 无法连接到Docker Hub。可能存在网络问题。
    echo 建议: 请查看DOCKER_TROUBLESHOOTING.md获取解决方案。
    echo.
    set /p continue=是否仍要继续? (Y/N): 
    if /i not "%continue%"=="Y" exit /b 1
)

echo 1. 构建Docker镜像...
docker build -t cryptosift-builder .
if %errorlevel% neq 0 (
    echo 错误: Docker镜像构建失败。
    exit /b 1
)

echo.
echo 2. 使用Docker构建APK...
REM 获取当前绝对路径
for %%i in ("%cd%") do set CURRENT_DIR=%%~fi
echo 使用路径: %CURRENT_DIR%

docker run --rm -e BUILDOZER_WARN_ON_ROOT=0 -v "%CURRENT_DIR%":/app cryptosift-builder
if %errorlevel% neq 0 (
    echo 错误: APK构建失败。
    exit /b 1
)

echo.
echo 3. 检查APK文件...
if exist "bin\cryptosift-0.1-arm64-v8a_armeabi-v7a-debug.apk" (
    echo 构建成功! APK文件位于: %cd%\bin\cryptosift-0.1-arm64-v8a_armeabi-v7a-debug.apk
) else (
    echo 警告: 未找到APK文件，请检查bin目录。
)

echo.
echo 4. 是否安装到已连接的Android设备? (Y/N)
set /p install=
if /i "%install%"=="Y" (
    echo 正在安装APK到设备...
    adb devices
    adb install -r "bin\cryptosift-0.1-arm64-v8a_armeabi-v7a-debug.apk"
    if %errorlevel% neq 0 (
        echo 警告: APK安装失败。请确保设备已连接并启用USB调试。
    ) else (
        echo APK已成功安装到设备!
    )
)

echo.
echo ===== 构建过程完成 =====
pause