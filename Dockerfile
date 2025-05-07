FROM python:3.13-slim

# 安装依赖
RUN apt update && apt install -y ffmpeg supervisor curl && \
    apt clean && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /transum

# 拷贝代码和依赖
COPY . /transum

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 环境变量可选配置
ENV MAX_CONNECTIONS=56
ENV GAIA_WHISPER_API_URL=http://18.246.56.248:8080/v1/audio/transcriptions
ENV GAIA_CHAT_API_URL=http://34.42.130.83:9080/v1/chat/completions
ENV GAIA_API_KEY=gaia-OTBiYjlmZDEtNTc3OS00MjI5LWI0NDgtZDIxNTNmYjEwZDRj-IYuaA5AxGFTywJWq
ENV REDIS_HOST=videolangua-prime-cache.kwqkti.ng.0001.usw2.cache.amazonaws.com
ENV REDIS_PORT=6379

# 复制 Supervisor 模板文件
COPY supervisord.conf.j2 /etc/supervisor/conf.d/supervisord.conf.j2

# 生成最终的 supervisord 配置
RUN apt update && apt install -y gettext && \
    envsubst < /etc/supervisor/conf.d/supervisord.conf.j2 > /etc/supervisor/conf.d/supervisord.conf

# 启动 Supervisor
CMD ["/usr/bin/supervisord", "-n"]
