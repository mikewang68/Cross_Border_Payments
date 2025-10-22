import logging
import os
from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()
# 配置日志记录
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db():
    db_config = {}
    required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_DATABASE']
    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            logging.error(f"环境变量 {var} 未设置，请检查。")
            return None
        if var == 'DB_PORT':
            try:
                value = int(value)
            except ValueError:
                logging.error(f"环境变量 {var} 的值不是有效的整数，请检查。")
                return None
        db_config[var[3:].lower()] = value
    return db_config


def get_tele_token():
    var = 'BOT_TOKEN'
    value = os.getenv(var)

    if value is None:
        logging.error(f"环境变量 {var} 未设置，请检查。")
        return None

    tele_config = {var.lower(): value}  # 统一键名格式为小写
    return tele_config


def get_email():
    email_config = {}
    required_vars = ['MAIL_SERVER', 'MAIL_USE_SSL', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER']
    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            logging.error(f"环境变量 {var} 未设置，请检查。")
            return None
        if var == 'MAIL_USE_SSL':
            value = value.lower() == 'true'
        elif var == 'MAIL_PORT':
            try:
                value = int(value)
            except ValueError:
                logging.error(f"环境变量 {var} 的值不是有效的整数，请检查。")
                return None
        email_config[var.lower()] = value
    return email_config



