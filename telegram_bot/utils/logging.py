'''
    1.此文件用于记录日志,logger配置在大多数文件中,用于在控制台查看程序运行的过程,给予反馈
'''

import logging

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    return logging.getLogger(__name__)

logger = setup_logging() 