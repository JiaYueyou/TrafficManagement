class Config:
    # 数据库配置
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'root'
    MYSQL_DB = 'city_traffic'
    MYSQL_CHARSET = 'utf8mb4'

    # 连接池配置
    MYSQL_POOL_SIZE = 5
    MYSQL_POOL_RECYCLE = 3600
    MYSQL_POOL_MAX_OVERFLOW = 5

    DEBUG = True

    # 跨域配置
    CORS_ORIGINS = [
        'http://localhost:8080', 
        'http://127.0.0.1:8080'
    ]

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}