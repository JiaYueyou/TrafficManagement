# routes/statistics.py
from flask import Blueprint, jsonify, request
from utils.database import get_connection
from datetime import datetime, timedelta
import json
import pymysql

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/api/statistics/traffic', methods=['GET'])
def get_traffic_statistics():
    """获取交通统计数据"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        
        # 获取查询参数
        location_id = request.args.get('location_id', type=int)
        days = request.args.get('days', 7, type=int)
        stat_type = request.args.get('type', 'daily')  # daily, hourly
        
        # 构建SQL查询
        if stat_type == 'daily':
            # 按天统计
            sql = """
                SELECT l.name as location_name, ts.stat_date,
                       AVG(ts.avg_vehicle_count) as daily_avg_count,
                       MAX(ts.max_vehicle_count) as daily_max_count,
                       AVG(ts.avg_speed) as daily_avg_speed
                FROM traffic_statistics ts
                JOIN locations l ON ts.location_id = l.id
                WHERE ts.stat_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            """
            params = [days]
            
            if location_id:
                sql += " AND ts.location_id = %s"
                params.append(location_id)
            
            sql += """
                GROUP BY l.id, l.name, ts.stat_date
                ORDER BY ts.stat_date ASC
            """
        else:
            # 按小时统计
            sql = """
                SELECT l.name as location_name, ts.stat_hour,
                       AVG(ts.avg_vehicle_count) as hourly_avg_count,
                       MAX(ts.max_vehicle_count) as hourly_max_count,
                       AVG(ts.avg_speed) as hourly_avg_speed
                FROM traffic_statistics ts
                JOIN locations l ON ts.location_id = l.id
                WHERE ts.stat_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            """
            params = [days]
            
            if location_id:
                sql += " AND ts.location_id = %s"
                params.append(location_id)
            
            sql += """
                GROUP BY l.id, l.name, ts.stat_hour
                ORDER BY ts.stat_hour ASC
            """
        
        cursor.execute(sql, params)
        statistics = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': statistics,
            'count': len(statistics),
            'type': stat_type,
            'days': days
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"获取统计数据失败: {str(e)}"
        }), 500

@statistics_bp.route('/api/statistics/peak-hours', methods=['GET'])
def get_peak_hours_analysis():
    """获取高峰时段分析"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        
        # 获取查询参数
        location_id = request.args.get('location_id', type=int)
        days = request.args.get('days', 7, type=int)
        
        # 分析早晚高峰时段
        sql = """
            SELECT l.name as location_name, ts.stat_hour,
                   AVG(ts.avg_vehicle_count) as avg_count,
                   AVG(ts.avg_speed) as avg_speed,
                   COUNT(*) as data_points
            FROM traffic_statistics ts
            JOIN locations l ON ts.location_id = l.id
            WHERE ts.stat_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            AND (ts.stat_hour BETWEEN 7 AND 9 OR ts.stat_hour BETWEEN 17 AND 19)
        """
        params = [days]
        
        if location_id:
            sql += " AND ts.location_id = %s"
            params.append(location_id)
        
        sql += """
            GROUP BY l.id, l.name, ts.stat_hour
            ORDER BY l.name, ts.stat_hour
        """
        
        cursor.execute(sql, params)
        peak_hours_data = cursor.fetchall()
        
        # 按地点分组数据
        peak_hours_by_location = {}
        for row in peak_hours_data:
            location_name = row['location_name']
            if location_name not in peak_hours_by_location:
                peak_hours_by_location[location_name] = []
            
            peak_hours_by_location[location_name].append({
                'hour': row['stat_hour'],
                'avg_count': row['avg_count'],
                'avg_speed': row['avg_speed']
            })
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': peak_hours_by_location,
            'count': len(peak_hours_by_location),
            'days': days
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"获取高峰时段分析失败: {str(e)}"
        }), 500