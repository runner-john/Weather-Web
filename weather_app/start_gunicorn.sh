#!/bin/bash

# 创建日志目录
mkdir -p logs

# 激活虚拟环境
source .venv/bin/activate

# 启动Gunicorn服务
gunicorn -c gunicorn.conf.py app:app

# 显示服务状态
echo "Gunicorn服务已启动，日志文件位于 logs/ 目录"
