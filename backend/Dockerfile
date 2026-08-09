# 使用 Python 3.10 作为基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 包和系统库
RUN apt-get update && \
    apt-get install -y libgl1 && \
    pip install -r requirements.txt

# 复制文件
COPY . .

# 暴露端口（Hugging Face 默认是 7860）
EXPOSE 7860

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
