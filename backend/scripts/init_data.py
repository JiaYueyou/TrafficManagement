# scripts/init_data.py
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_connection
from datetime import datetime, timedelta
import random

def insert_test_locations():
    """插入测试地点数据"""
    locations = [
        {
            'name': '信阳学院',
            'latitude': 32.117346,
            'longitude': 114.089052,
            'address': '信阳市金牛山街道',
            'district': '浉河区',
            'road_type': '新七大道'
        },
        {
            'name': '信阳火车站',
            'latitude': 32.128743,
            'longitude': 114.082303,
            'address': '信阳站',
            'district': '信阳市平桥区',
            'road_type': '新华东路'
        },
        {
            'name': '信阳农林学院',
            'latitude': 32.162588,
            'longitude': 114.124345,
            'address': '信阳市平桥区',
            'district': '平桥区',
            'road_type': '北环路1号'
        }
    ]
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        for location in locations:
            sql = """
            INSERT INTO locations (name, latitude, longitude, address, district, road_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                location['name'], 
                location['latitude'], 
                location['longitude'],
                location['address'], 
                location['district'], 
                location['road_type']
            ))
        
        conn.commit()
        print(f"成功插入 {len(locations)} 条地点数据")
        
        # 获取插入的地点ID
        cursor.execute("SELECT id, name FROM locations")
        locations_data = cursor.fetchall()
        return locations_data
        
    except Exception as e:
        conn.rollback()
        print(f"插入地点数据失败: {e}")
        return []
    finally:
        conn.close()

def insert_test_traffic_data(locations_data):
    """插入测试交通数据"""
    if not locations_data:
        print("没有可用的地点数据")
        return
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # 为每个地点生成过去24小时的数据
        now = datetime.now()
        
        for location_id, location_name in locations_data:
            for hours_ago in range(24, 0, -1):
                data_time = now - timedelta(hours=hours_ago)
                
                # 根据时间段模拟不同的交通状况
                hour = data_time.hour
                if 7 <= hour <= 9 or 17 <= hour <= 19:  # 早晚高峰
                    vehicle_count = random.randint(80, 100)
                    avg_speed = random.uniform(15, 30)
                    congestion_level = random.choice(['medium', 'high'])
                elif 22 <= hour or hour <= 6:  # 夜间
                    vehicle_count = random.randint(5, 20)
                    avg_speed = random.uniform(50, 70)
                    congestion_level = 'low'
                else:  # 平峰
                    vehicle_count = random.randint(30, 70)
                    avg_speed = random.uniform(35, 50)
                    congestion_level = random.choice(['low', 'medium'])
                
                sql = """
                INSERT INTO traffic_data (location_id, vehicle_count, avg_speed, congestion_level, data_time)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    location_id,
                    vehicle_count,
                    avg_speed,
                    congestion_level,
                    data_time
                ))
        
        conn.commit()
        print(f"成功插入 {len(locations_data) * 24} 条交通数据")
        
    except Exception as e:
        conn.rollback()
        print(f"插入交通数据失败: {e}")
    finally:
        conn.close()

def generate_traffic_statistics(locations_data):
    """生成交通统计数据"""
    if not locations_data:
        print("没有可用的地点数据")
        return
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # 为每个地点生成过去7天的统计数据
        now = datetime.now()
        
        for location_id, location_name in locations_data:
            for days_ago in range(7, 0, -1):
                stat_date = (now - timedelta(days=days_ago)).date()
                
                # 为每天生成24小时的统计数据
                for hour in range(24):
                    # 查询该地点该日期该小时的所有交通数据
                    sql = """
                    SELECT AVG(vehicle_count) as avg_count, 
                           MAX(vehicle_count) as max_count,
                           MIN(vehicle_count) as min_count,
                           AVG(avg_speed) as avg_speed
                    FROM traffic_data
                    WHERE location_id = %s AND DATE(data_time) = %s AND HOUR(data_time) = %s
                    """
                    cursor.execute(sql, (location_id, stat_date, hour))
                    result = cursor.fetchone()
                    
                    if result and result[0] is not None:
                        avg_count, max_count, min_count, avg_speed = result
                        
                        # 确定是否为高峰时段
                        is_peak = 7 <= hour <= 9 or 17 <= hour <= 19
                        
                        sql = """
                        INSERT INTO traffic_statistics 
                        (location_id, stat_date, stat_hour, avg_vehicle_count, max_vehicle_count, 
                         min_vehicle_count, avg_speed, peak_hours)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        avg_vehicle_count = VALUES(avg_vehicle_count),
                        max_vehicle_count = VALUES(max_vehicle_count),
                        min_vehicle_count = VALUES(min_vehicle_count),
                        avg_speed = VALUES(avg_speed),
                        peak_hours = VALUES(peak_hours)
                        """
                        cursor.execute(sql, (
                            location_id,
                            stat_date,
                            hour,
                            avg_count,
                            max_count,
                            min_count,
                            avg_speed,
                            json.dumps({'is_peak': is_peak})
                        ))
            
            conn.commit()
            print(f"成功生成地点 {location_name} 的统计数据")
        
    except Exception as e:
        conn.rollback()
        print(f"生成统计数据失败: {e}")
    finally:
        conn.close()

def main():
    print("开始插入测试数据...")
    
    # 1. 插入地点数据
    locations_data = insert_test_locations()
    
    # 2. 插入交通数据
    insert_test_traffic_data(locations_data)
    
    # 3. 生成统计数据
    generate_traffic_statistics(locations_data)
    
    print("测试数据插入完成!")

if __name__ == "__main__":
    main()