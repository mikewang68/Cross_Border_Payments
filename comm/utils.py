import logging
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()
# 配置日志记录
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("error.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def flatten_dict(d, parent_key='', sep='_'):
    """
    该函数用于将嵌套的字典进行扁平化处理
    """
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
