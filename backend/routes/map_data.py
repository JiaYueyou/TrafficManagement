from flask import Blueprint, jsonify, request
from utils.database import get_connection
import pymysql

map_data_bp = Blueprint('map_data', __name__)

@map_data_bp.route('/api/locations', methods=['GET'])
def get_locations():
    """获取所有监测地点位置信息"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

        # 获取查询参数
        district = request.args.get('district')
        road_type = request.args.get('road_type')

        # 构建 SQL 查询
        sql = "SELECT * FROM locations WHERE 1=1"
        params = []

        if district:
            sql += " AND district = %s"
            params.append(district)

        if road_type:
            sql += " AND road_type = %s"
            params.append(road_type)

        cursor.execute(sql, params)
        locations = cursor.fetchall()

        # 为每个地点获取最新的交通数据
        for location in locations:
            cursor.execute("""
            SELECT vehicle_count, avg_speed, congestion_level, data_time
            FROM traffic_data
            WHERE location_id = %s
            ORDER BY data_time DESC
            LIMIT 1
            """, (location['id']))

            latest_data = cursor.fetchone()
            if latest_data:
                location['latest_traffic'] = latest_data
            
        conn.close()

        return jsonify({
            'status': 'success',
            'data': location,
            'count': len(locations)
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"获取地点数据失败: {str(e)}"
        }), 500
    
@map_data_bp.route('/api/locations/<int:location_id>/traffic')
def get_location_traffic(location_id):
    """获取指定地点的实时交通数据"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

        # 获取地点数据
        cursor.execute("SELECT * FROM locations WHERE id = %s", (location_id))
        location = cursor.fetchone()

        if not location:
            return jsonify({
                'status': 'error',
                'message': f"地点不存在: {location_id}"
            }), 404
        
        # 获取最新的交通数据
        cursor.execute("""
            SELECT vehicle_count, avg_speed, congestion_level, data_time
            FROM traffic_data
            WHERE location_id = %s
            ORDER BY data_time DESC
            LIMIT 1
        """, (location_id))

        latest_data = cursor.fetchone()

        # 获取过去24小时的交通数据
        cursor.execute("""
            SELECT vehicle_count, avg_speed, congestion_level, data_time
            FROM traffic_data
            WHERE location_id = %s AND data_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY data_time ASC
        """, (location["id"]))

        daily_data = cursor.fetchall()

        conn.close()

        return jsonify({
            'status': "success",
            'data': {
                'location': location,
                'latest_traffic': latest_data,
                'daily_traffic': daily_data
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"获取地点数据失败: {str(e)}"
        }), 500