from flask import jsonify
from comm.utils import get_email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

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

            return jsonify({"message": "Email sent successfully!"}), 200

        except Exception as e:

            return jsonify({"error": f"Error sending email: {e}"}), 500
