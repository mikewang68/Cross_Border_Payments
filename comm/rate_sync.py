import schedule
import asyncio
import logging
from db_api import query_database, query_field_from_table
from galileo_flask.official_rate_script import fetch_exchange_rate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler("async.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# 初始化全局变量
time_sync_start = '10:00'
time_sync_end = '16:00'

# 初始化版本数据
version_data = []


# 获取平台列表
async def query_version():
    global version_data
    try:
        version_data = query_field_from_table('async_ctrl', 'version')

    except Exception as e:
        logger.error(f"查询版本信息时出错: {e}")


async def update_schedule():
    """动态更新定时任务"""
    global time_sync_start, time_sync_end

    try:
        async_datas = await asyncio.to_thread(
            query_database, 'async_ctrl', 'version', 'J1'
        )

        for async_data in async_datas:
            new_start = async_data.get('daily_start')
            new_end = async_data.get('daily_end')

            # 验证并更新时间
            if new_start:
                time_sync_start = new_start
            if new_end:
                time_sync_end = new_end

        # 重新设置定时任务
        schedule.clear()
        # 改为同步函数包装
        schedule.every().day.at(time_sync_start).do(run_get_rate)
        schedule.every().day.at(time_sync_end).do(run_get_rate)

    except Exception as e:
        logger.error(f"更新定时任务失败: {e}")


async def get_rate():
    """获取汇率"""
    try:
        loop = asyncio.get_running_loop()
        for version in version_data:
            logger.info('开始获取汇率')
            await loop.run_in_executor(None, fetch_exchange_rate, version)
    except Exception as e:
        logger.error(f"获取汇率失败: {e}")


# 新增同步包装函数
def run_get_rate():
    loop = asyncio.get_event_loop()
    loop.create_task(get_rate())


async def schedule_manager():
    """定时任务管理器"""
    while True:
        # 每5分钟更新一次定时任务配置
        await asyncio.sleep(300)
        await update_schedule()


async def run_schedule():
    """运行定时任务"""
    while True:
        schedule.run_pending()
        next_interval = schedule.idle_seconds()
        if next_interval is None:
            next_interval = 1
        print('下次任务时间：next_interval', next_interval)
        await asyncio.sleep(next_interval)


async def main():
    # 初始化定时任务
    await update_schedule()
    # 查询平台
    await query_version()

    # 启动多个协程
    await asyncio.gather(
        schedule_manager(),
        run_schedule()
    )


if __name__ == "__main__":
    asyncio.run(main())