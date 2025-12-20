import sqlite3
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'weather_cache.db')

def check_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("数据库连接成功！")
        print("\n--- 检查表格结构 ---")
        
        # 获取所有表格
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\n{table_name} 表结构：")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  {column[1]} ({column[2]})")
        
        print("\n--- 检查weather_cache表数据 ---")
        cursor.execute("SELECT COUNT(*) FROM weather_cache;")
        count = cursor.fetchone()[0]
        print(f"缓存数据总数：{count}")
        
        if count > 0:
            cursor.execute("SELECT DISTINCT city FROM weather_cache;")
            cities = cursor.fetchall()
            print("缓存的城市：")
            for city in cities:
                print(f"  - {city[0]}")
            
            cursor.execute("SELECT * FROM weather_cache ORDER BY timestamp DESC LIMIT 5;")
            recent = cursor.fetchall()
            print("\n最近5条缓存数据：")
            for row in recent:
                print(f"  {row[1]}: {row[2]}, {row[4]}, {row[10]}")
        
        print("\n--- 检查historical_weather表数据 ---")
        cursor.execute("SELECT COUNT(*) FROM historical_weather;")
        count = cursor.fetchone()[0]
        print(f"历史数据总数：{count}")
        
        if count > 0:
            cursor.execute("SELECT DISTINCT city FROM historical_weather;")
            cities = cursor.fetchall()
            print("历史数据中的城市：")
            for city in cities:
                print(f"  - {city[0]}")
            
            cursor.execute("SELECT * FROM historical_weather ORDER BY record_date DESC, record_hour DESC LIMIT 5;")
            recent = cursor.fetchall()
            print("\n最近5条历史数据：")
            for row in recent:
                print(f"  {row[1]}, {row[9]} {row[10]}时, {row[2]}, {row[4]}, AQI:{row[12]}")
        
        conn.close()
        print("\n数据库检查完成！")
        
    except sqlite3.Error as e:
        print(f"数据库错误：{e}")
    except Exception as e:
        print(f"其他错误：{e}")

if __name__ == "__main__":
    check_database()
