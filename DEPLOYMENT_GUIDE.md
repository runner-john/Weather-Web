# 云服务器天气可视化网站部署指南

## 环境准备

### 1. 云服务器选择
- 推荐使用阿里云、腾讯云或AWS等主流云服务提供商
- 操作系统选择：Ubuntu 20.04 LTS 或 CentOS 7/8
- 建议配置：至少2核4G内存，50GB存储空间

### 2. 服务器环境搭建

#### 更新系统包
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y && sudo yum upgrade -y
```

#### 安装Python环境
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv -y

# CentOS/RHEL
sudo yum install python3 python3-pip python3-venv -y
```

#### 安装Gunicorn和Nginx
```bash
# Ubuntu/Debian
sudo apt install gunicorn nginx -y

# CentOS/RHEL
sudo yum install gunicorn nginx -y
```

## 项目部署

### 1. 上传项目文件
使用SCP或Git将项目文件上传到服务器：

```bash
# 使用SCP上传
scp -r weather_app root@your-server-ip:/home/

# 或使用Git克隆
cd /home
git clone <your-repository-url>
```

### 2. 创建虚拟环境并安装依赖
```bash
cd /home/weather_app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 配置Gunicorn

#### 创建Gunicorn服务配置文件
```bash
sudo nano /etc/systemd/system/weather_app.service
```

#### 写入以下配置
```ini
[Unit]
Description=Gunicorn instance to serve weather_app
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/weather_app
Environment="PATH=/home/weather_app/venv/bin"
ExecStart=/home/weather_app/venv/bin/gunicorn --workers 3 --bind unix:weather_app.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

#### 启动Gunicorn服务
```bash
sudo systemctl start weather_app
sudo systemctl enable weather_app
```

#### 检查服务状态
```bash
sudo systemctl status weather_app
```

### 4. 配置Nginx

#### 创建Nginx配置文件
```bash
sudo nano /etc/nginx/sites-available/weather_app
```

#### 写入以下配置
```nginx
server {
    listen 80;
    server_name your-server-ip your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/weather_app/weather_app.sock;
    }

    location /static {
        alias /home/weather_app/app/static;
    }

    location /templates {
        alias /home/weather_app/app/templates;
        deny all;
    }
}
```

#### 启用配置文件
```bash
sudo ln -s /etc/nginx/sites-available/weather_app /etc/nginx/sites-enabled/
```

#### 测试Nginx配置
```bash
sudo nginx -t
```

#### 重启Nginx服务
```bash
sudo systemctl restart nginx
```

### 5. 配置防火墙

#### 允许HTTP流量
```bash
# Ubuntu (ufw)
sudo ufw allow 'Nginx HTTP'

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

## SSL证书配置（可选但推荐）

使用Let's Encrypt获取免费SSL证书：

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取并安装证书
sudo certbot --nginx -d your-domain.com

# 验证自动续期
sudo certbot renew --dry-run
```

## 项目维护

### 1. 更新项目代码
```bash
cd /home/weather_app
source venv/bin/activate
# 拉取最新代码或上传更新
# 如果有依赖变化，重新安装依赖
pip install -r requirements.txt
# 重启服务
deactivate
sudo systemctl restart weather_app
sudo systemctl restart nginx
```

### 2. 查看日志
```bash
# Gunicorn日志
sudo journalctl -u weather_app

# Nginx访问日志
sudo tail -f /var/log/nginx/access.log

# Nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

### 3. 数据库管理
```bash
# 进入项目目录
cd /home/weather_app
# 使用SQLite管理工具连接数据库
sqlite3 app/weather_cache.db
```

## 常见问题排查

1. **Gunicorn服务启动失败**
   - 检查配置文件中的路径是否正确
   - 确保www-data用户对项目目录有读写权限
   - 查看日志：`sudo journalctl -u weather_app`

2. **Nginx 502 Bad Gateway**
   - 检查Gunicorn服务是否正常运行
   - 确保socket文件存在且Nginx有权限访问
   - 查看Nginx错误日志

3. **数据库连接问题**
   - 确保SQLite数据库文件有正确的读写权限
   - 检查数据库路径配置

4. **API调用失败**
   - 检查服务器网络连接
   - 确保防火墙允许对外HTTP请求
   - 查看应用日志中的错误信息

## 性能优化建议

1. **增加Gunicorn工作进程数**
   - 根据服务器CPU核心数调整workers参数，一般为：核心数 × 2 + 1

2. **启用Nginx缓存**
   - 为静态资源和API响应配置缓存策略

3. **数据库优化**
   - 定期清理过期的缓存数据
   - 对频繁查询的字段建立索引

4. **使用CDN加速**
   - 将静态资源（CSS、JavaScript、图片）托管到CDN

通过以上步骤，您应该能够成功部署天气可视化网站并通过公网访问。如果遇到任何问题，请参考常见问题排查部分或查看相关日志文件。