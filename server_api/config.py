import os

# DB配置
HOSTNAME = "localhost"
PORT = "3306"
USERNAME = "root"
PASSWORD = "971112"
DATABASE = "gsalary"
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8"


    # 邮件配置
MAIL_SERVER = "smtp.163.com"  # 使用 qq 的 SMTP 服务器
MAIL_USE_SSL = True  # 使用 TLS
MAIL_PORT = 465  # SMTP 端口
MAIL_USERNAME = "15542381397@163.com"  # 邮箱用户名
MAIL_PASSWORD = "MDvpC39Pv4KAWQLe"  # 邮箱密码
MAIL_DEFAULT_SENDER = "15542381397@163.com"  # 邮箱用户名