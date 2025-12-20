import requests
import urllib.parse

# 和风天气API配置
WEATHER_API_KEY = 'b4e323c6d79445a79437fa5e7fbadf96.lAkclf0IDT8u3WaO'
WEATHER_API_URL = 'https://devapi.qweather.com/v7/weather/now'

# 测试城市
city = '北京'

# 对城市名称进行URL编码
encoded_city = urllib.parse.quote(city)

# 构建API请求URL
url = f'{WEATHER_API_URL}?location={encoded_city}&key={WEATHER_API_KEY}'

print(f"请求URL: {url}")

try:
    # 发送API请求
    response = requests.get(url, timeout=5)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    # 解析JSON
    data = response.json()
    print(f"解析后的数据: {data}")
except Exception as e:
    print(f"错误: {e}")
