import json
from datetime import datetime
from comm.db_api import query_database
from comm.foramt_data import format_transactions
from comm.paginate import paginate_data


# 交易数据处理
def query_card_transactions(card_id_list,limit,page):

    query = {
        'page': f'{page}',
        'limit': f'{limit}',
        'card_id':f'{card_id_list}'
    }

    transaction_condition = {'card_id': card_id_list}

    # 获取交易数据
    card_transactions = query_database('card_transactions',transaction_condition)

    # 格式化交易数据
    formatted_transactions = format_transactions(card_transactions)

    # 倒序排列
    sorted_transactions = sorted(formatted_transactions, key=lambda x: datetime.fromisoformat(x['transaction_time'].replace('Z', '+00:00')),reverse=True)

    # 获取数据
    card_transaction,total_count,total_page,code,message = paginate_data(sorted_transactions, limit, page)

    # 判断查询结果
    if card_transaction is not None:

        result = {
            'result': 'S',
            'code': f'{code}',
            'message': f'{message}'
        }
    else:

        result = {
            'result': 'F',
            'code': f'{code}',
            'message': f'{message}'
        }

    # 合并字典
    data_dict = {'result':result,
                 'data':{'query':query,
                         'transactions':card_transaction,
                         'page': page,
                         'limit': limit,
                         'total_count': total_count,
                         'total_page': total_page,
                        }
                 }
    return json.dumps(data_dict, sort_keys=False)

