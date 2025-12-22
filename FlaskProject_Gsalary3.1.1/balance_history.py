import json
from datetime import datetime
from comm.db_api import query_database
from comm.foramt_data import format_balance_history
from comm.paginate import paginate_data


# 交易数据处理
def query_balance_history(card_id_list,limit,page):

    query = {
        'page': f'{page}',
        'limit': f'{limit}',
        'card_id':f'{card_id_list}'
    }

    balance_condition = {'card_id': card_id_list}

    # 获取交易数据
    balance_history_data = query_database('balance_history',balance_condition)

    # 格式化交易数据
    formatted_balance_history = format_balance_history(balance_history_data)

    # 倒序排列
    sorted_balance_history = sorted(formatted_balance_history, key=lambda x: datetime.fromisoformat(x['transaction_time'].replace('Z', '+00:00')),reverse=True)

    # 获取数据
    balance_history,total_count,total_page,code,message = paginate_data(sorted_balance_history, limit, page)

    # 判断查询结果
    if balance_history is not None:

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
                         'history':balance_history,
                         'page': page,
                         'limit': limit,
                         'total_count': total_count,
                         'total_page': total_page,
                        }
                 }

    return json.dumps(data_dict, sort_keys=False)

