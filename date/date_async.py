import schedule
import asyncio
import logging

from email_push import push_monthly_report
from tele_push import push_daily_report
from db_api import query_database
from official_rate_script import fetch_exchange_rate
from datetime import datetime


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("async.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# 初始化全局变量
time_sync_start = '10:00'
time_sync_end = '16:00'
time_daily_report = '06:00'
time_monthly_report = '06:00'


async def update_schedule():
    """动态更新定时任务"""
    global time_sync_start, time_sync_end, time_daily_report,time_monthly_report,date_monthly_report

    try:
        async_datas = await asyncio.to_thread(
            query_database, 'async_ctrl', 'version', 'J2'
        )

        for async_data in async_datas:
            new_start = async_data.get('daily_start')
            new_end = async_data.get('daily_end')
            daily_report = async_data.get('daily_report')
            monthly_report_time = async_data.get('monthly_time')
            monthly_report_date = async_data.get('monthly_date')

            # 验证并更新时间
            if new_start:
                time_sync_start = new_start
            if new_end:
                time_sync_end = new_end
            if daily_report:
                time_daily_report = daily_report
            if monthly_report_time:
                time_monthly_report = monthly_report_time
            if monthly_report_date:
                date_monthly_report = monthly_report_date

        # 重新设置定时任务
        schedule.clear()
        schedule.every().day.at(time_sync_start).do(run_get_rate)
        schedule.every().day.at(time_sync_end).do(run_get_rate)
        schedule.every().day.at(time_daily_report).do(run_push_daily_report)
        schedule.every().day.at(time_monthly_report).do(run_push_monthly_report)

    except Exception as e:
        logger.error(f"更新定时任务失败: {e}")


async def async_push_daily_report():
    try:
        loop = asyncio.get_running_loop()
        logger.info('开始推送日报')
        await loop.run_in_executor(None, push_daily_report)
    except Exception as e:
        logger.error(f"推送日报失败: {e}")


async def async_get_rate():
    try:
        loop = asyncio.get_running_loop()
        logger.info('开始获取汇率')
        await loop.run_in_executor(None, fetch_exchange_rate)
    except Exception as e:
        logger.error(f"获取汇率失败: {e}")

async def async_push_monthly_report():
    try:
        loop = asyncio.get_running_loop()
        logger.info('开始推送月报')
        await loop.run_in_executor(None, push_monthly_report)
    except Exception as e:
        logger.error(f"推送月报失败: {e}")


def run_push_daily_report():
    loop = asyncio.get_event_loop()
    loop.create_task(async_push_daily_report())


def run_get_rate():
    loop = asyncio.get_event_loop()
    loop.create_task(async_get_rate())



def run_push_monthly_report():
    # 每天都执行，但只有每月3号才真正执行月报推送
    if datetime.now().day == int(date_monthly_report):
        loop = asyncio.get_event_loop()
        loop.create_task(async_push_monthly_report())



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
        print('下次任务时间：', next_interval)
        await asyncio.sleep(next_interval)


async def main():
    # 初始化定时任务
    await update_schedule()

    # 启动多个协程
    await asyncio.gather(
        schedule_manager(),
        run_schedule()
    )


if __name__ == "__main__":
    asyncio.run(main())
