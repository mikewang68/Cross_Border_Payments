import requests
from bs4 import BeautifulSoup
import pymysql
import time
import random
from datetime import datetime

FEE = 0.01
PERCENTAGE = 0.03

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

# 设置目标货币列表
currencies = ['CNY', 'HKD', 'JPY', 'EUR', 'GBP', 'AUD', 'CAD']
# currencies = ['CNY', 'HKD', 'JPY', 'EUR', 'GBP', 'AUD', 'CAD', 'SGD', 'CHF', 'NZD',
#               'PHP', 'VND', 'MYR', 'THB', 'IDR', 'KRW', 'NGN', 'INR', 'AED', 'KHR', 
#               'TWD', 'KZT', 'MXN', 'TRY', 'MOP', 'PKR', 'ARS', 'MDL', 'ALL', 'ZMZ', 
#               'IQD', 'DZD']
PROXY = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

def update_exchange_rate(currency, rate):
    # 创建数据库连接
    connection = pymysql.connect(host='127.0.0.1', user='root', password='092518', database='galileo')
    cursor = connection.cursor()

    # 查询currency是否存在
    cursor.execute("SELECT * FROM exchange_usdt WHERE currency = %s", (currency,))
    result = cursor.fetchone()

    # 计算usdt_cost, index_quote 和 percentage_quote
    usdt_cost = float(rate)/ (1 - FEE)
    index_quote = round(usdt_cost, 5)  # 保留五位小数
    percentage_quote = float(rate) / (1 - PERCENTAGE)

    if result:  # 如果currency存在，更新official_rate
        cursor.execute("""
            UPDATE exchange_usdt
            SET official_rate = %s, usdt_cost = %s, index_quote = %s, percentage_quote = %s , fee = %s, percentage = %s
            WHERE currency = %s
        """, (rate, usdt_cost, index_quote, percentage_quote, FEE, PERCENTAGE, currency))
    else:  # 如果currency不存在，插入新数据
        cursor.execute("""
            INSERT INTO exchange_usdt (currency, official_rate, exchange_provider, fee, usdt_cost, index_quote, percentage, percentage_quote)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (currency, rate, '兑换商1', FEE, usdt_cost, index_quote, PERCENTAGE, percentage_quote))  # 假设其他字段的值为默认值

    # 提交更改并关闭连接
    connection.commit()
    cursor.close()
    connection.close()

def google_fetch_exchange_rate(currency):
    url = f"https://www.google.com/finance/quote/{currency}-USD?sa=X&ved=2ahUKEwi6gX2q6vD9AhVRAxAIHS9gBt0Q3ecFegQINBAY"
    user_agent = random.choice(user_agents)
    headers = {
        "User-Agent": f"{user_agent}"
    }
    response = requests.get(url, headers=headers,proxies=PROXY)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取汇率
    try:
        exchange_rate = soup.find('div', {'class': 'YMlKec fxKbKc'}).text
        exchange_rate = float(exchange_rate.replace(',', ''))
        return exchange_rate
    except AttributeError:
        return None
    
def xe_fetch_exchange_rate(currency):
    url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={currency}&To=USD"
    # user_agent = random.choice(user_agents)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers, proxies=PROXY)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取汇率
    try:
        exchange_rate = soup.find('p', {'class': 'sc-294d8168-1 hVDvqw'}).text
        exchange_rate = float(exchange_rate.split(' ')[0])
        return exchange_rate
    except AttributeError:
        return None
    
def main():
    for currency in currencies:
        rate = google_fetch_exchange_rate(currency)
        if rate is not None:
            update_exchange_rate(currency, rate)
            print(currency + '--USD:' + str(rate)+ ' (' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +')')
            print(currency + '已写入数据库')
        else:
            print(f"Failed to fetch rate for {currency}")
        i = random.randint(10,20)
        time.sleep(i)

if __name__ == "__main__":
    main()


    
        