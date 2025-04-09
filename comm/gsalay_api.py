import hashlib
from typing import Dict, Any, Optional
import base64
import time
import urllib.parse
import requests
import json
import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from urllib.parse import urlencode
from comm.db_api import query_database


# 配置日志记录
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("error.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def load_private_key(system_id):

    data = query_database('system_key', 'system', system_id)

    for item in data:
        if item.get('system') == system_id:
            private_key_pem_str = item.get('key')
            converted_key_str = private_key_pem_str.replace("\\n", "\n")
            private_key_data = converted_key_str.encode('utf-8')
            break
    else:
        logger.error(f"未找到 {system_id} 的信息。")

    try:
        private_key = serialization.load_pem_private_key(private_key_data, password=None, backend=default_backend())

        return private_key
    except Exception as e:
        print(f"加载私钥时出错: {e}")
        return None

def load_app_id(system_id):

    data = query_database('system_key', 'system', system_id)

    for item in data:
        if item.get('system') == system_id:
            appid = item.get('appid')
            break
    else:
        logger.error(f"未找到 {system_id} 的信息。")
        
    return appid



class GSalaryAPI:
    def __init__(self):
        self.gsalary_base_url = "https://api.gsalary.com"

    def make_gsalary_request(self, method: str, endpoint: str, system_id: str, data: Optional[Dict] = None,
                             params: Optional[Dict] = None) -> Dict[str, Any]:
        # 计算body_hash by 裴振宇
        if data:
            json_str = json.dumps(data)
            body_hash_str = base64.b64encode(hashlib.sha256(json_str.encode('utf-8')).digest()) # b'PVRmqiVh1wxhelobc+aZtBHg9UXVW4n0LY97ayhPeEQ='
            body_hash = body_hash_str.decode('utf-8')
        else:
            body_hash = ''
        private_key = load_private_key(system_id)
        if private_key is None:
            return {}

        url = f"{self.gsalary_base_url}{endpoint}"
        timestamp = str(int(time.time() * 1000))  # 时间戳（毫秒）

        appid = load_app_id(system_id)
        if appid is None:
            return {}

        if params is not None:
            param_str = urllib.parse.urlencode(params)
            path = f"{endpoint}?{param_str}"
        else:
            path = endpoint
        sign_base = f'''{method} {path}
{appid}
{timestamp}
{body_hash}
'''
        signature = private_key.sign(
            sign_base.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        signature_base64 = base64.b64encode(signature).decode('utf-8')
        signature_url_encoded = urllib.parse.quote(signature_base64)

        headers = {
            'X-Appid': appid,
            'Authorization': f'algorithm=RSA2,time={timestamp},signature={signature_url_encoded}',
            "Content-Type": "application/json"
        }

        try:
            if params is not None:
                response = requests.request(method, url, headers=headers, json=data, params=params)
            else:
                response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            logger.error(f"HTTP error occurred: {response.json()}")
            return {}
        except Exception as err:
            logger.error(f"Other error occurred: {err}")
            return {}

    # 账户操作 - 钱包
    def get_wallet_balance(self, system_id, params: Optional[dict] = None) -> Dict[str, Any]:
        """获取钱包余额

        Args:
            currency: 指定货币类型
        """

        return self.make_gsalary_request("GET", "/v1/wallets/balance", system_id=system_id, params=params)


    def get_wallet_transactions(self, system_id,start_date: Optional[str] = None, end_date: Optional[str] = None,
                               page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取钱包交易记录
        
        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            page: 页码
            page_size: 每页记录数
        """
        params = {
            "page": page,
            "limit": page_size
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self.make_gsalary_request("GET", "/v1/wallets/transactions", system_id=system_id, params=params)
    
    def wallet_deposit(self, system_id,data: Dict) -> Dict[str, Any]:
        """钱包充值
        
        Args:
            data: 充值信息，包含金额、币种等
        """
        return self.make_gsalary_request("POST", "/wallet/deposit",system_id,data)
    
    def wallet_withdraw(self, system_id,data: Dict) -> Dict[str, Any]:
        """钱包提现
        
        Args:
            data: 提现信息，包含金额、币种、银行账户等
        """
        return self.make_gsalary_request("POST", "/wallet/withdraw",system_id,data)
    
    def get_wallet_deposit_status(self, system_id,transaction_id: str) -> Dict[str, Any]:
        """查询充值状态
        
        Args:
            transaction_id: 交易ID
        """
        return self.make_gsalary_request("GET", f"/wallet/deposit/{transaction_id}", system_id=system_id)
    
    def get_wallet_withdraw_status(self, system_id,transaction_id: str) -> Dict[str, Any]:
        """查询提现状态
        
        Args:
            transaction_id: 交易ID
        """
        return self.make_gsalary_request("GET", f"/wallet/withdraw/{transaction_id}")

    # 账户操作 - 汇率
    def get_exchange_rate(self, system_id,from_currency: str, to_currency: str) -> Dict[str, Any]:
        """获取汇率信息
        
        Args:
            from_currency: 源货币代码
            to_currency: 目标货币代码
        """
        return self.make_gsalary_request("GET", f"/exchange/rate/{from_currency}/{to_currency}")
    
    def get_all_exchange_rates(self, system_id,base_currency: str) -> Dict[str, Any]:
        """获取所有汇率信息
        
        Args:
            base_currency: 基础货币代码
        """
        return self.make_gsalary_request("GET", f"/exchange/rates/{base_currency}")
    
    def get_exchange_history(self, system_id,from_currency: str, to_currency: str, 
                            start_date: str, end_date: str) -> Dict[str, Any]:
        """获取汇率历史
        
        Args:
            from_currency: 源货币代码
            to_currency: 目标货币代码
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
        """
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self.make_gsalary_request("GET", f"/exchange/history/{from_currency}/{to_currency}", system_id=system_id, params=params)

    # 卡片操作 - 持卡人
    def create_card_holder(self, system_id,data: Dict) -> Dict[str, Any]:
        """创建持卡人
        
        Args:
            data: 持卡人信息，包含姓名、地址、联系方式等
        
        """
        return self.make_gsalary_request("POST", "/v1/card_holders",system_id, data)

    
    def get_card_holders(self, system_id,params: Optional[dict] = None) -> Dict[str, Any]:
        """获取持卡人列表
        Args:
            card_holder_id: 指定持卡人编号
        """
        return self.make_gsalary_request("GET", "/v1/card_holders", system_id=system_id, params=params)

    def update_card_holder(self, system_id, holder_id: str, data: Dict) -> Dict[str, Any]:
        """更新持卡人信息
        
        Args:
            holder_id: 持卡人ID
            data: 需要更新的持卡人信息
        """
        return self.make_gsalary_request("PUT", f"/v1/card_holders/{holder_id}",system_id, data)
    
    def delete_card_holder(self, system_id,holder_id: str) -> Dict[str, Any]:
        """删除持卡人
        
        Args:
            holder_id: 持卡人ID
        """
        return self.make_gsalary_request("DELETE", f"/card-holders/{holder_id}")

    # 卡片操作 - 卡片
    def get_card_quota(self, system_id,card_id: str) -> Dict[str, Any]:
        """获取卡片可用额度
        
        Args:
            card_id: 卡片ID
        """
        return self.make_gsalary_request("GET", f"/cards/{card_id}/quota")

    def get_product_codes(self, system_id) -> Dict[str, Any]:
        """获取可用产品代码列表"""
        return self.make_gsalary_request("GET", "/v1/card_support/products",system_id)

    def apply_new_card(self, system_id,data: Dict) -> Dict[str, Any]:
        """申请新卡
        
        Args:
            data: 申请信息，包含持卡人ID、产品代码等
        """
        return self.make_gsalary_request("POST", "/cards/apply", data)
    
    def batch_apply_cards(self, system_id,data: Dict) -> Dict[str, Any]:
        """批量申请新卡
        
        Args:
            data: 批量申请信息，包含持卡人ID列表、产品代码等
        """
        return self.make_gsalary_request("POST", "/cards/batch-apply", data)

    def get_card_apply_result(self, system_id,apply_id: str) -> Dict[str, Any]:
        """查询新卡申请结果
        
        Args:
            apply_id: 申请ID
        """
        return self.make_gsalary_request("GET", f"/cards/apply/{apply_id}")
    
    def get_batch_apply_result(self, system_id,batch_id: str) -> Dict[str, Any]:
        """查询批量申请结果
        
        Args:
            batch_id: 批量申请ID
        """
        return self.make_gsalary_request("GET", f"/cards/batch-apply/{batch_id}")

    def query_cards(self, system_id,params: Optional[dict] = None) -> Dict[str, Any]:
        """查询卡片列表
        
        Args:
            params: 查询参数，可包含持卡人ID、状态等
        """
        return self.make_gsalary_request("GET", "/v1/cards", system_id=system_id, params=params)
    
    def query_cards_info(self, system_id,card_id: str) -> Dict[str, Any]:
        """查询卡片信息     
        Args:
            card_id: 卡片ID,用于查询卡片更详细的信息
        """
        return self.make_gsalary_request("GET", f"/v1/cards/{card_id}", system_id=system_id)


    def modify_card(self, system_id,card_id: str, data: Dict) -> Dict[str, Any]:
        """修改卡片信息
        
        Args:
            card_id: 卡片ID
            data: 需要修改的卡片信息
        """
        return self.make_gsalary_request("PUT", f"/v1/cards/{card_id}", system_id=system_id, data = data)

    def cancel_card(self, system_id,card_id: str) -> Dict[str, Any]:
        """注销卡片
        
        Args:
            card_id: 卡片ID
        """
        return self.make_gsalary_request("DELETE", f"/v1/cards/{card_id}",system_id=system_id)


    def get_card_secure_info(self, system_id,card_id: str) -> Dict[str, Any]:
        """获取卡片安全信息
        
        Args:
            card_id: 卡片ID
        """
        return self.make_gsalary_request("GET", f"/v1/cards/{card_id}/secure_info",system_id=system_id)

    def modify_card_balance(self, system_id, data: Dict) -> Dict[str, Any]:
        """修改卡片余额
        
        Args:
            card_id: 卡片ID
            data: 余额修改信息，包含金额、币种、描述等
        """
        return self.make_gsalary_request("POST", f"/v1/cards/balance_modifies", system_id=system_id, data = data)
    
    def batch_modify_balance(self, system_id,data: Dict) -> Dict[str, Any]:
        """批量修改卡片余额
        
        Args:
            data: 包含卡片ID列表、金额等信息
        """
        return self.make_gsalary_request("POST", "/cards/batch-balance", data)

    def check_balance_modify_status(self, system_id,operation_id: str) -> Dict[str, Any]:
        """检查余额修改状态
        
        Args:
            operation_id: 操作ID
        """
        return self.make_gsalary_request("GET", f"/cards/balance/{operation_id}")
    
    def check_batch_balance_status(self, system_id,batch_id: str) -> Dict[str, Any]:
        """检查批量余额修改状态
        
        Args:
            batch_id: 批量操作ID
        """
        return self.make_gsalary_request("GET", f"/cards/batch-balance/{batch_id}")

    def freeze_unfreeze_card(self, system_id,card_id: str, data: Dict) -> Dict[str, Any]:
        """冻结/解冻卡片
        
        Args:
            card_id: 卡片ID
            freeze: True表示冻结，False表示解冻
        """
        # action = "freeze" if freeze else "unfreeze"
        return self.make_gsalary_request("PUT", f"/v1/cards/{card_id}/freeze_status",system_id=system_id,data=data)


    def get_card_transactions(self, system_id, params: Optional[Dict] = None) -> Dict[str, Any]:
        """获取卡片交易记录
        
        Args:
            card_id: 卡片ID
            params: 查询参数，可包含日期范围、交易类型等
        """
        return self.make_gsalary_request("GET", "/v1/card_bill/card_transactions", system_id=system_id, params=params)

    def get_card_balance_history(self, system_id, params: Optional[Dict] = None) -> Dict[str, Any]:
        """获取卡片余额历史
        
        Args:
            card_id: 卡片ID
            params: 查询参数，可包含日期范围等
        """
        return self.make_gsalary_request("GET", "/v1/card_bill/balance_history", system_id=system_id, params=params)

    def modify_card_contact(self, system_id,card_id: str, data: Dict) -> Dict[str, Any]:
        """修改卡片联系信息
        
        Args:
            card_id: 卡片ID
            data: 联系信息，可包含电话、邮箱等
        """
        return self.make_gsalary_request("PUT", f"/cards/{card_id}/contact", data)

    def delete_card_email(self, system_id,card_id: str, email: str) -> Dict[str, Any]:
        """删除卡片邮箱
        
        Args:
            card_id: 卡片ID
            email: 要删除的邮箱地址
        """
        return self.make_gsalary_request("DELETE", f"/cards/{card_id}/email/{email}")
    
    def add_card_email(self, system_id,card_id: str, email: str) -> Dict[str, Any]:
        """添加卡片邮箱
        
        Args:
            card_id: 卡片ID
            email: 要添加的邮箱地址
        """
        return self.make_gsalary_request("POST", f"/cards/{card_id}/email", {"email": email})
    
    def verify_card_email(self, system_id,card_id: str, email: str, code: str) -> Dict[str, Any]:
        """验证卡片邮箱
        
        Args:
            card_id: 卡片ID
            email: 邮箱地址
            code: 验证码
        """
        return self.make_gsalary_request("POST", f"/cards/{card_id}/email/verify", {"email": email, "code": code})

    # 付款操作 - 收款人
    def create_payee(self, system_id,data: Dict) -> Dict[str, Any]:
        """创建收款人
        
        Args:
            data: 收款人信息，包含姓名、银行账户等
        """
        return self.make_gsalary_request("POST", "/payees", data)
    
    def create_batch_payees(self, system_id,data: Dict) -> Dict[str, Any]:
        """批量创建收款人
        
        Args:
            data: 包含多个收款人信息的列表
        """
        return self.make_gsalary_request("POST", "/payees/batch", data)

    def get_payee(self, system_id,payee_id: str) -> Dict[str, Any]:
        """获取收款人信息
        
        Args:
            payee_id: 收款人ID
        """
        return self.make_gsalary_request("GET", f"/payees/{payee_id}")
    
    # 查询收款人列表
    def get_payees(self, system_id,params: Optional[Dict] = None) -> Dict[str, Any]:
        """获取收款人列表
        
        Args:
            params: 查询参数，可包含页码等
        """
        return self.make_gsalary_request("GET", "/v1/remittance/payees", system_id=system_id)

    # 查询可用的付款方式
    def get_available_payment_methods(self, system_id, ) -> Dict[str, Any]:
        """获取可用付款方式列表"""
        return self.make_gsalary_request("GET", "/v1/remittance/available_payment_methods", system_id=system_id)
    
    # 查看收款人的可用收款账户
    def get_payee_accounts(self, system_id,payee_id: str) -> Dict[str, Any]:
        """获取收款人可用账户列表
        
        Args:
            payee_id: 收款人ID
        """
        return self.make_gsalary_request("GET", f"/v1/remittance/payees/{payee_id}/accounts", system_id=system_id)
    
    # 获取收款人账户表单
    def get_payee_account_form(self, system_id, payee_id: str, data:Dict) -> Dict[str, Any]:
        """获取收款人账户表单
        Args:
            payee_id: 收款人ID
        """
        return self.make_gsalary_request("GET", f"/v1/remittance/payees/{payee_id}/account_register_format", system_id=system_id, data=data)
    
    def update_payee(self, system_id,payee_id: str, data: Dict) -> Dict[str, Any]:
        """更新收款人信息
        
        Args:
            payee_id: 收款人ID
            data: 需要更新的信息
        """
        return self.make_gsalary_request("PUT", f"/payees/{payee_id}", data)
    
    def delete_payee(self, system_id,payee_id: str) -> Dict[str, Any]:
        """删除收款人
        
        Args:
            payee_id: 收款人ID
        """
        return self.make_gsalary_request("DELETE", f"/payees/{payee_id}")

    # 付款操作 - 付款人
    def create_payer(self, system_id,data: Dict) -> Dict[str, Any]:
        """创建付款人
        
        Args:
            data: 付款人信息
        """
        return self.make_gsalary_request("POST", "/payers", data)
    
    def create_batch_payers(self, system_id,data: Dict) -> Dict[str, Any]:
        """批量创建付款人
        
        Args:
            data: 包含多个付款人信息的列表
        """
        return self.make_gsalary_request("POST", "/payers/batch", data)

    def get_payer(self, system_id,payer_id: str) -> Dict[str, Any]:
        """获取付款人信息
        
        Args:
            payer_id: 付款人ID
        """
        return self.make_gsalary_request("GET", f"/payers/{payer_id}")
    
    def get_payers(self, system_id,params: Optional[Dict] = None) -> Dict[str, Any]:
        """获取付款人列表
        
        Args:
            params: 查询参数
        """
        return self.make_gsalary_request("GET", "/payers", system_id=system_id, params=params)
    
    def update_payer(self, system_id,payer_id: str, data: Dict) -> Dict[str, Any]:
        """更新付款人信息
        
        Args:
            payer_id: 付款人ID
            data: 需要更新的信息
        """
        return self.make_gsalary_request("PUT", f"/payers/{payer_id}", data)
    
    def delete_payer(self, system_id,payer_id: str) -> Dict[str, Any]:
        """删除付款人
        
        Args:
            payer_id: 付款人ID
        """
        return self.make_gsalary_request("DELETE", f"/payers/{payer_id}")

    # 付款操作 - 汇款
    def create_remittance(self, system_id,data: Dict) -> Dict[str, Any]:
        """创建汇款
        
        Args:
            data: 汇款信息，包含付款人、收款人、金额等
        """
        return self.make_gsalary_request("POST", "/remittances", data)
    
    def create_batch_remittances(self, system_id,data: Dict) -> Dict[str, Any]:
        """批量创建汇款
        
        Args:
            data: 包含多个汇款信息的列表
        """
        return self.make_gsalary_request("POST", "/remittances/batch", data)

    def get_remittance_status(self, system_id,remittance_id: str) -> Dict[str, Any]:
        """获取汇款状态
        
        Args:
            remittance_id: 汇款ID
        """
        return self.make_gsalary_request("GET", f"/remittances/{remittance_id}")
    
    def get_batch_remittance_status(self, system_id,batch_id: str) -> Dict[str, Any]:
        """获取批量汇款状态
        
        Args:
            batch_id: 批量汇款ID
        """
        return self.make_gsalary_request("GET", f"/remittances/batch/{batch_id}")
    
    def get_remittances(self, system_id,params: Optional[Dict] = None) -> Dict[str, Any]:
        """获取汇款列表
        
        Args:
            params: 查询参数，可包含日期范围、状态等
        """
        return self.make_gsalary_request("GET", "/remittances", system_id=system_id, params=params)
    
    def cancel_remittance(self, system_id,remittance_id: str) -> Dict[str, Any]:
        """取消汇款
        
        Args:
            remittance_id: 汇款ID
        """
        return self.make_gsalary_request("DELETE", f"/remittances/{remittance_id}")

    # Webhook操作
    def register_webhook(self, system_id,data: Dict) -> Dict[str, Any]:
        """注册Webhook
        
        Args:
            data: Webhook信息，包含URL、事件类型等
        """
        return self.make_gsalary_request("POST", "/webhooks", data)

    def get_webhook_list(self) -> Dict[str, Any]:
        """获取Webhook列表"""
        return self.make_gsalary_request("GET", "/webhooks")
    
    def get_webhook(self, system_id,webhook_id: str) -> Dict[str, Any]:
        """获取特定Webhook详情
        
        Args:
            webhook_id: Webhook ID
        """
        return self.make_gsalary_request("GET", f"/webhooks/{webhook_id}")
    
    def update_webhook(self, system_id,webhook_id: str, data: Dict) -> Dict[str, Any]:
        """更新Webhook
        
        Args:
            webhook_id: Webhook ID
            data: 需要更新的Webhook信息
        """
        return self.make_gsalary_request("PUT", f"/webhooks/{webhook_id}", data)

    def delete_webhook(self, system_id,webhook_id: str) -> Dict[str, Any]:
        """删除Webhook
        
        Args:
            webhook_id: Webhook ID
        """
        return self.make_gsalary_request("DELETE", f"/webhooks/{webhook_id}")
    
    def test_webhook(self, system_id,webhook_id: str, event_type: str) -> Dict[str, Any]:
        """测试Webhook
        
        Args:
            webhook_id: Webhook ID
            event_type: 事件类型
        """
        return self.make_gsalary_request("POST", f"/webhooks/{webhook_id}/test", {"event_type": event_type})
    
    def get_webhook_events(self) -> Dict[str, Any]:
        """获取所有支持的Webhook事件类型"""
        return self.make_gsalary_request("GET", "/webhooks/events")
    
    def get_webhook_logs(self, system_id,webhook_id: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """获取Webhook调用日志
        
        Args:
            webhook_id: Webhook ID
            params: 查询参数，如日期范围
        """
        return self.make_gsalary_request("GET", f"/webhooks/{webhook_id}/logs", system_id=system_id, params=params)
