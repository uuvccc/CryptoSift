FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git zip unzip openjdk-17-jdk python3.9 python3-pip \
    python3-setuptools python3-wheel build-essential \
    libssl-dev libffi-dev python3-dev libltdl-dev \
    autoconf automake libtool zlib1g-dev wget curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir \
    buildozer==1.5.0 \
    cython==0.29.33 \
    virtualenv

RUN mkdir -p /root/.android && \
    touch /root/.android/repositories.cfg && \
    echo "8933bad161af4178b1185d1a37fbf41ea5269c55\nd56f5187479451eabf01fb78af6dfcb131a6481e" > /root/.android/android-sdk-license && \
    echo "84831b9409646a918e30573bab4c9c91346d8abd" > /root/.android/android-sdk-preview-license

RUN mkdir -p /opt/android-sdk/cmdline-tools && \
    cd /opt/android-sdk/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip commandlinetools-linux-9477386_latest.zip && \
    rm commandlinetools-linux-9477386_latest.zip && \
    mv cmdline-tools latest && \
    ln -s /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager /usr/local/bin/

RUN yes | sdkmanager "platform-tools" "build-tools;33.0.2" "platforms;android-33" && \
    ln -s /opt/android-sdk/build-tools/33.0.2/aidl /usr/local/bin/

WORKDIR /app
ENV ANDROID_SDK_ROOT=/opt/android-sdk \
    PATH="/opt/android-sdk/platform-tools:/opt/android-sdk/build-tools/33.0.2:/root/.local/bin:${PATH}" \
    BUILDOZER_ALLOW_ROOT=1 \
    BUILDOZER_WARN_ON_ROOT=0

CMD ["sh", "-c", "buildozer -v android debug 2>&1 | tee build.log || (echo 'Build failed!'; exit 1)"]