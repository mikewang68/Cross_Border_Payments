from comm.db_api import insert_database, update_database, batch_update_database,query_database,query_field_from_table
from comm.flat_data import flat_data
from comm.gsalay_api import GSalaryAPI
import json

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

def modify_response_data_insert(version, result):
    try:
        data = []
        flatten_data = flat_data(version, result, 'data')
        data.append(flatten_data)
        if isinstance(flatten_data, dict):
            insert_database('modify_respdata', data)
            print('调额ResponsesData插入数据库成功')
        else:
            print(f"错误: flatten_data不是字典，无法插入数据库")
    except Exception as e:
        print(f"卡片调额回复数据插入数据库出错: {e}")

def realtime_insert_payers(version):
    gsalary = GSalaryAPI()
    result = gsalary.get_payers(system_id=version)
    flatten_data = flat_data(version, result, 'data', 'payers')
    for i in flatten_data:
        if 'business_scopes' in i:
            business_scopes_list = i.get("business_scopes", [])
            i["business_scopes"] = json.dumps(business_scopes_list)
    # 插入数据库
    insert_database('payers', flatten_data)

def realtime_insert_payers_info(version, result):
    try:
        data = []
        flatten_data = flat_data(version, result, 'data')
        if 'business_scopes' in flatten_data:
            business_scopes_list = flatten_data.get("business_scopes", [])
            flatten_data["business_scopes"] = json.dumps(business_scopes_list)
        data.append(flatten_data)
        # 插入数据库
        insert_database('payers_info', data)
    except Exception as e:
        print(f"付款人信息插入数据库出错: {e}")

if __name__ == '__main__':
    realtime_card_info_update(version='J1', card_id='2025011911400101632500617552')
