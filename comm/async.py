import asyncio
import logging
from db_api import insert_database, update_database, batch_update_database
from flat_data import flat_data
from db_api import query_database
from db_api import query_field_from_table
from comm.gsalay_api import GSalaryAPI

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
        flatten_data = flat_data(version, data, 'data', 'transactions')
        insert_database('card_transactions', flatten_data)
    except Exception as e:
        logger.error(f"插入交易明细时出错: {e}")
# 插入钱包交易明细
async def wallet_transactions(version):
    try:
        logger.info(f'插入{version}平台交易明细')
        data = gsalary.get_wallet_transactions(version)
        flatten_data = flat_data(version, data, 'data', 'trans')
        insert_database('wallet_transactions', flatten_data)
    except Exception as e:
        logger.error(f"插入交易明细时出错: {e}")

# 插入用户信息
async def card_holder_insert(version):
    try:
        logger.info(f'插入{version}平台用户信息')
        data = gsalary.get_card_holders(version)
        flatten_data = flat_data(version, data, 'data', 'card_holders')
        insert_database('card_holder', flatten_data)
    except Exception as e:
        logger.error(f"插入用户信息时出错: {e}")

# 对于card_holder表，更新所有用户信息
async def card_holder_update(version):
    try:
        logger.info(f'更新{version}平台用户信息')
        data = gsalary.get_card_holders(version)
        flatten_data = flat_data(version, data, 'data', 'card_holders')
        batch_update_database('card_holder', flatten_data, condition1='card_holder_id') 
    except Exception as e:
        logger.error(f"更新用户信息时出错: {e}")

# 对于cards表，获取已开卡的基础信息，插入cards表中
async def cards_insert(version):
    try:
        logger.info(f'更新{version}平台所有卡基础信息')
        data = gsalary.query_cards(version)
        flatten_data = flat_data(version, data, 'data', 'cards')
        insert_database('cards', flatten_data)
    except Exception as e:
        logger.error(f"插入卡基础信息时出错: {e}")

# 对于cards表，获取所有卡的基础信息，更新到cards表中
async def cards_update(version):
    try:
        logger.info(f'更新{version}平台所有卡基础信息')
        data = gsalary.query_cards(version)
        flatten_data = flat_data(version, data, 'data', 'card_holders')
        batch_update_database('cards', flatten_data, condition1='card_id') 
    except Exception as e:
        logger.error(f"插入卡基础信息时出错: {e}")

# 对于cards_info，获取具体卡的详细信息，插入到cards_info表中
async def cards_info_insert(version):
    try:
        card_id_data = query_database('cards', 'version', version)
        data = []
        for i in card_id_data:
            card_id = i.get('card_id')
            result = gsalary.query_cards_info(version, card_id)
            flatten_data = flat_data(version, result, 'data')
            data.append(flatten_data)
        insert_database('cards_info', data)
    except Exception as e:
        logger.error(f"插入卡信息时出错: {e}")
# 对于cards_info，获取具体卡的详细信息，更新到cards_info表中
async def cards_info_update(version):
    try:
        card_id_data = query_database('cards', 'version', version)
        data = []
        for i in card_id_data:
            card_id = i.get('card_id')
            result = gsalary.query_cards_info(version, card_id)
            flatten_data = flat_data(version, result, 'data')
            data.append(flatten_data)
        batch_update_database('cards_info', data, condition1='card_id')
    except Exception as e:
        logger.error(f"更新卡信息时出错: {e}")
# 对于cards_secure_info，获取所有卡的机密信息，插入到cards_secure_info表中
async def cards_secure_info_insert(version):
    try:
        card_id_data = query_database('cards', 'version', version)
        data = []
        for i in card_id_data:
            card_id = i.get('card_id')
            result = gsalary.get_card_secure_info(version, card_id)
            flatten_data = flat_data(version, result, 'data')
            flatten_data['card_id'] = card_id
            data.append(flatten_data) 
        insert_database('cards_secure_info', data)
    except Exception as e:
        logger.error(f"插入卡机密信息时出错: {e}")
# 对于cards_secure_info，获取所有卡的机密信息，更新到cards_secure_info表中
async def cards_secure_info_update(version):
    try:
        card_id_data = query_database('cards', 'version', version)
        data = []
        for i in card_id_data:
            card_id = i.get('card_id')
            result = gsalary.get_card_secure_info(version, card_id)
            flatten_data = flat_data(version, result, 'data')
            flatten_data['card_id'] = card_id
            data.append(flatten_data)
        batch_update_database('cards_secure_info', data, condition1='card_id')
    except Exception as e:
        logger.error(f"更新卡机密信息时出错: {e}")


# 插入余额明细
async def balance_history(version):
    logger.info(f'插入{version}平台余额明细')
    try:
        data = gsalary.get_card_balance_history(version)
        flatten_data = flat_data(version,data, 'data', 'history')
        insert_database('balance_history', flatten_data)
    except Exception as e:
        logger.error(f"插入余额明细时出错: {e}")



async def wallet_balance(version):
    logger.info(f'更新{version}钱包余额明细')
    try:
        
        params = {
            'currency': 'USD'
        }


        where = {
            'currency': 'USD',
            'version': f'{version}'
        }
        data = gsalary.get_wallet_balance(version,params )
        print(data)
        flatten_data = flat_data(version,data, 'data')
        amo = flatten_data.get('amount')
        ava = flatten_data.get('available')

        set = {
            'amount':  f'{amo}',
            'available': f'{ava}'
        }

        update_database('wallet_balance', set,where) #表名
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
            wallet_balance(version),
            card_holder_insert(version),
            wallet_transactions(version),
            batch_update_database(version)
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