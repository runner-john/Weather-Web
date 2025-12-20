#!/usr/bin/env python3
# 测试API响应格式
import requests
import json

# 测试城市列表
test_cities = ['北京', '上海', '广州']

for city in test_cities:
    try:
        url = f'http://127.0.0.1:5000/weather?city={city}'
        response = requests.get(url, timeout=10)
        
        print(f"\n=== 测试城市: {city} ===")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容类型: {response.headers.get('Content-Type')}")
        
        # 尝试解析JSON
        try:
            data = response.json()
            print(f"JSON数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print("✅ 成功解析JSON")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"原始响应内容: {response.text[:500]}...")
            
    except Exception as e:
        print(f"\n=== 测试城市: {city} ===")
        print(f"❌ 请求失败: {e}")

print("\n=== 测试完成 ===")