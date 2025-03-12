import pymysql
import logging
from comm.utils import get_db

logging.basicConfig(
    filename='db.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_db_connection():
    try:
        # 获取数据库配置信息
        db = get_db()
        if db is None:
            logging.error("无法获取有效的数据库配置信息，连接失败。")
            return None
        conn = pymysql.connect(
            user=db.get('user'),
            password=db.get('password'),
            host=db.get('host'),
            port=db.get('port'),
            database=db.get('database')
        )
        return conn
    except pymysql.Error as e:
        logging.error(f"数据库连接错误: {e}")
        return None

def insert_database(table_name, records):
    conn = create_db_connection()
    if conn is None:
        logging.error("无法建立数据库连接，程序退出。")
        return

    cursor = conn.cursor()
    for record in records:
        columns = ', '.join(record.keys())
        values = ', '.join(['%s'] * len(record))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        val = tuple(record.values())
        try:
            cursor.execute(sql, val)
            logging.info(f"成功插入记录: {record.get('insert_time')}")
        except pymysql.Error as err:
            if err.args[0] == 1062:  # 检查是否为主键冲突错误
                logging.info(f"检测到重复数据: {record.get('insert_time')}，错误信息: {err}")
            else:
                logging.info(f"插入数据时发生错误，错误信息: {err}")
                conn.rollback()
                return

    conn.commit()
    cursor.close()
    conn.close()

def update_database(table_name, set_column, set_value, where_column, where_value):
    conn = create_db_connection()
    if conn is None:
        logging.error("无法建立数据库连接，程序退出。")
        return

    cursor = conn.cursor()
    try:
        # 构建 SQL 更新语句
        sql = f"UPDATE {table_name} SET {set_column} = %s WHERE {where_column} = %s"
        cursor.execute(sql, (set_value, where_value))
        conn.commit()
        logging.info(f"成功更新 {cursor.rowcount} 条记录。")
    except pymysql.Error as err:
        logging.error(f"更新数据时出现错误: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def query_database(table_name, column_name, query_value):
    conn = create_db_connection()
    if conn is None:
        logging.error("无法建立数据库连接，程序退出。")
        return []

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 构建 SQL 查询语句
        sql = f"SELECT * FROM {table_name} WHERE {column_name} = %s"
        cursor.execute(sql, (query_value,))
        results = cursor.fetchall()
        return results
    except pymysql.Error as err:
        logging.error(f"查询数据时出现错误: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def query_all_from_table(table_name):
    conn = create_db_connection()
    if conn is None:
        logging.error("无法建立数据库连接，程序退出。")
        return []

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 构建全量查询的 SQL 语句
        sql = f"SELECT * FROM {table_name}"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except pymysql.Error as err:
        logging.error(f"查询数据时出现错误: {err}")
        return []
    finally:
        cursor.close()
        conn.close()