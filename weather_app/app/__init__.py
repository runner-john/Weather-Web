from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

app = Flask(__name__)

# 配置CORS支持所有来源
CORS(app)

# 配置API请求限流
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute", "10 per second"],
    storage_uri="memory://",
)

from app import views
