from datetime import datetime


def format_transactions(original_data):

    result = []
    for item in original_data:
        format_item = {
            "transaction_id": item["transaction_id"],
            "card_id": item["card_id"],
            "mask_card_number": item["mask_card_number"],
            "transaction_time": flat_date(item["transaction_time"]),
            "confirm_time": item["confirm_time"],
            "transaction_amount": {
                "amount": float(item["transaction_amount"]),
                "currency": item["transaction_amount_currency"]
            },
            "accounting_amount": {
                "amount": float(item["accounting_amount"]),
                "currency": item["accounting_amount_currency"]
            },
            "surcharge": {
                "amount": float(item["surcharge_amount"]),
                "currency": item["surcharge_currency"]
            },
            "biz_type": item["biz_type"],
            "status": item["status"]
        }
        result.append(format_item)

    return result

def format_balance_history(original_data):

    result = []
    for item in original_data:
        format_item = {
            "log_id": item["log_id"],
            "transaction_id": item["transaction_id"],
            "bill_date": item["bill_date"].strftime('%Y-%m-%d'),
            "transaction_time": flat_date(item["transaction_time"]),
            "mask_card_number": item["mask_card_number"],
            "card_id": item["card_id"],
            "amount": {
                "amount": float(item["amount"]),
                "currency": item["amount_currency"]
            },
            "txn_type": item["txn_type"],
            "balance_after_transaction": {
                "amount": float(item["balance_after_transaction_amount"]),
                "currency": item["balance_after_transaction_currency"]
            },

        }
        result.append(format_item)

    return result

def flat_date (date):
    try:

        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))

        formatted_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_str
    except ValueError:
        print(f"输入的时间字符串 {date} 格式不正确，无法解析。")
        return None