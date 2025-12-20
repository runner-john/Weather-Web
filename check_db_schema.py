#!/usr/bin/env python3
# 检查数据库表结构
import sqlite3
import os

# 数据库文件路径
DB_PATH = os.path.join('weather_app', 'app', 'weather_cache.db')

def check_database_schema():
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("数据库表结构：")
        print("=" * 50)
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\n表名: {table_name}")
            print(f"-" * 20)
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for column in columns:
                col_id, col_name, col_type, col_notnull, col_default, col_pk = column
                print(f"{col_name} ({col_type})" + 
                      (" NOT NULL" if col_notnull else "") +
                      (" DEFAULT '{}'" if isinstance(col_default, str) else " DEFAULT {}").format(col_default) if col_default else "" +
                      (" PRIMARY KEY" if col_pk else ""))
            
            # 显示前5条数据示例
            print(f"\n数据示例 (前5条):")
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        print(row)
                else:
                    print("无数据")
            except Exception as e:
                print(f"获取数据失败: {e}")
        
        conn.close()
        print("\n" + "=" * 50)
        print("数据库结构检查完成！")
        
    except sqlite3.Error as e:
        print(f"数据库操作失败: {e}")
    except Exception as e:
        print(f"程序错误: {e}")

if __name__ == "__main__":
    check_database_schema()