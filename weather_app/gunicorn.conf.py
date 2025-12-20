# Gunicorn 配置文件

# 绑定地址和端口
bind = '0.0.0.0:5000'

# 工作进程数（推荐为CPU核心数 * 2 + 1）
workers = 3

# 工作模式（sync, gevent, eventlet等）
worker_class = 'sync'

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 100

# 访问日志和错误日志
accesslog = './logs/gunicorn_access.log'
errorlog = './logs/gunicorn_error.log'

# 日志级别（debug, info, warning, error, critical）
loglevel = 'info'

# PID文件
pidfile = './logs/gunicorn.pid'

# 后台运行（部署时使用）
daemon = True

# 应用路径
wsgi_app = 'app:app'
