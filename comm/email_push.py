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


def generate_table_header(region):

    return push_language.HEADERS.get(region, push_language.HEADERS['US'])


def get_table_name(table_name,region):

    return push_language.TABLE_MAPPING.get(table_name, {}).get(region, table_name)


def get_biz_type_text(biz_type, region):

    return push_language.BIZ_TYPE_MAPPING.get(biz_type, {}).get(region, biz_type)


def generate_email_body(data, region):

    header = generate_table_header(region)
    table_header = "<tr>" + "".join(f"<th>{h}</th>" for h in header) + "</tr>"
    table_rows = ""

    for row in data:
        transaction_info = f"{row['transaction_amount']} {row['transaction_amount_currency']}"
        accounting_info = f"{row['accounting_amount']} {row['accounting_amount_currency']}"
        surcharge_info = f"{row['surcharge_amount']} {row['surcharge_currency']}"
        biz_type = get_biz_type_text(row['biz_type'], region)
        table_rows += "<tr>"
        table_rows += f"<td>{row['transaction_time']}</td>"
        table_rows += f"<td>{transaction_info}</td>"
        table_rows += f"<td>{accounting_info}</td>"
        table_rows += f"<td>{surcharge_info}</td>"
        table_rows += f"<td>{biz_type}</td>"
        table_rows += "</tr>"
    table = f"<table border='1'>{table_header}{table_rows}</table>"
    transaction_text = get_table_name('TRANSACTION_DATA', region)
    return f"<html><body><h3>{transaction_text}</h3>{table}</body></html>"


if __name__ == "__main__":
    try:
        start_date, end_date = get_monthly_date()
        start_date_str = flat_date(start_date)
        end_date_str = flat_date(end_date)
        data = query_date_from_table('card_transactions', 'transaction_time', start_date_str, end_date_str)

        email_pusher = EmailPusher()
        to_email = "842457745@qq.com"
        subject = "测试邮件"
        body = generate_email_body(data, 'CN')

        email_pusher.send_email(to_email, subject, body)

    except ValueError as e:
        print(f"值错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")



