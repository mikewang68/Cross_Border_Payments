import logging
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()
# 配置日志记录
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        # 处理键名拼接，去除重复部分
        if parent_key:
            parent_parts = parent_key.split(sep)
            k_parts = k.split(sep)
            new_parts = []
            for part in k_parts:
                if part not in parent_parts:
                    new_parts.append(part)
            new_key_parts = parent_parts + new_parts
            new_key = sep.join(new_key_parts)
        else:
            new_key = k

        if isinstance(v, dict):
            # 递归处理嵌套字典
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # 处理列表元素，如果列表元素是字典，也进行扁平化
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    sub_items = flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items()
                    items.extend(sub_items)
                else:
                    items.append((f"{new_key}{sep}{i}", item))
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
