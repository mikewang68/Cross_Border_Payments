from sqlalchemy.event import remove

from comm.utils import get_email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from comm.flat_data import flat_date
from db_api import query_date_from_table
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
        message.attach(MIMEText(body, 'html'))

        # 添加邮件正文
        message.attach(MIMEText(body, "plain"))

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
    last_month_2nd = datetime(last_year, last_month, 2)
    this_month_1st = datetime(now.year, now.month, 1)
    return last_month_2nd, this_month_1st


def get_table_header(table_name,region):

    return push_language.HEADERS[table_name][region]


def get_table_name(table_name,region):

    return push_language.TABLE_MAPPING.get(table_name, {}).get(region, table_name)


def get_biz_type_text(biz_type, region):

    return push_language.BIZ_TYPE_MAPPING.get(biz_type, {}).get(region, biz_type)


def make_head (header_data):

    head = "<tr>" + "".join(f"<th>{h}</th>" for h in header_data) + "</tr>"

    return head


def make_email_body(transaction_data,region,qd_level,card_id,accounting_info,customer_transaction,billing_cycle):

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
    accounting_income = accounting_info.get('income')
    accounting_expense = accounting_info.get('expense')
    accounting_info_table_rows = ""

    # 客户交易统计列表
    customer_transaction_text = get_table_name('CUSTOMER_TRANSACTION_STATISTICS', region)
    customer_transaction_header_data = get_table_header('customer_transaction_headers',region)
    customer_transaction_table_header = make_head(customer_transaction_header_data)
    customer_income = customer_transaction.get('income')
    customer_expense = customer_transaction.get('expense')
    customer_transaction_table_rows = ""

    # 交易明细
    for row in transaction_data:
        transaction_info = f"{row['transaction_amount']} {row['transaction_amount_currency']}"
        accounting_info = f"{row['accounting_amount']} {row['accounting_amount_currency']}"
        surcharge_info = f"{row['surcharge_amount']} {row['surcharge_currency']}"
        biz_type = get_biz_type_text(row['biz_type'], region)
        transaction_table_rows += "<tr>"
        transaction_table_rows += f"<td>{row['transaction_time']}</td>"
        transaction_table_rows += f"<td>{transaction_info}</td>"
        transaction_table_rows += f"<td>{accounting_info}</td>"
        transaction_table_rows += f"<td>{surcharge_info}</td>"
        transaction_table_rows += f"<td>{biz_type}</td>"
        transaction_table_rows += "</tr>"

    card_info_table_rows += "<tr>"
    card_info_table_rows += f"<td>{card_id}</td>"
    card_info_table_rows += f"<td>{billing_cycle}</td>"
    card_info_table_rows += "</tr>"

    # 账务明细
    for row in accounting_info:
        accounting_info_table_rows += "<tr>"
        accounting_info_table_rows += f"<td>{accounting_income}</td>"
        accounting_info_table_rows += f"<td>{accounting_expense}</td>"
        accounting_info_table_rows += "</tr>"

    customer_transaction_table_rows += "<tr>"
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

    if qd_level in (0,1):

        body_str = body_str_1 + body_str_2 + body_str_3

    else:

        body_str = body_str_1 + body_str_3


    return body_str


def push_monthly_report():
    try:
        start_date, end_date = get_monthly_date()
        start_date_str = flat_date(start_date)
        end_date_str = flat_date(end_date)
        transaction_data = query_date_from_table('card_transactions', 'transaction_time', start_date_str, end_date_str)
        billing_cycle = start_date_str + '-' + end_date_str
        card_id = '123'
        remove_value = ["T","Z"]

        for data in transaction_data :

            for value in remove_value :

                data['transaction_time'] = data['transaction_time'].replace(value," ")

        accounting_info = {
            'income': {'USD':'0','MYR':'121'},
            'expense':{'USD':'120','MYR':'155'}

        }

        customer_transaction = {
            'income': {'USD':'0','MYR':'121'},
            'expense':{'USD':'120','MYR':'155'}

        }



        email_pusher = EmailPusher()
        to_email = "842457745@qq.com"
        subject = "测试邮件"
        body = make_email_body(transaction_data=transaction_data, region='CN',qd_level=0,card_id=card_id,billing_cycle=billing_cycle,accounting_info = accounting_info,customer_transaction = customer_transaction)

        email_pusher.send_email(to_email, subject, body)

    except ValueError as e:
        print(f"值错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")



