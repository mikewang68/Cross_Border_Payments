# 用于格式化入库数据

from datetime import datetime

def flatten_dict(d, parent_key='', sep='_'):

    items = []
    for k, v in d.items():
        # 检查新键名是否会造成重复
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if parent_key and k == parent_key.split(sep)[-1]:
            new_key = parent_key
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

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

# 用于格式化电报交易推送消息
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


# 用于格式化电报日报推送消息
def format_currency_amount(currency_amount):
    currency_str = ""
    for currency, amount in currency_amount.items():
        currency_str += f"{currency}: {amount};"
    return currency_str.strip()

def format_top3_card(top3_card):
    top3_card_str = ""
    for number, count in top3_card.items():
        top3_card_str += f"{number}: {count};"
    return top3_card_str.strip()


def flat_daily_report(data,region,date):
    messages = {
        "US": {
            "title": "📌 Daily Report",
            "wallet_count": "📝 Wallet Transaction Count",
            "wallet_income_amount": "💰 Wallet Income Amount",
            "wallet_expense_amount": "💰 Wallet Expense Amount",
            "card_count": "📝 Card Transaction Count",
            "card_income_amount": "💰 Card Income Amount",
            "card_expense_amount": "💰 Card Expense Amount",
            "top3_card": "📝 Top 3 Cards",
            "no_top3_card": "📝 No Card Consumption",
            "failed_status_count":"📝 Abnormal Transactions"


        },
        "CN": {
            "title": "📌 日报",
            "wallet_count": "📝 钱包交易数",
            "wallet_income_amount": "💰 钱包入账金額",
            "wallet_expense_amount": "💰 钱包出账金額",
            "card_count": "📝 卡片交易数",
            "card_income_amount": "💰 卡片入账金额",
            "card_expense_amount": "💰 卡片出账金额",
            "top3_card": "📝 消费次数Top3",
            "no_top3_card": "📝 无卡消费",
            "failed_status_count":"📝 异常交易数"
        },
        "JP": {
            "title": "📌 日報",
            "wallet_count": "📝 ウォレット取引回数",
            "wallet_income_amount": "💰 ウォレット収入金額",
            "wallet_expense_amount": "💰 ウォレット支出金額",
            "card_count": "📝 カード取引回数",
            "card_income_amount": "💰 カード収入金額",
            "card_expense_amount": "💰 カード支出金額",
            "top3_card": "📝 消費回数上位3件",
            "no_top3_card": "📝 カードによる消費なし",
            "failed_status_count":"📝 異常取引"
        }
    }
    lang = messages.get(region, messages["US"])

    formatted_messages = []

    # 格式化title
    title_message = {
        lang["title"]: date,
    }
    formatted_messages.append(title_message)

    # 格式化钱包交易信息
    if "wallet_count" in data and "wallet_income_amount" in data and "wallet_expense_amount" in data:
        wallet_message = {lang["wallet_count"]: data["wallet_count"],
                          lang["wallet_income_amount"]: format_currency_amount(data["wallet_income_amount"]),
                          lang["wallet_expense_amount"]: format_currency_amount(data["wallet_expense_amount"])}
        formatted_messages.append(wallet_message)

    # 格式化卡交易信息
    if "card_count" in data and "card_income_amount" in data and "card_expense_amount" in data:
        card_message = {lang["card_count"]: data["card_count"],
                        lang["card_income_amount"]: format_currency_amount(data["card_income_amount"]),
                        lang["card_expense_amount"]: format_currency_amount(data["card_expense_amount"])}
        formatted_messages.append(card_message)

    # 格式化消费前3信息
    if "top3_card" in data :

        top3_card_dict = data.get("top3_card")

        if top3_card_dict is None:
            top3_card_message = {
                lang["no_top3_card"]:"",
            }
            formatted_messages.append(top3_card_message)
        else:
            card_message = {lang["top3_card"]:format_top3_card(data["top3_card"])}
            formatted_messages.append(card_message)

    # 格式化异常交易数
    if "failed_status_count" in data :

        failed_status_message = {lang["failed_status_count"]: data["failed_status_count"],}
        formatted_messages.append(failed_status_message)


    formatted_info = ""
    for item in formatted_messages:
        for key, value in item.items():
            formatted_info += f"{key}: {value}\n"

    return formatted_info

def flat_date (date):

    date_time = date.strftime('%Y-%m-%dT%H:%M:%S.%f')

    return date_time