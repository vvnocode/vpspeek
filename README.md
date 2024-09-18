## 功能介绍

- 可以自动执行测速，也可以手动执行。
- 可以配置在一个时间范围内随机选择下次执行时间，这样定时任务的特征会小一点。
- 可以对测速结果查询、排序。
- 可以配置运行模式，防止被人攻击
- 支持一键安装&升级。
- 支持配置用户时区，让部署在不同时区vps上的显示更友好。默认用户时区Asia/Shanghai。

### 页面展示

输入ip:5000访问

![](https://s1.locimg.com/2024/09/18/bdb8e17c0bcd7.png)

### 运行资源占用

- 二进制文件大小9M，运行时内存占用41M左右
  ![](https://s1.locimg.com/2024/09/18/ab84785aeb29f.png)

- docker镜像大小在27M左右，运行时占用系统内存25M左右。
  ![](https://s1.locimg.com/2024/09/16/b050a4d1e0127.png)

## 使用

### 安装

- 安装到vps上，可以测试国际网络速度。
- 安装到nas上，可以测试nas从测速地址（可在conf.yaml配置）下载文件的速度。

#### 使用脚本安装

此脚本会安装编译好的二进制文件。运行会自动生成conf.yam配置文件和数据存储data.json文件。
如果更改配置文件conf.yaml，需要运行`systemctl restart vpspeek`重启服务。

```shell
curl -L https://raw.githubusercontent.com/vvnocode/vpspeek/master/install.sh -o vpspeek.sh && chmod +x vpspeek.sh && sudo ./vpspeek.sh
```

#### 使用docker命令行

```shell
docker run --name vpspeek -p 5000:5000 vvnocode/vpspeek:latest
# 映射文件
docker run --name vpspeek -p 5000:5000 -v /mnt/user/appdata/vpspeek/vvnode/data.json:/app/data.json -v /mnt/user/appdata/vpspeek/vvnode/conf.yaml:/app/conf.yaml vvnocode/vpspeek:latest
```

#### 使用docker-compose

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

#### 注意

使用docker安装且需要映射文件的，需要确保映射的宿主机文件存在。

1. 需要创建conf.yaml，可以是空文件。
2. 需要创建data.json，可以是空文件。

### 配置

- 默认配置即可使用，如需修改，请修改conf.yaml。
- 可以自行配置测速地址，默认是cloudflare的测速地址。
- 可以对模式进行配置。conf.yaml中，mode默认是default。full：完整的功能，调用接口无安全验证，后续会改为使用密码登录；default：无安全验证，但是只能查询，关闭手动测速接口；safe：接口需要在header增加校验，参数为conf.yaml的key；
- 默认配置在极限情况下，每天测速下载最少为60/max_interval\*24\*100M，当max_interval=60时，每日下载量最多2400M数据。
- 默认配置在极限情况下，每天测速下载最少为60/min_interval\*24\*100M，当min_interval=30时，每日下载量最多4800M数据。
- 如果配置合理，任务分散到24小时执行，并不会对服务器造成过大压力。

## 开发

基于curl命令下载指定大小的文件达到测速目的。

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