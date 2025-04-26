from decimal import Decimal
from comm.utils import get_email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from comm.flat_data import flat_date
from db_api import query_date_from_table, query_all_from_table
from datetime import datetime
from push_language import PushLanguage


class EmailPusher:
    def __init__(self):
        self.config = get_email()
        if self.config is None:
            raise ValueError("无法获取有效的邮件配置，请检查环境变量。")
        self.MAIL_SERVER = self.config['mail_server']
        self.MAIL_USE_SSL = self.config['mail_use_ssl']
        self.MAIL_PORT = self.config['mail_port']
        self.MAIL_USERNAME = self.config['mail_username']
        self.MAIL_PASSWORD = self.config['mail_password']
        self.MAIL_DEFAULT_SENDER = self.config['mail_default_sender']

    def send_email(self, to_email, subject, body):
        # 创建邮件对象
        message = MIMEMultipart()
        message["From"] = self.MAIL_DEFAULT_SENDER
        message["To"] = to_email
        message["Subject"] = subject


        # 添加邮件正文
        message.attach(MIMEText(body, "plain"))
        message.attach(MIMEText(body, 'html'))

        try:
            # 连接到邮件服务器
            if self.MAIL_USE_SSL:
                server = smtplib.SMTP_SSL(self.MAIL_SERVER, self.MAIL_PORT)
            else:
                server = smtplib.SMTP(self.MAIL_SERVER, self.MAIL_PORT)
                server.starttls()

            # 登录邮箱
            server.login(self.MAIL_USERNAME, self.MAIL_PASSWORD)

            # 发送邮件
            text = message.as_string()
            server.sendmail(self.MAIL_DEFAULT_SENDER, to_email, text)

            # 关闭连接
            server.quit()
            print("邮件发送成功")
        except Exception as e:
            print(f"邮件发送失败: {e}")


push_language = PushLanguage()


def get_monthly_date():

    now = datetime.now()
    if now.month == 1:
        last_year = now.year - 1
        last_month = 12
    else:
        last_year = now.year
        last_month = now.month - 1
    last_month_2nd = datetime(last_year, last_month, 2).date()
    this_month_1st = datetime(now.year, now.month, 1).date()
    return last_month_2nd, this_month_1st


def get_table_header(table_name,region):
    if region not in push_language.HEADERS[table_name]:
        region = 'US'
    return push_language.HEADERS[table_name][region]


def get_table_name(table_name,region):
    if region not in push_language.TABLE_MAPPING[table_name]:
        region = 'US'
    return push_language.TABLE_MAPPING.get(table_name, {}).get(region, table_name)


def get_biz_type_text(biz_type, region):
    if region not in push_language.BIZ_TYPE_MAPPING[biz_type]:
        region = 'US'
    return push_language.BIZ_TYPE_MAPPING.get(biz_type, {}).get(region, biz_type)


def make_head (header_data):

    head = "<tr>" + "".join(f"<th>{h}</th>" for h in header_data) + "</tr>"

    return head


def make_email_body(transaction_data,region,qd_level,mask_card_number,accounting_transaction,billing_cycle,customer_transaction=None):

    style = """
            <head>      
            <style>
                table {
                    border-collapse: collapse;
                }
                table, th, td {
                    border: 1px solid black;
                }
                th {
                    background-color: lightgray;
                }
            </style>
            </head>
        """

    # 交易明细列表
    transaction_text = get_table_name('TRANSACTION_DATA', region)
    transaction_header_data = get_table_header('transaction_headers',region)
    transaction_table_header = make_head(transaction_header_data)
    transaction_table_rows = ""

    # 卡信息列表
    card_info_text = get_table_name('CARD_INFO', region)
    card_info_header_data = get_table_header('card_info_headers',region)
    card_info_table_header = make_head(card_info_header_data)
    card_info_table_rows = ""

    # 账务明细列表
    accounting_info_text = get_table_name('ACCOUNTING_INFO', region)
    accounting_info_header_data = get_table_header('accounting_info_headers',region)
    accounting_info_table_header = make_head(accounting_info_header_data)
    accounting_info_table_rows = ""

    # 客户交易统计列表
    customer_transaction_text = get_table_name('ALL_TRANSACTION_STATISTICS', region)
    customer_transaction_header_data = get_table_header('customer_transaction_headers',region)
    customer_transaction_table_header = make_head(customer_transaction_header_data)
    customer_transaction_table_rows = ""

    # 交易明细
    for transaction_row in transaction_data:
        transaction_info = f"{transaction_row['transaction_amount']} {transaction_row['transaction_amount_currency']}"
        accounting_info = f"{transaction_row['accounting_amount']} {transaction_row['accounting_amount_currency']}"
        surcharge_info = f"{transaction_row['surcharge_amount']} {transaction_row['surcharge_currency']}"
        biz_type = get_biz_type_text(transaction_row['biz_type'], region)
        transaction_table_rows += "<tr>"
        transaction_table_rows += f"<td>{transaction_row['transaction_time']}</td>"
        transaction_table_rows += f"<td>{transaction_info}</td>"
        transaction_table_rows += f"<td>{accounting_info}</td>"
        transaction_table_rows += f"<td>{surcharge_info}</td>"
        transaction_table_rows += f"<td>{biz_type}</td>"
        transaction_table_rows += "</tr>"

    card_info_table_rows += "<tr>"
    card_info_table_rows += f"<td>{mask_card_number}</td>"
    card_info_table_rows += f"<td>{billing_cycle}</td>"
    card_info_table_rows += "</tr>"

    # 账务明细
    accounting_currencies = set(accounting_transaction['income'].keys()).union(set(accounting_transaction['expense'].keys()))
    for accounting_currency in accounting_currencies:
        accounting_income = accounting_transaction['income'].get(accounting_currency, '0')
        accounting_expense = accounting_transaction['expense'].get(accounting_currency, '0')
        accounting_info_table_rows += "<tr>"
        accounting_info_table_rows += f"<td>{accounting_currency}</td>"
        accounting_info_table_rows += f"<td>{accounting_income}</td>"
        accounting_info_table_rows += f"<td>{accounting_expense}</td>"
        accounting_info_table_rows += "</tr>"

    # 客户账务明细
    if customer_transaction :

        customer_currencies = set(customer_transaction['income'].keys()).union(set(customer_transaction['expense'].keys()))
        for customer_currency in customer_currencies:
            customer_income = customer_transaction['income'].get(customer_currency, '0')
            customer_expense = customer_transaction['expense'].get(customer_currency, '0')
            customer_transaction_table_rows += "<tr>"
            customer_transaction_table_rows += f"<td>{customer_currency}</td>"
            customer_transaction_table_rows += f"<td>{customer_income}</td>"
            customer_transaction_table_rows += f"<td>{customer_expense}</td>"
            customer_transaction_table_rows += "</tr>"


    transaction_table = f"<table border='1'>{transaction_table_header}{transaction_table_rows}</table>"
    card_info_table = f"<table border='1'>{card_info_table_header}{card_info_table_rows}</table>"
    accounting_info_table = f"<table border='1'>{accounting_info_table_header}{accounting_info_table_rows}</table>"
    customer_transaction_table = f"<table border='1'>{customer_transaction_table_header}{customer_transaction_table_rows}</table>"



    body_str_1 = f"""
                    <html>
                        {style}
                        <body>
                            <h3>{card_info_text}</h3>
                            {card_info_table}
                            <h3>{accounting_info_text}</h3>
                            {accounting_info_table}
                            <h3>{transaction_text}</h3>
                            {transaction_table}
                """
    body_str_2 = f"""
                    <h3>{customer_transaction_text}</h3>
                    {customer_transaction_table}
                """


    body_str_3 = """
                        </body>
                    </html>
                """

    if qd_level in ("0","1"):

        body_str = body_str_1 + body_str_2 + body_str_3

    else:

        body_str = body_str_1 + body_str_3


    return body_str


def push_monthly_report():
    email_pusher = EmailPusher()
    subject = "测试邮件"

    # 获取月报时间
    start_date, end_date = get_monthly_date()
    start_date_str = str(start_date)
    end_date_str = str(end_date)
    # 账单周期
    billing_cycle = start_date_str + '~' + end_date_str

    # 获取所有用户列表
    card_holders = query_all_from_table('card_holder')
    # 获取所有卡列表
    cards = query_all_from_table('cards')

    # 获取交易列表
    card_transactions = query_date_from_table("card_transactions", "transaction_time", start_date, end_date)

    # 用户分级
    # 遍历用户列表
    for card_holder in card_holders:

        # # 获取邮箱
        # email = card_holder.get('email')
        email = '842457745@qq.com'

        # 获取用户国籍
        region = card_holder.get('region')

        # 判断用户等级
        qd_level = card_holder.get('qd_level')

        # 获取card_holder_id
        card_holder_id = card_holder.get('card_holder_id')

        # 初始化卡号
        mask_card_number = 'test00'
        card_id = 'test01'
        # 获取卡号
        for card in cards :
            current_card_holder_id = card.get('card_holder_id')
            if current_card_holder_id == card_holder_id :
                mask_card_number = card.get('mask_card_number')
                card_id = card.get('card_id')

        if not qd_level:
            continue

        # 管理员操作
        if qd_level == '0':

            # 初始化账户各类货币交易额
            accounting_income_dict = {'USD': '0'}
            accounting_expense_dict = {'USD': '0'}
            # 初始化客户各类货币交易额
            customer_income_dict = {'USD': '0'}
            customer_expense_dict = {'USD': '0'}
            # 初始化当前用户交易数据
            transaction_list = []

            # 遍历交易数据生成当前用户交易列表
            for card_transaction in card_transactions :
                current_card_id = card_transaction.get('card_id')
                current_status = card_transaction.get('status')
                if card_id == current_card_id and current_status != "FAILED" :
                    transaction_list.append(card_transaction)

            for data in transaction_list:
                data['transaction_time'] = flat_date(data['transaction_time'])

            for card_transactions_data in transaction_list:

                mask_card_number = card_transactions_data.get('mask_card_number')
                currency = card_transactions_data.get('transaction_amount_currency')
                amount = card_transactions_data.get('transaction_amount')
                biz_type = card_transactions_data.get('biz_type')
                status = card_transactions_data.get('status')

                if status == "SUCCEED" and biz_type != "AUTH":
                    if amount > 0:
                        current_income = Decimal(str(accounting_income_dict.get(currency, 0)))
                        accounting_income_dict[currency] = current_income + amount
                    else:
                        current_expense = Decimal(str(accounting_expense_dict.get(currency, 0)))
                        accounting_expense_dict[currency] = current_expense + amount

            # 遍历名下所有客户交易数据
            for customer_data in card_transactions:
                customer_currency = customer_data.get('transaction_amount_currency')
                customer_amount = customer_data.get('transaction_amount')
                customer_biz_type = customer_data.get('biz_type')
                customer_status = customer_data.get('status')

                if customer_status == "SUCCEED" and customer_biz_type != "AUTH":
                    if customer_amount > 0:
                        customer_current_income = Decimal(str(customer_income_dict.get(customer_currency, 0)))
                        customer_income_dict[customer_currency] = customer_current_income + customer_amount
                    else:
                        customer_current_expense = Decimal(str(customer_expense_dict.get(customer_currency, 0)))
                        customer_expense_dict[customer_currency] = customer_current_expense + customer_amount

            # 合并字典
            accounting_transaction = {
                "income": accounting_income_dict,
                "expense": accounting_expense_dict,
            }
            customer_transaction = {
                "income": customer_income_dict,
                "expense": customer_expense_dict,
            }

            body = make_email_body(transaction_data=transaction_list, region=region ,qd_level=qd_level,
                                   mask_card_number=mask_card_number, billing_cycle=billing_cycle,
                                   accounting_transaction=accounting_transaction,
                                   customer_transaction=customer_transaction)

            email_pusher.send_email(email, subject, body)

        # 加盟商操作
        if qd_level == '1':

            # 初始化账户各类货币交易额
            accounting_income_dict = {'USD': '0'}
            accounting_expense_dict = {'USD': '0'}
            # 初始化客户各类货币交易额
            customer_income_dict = {'USD': '0'}
            customer_expense_dict = {'USD': '0'}
            # 初始化当前用户交易数据
            transaction_list = []

            # 遍历交易数据生成当前用户交易列表
            for card_transaction in card_transactions :
                current_card_id = card_transaction.get('card_id')
                current_status = card_transaction.get('status')
                if card_id == current_card_id and current_status != "FAILED" :
                    transaction_list.append(card_transaction)

            for data in transaction_list:
                data['transaction_time'] = flat_date(data['transaction_time'])

            for card_transactions_data in transaction_list:

                mask_card_number = card_transactions_data.get('mask_card_number')
                currency = card_transactions_data.get('transaction_amount_currency')
                amount = card_transactions_data.get('transaction_amount')
                biz_type = card_transactions_data.get('biz_type')
                status = card_transactions_data.get('status')

                if status == "SUCCEED" and biz_type != "AUTH":
                    if amount > 0:
                        current_income = Decimal(str(accounting_income_dict.get(currency, 0)))
                        accounting_income_dict[currency] = current_income + amount
                    else:
                        current_expense = Decimal(str(accounting_expense_dict.get(currency, 0)))
                        accounting_expense_dict[currency] = current_expense + amount

            # 初始化筛选后的用户列表
            card_holder_list = []

            # 获取名下用户数据
            for card_holder in card_holders:

                qd_id = card_holder.get('qd_id')

                if card_holder_id == qd_id:
                    card_holder_list.append(card_holder)

            # 构建 card_id 到 card_transactions 的映射
            card_transaction_map = {card_transaction.get('card_id'): [] for card_transaction in card_transactions}
            for card_transaction in card_transactions:
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

                        # 处理卡片的交易明细
                        for card_transactions_data in current_card_transactions:

                            currency = card_transactions_data.get('transaction_amount_currency')
                            amount = card_transactions_data.get('transaction_amount')
                            biz_type = card_transactions_data.get('biz_type')
                            status = card_transactions_data.get('status')

                            if status == "SUCCEED" and biz_type != "AUTH":

                                if amount > 0:

                                    customer_income = Decimal(str(customer_income_dict.get(currency, 0)))
                                    customer_income_dict[currency] = customer_income + amount

                                else:

                                    customer_expense = Decimal(str(customer_expense_dict.get(currency, 0)))
                                    customer_expense_dict[currency] = customer_expense + amount


            # 合并字典
            accounting_transaction = {
                "income": accounting_income_dict,
                "expense": accounting_expense_dict,
            }
            customer_transaction = {
                "income": customer_income_dict,
                "expense": customer_expense_dict,
            }


            body = make_email_body(transaction_data=transaction_list, region=region,qd_level=qd_level,
                                   mask_card_number=mask_card_number,billing_cycle=billing_cycle,
                                   accounting_transaction = accounting_transaction,
                                   customer_transaction = customer_transaction)

            email_pusher.send_email(email, subject, body)


        # 加盟商操作
        if qd_level == '2':

            # 初始化账户各类货币交易额
            accounting_income_dict = {'USD': '0'}
            accounting_expense_dict = {'USD': '0'}

            # 初始化当前用户交易数据
            transaction_list = []

            # 遍历交易数据生成当前用户交易列表
            for card_transaction in card_transactions :
                current_card_id = card_transaction.get('card_id')
                current_status = card_transaction.get('status')
                if card_id == current_card_id and current_status != "FAILED" :
                    transaction_list.append(card_transaction)

            for data in transaction_list:
                data['transaction_time'] = flat_date(data['transaction_time'])

            for card_transactions_data in transaction_list:

                mask_card_number = card_transactions_data.get('mask_card_number')
                currency = card_transactions_data.get('transaction_amount_currency')
                amount = card_transactions_data.get('transaction_amount')
                biz_type = card_transactions_data.get('biz_type')
                status = card_transactions_data.get('status')

                if status == "SUCCEED" and biz_type != "AUTH":
                    if amount > 0:
                        current_income = Decimal(str(accounting_income_dict.get(currency, 0)))
                        accounting_income_dict[currency] = current_income + amount
                    else:
                        current_expense = Decimal(str(accounting_expense_dict.get(currency, 0)))
                        accounting_expense_dict[currency] = current_expense + amount

            # 合并字典
            accounting_transaction = {
                "income": accounting_income_dict,
                "expense": accounting_expense_dict,
            }

            body = make_email_body(transaction_data=transaction_list, region=region,qd_level=qd_level,
                                   mask_card_number=mask_card_number,billing_cycle=billing_cycle,
                                   accounting_transaction = accounting_transaction)

            email_pusher.send_email(email, subject, body)


