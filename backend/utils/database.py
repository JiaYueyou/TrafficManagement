import pymysql
from dbutils.pooled_db import PooledDB
from config import config

# 创建数据库连接池
def create_connection_pool(config_name='default'):
    """
    创建数据库连接池
    :param config_name: 配置名称
    :return: 数据库连接池
    """
    cfg = config[config_name]

    pool = PooledDB(
        creator=pymysql,  # 使用PyMySQL创建连接
        maxconnections=cfg.MYSQL_POOL_SIZE,  # 连接池大小
        mincached=2,  # 初始化时，链接池中至少创建的空闲链接
        maxcached=5,  # 链接池中最多闲置的链接
        maxshared=3,  # 链接池中最多共享的链接数量
        blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待
        maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
        setsession=[],  # 开始会话前执行的命令列表
        host=cfg.MYSQL_HOST,
        port=cfg.MYSQL_PORT,
        user=cfg.MYSQL_USER,
        password=cfg.MYSQL_PASSWORD,
        database=cfg.MYSQL_DB,
        charset=cfg.MYSQL_CHARSET,
        cursorclass=pymysql.cursors.Cursor  # 返回字典格式的查询结果
    )

    return pool

# 获取数据库连接
def get_connection(config_name='default'):
    """
    获取数据库连接
    :param config_name: 配置名称
    :return: 数据库连接
    """
    pool = create_connection_pool(config_name)
    conn = pool.connection()
    return conn

# 执行查询
def execute_query(sql, params=None, config_name='default'):
    """
    执行查询语句
    :param sql: SQL语句
    :param params: 参数
    :param config_name: 配置名称
    :return: 查询结果
    """
    conn = None
    cursor = None
    try:
        conn = get_connection(config_name)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        return result
    except Exception as e:
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 执行增删改
def execute_update(sql, params=None, config_name='default'):
    """
    执行增删改语句
    :param sql: SQL语句
    :param params: 参数
    :param config_name: 配置名称
    :return: 受影响的行数
    """
    conn = None
    cursor = None
    try:
        conn = get_connection(config_name)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()