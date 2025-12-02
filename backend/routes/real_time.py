from flask import Blueprint, request, jsonify
from utils.database import get_connection
from datetime import datetime, timedelta
import pymysql

real_time_bp = Blueprint("real_time", __name__)

@real_time_bp.route('/api/real-time/traffic', methods=['GET'])
def get_real_time_traffic():
    """获取实时交通数据"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

        # 获取查询参数
        limit = request.args.get('limit', 50, type=int)
        congestion_level = request.args.get('congestion_level')

        # 构建 SQL 查询
        sql = """
            SELECT td.*, l.name, l.latitude, l.longitude, l.district, l.road_type
            FROM traffic_data td
            JOIN locations l ON td.location_id = l.id
            WHERE td.data_time >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """
        params = []

        if congestion_level:
            sql += " AND td.congestion_level = %s"
            params.append(congestion_level)

        sql += " ORDER BY td.data_time DESC LIMIT %s"
        params.append(limit)

        cursor.execute(sql, params)
        traffic_data = cursor.fetchall()

        conn.close()

        return jsonify({
            'status': 'success',
            'data': traffic_data,
            'count': len(traffic_data),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"获取实时数据失败: {str(e)}"
        }), 500
    
@real_time_bp.route('/api/real-time/congestion', methods=['GET'])
def get_congestion_areas():
    """获取拥堵区域"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        
        # 获取当前拥堵的地点
        cursor.execute("""
            SELECT l.id, l.name, l.latitude, l.longitude, l.district,
                   td.vehicle_count, td.avg_speed, td.congestion_level, td.data_time
            FROM locations l
            JOIN traffic_data td ON l.id = td.location_id
            WHERE td.congestion_level = 'high'
            AND td.data_time >= DATE_SUB(NOW(), INTERVAL 30 MINUTE)
            ORDER BY td.data_time DESC
        """)
        
        congestion_areas = cursor.fetchall()
        
        # 按区域统计拥堵情况
        cursor.execute("""
            SELECT l.district, COUNT(*) as congestion_count
            FROM locations l
            JOIN traffic_data td ON l.id = td.location_id
            WHERE td.congestion_level = 'high'
            AND td.data_time >= DATE_SUB(NOW(), INTERVAL 30 MINUTE)
            GROUP BY l.district
            ORDER BY congestion_count DESC
        """)
        
        district_stats = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'congestion_areas': congestion_areas,
                'district_stats': district_stats
            },
            'count': len(congestion_areas),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"获取拥堵数据失败: {str(e)}"
        }), 500