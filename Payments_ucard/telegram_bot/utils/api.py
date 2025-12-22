'''
    1.此文件存放后端的api,用于和后端进行通信获取数据
    2.提供post_request方法,别的文件调用并传入endpoint,获取到相应的json数据
'''

import aiohttp
from utils.logging import logger
import asyncio
from typing import Tuple, Optional, Any


API_URL = "http://47.93.79.49:5001"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

async def post_request(endpoint: str, json_data: dict, retries: int = MAX_RETRIES) -> Tuple[Optional[Any], int]:
    """
    发送POST请求到API，支持重试机制
    
    Args:
        endpoint: API端点
        json_data: POST数据
        retries: 最大重试次数
        
    Returns:
        tuple: (响应数据, 状态码)
    """
    url = f"{API_URL}{endpoint}"
    attempt = 0
    
    while attempt < retries:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_data) as response:
                    data = await response.json()
                    return data, response.status
        except Exception as e:
            attempt += 1
            if attempt == retries:
                logger.error(f"API request failed after {retries} attempts: {str(e)}")
                return None, 500
            logger.warning(f"API request attempt {attempt} failed: {str(e)}")
            await asyncio.sleep(RETRY_DELAY) 