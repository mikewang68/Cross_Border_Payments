from comm.db_api import query_all_from_table
from datetime import datetime, timedelta
from decimal import Decimal
from comm.tele_push import tele_pusher
from flat_data import flat_daily_report

def push_daily_report ():

    cards = query_all_from_table('cards')

    card_transactions = query_all_from_table('card_transactions')

    # 获取所有用户列表
    card_holders = query_all_from_table('card_holder')

    # 遍历用户列表
    for card_holder in card_holders :

        # 获取电报账号
        chat_id = card_holder.get('telegram_id')

        # 获取用户国籍
        region = card_holder.get('region')

        # 判断用户等级
        qd_level = card_holder.get('qd_level')

        # 获取加盟商card_holder_id
        card_holder_id = card_holder.get('card_holder_id')

        if not qd_level :
            continue

        # 管理员操作
        if qd_level == '0' :

            # 获取全部用户数据
            card_holder_list = card_holders

            push_message = make_daily_report (card_holder_list,qd_level,region,cards,card_transactions)

            response = tele_pusher.push_message(push_message, chat_id)

            print(response)


        # 加盟商操作
        if qd_level == '1' :

            # 初始化筛选后的用户列表
            card_holder_list = []

            # 获取名下用户数据
            for card_holder in card_holders :

                qd_id = card_holder.get('qd_id')

                if card_holder_id == qd_id :

                    card_holder_list.append(card_holder)

            push_message = make_daily_report (card_holder_list,qd_level,region,cards,card_transactions)

            response = tele_pusher.push_message(push_message, chat_id)

            print(response)


# 制作日报

def make_daily_report (card_holder_list,qd_level,region,cards,card_transactions):

    # 获取前一天的日期
    current_date = datetime.now()
    previous_date = current_date - timedelta(days=14)
    previous_date_str = previous_date.strftime('%Y-%m-%d')

    # 获取前一天交易数据

    # 初始化钱包交易明细列表
    wallet_transactions_list = []

    # 处理钱包交易明细
    wallet_transactions = query_all_from_table('wallet_transactions')

    # 遍历钱包交易明细
    for wallet_transaction in wallet_transactions:

        # 获取对应日期的交易明细
        transaction_time = wallet_transaction.get('transaction_time')

        # 提取数据库日期中的年月日部分
        transaction_date = datetime.fromisoformat(transaction_time.replace("Z", "+00:00")).strftime('%Y-%m-%d')

        if previous_date_str == transaction_date:
            wallet_transactions_list.append(wallet_transaction)

    # 初始化卡交易明细列表
    card_transactions_list = []

    # 遍历卡交易明细
    for card_transaction in card_transactions:

        # 获取对应日期的交易明细
        transaction_time = card_transaction.get('transaction_time')

        # 提取数据库日期中的年月日部分
        transaction_date = datetime.fromisoformat(transaction_time.replace("Z", "+00:00")).strftime('%Y-%m-%d')

        if previous_date_str == transaction_date:
            card_transactions_list.append(card_transaction)


    if qd_level == '0':

        # 初始化钱包各类货币交易额
        wallet_income_dict = {'USD': '0'}
        wallet_expense_dict = {'USD': '0'}

        # 初始化卡各类货币交易额
        card_income_dict = {'USD': '0'}
        card_expense_dict = {'USD': '0'}

        # 初始化卡片信息
        mask_card_dict = {}

        # 钱包交易笔数
        wallet_count = len(wallet_transactions_list)


        for wallet_transaction_data in wallet_transactions_list:

            currency = wallet_transaction_data.get('amount_currency')

            amount = wallet_transaction_data.get('amount')

            if amount > 0:
                current_income = Decimal(str(wallet_income_dict.get(currency, 0)))
                wallet_income_dict[currency] = current_income + amount
            else:
                current_expense = Decimal(str(wallet_expense_dict.get(currency, 0)))
                wallet_expense_dict[currency] = current_expense + amount


        # 处理卡交易明细
        # 卡交易笔数
        card_count =len(card_transactions_list)
        # 异常交易数
        failed_status_count = 0

        for card_transactions_data in card_transactions_list:

            mask_card_number = card_transactions_data.get('mask_card_number')
            currency = card_transactions_data.get('transaction_amount_currency')
            amount = card_transactions_data.get('transaction_amount')
            biz_type = card_transactions_data.get('biz_type')
            status = card_transactions_data.get('status')

            if status in ("FAILED", "VOID", "REJECTED"):

                failed_status_count += 1

            else:

                if biz_type != "SERVICE_FEE" :

                    if mask_card_number in mask_card_dict :
                        mask_card_dict[mask_card_number] += 1
                    else:
                        mask_card_dict[mask_card_number] = 1

            if status == "SUCCEED":
                if amount > 0:
                    current_income = Decimal(str(card_income_dict.get(currency, 0)))
                    card_income_dict[currency] = current_income + amount
                else:
                    current_expense = Decimal(str(card_expense_dict.get(currency, 0)))
                    card_expense_dict[currency] = current_expense + amount

        sorted_cards = sorted(mask_card_dict.items(), key=lambda item: item[1], reverse=True)
        top_three = sorted_cards[:3]
        top3_card_dict = dict(top_three)

        # 合并字典
        result_data = {
            "wallet_income_amount": wallet_income_dict,
            "wallet_expense_amount": wallet_expense_dict,
            "wallet_count": wallet_count,
            "card_income_amount": card_income_dict,
            "card_expense_amount": card_expense_dict,
            "card_count": card_count,
            "top3_card": top3_card_dict,
            "failed_status_count":failed_status_count
        }
        # 格式化消息
        result_data = flat_daily_report(result_data,region,previous_date_str)

        return result_data

    elif qd_level == '1':

        # 初始化卡各类货币交易额
        card_income_dict = {'USD': '0'}
        card_expense_dict = {'USD': '0'}

        # 初始化卡片信息
        mask_card_dict = {}
        failed_status_count = 0
        card_count = 0

        # 构建 card_id 到 card_transactions 的映射，避免多层嵌套循环
        card_transaction_map = {card_transaction.get('card_id'): [] for card_transaction in card_transactions_list}
        for card_transaction in card_transactions_list:
            card_id = card_transaction.get('card_id')
            if card_id in card_transaction_map:
                card_transaction_map[card_id].append(card_transaction)

        # 遍历加盟商名下的用户 list 获取 card_holder_id
        for card_holder in card_holder_list:
            card_holder_id = card_holder.get('card_holder_id')
            # 获取当前用户的 card 列表
            current_user_cards = [card for card in cards if card.get('card_holder_id') == card_holder_id]

            # 遍历当前用户的 card 列表
            for card_data in current_user_cards:
                card_id = card_data.get('card_id')
                # 获取当前卡片的交易列表
                current_card_transactions = card_transaction_map.get(card_id, [])

                # 处理当前卡片的交易明细
                for card_transactions_data in current_card_transactions:
                    card_count += 1
                    mask_card_number = card_transactions_data.get('mask_card_number')
                    currency = card_transactions_data.get('transaction_amount_currency')
                    amount = card_transactions_data.get('transaction_amount')
                    biz_type = card_transactions_data.get('biz_type')
                    status = card_transactions_data.get('status')

                    if status in ("FAILED", "VOID", "REJECTED"):
                        failed_status_count += 1
                    else:
                        if biz_type != "SERVICE_FEE":
                            mask_card_dict[mask_card_number] = mask_card_dict.get(mask_card_number, 0) + 1

                    if status == "SUCCEED":
                        if amount > 0:

                            current_income = Decimal(str(card_income_dict.get(currency, 0)))
                            card_income_dict[currency] = current_income + amount
                        else:

                            current_expense = Decimal(str(card_expense_dict.get(currency, 0)))
                            card_expense_dict[currency] = current_expense + amount


        sorted_cards = sorted(mask_card_dict.items(), key=lambda item: item[1], reverse=True)
        top_three = sorted_cards[:3]
        top3_card_dict = dict(top_three)

        # 合并字典
        result_data = {
            "card_income_amount": card_income_dict,
            "card_expense_amount": card_expense_dict,
            "card_count": card_count,
            "top3_card": top3_card_dict,
            "failed_status_count": failed_status_count
        }
        # 格式化消息
        result_data = flat_daily_report(result_data, region, previous_date_str)

        return result_data
