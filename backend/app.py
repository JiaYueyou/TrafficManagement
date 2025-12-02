from flask import Flask, jsonify
from flask_cors import CORS
from routes.map_data import map_data_bp
from routes.real_time import real_time_bp
from routes.statistics import statistics_bp
import os
from config import config

def create_app(config_name=None):
    """
    创建Flask应用
    :param config: 配置名称
    :return: Flask实例
    """
    app = Flask(__name__)

    # 加载配置
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])

    # 启用CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

    # 注册蓝图
    app.register_blueprint(map_data_bp)
    app.register_blueprint(real_time_bp)
    app.register_blueprint(statistics_bp)


    # 基础路由
    @app.route('/')
    def hello():
        return jsonify({
            'message': 'Hello from Flask backend!',
            'status': 'success'
        })

    # 测试数据库连接的路由
    @app.route('/api/test-db')
    def test_db():
        try:
            from utils.database import execute_query
            result = execute_query("SELECT 1 as test")
            return jsonify({
                'message': 'Database connection successful',
                'data': result,
                'status': 'success'
            })
        except Exception as e:
            return jsonify({
                'message': 'Database connection failed',
                'error': str(e),
                'status': 'error'
            }), 500
        
    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
