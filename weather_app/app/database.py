import sqlite3
import datetime
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'weather_cache.db')

class WeatherDatabase:
    def __init__(self):
        # 初始化时创建表结构
        self.create_tables()
    
    def connect(self):
        """连接到SQLite数据库"""
        try:
            conn = sqlite3.connect(DB_PATH)
            return conn
        except sqlite3.Error as e:
            print(f"数据库连接失败: {e}")
            return None
    
    def create_tables(self):
        """创建数据库表"""
        conn = self.connect()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # 创建天气缓存表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    temperature TEXT,
                    humidity TEXT,
                    weather TEXT,
                    wind TEXT,
                    wind_dir TEXT,
                    pressure TEXT,
                    visibility TEXT,
                    aqi REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 为city和timestamp添加索引，提高查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_city ON weather_cache (city)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_timestamp ON weather_cache (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_city_timestamp ON weather_cache (city, timestamp)')
            
            # 创建热门城市表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS popular_cities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL UNIQUE
                )
            ''')
            
            # 创建历史天气表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historical_weather (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    temperature TEXT,
                    humidity TEXT,
                    weather TEXT,
                    wind TEXT,
                    wind_dir TEXT,
                    pressure TEXT,
                    visibility TEXT,
                    aqi REAL,
                    record_date DATE NOT NULL,
                    record_hour INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(city, record_date, record_hour)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # 初始化热门城市数据
            self.init_popular_cities()
            
        except sqlite3.Error as e:
            print(f"创建表失败: {e}")
            if conn:
                conn.close()
    
    def init_popular_cities(self):
        """初始化热门城市数据"""
        popular_cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安', '重庆', '南京']
        
        conn = self.connect()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            for city in popular_cities:
                cursor.execute('INSERT OR IGNORE INTO popular_cities (city) VALUES (?)', (city,))
            
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"初始化热门城市失败: {e}")
            if conn:
                conn.close()
    
    def get_cached_weather(self, city):
        """获取缓存的天气数据，有效期1小时"""
        conn = self.connect()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            
            # 查询1小时内的缓存数据，明确指定字段顺序
            cursor.execute('''
                SELECT city, temperature, humidity, weather, wind, wind_dir, pressure, visibility, aqi, timestamp 
                FROM weather_cache 
                WHERE city = ? AND timestamp >= datetime('now', '-1 hours')
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (city,))
            
            row = cursor.fetchone()
            if row:
                result = {
                    'city': row[0],
                    'temperature': row[1],
                    'humidity': row[2],
                    'weather': row[3],
                    'wind': row[4],
                    'wind_dir': row[5],
                    'pressure': row[6],
                    'visibility': row[7],
                    'aqi': row[8],
                    'timestamp': row[9]
                }
            else:
                result = None
            
            conn.close()
            return result
        except sqlite3.Error as e:
            print(f"获取缓存数据失败: {e}")
            if conn:
                conn.close()
            return None
    
    def save_weather(self, weather_data):
        """保存天气数据到缓存"""
        conn = self.connect()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO weather_cache (city, temperature, humidity, weather, wind, wind_dir, pressure, visibility, aqi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                weather_data['city'],
                weather_data['temperature'],
                weather_data['humidity'],
                weather_data['weather'],
                weather_data['wind'],
                weather_data['wind_dir'],
                weather_data['pressure'],
                weather_data['visibility'],
                weather_data.get('aqi', 0)
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"保存天气数据失败: {e}")
            if conn:
                conn.close()
            return False
    
    def get_popular_cities(self):
        """获取热门城市列表"""
        conn = self.connect()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT city FROM popular_cities ORDER BY id')
            result = [row[0] for row in cursor.fetchall()]
            conn.close()
            return result
        except sqlite3.Error as e:
            print(f"获取热门城市失败: {e}")
            if conn:
                conn.close()
            return []
    
    def save_historical_weather(self, weather_data):
        """保存天气数据到历史表（每天每小时只保存一条）"""
        conn = self.connect()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # 获取当前日期和小时
            now = datetime.datetime.now()
            record_date = now.strftime('%Y-%m-%d')
            record_hour = now.hour
            
            cursor.execute('''
                INSERT OR REPLACE INTO historical_weather 
                (city, temperature, humidity, weather, wind, wind_dir, pressure, visibility, aqi, record_date, record_hour)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                weather_data['city'],
                weather_data['temperature'],
                weather_data['humidity'],
                weather_data['weather'],
                weather_data['wind'],
                weather_data['wind_dir'],
                weather_data['pressure'],
                weather_data['visibility'],
                weather_data.get('aqi', 0),
                record_date,
                record_hour
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"保存历史天气数据失败: {e}")
            if conn:
                conn.close()
            return False
    
    def get_historical_weather(self, city, days=7):
        """获取指定城市最近几天的历史天气数据"""
        conn = self.connect()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, city, temperature, humidity, weather, wind, wind_dir, pressure, visibility, aqi, record_date, record_hour, timestamp 
                FROM historical_weather 
                WHERE city = ? AND record_date >= datetime('now', '-' || ? || ' days')
                ORDER BY record_date DESC, record_hour DESC
            ''', (city, days))
            
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append({
                    'city': row[1],
                    'temperature': row[2],
                    'humidity': row[3],
                    'weather': row[4],
                    'wind': row[5],
                    'wind_dir': row[6],
                    'pressure': row[7],
                    'visibility': row[8],
                    'aqi': row[9],
                    'record_date': row[10],
                    'record_hour': row[11],
                    'timestamp': row[12]
                })
            
            conn.close()
            return result
        except sqlite3.Error as e:
            print(f"获取历史天气数据失败: {e}")
            if conn:
                conn.close()
            return []
    
    def get_historical_weather_by_date(self, city, date):
        """根据指定城市和日期获取历史天气数据"""
        conn = self.connect()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, city, temperature, humidity, weather, wind, wind_dir, pressure, visibility, aqi, record_date, record_hour, timestamp 
                FROM historical_weather 
                WHERE city = ? AND record_date = ?
                ORDER BY record_hour ASC
            ''', (city, date))
            
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append({
                    'city': row[1],
                    'temperature': row[2],
                    'humidity': row[3],
                    'weather': row[4],
                    'wind': row[5],
                    'wind_dir': row[6],
                    'pressure': row[7],
                    'visibility': row[8],
                    'aqi': row[9],
                    'record_date': row[10],
                    'record_hour': row[11],
                    'timestamp': row[12]
                })
            
            conn.close()
            return result
        except sqlite3.Error as e:
            print(f"获取指定日期历史天气失败: {e}")
            if conn:
                conn.close()
            return []
    
    def close(self):
        """关闭数据库连接"""
        # 由于我们在每个方法中都创建并关闭自己的连接，所以这个方法不再需要做任何事情
        pass
