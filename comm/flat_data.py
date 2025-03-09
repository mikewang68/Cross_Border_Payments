# 用于格式化入库数据

from datetime import datetime
from utils import flatten_dict

def flat_data(json_data, p1=None, p2=None):

    if p1 is not None and p2 is not None:
        # 如果传入了 p1 和 p2，使用它们提取数据列表
        data_list = json_data[f'{p1}'][f'{p2}']

    elif p1 is not None and p2 is None:
        # 如果传入了 p1
        data_list = json_data[f'{p1}']

    else:
        # 如果没有传入 p1 和 p2
        raise ValueError("必须传入 p1 参数，用于指定从 JSON 数据中提取数据列表的键。")

    flattened_records = []
    for data in data_list:
        print(data)
        flat_data = flatten_dict(data)
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S%f")
        flat_data['insert_time'] = formatted_time
        flattened_records.append(flat_data)

    return flattened_records