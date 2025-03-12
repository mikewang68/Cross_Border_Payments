import asyncio
from db_api import insert_database
from flat_data import flat_data
from db_api import query_database
from db_api import query_all_from_table
from db_api import update_database
from gsalay_api import GSalaryAPI


#-------------------------- 伽利略任务Start------------------------------------------------------

gsalary = GSalaryAPI()
time = 60



async def async_time (version,time):
    # ------------------- 获取执行周期
    async_ctrl = query_database('async_ctrl', 'version', 'J1')
    record = async_ctrl[0]
    time = record.get('async_time')




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


# 模拟获取用户信息
async def get_user_info():

    return


# 主任务函数，异步执行所有信息获取
async def fetch_info():
    tasks = [
        card_transactions('J1'),
        balance_history('J1'),
        get_user_info(),
        async_time('J1',time)
    ]

    # 使用 asyncio.gather 并行执行所有任务
    await asyncio.gather(*tasks)


    await asyncio.sleep(int(time))


# 运行异步程序
async def main():
    # 启动定时任务
    await fetch_info()


# 启动程序
asyncio.run(main())
