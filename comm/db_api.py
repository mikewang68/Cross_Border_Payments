import pymysql
import logging
from comm.utils import get_db

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("error.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


def create_db_connection():
    try:
        # 获取数据库配置信息
        db = get_db()
        if db is None:
            logger.error("无法获取有效的数据库配置信息，连接失败。")
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
        logger.error(f"数据库连接错误: {e}")
        return None

# ----------------------------------------------------insert-----------------------------------------------------------

def insert_database(table_name, records):
    conn = create_db_connection()
    if conn is None:
        logger.error("无法建立数据库连接，程序退出。")
        return

    cursor = conn.cursor()

    # 获取表的实际字段列表
    try:
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns_in_table = [column[0] for column in cursor.fetchall()]
    except pymysql.Error as err:
        logger.error(f"获取表结构信息时发生错误，错误信息: {err}")
        conn.close()
        return

    for record in records:
        # 过滤掉表中不存在的字段
        valid_record = {key: value for key, value in record.items() if key in columns_in_table}
        columns = ', '.join(valid_record.keys())
        values = ', '.join(['%s'] * len(valid_record))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        val = tuple(valid_record.values())
        try:
            cursor.execute(sql, val)
            logger.info(f"成功插入记录: {valid_record.get('insert_time')}")
        except pymysql.Error as err:
            if err.args[0] == 1062:  # 检查是否为主键冲突错误
                logger.info(f"检测到重复数据: {valid_record.get('insert_time')}，错误信息: {err}")
            else:
                logger.info(f"插入数据时发生错误，错误信息: {err}")
                conn.rollback()
                return

    conn.commit()
    cursor.close()
    conn.close()


# ---------------------------------------------update------------------------------------------------------------------


def update_database(table_name, set_columns_values, where_conditions):
    conn = create_db_connection()
    if conn is None:
        logger.error("无法建立数据库连接，程序退出。")
        return False

    cursor = conn.cursor()
    try:
        # 构建 SET 子句
        set_clauses = []
        values = []
        for column, value in set_columns_values.items():
            set_clauses.append(f"{column} = %s")
            values.append(value)
        set_str = ", ".join(set_clauses)

        # 构建 WHERE 子句和参数列表
        where_clause = []
        for column, value in where_conditions.items():
            where_clause.append(f"{column} = %s")
            values.append(value)

        where_str = " AND ".join(where_clause)

        # 构建完整的 SQL 更新语句
        sql = f"UPDATE {table_name} SET {set_str} WHERE {where_str}"
        cursor.execute(sql, values)
        conn.commit()
        logger.info(f"成功更新 {cursor.rowcount} 条记录。")
        return True
    except pymysql.Error as err:
        logger.error(f"更新数据时出现错误: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


# 对于单个表中的所有记录进行更新/暂时操作
# table_name: 表名，set_columns_values: 数据，condition1: 条件字段名1，condition2: 条件字段名2(如果表中含有两个主键，可添加condition2)
def batch_update_database(table_name, set_columns_values, condition1=None, condition2=None):
    conn = create_db_connection()
    if conn is None:
        logger.error("无法建立数据库连接，程序退出。")
        return False
    cursor = conn.cursor()
    try:
        for i in set_columns_values:

            if condition1 is not None and condition2 is None:
                conditiondata1 = i.pop(condition1)
            else:
                conditiondata1 = i.pop(condition1)
                conditiondata2 = i.pop(condition2)
            # 构建set子句
            set_clauses = []
            values = []
            for col, val in i.items():
                set_clauses.append(f"{col} = %s")
                values.append(val)
            set_str = ", ".join(set_clauses)
            # 构建where子句
            where_clause = []
            if condition2 is None:
                where_clause.append(f"{condition1} = %s")
                values.append(conditiondata1)
                where_str = ''.join(where_clause)
            else:
                where_clause.append(f"{condition1} = %s")
                where_clause.append(f"{condition2} = %s")
                values.append(conditiondata1)
                values.append(conditiondata2)
                where_str = ' AND '.join(where_clause)

            sql = f"UPDATE {table_name} SET {set_str} WHERE {where_str}"
            cursor.execute(sql, values)
            conn.commit()
        return True
    except pymysql.Error as err:
        logger.error(f"更新数据时出现错误: {err}")
        return False
    finally:
        cursor.close()
        conn.close()


# ------------------------------------------query---------------------------------------------------------------------


def query_database(table_name, column_name, query_value):
    conn = create_db_connection()
    if conn is None:
        logger.error("无法建立数据库连接，程序退出。")
        return []

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 构建 SQL 查询语句
        sql = f"SELECT * FROM {table_name} WHERE {column_name} = %s"
        cursor.execute(sql, (query_value,))
        results = cursor.fetchall()
        return results
    except pymysql.Error as err:
        logger.error(f"查询数据时出现错误: {err}")
        return []
    finally:
        cursor.close()
        conn.close()


def query_field_from_table(table_name, field_name, condition=None):
    conn = create_db_connection()
    if conn is None:
        logger.error("无法建立数据库连接，程序退出。")
        return []

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 构建查询 SQL 语句
        sql = f"SELECT {field_name} FROM {table_name}"
        if condition:
            sql += f" WHERE {condition}"
        cursor.execute(sql)
        results = cursor.fetchall()
        # 提取指定字段的值
        field_values = [row[field_name] for row in results]
        return field_values
    except pymysql.Error as err:
        logger.error(f"查询数据时出现错误: {err}")
        return []
    except KeyError:
        logger.error(f"未找到指定的字段: {field_name}")
        return []
    finally:
        cursor.close()
        conn.close()


def query_all_from_table(table_name):
    conn = create_db_connection()
    if conn is None:
        logger.error("无法建立数据库连接，程序退出。")
        return []

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 构建全量查询的 SQL 语句
        sql = f"SELECT * FROM {table_name}"
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except pymysql.Error as err:
        logger.error(f"查询数据时出现错误: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def query_match_from_table(table_name, column_name,column_value,m):
    conn = create_db_connection()
    if conn is None:
        logger.error("无法建立数据库连接，程序退出。")
        return []

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        sql =f'SELECT * FROM {table_name} WHERE {column_name} {m} %s ORDER BY {column_name}'

        cursor.execute(sql, (column_value,))
        results = cursor.fetchall()
        return results
    except pymysql.Error as err:
        logger.error(f"查询数据时出现错误: {err}")
        return []
    finally:
        cursor.close()
        conn.close()