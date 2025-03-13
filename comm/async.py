import asyncio

import logging

from db_api import insert_database
from flat_data import flat_data
from db_api import query_database
from db_api import query_field_from_table
from gsalay_api import GSalaryAPI

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

handler = logging.FileHandler("async.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


# 初始化伽利略 API
gsalary = GSalaryAPI()
# 初始化执行周期
time = 60
# 初始化版本数据
version_data = []




# 获取平台列表
async def query_version():
    global version_data
    try:
        version_data = query_field_from_table('async_ctrl', 'version')

    except Exception as e:
        logger.error(f"查询版本信息时出错: {e}")

# 获取执行周期
async def async_time():
    global time
    try:
        async_datas = query_database('async_ctrl', 'version', 'J1')
        for async_data in async_datas:
            time = async_data.get('async_time')
            if time is not None:
                time = int(time)

    except Exception as e:
        logger.error(f"查询执行周期时出错: {e}")

# 插入交易明细
async def card_transactions(version):
    try:
        logger.info(f'插入{version}平台交易明细')
        data = gsalary.get_card_transactions(version)
        flatten_data = flat_data(version,data, 'data', 'transactions')
        insert_database('card_transactions', flatten_data)
    except Exception as e:
        logger.error(f"插入交易明细时出错: {e}")

# 插入余额明细
async def balance_history(version):
    logger.info(f'插入{version}平台余额明细')
    try:

        data = gsalary.get_card_balance_history(version)
        flatten_data = flat_data(version,data, 'data', 'history')
        insert_database('balance_history', flatten_data)
    except Exception as e:
        logger.error(f"插入余额明细时出错: {e}")

# 模拟获取用户信息
async def get_user_info():
    try:
        return
    except Exception as e:
        print(f"获取用户信息时出错: {e}")

async def wallet_balance(version):
    logger.info(f'插入{version}钱包余额明细')
    try:

        data = gsalary.get_wallet_balance(version)
        flatten_data = flat_data(data, 'data')
        insert_database('wallet_balance', flatten_data) #表名
    except Exception as e:
        logger.error(f"插入钱包余额明细时出错: {e}")

# 主任务函数，异步执行所有信息获取
async def fetch_info():
    # 查询平台
    await query_version()
    # 查询执行周期时间
    await async_time()
    all_tasks = []
    for version in version_data:

        tasks = [
            card_transactions(version),
            balance_history(version),
            get_user_info()
        ]
        all_tasks.extend(tasks)

    try:
        # 执行所有任务
        await asyncio.gather(*all_tasks)
    except Exception as e:
        logger.error(f"执行任务时出错: {e}")

    await asyncio.sleep(time)

# 运行异步程序
async def main():
    # 启动定时任务
    while True:
        await fetch_info()

# 启动程序
asyncio.run(main())