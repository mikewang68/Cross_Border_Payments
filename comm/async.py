import asyncio
from db_api import insert_database
from flat_data import flat_data
from db_api import query_database
from db_api import query_all_from_table
from db_api import update_database
from gsalay_api import GSalaryAPI



#-------------------------- 伽利略任务Start------------------------------------------------------

gsalary = GSalaryAPI()
# 插入交易明细
async def card_transactions(version):
    data = gsalary.get_card_transactions(version)
    flatten_data = flat_data(data, 'data', 'transactions')
    insert_database('card_transactions', flatten_data)

# 插入余额明细
async def balance_history(version):
    data = gsalary.get_card_balance_history(version)
    flatten_data = flat_data(data, 'data', 'history')
    insert_database('balance_history', flatten_data)
#-------------------------- 伽利略任务End--------------------------------------------------------

















# --------------------------------任务定时启动Start-----------------------------------------------------
async def periodic_task():
    while True:


#--------------------伽利略1
        # 插入交易明细
        await card_transactions('J1')

        # 插入余额明细
        await balance_history('J1')


#--------------------伽利略2
        # 插入交易明细
        await card_transactions('J2')

        # 插入余额明细
        await balance_history('J2')


#------------------- 获取执行周期
        async_ctrl = query_database('async_ctrl','version','J1')
        record = async_ctrl[0]
        sleep_time = record.get('async_time')
        await asyncio.sleep(int(sleep_time))

# --------------------------------任务定时启动End-------------------------------------------------------






if __name__ == "__main__":
    asyncio.run(periodic_task())