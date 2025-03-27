import logging
import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
from comm.db_api import query_field_from_table,create_db_connection,query_database

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("rate.log",encoding="utf-8")
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# -----------------------------------------------初始化----------------------------------------------------------

# currencies = ['CNY', 'HKD', 'JPY', 'EUR', 'GBP', 'AUD', 'CAD', 'SGD', 'CHF', 'NZD',
#               'PHP', 'VND', 'MYR', 'THB', 'IDR', 'KRW', 'NGN', 'INR', 'AED', 'KHR',
#               'TWD', 'KZT', 'MXN', 'TRY', 'MOP', 'PKR', 'ARS', 'MDL', 'ALL', 'ZMZ',
#               'IQD', 'DZD']

currencies = ['CNY', 'HKD', 'JPY', 'EUR', 'GBP', 'AUD']

channel='google'

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/85.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL Build/QD1A.190821.007) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; Galaxy S10e Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.119 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; OnePlus 9 Pro Build/RKQ1.200826.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36"
]

PROXY = {
    "http": "http://127.0.0.1:7897",
    "https": "http://127.0.0.1:7897"
}
# ---------------------------------------------------初始化------------------------------------------------



def update_to_usd(currency, rate):

    # 创建数据库连接
    conn = create_db_connection()
    if conn is None:
        logger.error("无法建立数据库连接，程序退出。")
        return

    cursor = conn.cursor()


    # 查询currency是否存在
    cursor.execute("SELECT * FROM exchange_usdt WHERE currency_from = %s AND currency_to = 'USD'",(currency,))
    result = cursor.fetchone()
    current_time = datetime.now()
    insert_time = current_time.strftime("%Y%m%d%H%M%S%f")

    if result:  # 如果currency存在，更新official_rate
        cursor.execute("""
            UPDATE exchange_usdt
            SET official_rate = %s,insert_time = %s
            WHERE currency_from = %s AND currency_to = 'USD'
        """, (rate, insert_time, currency))
    else:  # 如果currency不存在，插入新数据
        cursor.execute("""
            INSERT INTO exchange_usdt (currency_from, currency_to,official_rate, insert_time)
            VALUES (%s, %s, %s, %s)
        """, (currency, 'USD',rate, insert_time))  # 假设其他字段的值为默认值

    # 提交更改并关闭连接
    conn.commit()
    cursor.close()
    conn.close()


def update_from_usd(currency, rate):

    # 创建数据库连接
    conn = create_db_connection()
    if conn is None:
        logger.error("无法建立数据库连接，程序退出。")
        return

    cursor = conn.cursor()


    # 查询currency是否存在
    cursor.execute("SELECT * FROM exchange_usdtWHERE currency_to = %s AND currency_from = 'USD'",(currency,))
    result = cursor.fetchone()
    current_time = datetime.now()
    insert_time = current_time.strftime("%Y%m%d%H%M%S%f")

    if result:  # 如果currency存在，更新official_rate
        cursor.execute("""
            UPDATE exchange_usdt
            SET official_rate = %s,insert_time = %s
            WHERE currency_to = %s AND currency_from = 'USD'
        """, (rate, insert_time, currency))
    else:  # 如果currency不存在，插入新数据
        cursor.execute("""
            INSERT INTO exchange_usdt (currency_from, currency_to,official_rate, insert_time)
            VALUES (%s, %s, %s, %s)
        """, ('USD', currency,rate, insert_time))  # 假设其他字段的值为默认值

    # 提交更改并关闭连接
    conn.commit()
    cursor.close()
    conn.close()



def google_fetch_to_usd(currency):
    url = f"https://www.google.com/finance/quote/{currency}-USD?sa=X&ved=2ahUKEwi6gX2q6vD9AhVRAxAIHS9gBt0Q3ecFegQINBAY"
    user_agent = random.choice(user_agents)
    headers = {
        "User-Agent": f"{user_agent}"
    }
    response = requests.get(url, headers=headers, proxies=PROXY)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取汇率
    try:
        exchange_rate = soup.find('div', {'class': 'YMlKec fxKbKc'}).text
        exchange_rate = float(exchange_rate.replace(',', ''))
        return exchange_rate


    except Exception as e:

        logger.error(f"Google使用{user_agent}处理 {currency}--USD 时发生错误: {e}")

        return None

def google_fetch_from_usd(currency):
    url = f"https://www.google.com/finance/quote/USD-{currency}?sa=X&ved=2ahUKEwjvrOSqvKWMAxURrlYBHYFwD4UQmY0JegQIARAs"
    user_agent = random.choice(user_agents)
    headers = {
        "User-Agent": f"{user_agent}"
    }
    response = requests.get(url, headers=headers, proxies=PROXY)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取汇率
    try:
        exchange_rate = soup.find('div', {'class': 'YMlKec fxKbKc'}).text
        exchange_rate = float(exchange_rate.replace(',', ''))
        return exchange_rate

    except Exception as e:

        logger.error(f"Google使用{user_agent}处理 USD--{currency} 时发生错误: {e}")

        return None


def xe_fetch_to_usd(currency):
    url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={currency}&To=USD"
    user_agent = random.choice(user_agents)
    headers = {
        "User-Agent": f"{user_agent}"
    }
    response = requests.get(url, headers=headers, proxies=PROXY)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取汇率
    try:
        rate = soup.find('p', {'class': 'sc-294d8168-1 hVDvqw'}).text

        main_value = rate.split(' ')[0].replace('"', '').replace(',', '')

        decimal_part = soup.find("span", class_="faded-digits").text.strip()

        exchange_rate = float(main_value + decimal_part)
        return exchange_rate
    except Exception as e:
        logger.error(f"XE使用{user_agent}处理 {currency}--USD 时发生错误: {e}")
        return None

def xe_fetch_from_usd(currency):
    url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To={currency}"
    user_agent = random.choice(user_agents)
    headers = {
        "User-Agent": f"{user_agent}"
    }
    response = requests.get(url, headers=headers, proxies=PROXY)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取汇率
    try:
        rate = soup.find('p', {'class': 'sc-294d8168-1 hVDvqw'}).text

        main_value = rate.split(' ')[0].replace('"', '').replace(',', '')

        decimal_part = soup.find("span", class_="faded-digits").text.strip()

        exchange_rate = float(main_value + decimal_part)
        return exchange_rate
    except Exception as e:
        logger.error(f"XE使用{user_agent}处理USD--{currency} 时发生错误: {e}")
        return None


def fetch_exchange_rate():
    global currencies
    global channel

    data = query_field_from_table('region', 'currency', 'is_referenced = 1')
    currencies = list(set(data))

    print(currencies)

    for currency in currencies:
        try:
            if channel == 'google':
                rate_to_usd = google_fetch_to_usd(currency)
                rate_from_usd = google_fetch_from_usd(currency)
            else:
                rate_to_usd = xe_fetch_to_usd(currency)
                rate_from_usd = xe_fetch_from_usd(currency)

            if rate_to_usd is None:
                if channel == 'google':
                    rate_to_usd = xe_fetch_to_usd(currency)
                else:
                    rate_to_usd = google_fetch_to_usd(currency)

            if rate_from_usd is None:
                if channel == 'google':
                    rate_from_usd = xe_fetch_from_usd(currency)
                else:
                    rate_from_usd = google_fetch_from_usd(currency)

            # 处理 rate_to_usd
            if rate_to_usd is not None:
                update_to_usd(currency, rate_to_usd)
                print(f"{currency}--USD: {rate_to_usd} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                print(f"{currency} 已写入数据库")
            else:
                logger.error(f"Failed to fetch rate for {currency} to USD")

            # 处理 rate_from_usd
            if rate_from_usd is not None:
                update_from_usd(currency, rate_from_usd)
                print(f"USD--{currency}: {rate_from_usd} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                print(f"{currency} 已写入数据库")
            else:
                logger.error(f"Failed to fetch rate for USD to {currency}")

            i = random.randint(20, 40)
            time.sleep(i)

        except Exception as e:
            logger.error(f"在处理 {currency} 时发生错误: {e}")
            continue  # 错误发生时跳过当前循环，继续处理下一个货币