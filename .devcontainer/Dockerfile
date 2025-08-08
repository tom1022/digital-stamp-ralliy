FROM ubuntu:22.04

# 環境変数を設定
ENV DEBIAN_FRONTEND=noninteractive

ARG apt_get_server=ftp.jaist.ac.jp/pub/Linux
ARG username=vscode
ARG useruid=1000
ARG usergid=${useruid}


RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-distutils \
    git \
    wget \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1 && \
    groupadd --gid ${usergid} ${username} && \
    useradd -s /bin/bash --uid ${useruid} --gid ${usergid} -m ${username} && \
    echo ${username} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${username} && \
    chmod 0440 /etc/sudoers.d/${username}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN wget https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10x.pt -O yolov10x.pt

USER ${username}

# CMD ["python", "app.py"]
