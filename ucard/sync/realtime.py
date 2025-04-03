from comm.db_api import insert_database, update_database, batch_update_database,query_database,query_field_from_table
from comm.flat_data import flat_data
from comm.gsalay_api import GSalaryAPI

gsalary = GSalaryAPI()

def realtime_card_info_update(version, card_id):
    try:
        # 查询卡信息
        data = []
        result = gsalary.query_cards_info(version, card_id)
        flatten_data = flat_data(version, result, 'data')
        data.append(flatten_data)
        batch_update_database('cards_info', data, condition1='card_id')     
    except Exception as e:
        print(f"更新卡信息时出错: {e}")

def modify_response_data_insert(version, data):
    try:
        flatten_data = flat_data(version, data, 'data')
        insert_database('balancemodify_respdata',flatten_data)
    except Exception as e:
        print(f"卡片调额回复数据插入数据库出错: {e}")

if __name__ == '__main__':
    realtime_card_info_update(version='J1', card_id='2025011911400101632500617552')
