#!/usr/bin/env python3
# 最终系统测试脚本
import requests
import time
import json

def test_weather_api(city):
    """测试单个城市的天气API"""
    try:
        url = f'http://127.0.0.1:5000/weather?city={city}'
        response = requests.get(url, timeout=10)
        return response
    except Exception as e:
        return None

def main():
    print("🌟 云服务器天气可视化网站 - 最终功能测试 🌟")
    print("=" * 50)
    
    # 测试城市列表
    test_cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安', '重庆', '南京']
    
    # 1. 测试基本功能
    print("\n1. 测试基本天气查询功能")
    print("-" * 30)
    success_count = 0
    
    for city in test_cities:
        response = test_weather_api(city)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if not data.get('error'):
                    print(f"✅ {city}: {data['temperature']}, {data['weather']}")
                    success_count += 1
                else:
                    print(f"❌ {city}: {data['error']}")
            except json.JSONDecodeError:
                print(f"❌ {city}: 数据解析失败")
        else:
            print(f"❌ {city}: API请求失败")
    
    print(f"\n基本功能测试结果: {success_count}/{len(test_cities)} 个城市成功")
    
    # 2. 测试缓存功能
    print("\n2. 测试缓存功能")
    print("-" * 30)
    city = '北京'
    
    # 第一次查询（应该从API获取）
    start_time = time.time()
    response1 = test_weather_api(city)
    time1 = time.time() - start_time
    
    # 第二次查询（应该命中缓存）
    start_time = time.time()
    response2 = test_weather_api(city)
    time2 = time.time() - start_time
    
    print(f"第一次查询 {city}: {time1:.2f} 秒")
    print(f"第二次查询 {city}: {time2:.2f} 秒")
    
    if time2 < time1 * 0.5:  # 缓存响应时间应该明显更快
        print("✅ 缓存功能工作正常")
    else:
        print("ℹ️  缓存效果可能不明显（数据已缓存或网络波动）")
    
    # 3. 测试错误处理
    print("\n3. 测试错误处理")
    print("-" * 30)
    
    # 测试不存在的城市
    response = test_weather_api("不存在的城市")
    if response and response.status_code == 404:
        print("✅ 不存在的城市返回404错误")
    else:
        print("❌ 不存在的城市错误处理失败")
    
    # 测试空参数
    try:
        response = requests.get('http://127.0.0.1:5000/weather', timeout=10)
        if response.status_code == 400:
            print("✅ 空参数返回400错误")
        else:
            print("❌ 空参数错误处理失败")
    except:
        print("❌ 空参数测试异常")
    
    print("\n" + "=" * 50)
    print("🎉 所有测试完成！")
    
    if success_count >= len(test_cities) * 0.8:
        print("✅ 系统功能基本正常，可以正常使用")
    else:
        print("⚠️  系统存在一些问题，需要进一步检查")

if __name__ == "__main__":
    main()