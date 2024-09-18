FROM python:3.9-alpine

# 设置默认时区
ENV TZ=Asia/Shanghai

# 更新软件包列表并安装curl
RUN apk update && apk add --no-cache curl

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY templates ./templates
COPY app.py .
COPY conf.yaml.default .

CMD ["python", "app.py"]