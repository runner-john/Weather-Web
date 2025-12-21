from flask import render_template, request, jsonify
from app import app, limiter
import requests
import os
import random
from dotenv import load_dotenv
import urllib.parse
import datetime
from app.database import WeatherDatabase

load_dotenv()

# 使用Open-Meteo API（免费无需API密钥）
# 地理编码API - 根据城市名称获取经纬度
GEOCODING_API_URL = 'https://geocoding-api.open-meteo.com/v1/search'
# 当前天气API
WEATHER_API_URL = 'https://api.open-meteo.com/v1/forecast'

# 城市坐标映射表（针对Open-Meteo无法识别的中文城市）
city_coordinates = {
    # 直辖市
    '北京': {'latitude': 39.9042, 'longitude': 116.4074, 'name': '北京'},
    '上海': {'latitude': 31.2304, 'longitude': 121.4737, 'name': '上海'},
    '天津': {'latitude': 39.1256, 'longitude': 117.1902, 'name': '天津'},
    '重庆': {'latitude': 29.4316, 'longitude': 106.9123, 'name': '重庆'},
    
    # 省会城市
    '广州': {'latitude': 23.1291, 'longitude': 113.2644, 'name': '广州'},
    '深圳': {'latitude': 22.5431, 'longitude': 114.0579, 'name': '深圳'},
    '杭州': {'latitude': 30.2741, 'longitude': 120.1551, 'name': '杭州'},
    '成都': {'latitude': 30.5728, 'longitude': 104.0668, 'name': '成都'},
    '武汉': {'latitude': 30.5928, 'longitude': 114.3055, 'name': '武汉'},
    '西安': {'latitude': 34.3416, 'longitude': 108.9398, 'name': '西安'},
    '南京': {'latitude': 32.0603, 'longitude': 118.7969, 'name': '南京'},
    '昆明': {'latitude': 25.0389, 'longitude': 102.7183, 'name': '昆明'},
    '呼和浩特': {'latitude': 40.8181, 'longitude': 111.7626, 'name': '呼和浩特'},
    '拉萨': {'latitude': 29.6524, 'longitude': 91.1735, 'name': '拉萨'},
    '乌鲁木齐': {'latitude': 43.8256, 'longitude': 87.6168, 'name': '乌鲁木齐'},
    '银川': {'latitude': 38.4681, 'longitude': 106.2328, 'name': '银川'},
    '西宁': {'latitude': 36.6171, 'longitude': 101.7782, 'name': '西宁'},
    '南宁': {'latitude': 22.8170, 'longitude': 108.3661, 'name': '南宁'},
    '济南': {'latitude': 36.6683, 'longitude': 117.0203, 'name': '济南'},
    '石家庄': {'latitude': 38.0428, 'longitude': 114.5149, 'name': '石家庄'},
    '哈尔滨': {'latitude': 45.8038, 'longitude': 126.5349, 'name': '哈尔滨'},
    '长春': {'latitude': 43.8256, 'longitude': 125.3245, 'name': '长春'},
    '沈阳': {'latitude': 41.8057, 'longitude': 123.4315, 'name': '沈阳'},
    '郑州': {'latitude': 34.8074, 'longitude': 113.4668, 'name': '郑州'},
    '合肥': {'latitude': 31.8206, 'longitude': 117.2272, 'name': '合肥'},
    '福州': {'latitude': 26.0745, 'longitude': 119.3062, 'name': '福州'},
    '南昌': {'latitude': 28.6827, 'longitude': 115.8595, 'name': '南昌'},
    '长沙': {'latitude': 28.2278, 'longitude': 112.9388, 'name': '长沙'},
    '贵阳': {'latitude': 26.5783, 'longitude': 106.7078, 'name': '贵阳'},
    '海口': {'latitude': 20.0440, 'longitude': 110.3593, 'name': '海口'},
    '兰州': {'latitude': 36.0580, 'longitude': 103.8235, 'name': '兰州'}
}

# 城市别名映射表，确保特殊城市能被正确识别
city_aliases = {
    '重庆': '重庆市',
    '西藏': '拉萨',
    '内蒙': '呼和浩特',
    '新疆': '乌鲁木齐',
    '内蒙古': '呼和浩特',  # 添加更多别名
    '广西': '南宁',
    '宁夏': '银川',
    '青海': '西宁'
}

# 数据库实例
weather_db = WeatherDatabase()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather')
@limiter.limit("60 per minute")  # 提高速率限制到每分钟60次
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': '请提供城市名称'}), 400

    try:
        # 从缓存获取数据（1小时内有效）
        cached_data = weather_db.get_cached_weather(city)
        if cached_data:
            return jsonify(cached_data), 200
        
        # 标准化城市名称：移除'市'后缀
        normalized_city = city.replace('市', '')
        
        # 使用别名（如果有）
        city_name = city_aliases.get(normalized_city, normalized_city)
        
        # 首先检查是否在城市坐标映射表中
        if city_name in city_coordinates:
            location = city_coordinates[city_name]
            latitude = location['latitude']
            longitude = location['longitude']
            city_name = location['name']
        else:
            # 如果不在映射表中，调用地理编码API
            geo_params = {
                'name': city_name,
                'country': 'CN',  # 指定中国
                'count': 5,  # 获取更多结果
                'language': 'zh'
            }
            
            geo_response = requests.get(GEOCODING_API_URL, params=geo_params, timeout=5)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data.get('results'):
                return jsonify({'error': '未找到该城市，请确认城市名称是否正确'}), 404
            
            # 获取经纬度
            location = geo_data['results'][0]
            latitude = location['latitude']
            longitude = location['longitude']
            city_name = location['name']
        
        # 最终标准化：确保存储的城市名称没有'市'后缀
        city_name = city_name.replace('市', '')
        
        # 2. 使用经纬度调用天气API获取天气数据
        weather_params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,showers,snowfall,cloud_cover,wind_speed_10m,wind_direction_10m,pressure_msl,visibility',
            'wind_speed_unit': 'kmh',
            'timezone': 'Asia/Shanghai'
        }
        
        weather_response = requests.get(WEATHER_API_URL, params=weather_params, timeout=5)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        if not weather_data.get('current'):
            return jsonify({'error': '获取天气信息失败: 数据格式错误'}), 400
        
        # 3. 提取天气数据
        current_data = weather_data['current']
        
        # 天气状况映射
        weather_conditions = {
            0: '晴朗',
            1: '晴间多云',
            2: '多云',
            3: '阴',
            45: '雾',
            48: '霾',
            51: '小雨',
            53: '中雨',
            55: '大雨',
            56: '冻雨',
            57: '冻雨',
            61: '小雨',
            63: '中雨',
            65: '大雨',
            66: '冻雨',
            67: '冻雨',
            71: '小雪',
            73: '中雪',
            75: '大雪',
            77: '雪粒',
            80: '阵雨',
            81: '阵雨',
            82: '强阵雨',
            85: '阵雪',
            86: '阵雪'
        }
        
        # 获取天气代码对应的天气状况
        weather_code = current_data.get('weather_code', 0)
        weather_text = weather_conditions.get(weather_code, '未知')
        
        # 风向映射
        wind_directions = {
            0: '北',
            45: '东北',
            90: '东',
            135: '东南',
            180: '南',
            225: '西南',
            270: '西',
            315: '西北',
            360: '北'
        }
        
        # 获取风向
        wind_dir_deg = current_data.get('wind_direction_10m', 0)
        # 找到最接近的风向
        closest_dir = min(wind_directions.keys(), key=lambda x: abs(x - wind_dir_deg))
        wind_dir_text = wind_directions[closest_dir]
        
        # 风速转换为风力等级
        wind_speed_kmh = current_data.get('wind_speed_10m', 0)
        wind_speed_mps = wind_speed_kmh / 3.6
        
        # 使用列表查找风力等级，更高效
        wind_levels = [(0.3, 0), (1.6, 1), (3.4, 2), (5.5, 3), (8.0, 4), 
                      (10.8, 5), (13.9, 6), (17.2, 7), (20.8, 8), (24.5, 9), 
                      (28.5, 10), (32.7, 11), (float('inf'), 12)]
        
        wind_level = 0
        for speed, level in wind_levels:
            if wind_speed_mps < speed:
                wind_level = level
                break
        
        # 生成合理的模拟AQI数据（0-500之间）
        # 根据天气状况调整AQI范围
        if weather_code in [45, 48]:  # 雾和霾
            aqi_value = random.randint(100, 300)  # 雾霾天气AQI较高
        elif wind_level >= 3:  # 风力较大时AQI较低
            aqi_value = random.randint(0, 100)
        else:  # 一般天气
            aqi_value = random.randint(50, 150)
        
        # 格式化输出
        result = {
            'city': city_name,
            'temperature': f'{current_data["temperature_2m"]}°C',
            'humidity': f'{current_data["relative_humidity_2m"]}%',
            'weather': weather_text,
            'wind': f'{wind_level}级',
            'wind_dir': wind_dir_text,
            'pressure': f'{current_data["pressure_msl"]}hPa',
            'visibility': f'{current_data["visibility"] / 1000}km',  # 转换为km
            'aqi': aqi_value
        }
        
        # 将获取的天气数据保存到数据库缓存
        weather_db.save_weather(result)
        
        # 同时保存到历史天气表（每天每小时只保存一条）
        weather_db.save_historical_weather(result)
        
        return jsonify(result), 200
    except requests.exceptions.Timeout:
        return jsonify({'error': '网络连接超时，请稍后重试'}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({'error': '网络连接失败，请检查网络设置'}), 500
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'API请求失败: {str(e)}'}), 500
    except (KeyError, IndexError) as e:
        return jsonify({'error': '数据解析失败，请确认城市名称是否正确'}), 400
    except Exception as e:
        return jsonify({'error': f'获取天气信息失败: {str(e)}'}), 500

@app.route('/historical')
@limiter.limit("60 per minute")
def get_historical_weather():
    city = request.args.get('city')
    date = request.args.get('date')
    
    if not city:
        return jsonify({'error': '请提供城市名称'}), 400
    
    if not date:
        return jsonify({'error': '请提供查询日期，格式：YYYY-MM-DD'}), 400
    
    try:
        # 标准化城市名称：移除'市'后缀
        normalized_city = city.replace('市', '')
        
        # 使用别名（如果有）
        city_name = city_aliases.get(normalized_city, normalized_city)
        
        # 验证日期格式
        datetime.datetime.strptime(date, '%Y-%m-%d')
        
        # 查询历史天气数据
        historical_data = weather_db.get_historical_weather_by_date(city_name, date)
        
        if not historical_data:
            return jsonify({'error': f'未找到{city}在{date}的历史天气数据'}), 404
        
        return jsonify({'city': city_name, 'date': date, 'data': historical_data}), 200
        
    except ValueError:
        return jsonify({'error': '日期格式错误，请使用YYYY-MM-DD格式'}), 400
    except Exception as e:
        return jsonify({'error': f'查询历史天气失败: {str(e)}'}), 500

@app.route('/weekly-forecast')
@limiter.limit("60 per minute")
def get_weekly_forecast():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': '请提供城市名称'}), 400

    try:
        # 标准化城市名称：移除'市'后缀
        normalized_city = city.replace('市', '')
        
        # 使用别名（如果有）
        city_name = city_aliases.get(normalized_city, normalized_city)
        
        # 首先检查是否在城市坐标映射表中
        if city_name in city_coordinates:
            location = city_coordinates[city_name]
            latitude = location['latitude']
            longitude = location['longitude']
            city_name = location['name']
        else:
            # 如果不在映射表中，调用地理编码API
            geo_params = {
                'name': city_name,
                'country': 'CN',  # 指定中国
                'count': 5,  # 获取更多结果
                'language': 'zh'
            }
            
            geo_response = requests.get(GEOCODING_API_URL, params=geo_params, timeout=5)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data.get('results'):
                return jsonify({'error': '未找到该城市，请确认城市名称是否正确'}), 404
            
            # 获取经纬度
            location = geo_data['results'][0]
            latitude = location['latitude']
            longitude = location['longitude']
            city_name = location['name']
        
        # 最终标准化：确保存储的城市名称没有'市'后缀
        city_name = city_name.replace('市', '')
        
        # 调用Open-Meteo API获取未来一周天气预报
        weather_params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,wind_speed_10m_max',
            'timezone': 'Asia/Shanghai',
            'forecast_days': 7  # 未来7天
        }
        
        weather_response = requests.get(WEATHER_API_URL, params=weather_params, timeout=5)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        if not weather_data.get('daily'):
            return jsonify({'error': '获取天气信息失败: 数据格式错误'}), 400
        
        # 提取未来一周天气数据
        daily_data = weather_data['daily']
        
        # 格式化输出
        forecast_data = []
        for i in range(len(daily_data['time'])):
            forecast_data.append({
                'date': daily_data['time'][i],
                'max_temp': daily_data['temperature_2m_max'][i],
                'min_temp': daily_data['temperature_2m_min'][i],
                'max_apparent_temp': daily_data['apparent_temperature_max'][i],
                'min_apparent_temp': daily_data['apparent_temperature_min'][i],
                'precipitation': daily_data['precipitation_sum'][i],
                'wind_speed_max': daily_data['wind_speed_10m_max'][i]
            })
        
        result = {
            'city': city_name,
            'forecast': forecast_data
        }
        
        return jsonify(result), 200
        
    except requests.exceptions.Timeout:
        return jsonify({'error': '网络连接超时，请稍后重试'}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({'error': '网络连接失败，请检查网络设置'}), 500
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'API请求失败: {str(e)}'}), 500
    except (KeyError, IndexError) as e:
        return jsonify({'error': '数据解析失败，请确认城市名称是否正确'}), 400
    except Exception as e:
        return jsonify({'error': f'获取天气信息失败: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'ok', 'message': 'Weather App is running'}), 200

@app.route('/popular-cities')
def get_popular_cities():
    """获取热门城市列表"""
    try:
        popular_cities = weather_db.get_popular_cities()
        return jsonify({'cities': popular_cities}), 200
    except Exception as e:
        return jsonify({'error': f'获取热门城市列表失败: {str(e)}'}), 500
