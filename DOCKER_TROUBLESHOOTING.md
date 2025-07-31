# Docker构建故障排除指南

## 常见问题与解决方案

### 0. Windows路径问题

**问题表现**：

```
docker: Error response from daemon: create %cd%: "%cd%" includes invalid characters for a local volume name, only "[a-zA-Z0-9][a-zA-Z0-9_.-]" are allowed. If you intended to pass a host directory, use absolute path
```

**解决方案**：

1. **在命令提示符(CMD)中使用绝对路径**
   - 使用完整的绝对路径替代`%cd%`：
   ```bash
   docker run --rm -e BUILDOZER_WARN_ON_ROOT=0 -v "D:\work\CryptoSift":/app cryptosift-builder
   ```

2. **在PowerShell中使用绝对路径**
   - 在PowerShell中，路径映射的格式与CMD略有不同：
   ```powershell
   docker run --rm -e BUILDOZER_WARN_ON_ROOT=0 -v "D:/work/CryptoSift:/app" cryptosift-builder
   ```
   - 注意：在PowerShell中，整个路径映射（包括源路径和目标路径）需要放在一对双引号内

3. **在PowerShell中使用`${PWD}`变量**
   - 如果您使用PowerShell，也可以使用`${PWD}`变量：
   ```powershell
   docker run --rm -e BUILDOZER_WARN_ON_ROOT=0 -v "${PWD}:/app" cryptosift-builder
   ```

3. **使用批处理脚本**
   - 我们已更新`build_android.bat`脚本，正确处理路径问题
   - 直接运行批处理脚本是最简单的解决方案：
   ```bash
   build_android.bat
   ```

### 1. 网络连接问题

**问题表现**：

```
ERROR: failed to build: failed to solve: python:3.9-slim: failed to resolve source metadata for docker.io/library/python:3.9-slim: failed to do request: Head "https://registry-1.docker.io/v2/library/python/manifests/3.9-slim": EOF
```

**解决方案**：

1. **检查网络连接**
   - 确保您的计算机能够访问互联网
   - 检查是否有防火墙或代理设置阻止了Docker访问Docker Hub

2. **配置Docker镜像加速**
   - 在中国大陆地区，可以使用国内Docker镜像加速服务
   - 打开Docker Desktop，进入设置 -> Docker Engine，添加以下配置：

   ```json
   {
     "registry-mirrors": [
       "https://registry.docker-cn.com",
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com"
     ]
   }
   ```

3. **使用替代基础镜像**
   - 我们已经更新了Dockerfile，使用Ubuntu基础镜像替代Python镜像
   - 这个修改已经应用到项目中，请重新尝试构建

4. **手动拉取基础镜像**
   - 在构建前先尝试手动拉取基础镜像：
   ```bash
   docker pull ubuntu:22.04
   ```

### 2. 构建过程中的权限问题

**问题表现**：

```
permission denied
```

**解决方案**：

1. **以管理员身份运行命令提示符或PowerShell**

2. **确保Docker Desktop有足够的权限**
   - 右键点击Docker Desktop图标，选择"以管理员身份运行"

### 3. Buildozer的root用户确认提示

**问题表现**：

```
Buildozer is running as root! 
This is not recommended, and may lead to problems later. 
Are you sure you want to continue [y/n]? Traceback (most recent call last): 
  File "/usr/local/bin/buildozer", line 8, in <module> 
    sys.exit(main()) 
  File "/usr/local/lib/python3.10/dist-packages/buildozer/scripts/client.py", line 13, in main 
    Buildozer().run_command(sys.argv[1:]) 
  File "/usr/local/lib/python3.10/dist-packages/buildozer/__init__.py", line 1003, in run_command 
    self.check_root() 
  File "/usr/local/lib/python3.10/dist-packages/buildozer/__init__.py", line 1042, in check_root 
    cont = input('Are you sure you want to continue [y/n]? ') 
EOFError: EOF when reading a line
```

**解决方案**：

1. **使用更新后的Dockerfile**
   - 我们已经更新了Dockerfile，添加了`ENV BUILDOZER_WARN_ON_ROOT=0`环境变量来自动跳过这个提示
   - 请重新构建Docker镜像：
   ```bash
   docker build -t cryptosift-builder .
   ```

2. **手动添加环境变量**
   - 如果您不想重新构建镜像，可以在运行容器时添加环境变量：
   ```bash
   docker run --rm -e BUILDOZER_WARN_ON_ROOT=0 -v "D:/work/CryptoSift":/app cryptosift-builder
   ```

### 4. 找不到buildozer配置文件

**问题表现**：

```
Traceback (most recent call last): 
  File "/usr/local/bin/buildozer", line 8, in <module> 
    sys.exit(main()) 
  File "/usr/local/lib/python3.10/dist-packages/buildozer/scripts/client.py", line 13, in main 
    Buildozer().run_command(sys.argv[1:]) 
  File "/usr/local/lib/python3.10/dist-packages/buildozer/__init__.py", line 1003, in run_command 
    self.check_root() 
  File "/usr/local/lib/python3.10/dist-packages/buildozer/__init__.py", line 1030, in check_root 
    warn_on_root = self.config.getdefault('buildozer', 'warn_on_root', '1') 
  File "/usr/local/lib/python3.10/dist-packages/buildozer/__init__.py", line 1184, in _get_config_default 
    set_config_token_from_env(section, token, self.config) 
  File "/usr/local/lib/python3.10/dist-packages/buildozer/__init__.py", line 1242, in set_config_token_from_env 
    config.set(section, token, env_var) 
  File "/usr/lib/python3.10/configparser.py", line 1206, in set 
    super().set(section, option, value) 
  File "/usr/lib/python3.10/configparser.py", line 904, in set 
    raise NoSectionError(section) from None 
configparser.NoSectionError: No section: 'buildozer'
```

**解决方案**：

1. **路径映射错误**
   - 检查您的Docker命令中的路径映射是否正确
   - 错误示例：
   ```bash
   docker run --rm -v "D:/work/CryptoSift/app":/app cryptosift-builder
   ```
   - 正确示例：
   ```bash
   docker run --rm -v "D:/work/CryptoSift":/app cryptosift-builder
   ```
   - 注意：路径映射的左侧应该是您的项目根目录（包含buildozer.spec文件的目录），而不是添加额外的`/app`

2. **确认buildozer.spec文件存在**
   - 确保项目根目录中存在buildozer.spec文件
   - 如果不存在，可以通过运行以下命令创建：
   ```bash
   buildozer init
   ```

### 5. 磁盘空间不足

**问题表现**：

```
no space left on device
```

**解决方案**：

1. **清理Docker缓存**
   ```bash
   docker system prune -a
   ```

2. **增加Docker Desktop的磁盘空间限制**
   - 打开Docker Desktop设置 -> Resources -> Disk image size

### 4. 构建超时

**问题表现**：

```
context deadline exceeded
```

**解决方案**：

1. **增加Docker构建超时时间**
   - 在Docker Desktop设置中增加超时时间

2. **分步构建**
   - 修改Dockerfile，将长时间运行的命令分成多个RUN指令

## 如果问题仍然存在

如果以上解决方案都不能解决您的问题，您可以尝试：

1. **重启Docker Desktop**

2. **重启计算机**

3. **尝试其他构建方法**
   - 参考[构建方法比较](BUILD_METHODS_COMPARISON.md)中的其他方法

4. **检查Docker日志**
   - 在Docker Desktop中查看详细日志