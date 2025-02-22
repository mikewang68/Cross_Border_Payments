import base64
import time
import urllib.parse
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# 1. 读取私钥文件
def load_private_key(file_path):
    with open(file_path, 'rb') as f:
        private_key_data = f.read()
    private_key = serialization.load_pem_private_key(private_key_data, password=None, backend=default_backend())

    return private_key

# 2. 构建签名基础字符串
def create_sign_base(method, path, appid, timestamp, body_hash):
    sign_base = f'''{method} {path}
{appid}
{timestamp}
{body_hash}
'''

    return sign_base

# 3. 使用私钥对签名基础字符串进行签名
def sign_data(private_key, sign_base):
    signature = private_key.sign(
        sign_base.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return base64.b64encode(signature).decode('utf-8')

# 4. 发送API请求
def query_balance_history(card_id,page,limit):
    method = "GET"
    sign_path = f"/v1/card_bill/balance_history?page={page}&limit={limit}&card_id={card_id}"  # 请求路径
    appid = "a4d1c06a-5d1d-4228-a982-1e337f7a6f6e"  # AppID
    private_key_path = "private_key.pem"  # 私钥文件路径

    timestamp = str(int(time.time() * 1000))  # 时间戳（毫秒）

    # 1. 计算请求体的哈希值
    body_hash = ""  # GET 请求没有请求体，所以是空字符串

    # 2. 构建签名基础字符串
    sign_base = create_sign_base(method, sign_path, appid, timestamp, body_hash)

    # 3. 读取私钥并生成签名
    private_key = load_private_key(private_key_path)
    signature_base64 = sign_data(private_key, sign_base)

    # 4. 对 Base64 编码后的签名进行 URL 编码
    signature_url_encoded = urllib.parse.quote(signature_base64)

    # 5. 设置请求头
    headers = {
        'X-Appid':appid,
        'Authorization':f'algorithm=RSA2,time={timestamp},signature={signature_url_encoded}',
        "Content-Type": "application/json"
    }


    # 6. 请求 URL
    url = f"https://api.gsalary.com/v1/card_bill/balance_history?page={page}&limit={limit}&card_id={card_id}"


    # 7. 发送请求
    response = requests.get(url, headers=headers)

    # 8. 输出响应结果
    if response.status_code == 200:
        print("Response Status Code: 200")
        print("Response Content:", response.json())

        response_data = response.json()  # 直接将响应解析为JSON格式（Python字典）

        # 从 'data' 中获取 'history' 列表
        data = response_data.get('data', {})
        transactions = data.get('history', [])

        # 遍历所有交易记录并提取关键信息
        for transaction in transactions:
            log_id = transaction.get('log_id')
            transaction_id = transaction.get('transaction_id') # 交易凭证号（交易流水号）
            bill_date=transaction.get('bill_date') # 账单日期
            transaction_time=transaction.get('transaction_time') # 账单时间
            mask_card_number = transaction.get('mask_card_number') # 加密卡号
            amount = transaction.get('amount', {}).get('amount')  # 交易金额
            currency = transaction.get('amount', {}).get('currency')  # 交易货币类型
            txn_type = transaction.get('txn_type') # 交易类型
            balance_after = transaction.get('balance_after_transaction', {}).get('amount') # 账户余额

            # 打印关键信息
            print(f"Log ID: {log_id}")
            print(f"Transaction ID: {transaction_id}")
            print(f"bill_date: {bill_date}")
            print(f"transaction_time: {transaction_time}")
            print(f"mask_card_number: {mask_card_number}")
            print(f"Amount: {amount} {currency}")
            print(f"Transaction Type: {txn_type}")
            print(f"Balance After Transaction: {balance_after} {currency}")
            print("------")
        return response.json()  # 返回 API 响应内容
    else:
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
        return response.json()  # 返回 API 响应内容
