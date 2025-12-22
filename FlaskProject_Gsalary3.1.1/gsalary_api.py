'''
实体卡接口
'''

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
    data = query_database('system_key', {'system':system_id,})

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
    data = query_database('system_key', {'system':system_id,})

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
            body_hash_str = base64.b64encode(
                hashlib.sha256(json_str.encode('utf-8')).digest())
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
            return response.json()
        except Exception as err:
            logger.error(f"Other error occurred: {err}")
            return response.json()

    def assign_card (self, system_id,data: Dict) -> Dict[str, Any]:
        """分配实体卡

        Args:
            data: card_number、card_holder_id、card_currency
        """
        return self.make_gsalary_request("POST", "/v1/cards/assign_card", system_id=system_id, data=data)

    def active_card (self, system_id, card_id,data: Dict) -> Dict[str, Any]:
        """激活实体卡

        Args:
            card_id: 卡片ID
            data: 卡的激活码、卡的新PIN(必须是6位数字)、无需PIN验证的卡交易的允许金额(默认值为200USD,可以为0)
        """
        return self.make_gsalary_request("POST", f"/v1/cards/{card_id}/active_card", system_id=system_id, data=data)

