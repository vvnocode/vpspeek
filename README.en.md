## Features

- Supports both automatic and manual speed testing.
- Can be configured to randomly select the next execution time within a specific time range, making the timing of tasks
  less predictable.
- Allows querying and sorting of speed test results.
- Supports different operation modes to prevent attacks.
- One-click installation and upgrade are supported.
- User timezone configuration is supported, making it more user-friendly for VPS deployments in different time zones.
  The default timezone is Asia/Shanghai.

### Interface

Access via `ip:5000`.

![](https://s1.locimg.com/2024/09/18/bdb8e17c0bcd7.png)

### Resource Usage

- Binary file size: 9M, with around 41M of memory usage during runtime.
  ![](https://s1.locimg.com/2024/09/18/ab84785aeb29f.png)

- Docker image size: around 27M, with around 25M of memory usage during runtime.
  ![](https://s1.locimg.com/2024/09/16/b050a4d1e0127.png)

## Usage

### Installation

- Install on a VPS to test international network speeds.
- Install on NAS to test download speeds from a specified speed test address (configured in `conf.yaml`).

#### Script Installation

This script installs the precompiled binary file. It will automatically generate a `conf.yaml` configuration file and a
`data.json` file for storing data.  
If you modify the `conf.yaml` file, you need to restart the service with `systemctl restart vpspeek`.

```shell
curl -L https://raw.githubusercontent.com/vvnocode/vpspeek/master/install.sh -o vpspeek.sh && chmod +x vpspeek.sh && sudo ./vpspeek.sh
```

#### Using Docker Command Line

```shell
docker run --name vpspeek -p 5000:5000 vvnocode/vpspeek:latest
```

Mapping file.

```shell
docker run --name vpspeek -p 5000:5000 -v /mnt/user/appdata/vpspeek/vvnode/data.json:/app/data.json -v /mnt/user/appdata/vpspeek/vvnode/conf.yaml:/app/conf.yaml vvnocode/vpspeek:latest
```

#### Using Docker Compose

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

#### Notes

If you are using Docker with file mapping, ensure that the mapped host files exist:

1. Create the `conf.yaml` file (it can be empty).
2. Create the `data.json` file (it can be empty).

### Configuration

- The default configuration works out of the box. If needed, modify the `conf.yaml` file.
- You can configure the speed test address; the default is Cloudflare's test server.
- You can configure different modes in `conf.yaml`. The default mode is `default`.
    - `full`: Full functionality, with no security checks on API requests (password login will be added in the future).
    - `default`: No security checks, but only query operations are allowed. Manual speed testing is disabled.
    - `safe`: API requests require a validation key in the header, which is defined in the `conf.yaml`.
- Under the default settings, the maximum daily download amount is calculated as `60 / max_interval * 24 * 100M`. For
  example, when `max_interval = 60`, the maximum daily download is 2400M.
- Similarly, under extreme conditions, the maximum daily download is `60 / min_interval * 24 * 100M`. For example, when
  `min_interval = 30`, the maximum daily download is 4800M.
- If configured appropriately, the tasks will be distributed across 24 hours and won't put too much pressure on the
  server.

## Development

The speed test is done by using the `curl` command to download files of a specified size.

```shell
curl -o /dev/null -s -w "%{size_download} %{time_total} %{speed_download}\n" 'https://speed.cloudflare.com/__down?during=download&bytes=104857600'
```

### Development Environment

- Python 3.9
- PyCharm

### Build

#### Building Binary

Packaging command:

```shell
pyinstaller --onefile --add-data "conf.yaml.default:." --add-data "templates:templates" --name vpspeek app.py 
```

#### Building Docker Image

```shell
# Building for amd64 and arm64 platforms separately
# For linux/amd64:
docker build --platform linux/amd64 -t vvnocode/vpspeek:0.3 .
# Tag the image:
docker tag vvnocode/vpspeek:0.3 vvnocode/vpspeek:latest
# Push to registry:
docker push vvnocode/vpspeek:0.3
docker push vvnocode/vpspeek:latest

# For linux/arm64:
docker build --platform linux/arm64 -t vvnocode/vpspeek:0.3 .
# Repeat tagging and pushing steps as above

# Build for both amd64 and arm64 simultaneously (if supported by your system):
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t vvnocode/vpspeek:0.1 --load .
# Tag the image:
docker tag vvnocode/vpspeek:0.1 vvnocode/vpspeek:latest
# Push to registry:
docker push vvnocode/vpspeek:0.1
docker push vvnocode/vpspeek:latest
```