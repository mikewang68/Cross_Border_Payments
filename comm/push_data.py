import logging
from db_api import update_database, query_all_from_table, query_database, query_match_from_table

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("error.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# 获取网络最新数据
def get_last_insert_time(fun):

    try:
        fun_data = query_all_from_table(fun)

        if fun_data:
            data = sorted(fun_data, key=lambda x: x["insert_time"], reverse=True)[0]
            last_insert_time = data.get('insert_time')

            return last_insert_time
        else:
            last_insert_time = None

            return last_insert_time

    except Exception as e:
        logger.error(f"查询{fun}insert_time时出错: {e}")

# 获取记录最新数据
def get_db_last_insert_time(fun):

    try:
        db_data = query_database('push_ctrl', 'function', fun)

        if db_data:
            for data in db_data:
                db_last_insert_time = data.get('last_insert_time')
                return db_last_insert_time
        else:
            db_last_insert_time = None
            return db_last_insert_time

    except Exception as e:
        logger.error(f"查询{fun}db_insert_time时出错: {e}")


# 更新最新数据
def upd_last_insert_time(fun,last_insert_time):

    if last_insert_time:

        set_data = {
            'last_insert_time': f'{last_insert_time}',
        }
        where_data = {
            'function': f'{fun}'
        }

        try:
            update_database('push_ctrl', set_data, where_data)
        except Exception as e:
            logger.error(f"更新{fun}last_insert_time时出错: {e}")


# 对比当前数据
def match_last_insert_time(last_insert_time,db_last_insert_time):
    state = False

    if last_insert_time <= db_last_insert_time:
        return state
    else:
        state = True
        return state

# 获取新插入数据
def get_new_ins_data(table_name,column_name,column_value,m):
    try:
        all_data = query_match_from_table(table_name, column_name,column_value,m)

        return all_data

    except Exception as e:
        logger.error(f"获取新插入数据时出错: {e}")


