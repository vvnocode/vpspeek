## 功能介绍

- 可以自动执行测速，也可以手动执行。
- 可以配置在一个时间范围内随机选择下次执行时间，这样定时任务的特征会小一点。
- 可以对测速结果查询、排序。
- 可以配置运行模式，防止被人攻击
- 支持一键安装&升级
- 支持配置用户时区，让部署在不同时区vps上的显示更友好。默认用户时区Asia/Shanghai。

### 页面展示

输入ip:5000访问

![](https://s1.locimg.com/2024/09/18/42aca6247a94a.png)

### 运行资源占用

运行时占用系统内存25M左右。

![](https://s1.locimg.com/2024/09/16/b050a4d1e0127.png)

## 开发

测速基于下面命令

```shell
curl -o /dev/null -s -w "%{size_download} %{time_total} %{speed_download}\n" 'https://speed.cloudflare.com/__down?during=download&bytes=104857600'
```

### 开发环境

- python 3.9
- PyCharm

### 构建

#### 构建二进制文件

打包命令

```shell
pyinstaller --onefile --add-data "conf.yaml.default:." --add-data "templates:templates" --name vpspeek app.py 
```

#### 构建docker镜像

```shell
#分别构建amd64、arm64
#linux/amd64
docker build --platform linux/amd64 -t vvnocode/vpspeek:0.3 .
#tag
docker tag vvnocode/vpspeek:0.3 vvnocode/vpspeek:latest
#推送
docker push vvnocode/vpspeek:0.3
docker push vvnocode/vpspeek:latest

#linux/arm64
docker build --platform linux/arm64 -t vvnocode/vpspeek:0.3 .
#重复上面操作tag、push

#同时构建amd64、arm64（我的电脑不支持）
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t vvnocode/vpspeek:0.1 --load .
#tag
docker tag vvnocode/vpspeek:0.1 vvnocode/vpspeek:latest
#推送
docker push vvnocode/vpspeek:0.1
docker push vvnocode/vpspeek:latest

```

## 使用

### 使用二进制文件一键运行脚本

此脚本运行会自动生成conf.yam配置文件和数据存储data.json文件。

```shell
curl -L https://raw.githubusercontent.com/vvnocode/vpspeek/master/install.sh -o vpspeek.sh && chmod +x vpspeek.sh && sudo ./vpspeek.sh
```

### 使用docker

- 命令行

```shell
docker run --name vpspeek -p 5000:5000 vvnocode/vpspeek:latest
# 映射文件
docker run --name vpspeek -p 5000:5000 -v /mnt/user/appdata/vpspeek/vvnode/data.json:/app/data.json -v /mnt/user/appdata/vpspeek/vvnode/conf.yaml:/app/conf.yaml vvnocode/vpspeek:latest
```

- docker-compose

```yaml
services:
  vpspeek:
    image: vvnocode/vpspeek:latest
    container_name: vpspeek
    ports:
      - "5000:5000"
    volumes:
      - /mnt/user/appdata/vpspeek/vvnode/data.json:/app/data.json
      - /mnt/user/appdata/vpspeek/vvnode/conf.yaml:/app/conf.yaml
    restart: unless-stopped
```

### 注意

如果需要将测速数据保存或者修改配置，先跑下容器，然后把要映射出来的文件拷贝出来再进行映射。

### 配置

默认配置即可使用，如需修改，请修改conf.yaml。
默认配置在极限情况下，每天测速下载最多4800M，最少2400M数据，且分散到24小时执行，并不会对服务器造成过大压力。

```yaml
# 服务端口
port: 5000
speedtest_url: https://speed.cloudflare.com/__down?during=download&bytes=104857600
# 下次执行最快分钟
min_interval: 30
# 下次执行最慢分钟
max_interval: 60
# vps 名称
vps_name: 我的xx
# 模式
# full：完整的功能，调用接口无安全验证；default：无安全验证，但是只能查询，关闭手动测速接口；safe：接口需要在header增加校验，参数为conf.yaml的key；
mode:
# 调用接口需要的key
key:
```
