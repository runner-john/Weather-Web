# 阿里云服务器部署说明

## 一、服务器环境准备

### 1. 登录阿里云服务器
```bash
ssh root@你的服务器IP
```

### 2. 安装Python环境
```bash
# 更新系统
apt-get update
apt-get upgrade -y

# 安装Python 3.9和虚拟环境工具
apt-get install -y python3.9 python3.9-dev python3-venv python3-pip

# 设置Python 3.9为默认
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
```

### 3. 安装Nginx
```bash
apt-get install -y nginx
```

## 二、项目部署

### 1. 上传项目到服务器
```bash
# 使用scp命令上传项目文件
scp -r ./weather_app root@你的服务器IP:/var/www/
```

### 2. 配置项目环境
```bash
# 进入项目目录
cd /var/www/weather_app

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装项目依赖
pip install -r requirements.txt
```

### 3. 配置Nginx反向代理
```bash
# 创建Nginx配置文件
nano /etc/nginx/sites-available/weather_app
```

将以下内容粘贴到配置文件中：
```nginx
server {
    listen 80;
    server_name 你的域名或服务器IP;

    # 静态文件处理
    location /static {
        alias /var/www/weather_app/app/static;
        expires 1d;
    }

    # 反向代理到Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 错误页面
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

启用Nginx配置：
```bash
ln -s /etc/nginx/sites-available/weather_app /etc/nginx/sites-enabled/

# 测试Nginx配置是否正确
nginx -t

# 重启Nginx服务
systemctl restart nginx
```

### 4. 启动Gunicorn服务
```bash
# 确保已激活虚拟环境
source .venv/bin/activate

# 创建日志目录
mkdir -p logs

# 启动Gunicorn服务
sh start_gunicorn.sh
```

## 三、服务管理

### 1. 启动服务
```bash
cd /var/www/weather_app
source .venv/bin/activate
sh start_gunicorn.sh
```

### 2. 停止服务
```bash
# 查看Gunicorn进程
ps aux | grep gunicorn

# 终止进程
kill -9 进程ID
```

### 3. 查看日志
```bash
# 查看访问日志
tail -f logs/gunicorn_access.log

# 查看错误日志
tail -f logs/gunicorn_error.log
```

## 四、常见问题排查

### 1. 无法访问网站
- 检查服务器安全组是否开放了80端口
- 检查Nginx服务是否正在运行：`systemctl status nginx`
- 检查Gunicorn服务是否正在运行：`ps aux | grep gunicorn`

### 2. 502 Bad Gateway错误
- 检查Gunicorn服务是否正在运行
- 检查Gunicorn配置文件中的绑定地址和端口是否正确
- 查看Nginx错误日志：`tail -f /var/log/nginx/error.log`

### 3. 500 Internal Server Error错误
- 查看Gunicorn错误日志：`tail -f logs/gunicorn_error.log`
- 检查项目依赖是否完整安装

## 五、功能验证

部署完成后，可以通过以下方式验证功能：

1. 访问网站首页：`http://你的服务器IP`
2. 查询天气信息：在搜索框中输入城市名称（如北京、上海）
3. 查看热门城市温度对比图表
4. 查看历史天气数据
5. 验证低温预警功能（查询气温较低的城市，如哈尔滨）

## 六、项目更新

1. 上传更新后的项目文件
2. 重启Gunicorn服务
```bash
# 停止当前服务
kill -9 $(cat logs/gunicorn.pid)

# 启动新服务
sh start_gunicorn.sh
```

## 七、注意事项

1. 确保服务器的安全组配置允许80端口访问
2. 定期备份数据库文件（`app/weather.db`）
3. 定期清理日志文件，避免占用过多磁盘空间
4. 如需使用域名访问，需将域名解析到服务器IP地址
