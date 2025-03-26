# 用于格式化入库数据

from datetime import datetime
from comm.utils import flatten_dict

def flat_data(version,json_data, p1=None, p2=None):

    if p1 is not None and p2 is not None:
        # 如果传入了 p1 和 p2，使用它们提取数据列表
        data_list = json_data[f'{p1}'][f'{p2}']
    elif p1 is not None and p2 is None:
        # 如果传入了 p1
        data = json_data[f'{p1}']
        flat_data = flatten_dict(data)
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S%f")
        flat_data['insert_time'] = formatted_time
        flat_data['version'] = version

        return flat_data

    else:
        # 如果没有传入 p1 和 p2
        raise ValueError("必须传入 p1 参数，用于指定从 JSON 数据中提取数据列表的键。")

    flattened_records = []
    for data in data_list:
        flat_data = flatten_dict(data)
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S%f")
        flat_data['insert_time'] = formatted_time
        flat_data['version'] = version
        flattened_records.append(flat_data)

    return flattened_records

# 用于格式化电报消息
def flat_messages(data, region):
    messages = {
        "CN": {
            "title": "📌 交易通知",
            "transaction_id": "🆔交易编号",
            "origin_transaction_id": "原始交易编号",
            "card_number": "💳卡号",
            "transaction_time": "🕒交易时间",
            "confirm_time": "⌚确认时间",
            "transaction_amount": "💰交易金额",
            "accounting_amount": "💵入账金额",
            "surcharge_amount": "💸手续费",
            "biz_type": "📝交易类型",
            "status": "交易状态",
            "merchant_name": "🏢商户名称",
            "merchant_region": "🌍商户地区",
        },
        "JP": {
            "title": "📌 取引通知",
            "transaction_id": "🆔取引番号",
            "origin_transaction_id": "元の取引番号",
            "card_number": "💳カード番号",
            "transaction_time": "🕒取引時間",
            "confirm_time": "⌚確認時間",
            "transaction_amount": "💰取引金額",
            "accounting_amount": "💵記帳金額",
            "surcharge_amount": "💸追加料金",
            "biz_type": "📝取引種類",
            "status": "取引状況",
            "merchant_name": "🏢加盟店名",
            "merchant_region": "🌍加盟店地域",
        },
        "US": {
            "title": "📌 Transaction Notification",
            "transaction_id": "🆔Transaction ID",
            "origin_transaction_id": "Original Transaction ID",
            "card_number": "💳Card Number",
            "transaction_time": "🕒Transaction Time",
            "confirm_time": "⌚Confirmation Time",
            "transaction_amount": "💰Transaction Amount",
            "accounting_amount": "💵Accounting Amount",
            "surcharge_amount": "💸Surcharge Amount",
            "biz_type": "📝Transaction Type",
            "status": "Status",
            "merchant_name": "🏢Merchant Name",
            "merchant_region": "🌍Merchant Region",
        },
    }
    lang = messages.get(region, messages["US"])

    formatted_messages = []

    for tx in data:

        formatted_tx = {
            lang["title"]:'',
            lang["transaction_id"]: tx["transaction_id"],
            lang["card_number"]: tx["mask_card_number"],
            lang["transaction_time"]: tx["transaction_time"],
            lang["confirm_time"]: tx["confirm_time"],
            lang["transaction_amount"]: f"{tx['transaction_amount']} {tx['transaction_amount_currency']}",
            lang["accounting_amount"]: f"{tx['accounting_amount']} {tx['accounting_amount_currency']}",
            lang["surcharge_amount"]: f"{tx['surcharge_amount']} {tx['surcharge_currency']}",
            lang["biz_type"]: tx["biz_type"],
            lang["status"]: tx["status"],
        }
        if tx.get("origin_transaction_id"):
            formatted_tx[lang["origin_transaction_id"]] = tx["origin_transaction_id"]
        if tx.get("merchant_name"):
            formatted_tx[lang["merchant_name"]] = tx["merchant_name"]
        if tx.get("merchant_region"):
            formatted_tx[lang["merchant_region"]] = tx["merchant_region"]
        formatted_messages.append(formatted_tx)

    return formatted_messages