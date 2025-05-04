from comm.db_api import insert_database, update_database, batch_update_database,query_database,query_field_from_table
from comm.flat_data import flat_data
from comm.gsalay_api import GSalaryAPI
import json
import time
import asyncio

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

def realtime_update_payers(version, payer_id, data):
    gsalary = GSalaryAPI()
    time.sleep(5)
    try:
        payers_data = gsalary.get_payers(system_id=version)
        if payers_data['result']['result'] == 'S':
            payers_flatten_data = flat_data(version, payers_data, 'data', 'payers')
            batch_update_database('payers', payers_flatten_data, condition1='payer_id')
            data_dict = []
            if data:
                payers_info_flatten_data = flat_data(version, data, 'data')
                data_dict.append(payers_info_flatten_data)
                batch_update_database('payers_info', data_dict, condition1='payer_id')
            else:
                print(f"更新payers_info表中{payer_id}时出错: 数据为空")
        else:
            print(f"更新payers表时出错: {payers_data['result']['message']}")
    except Exception as e:
        print(f"更新付款人信息时出错: {e}")

'''
    --------------------------------------------------收款人--------------------------------------------------
'''
def rt_get_payees(version):
    gsalary = GSalaryAPI()
    result = gsalary.get_payees(system_id=version)
    flatten_data = flat_data(version, result, 'data', 'payees')
    # 插入数据库
    insert_database('payees', flatten_data)

# 更新收款人列表
def rt_update_payees(version):
    gsalary = GSalaryAPI()
    result = gsalary.get_payees(system_id=version)
    flatten_data = flat_data(version, result, 'data', 'payees')
    print(flatten_data)
    # 插入数据库
    batch_update_database('payees', flatten_data, 'payee_id') 

# 查看收款人可用收款账户
def rt_get_payee_accounts(version):
    gsalary = GSalaryAPI()
    payees_id_data = query_field_from_table('payees', 'payee_id', f"version='{version}'")
    data = []
    for payee_id in payees_id_data:
        result = gsalary.get_payee_accounts(system_id = version, payee_id = payee_id)
        flatten_data = flat_data(version, result, 'data', 'accounts')
        # print(flatten_data)
        if flatten_data:
            account_data = flatten_data[0]
        else:
            continue
        # currencies_list = account_data.get("currencies", [])
        # account_data["currencies"] = currencies_list[0]
        account_data['payee_id'] = payee_id
        if 'form_fields' in account_data:
            # 提取并删除form_fields字段
            form_fields = account_data.pop('form_fields')
            # 将form字段提升到顶层
            for field in form_fields:
                account_data[field['key']] = field['value']
        # print(account_data)
        data.append(account_data)
    # print(data)
    # 插入数据库
    insert_database('payees_account', data)

def rt_update_payee_accounts(version):
    gsalary = GSalaryAPI()
    payees_id_data = query_field_from_table('payees', 'payee_id', f"version='{version}'")
    data = []
    for payee_id in payees_id_data:
        result = gsalary.get_payee_accounts(system_id = version, payee_id = payee_id)
        flatten_data = flat_data(version, result, 'data', 'accounts')
        # print(flatten_data)
        if flatten_data:
            account_data = flatten_data[0]
        else:
            continue
        account_data['payee_id'] = payee_id
        if 'form_fields' in account_data:
            # 提取并删除form_fields字段
            form_fields = account_data.pop('form_fields')
            # 将form字段提升到顶层
            for field in form_fields:
                account_data[field['key']] = field['value']
        # print(account_data)
        data.append(account_data)
    batch_update_database('payees_account', data, 'account_id')
        
# 查询可用付款方式
def rt_get_available_payment_methods(version):
    gsalary = GSalaryAPI()
    result = gsalary.get_available_payment_methods(system_id=version)
    flatten_data = flat_data(version, result, 'data', 'payment_methods')
    # 插入数据库
    insert_database('payees_availpay_methods', flatten_data)

# 更新可用付款方式
def rt_update_available_payment_methods(version):
    gsalary = GSalaryAPI()
    result = gsalary.get_available_payment_methods(system_id=version)
    flatten_data = flat_data(version, result, 'data', 'payment_methods')
    # 插入数据库
    batch_update_database('payees_availpay_methods', flatten_data, 'payment_method_id', 'version')

def rt_insert_supported_regions_currencies(version):
    gsalary = GSalaryAPI()
    data = ['BANK_TRANSFER', 'PAYPAL_USD']
    for item in data:
        result = gsalary.supported_regions_currencies(system_id=version, data=item)
        flatten_data = flat_data(version, result, 'data', 'countries')
        for i in flatten_data:
            i['currencies'] = json.dumps(i['currencies'])
            i['payment_method'] = item
        print(flatten_data)
        # 插入数据库
        insert_database('payees_sup_reg_cur', flatten_data)

def rt_update_supported_regions_currencies(version):
    gsalary = GSalaryAPI()
    data = ['BANK_TRANSFER', 'PAYPAL_USD']
    for item in data:
        result = gsalary.supported_regions_currencies(system_id=version, data=item)
        flatten_data = flat_data(version, result, 'data', 'countries')
        for i in flatten_data:
            i['currencies'] = json.dumps(i['currencies'])
            i['payment_method'] = item
        # print(flatten_data)
        # 插入数据库
        batch_update_database('payees_sup_reg_cur', flatten_data, 'country','payment_method','version')

'''
    --------------------------------------------------付款人--------------------------------------------------
'''
def rt_get_payers(version):
    gsalary = GSalaryAPI()
    result = gsalary.get_payers(system_id=version)
    flatten_data = flat_data(version, result, 'data', 'payers')
    print(flatten_data)
    for i in flatten_data:
        if 'business_scopes' in i:
            business_scopes_list = i.get("business_scopes", [])
            i["business_scopes"] = json.dumps(business_scopes_list)
    # 插入数据库
    insert_database('payers', flatten_data)

def rt_update_payers(version):
    gsalary = GSalaryAPI()
    result = gsalary.get_payers(system_id=version)
    flatten_data = flat_data(version, result, 'data', 'payers')
    print(flatten_data)
    for i in flatten_data:
        if 'business_scopes' in i:  
            business_scopes_list = i.get("business_scopes", [])
            i["business_scopes"] = json.dumps(business_scopes_list)
    batch_update_database('payers', flatten_data, 'payer_id')

# 查询付款人详情
def rt_get_payers_info(version):
    gsalary = GSalaryAPI()
    payers_id_data = query_field_from_table('payers', 'payer_id', f"version='{version}'")
    data = []
    for payer_id in payers_id_data:
        result = gsalary.get_payers_info(system_id=version, payer_id=payer_id)
        flatten_data = flat_data(version, result, 'data')
        if 'business_scopes' in flatten_data:
            business_scopes_list = flatten_data.get("business_scopes", [])
            flatten_data["business_scopes"] = json.dumps(business_scopes_list)
        data.append(flatten_data)
    # 插入数据库    
    insert_database('payers_info', data)

def rt_update_payers_info(version):
    gsalary = GSalaryAPI()
    payers_id_data = query_field_from_table('payers', 'payer_id', f"version='{version}'")
    data = []
    for payer_id in payers_id_data:
        result = gsalary.get_payers_info(system_id=version, payer_id=payer_id)
        flatten_data = flat_data(version, result, 'data')
        if 'business_scopes' in flatten_data:
            business_scopes_list = flatten_data.get("business_scopes", [])
            flatten_data["business_scopes"] = json.dumps(business_scopes_list)
        data.append(flatten_data)
    # 插入数据库    
    batch_update_database('payers_info', data, 'payer_id')

'''
    --------------------------------------------------付款单--------------------------------------------------
'''
def rt_get_remittance_orders(version):
    gsalary = GSalaryAPI()
    result = gsalary.get_remittance_orders(version)
    flatten_result = flat_data(version, result,'data','orders')
    print(flatten_result)
    insert_database('remittance_orders', flatten_result)

def rt_update_remittance_orders(version):
    gsalary = GSalaryAPI()
    result = gsalary.get_remittance_orders(version)
    flatten_result = flat_data(version, result,'data','orders')
    print(flatten_result)
    batch_update_database('remittance_orders', flatten_result, 'order_id')



if __name__ == '__main__':
    # realtime_card_info_update(version='J1', card_id='2025011911400101632500617552')
    pass