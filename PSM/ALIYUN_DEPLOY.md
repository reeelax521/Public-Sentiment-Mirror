# 阿里云部署 Public Sentiment Mirror

目标：让 `publicsentimentmirror.cyou` 直接打开 Streamlit 应用。

## 方案选择

Render 要求绑定银行卡时，可以改用阿里云完成。推荐方案是：

```text
阿里云 ECS 云服务器
→ 安装 Python、Git、Nginx
→ 拉取 GitHub 项目
→ Streamlit 在本机 8501 端口运行
→ Nginx 把 80/443 端口请求转发到 8501
→ 阿里云 DNS 把域名解析到 ECS 公网 IP
```

Streamlit 官方知识库也建议用 Nginx/Apache 这类 Web Server 做反向代理，把域名的 80 端口请求转发到 Streamlit 运行端口。

## 一、开通 ECS

在阿里云控制台开通一台 ECS：

- 地域：华东 1（杭州）、华北 2（北京）、华南 1（深圳）都可以
- 系统：Ubuntu 22.04 LTS
- 配置：1 核 1G 起步可试用，2G 内存更稳
- 公网 IP：需要
- 安全组开放端口：22、80、443

阿里云新用户可查看免费试用中心，部分 ECS 有免费试用资格。注意免费试用和带宽/数据盘等配置可能有费用边界，开通前看清楚价格。

## 二、域名解析

进入阿里云：

```text
云解析 DNS → publicsentimentmirror.cyou → 解析设置
```

添加两条 A 记录：

```text
主机记录: @
记录类型: A
记录值: ECS 公网 IP
```

```text
主机记录: www
记录类型: A
记录值: ECS 公网 IP
```

## 三、服务器安装环境

SSH 登录 ECS 后执行：

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git nginx
```

## 四、部署项目

如果你的 GitHub 仓库里根目录是 `PSM` 文件夹：

```bash
cd /opt
sudo git clone 你的GitHub仓库地址 public-sentiment-mirror-repo
sudo cp -r public-sentiment-mirror-repo/PSM public-sentiment-mirror
sudo chown -R $USER:$USER /opt/public-sentiment-mirror
```

如果仓库根目录直接就是 `app.py`、`src/`、`pages/`：

```bash
cd /opt
sudo git clone 你的GitHub仓库地址 public-sentiment-mirror
sudo chown -R $USER:$USER /opt/public-sentiment-mirror
```

安装依赖：

```bash
cd /opt/public-sentiment-mirror
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

测试运行：

```bash
streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

看到服务启动后，按 `Ctrl+C` 停止。

## 五、配置 systemd 后台服务

```bash
sudo cp /opt/public-sentiment-mirror/deploy/public-sentiment-mirror.service /etc/systemd/system/public-sentiment-mirror.service
sudo systemctl daemon-reload
sudo systemctl enable --now public-sentiment-mirror
sudo systemctl status public-sentiment-mirror
```

## 六、配置 Nginx

```bash
sudo cp /opt/public-sentiment-mirror/deploy/nginx-publicsentimentmirror.conf /etc/nginx/sites-available/publicsentimentmirror
sudo ln -s /etc/nginx/sites-available/publicsentimentmirror /etc/nginx/sites-enabled/publicsentimentmirror
sudo nginx -t
sudo systemctl reload nginx
```

此时访问：

```text
http://publicsentimentmirror.cyou
```

应该能看到应用。

## 七、配置 HTTPS

建议使用 Certbot：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d publicsentimentmirror.cyou -d www.publicsentimentmirror.cyou
```

完成后访问：

```text
https://publicsentimentmirror.cyou
```

## 八、常见问题

如果打不开：

- 检查阿里云安全组是否开放 80/443。
- 检查 DNS 是否解析到 ECS 公网 IP。
- 执行 `sudo systemctl status public-sentiment-mirror` 查看应用是否运行。
- 执行 `sudo nginx -t` 查看 Nginx 配置是否正确。
- 执行 `curl http://127.0.0.1:8501` 查看 Streamlit 本机服务是否正常。

