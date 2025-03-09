'''
    1.此文件用于处理菜单选择,由于菜单属于回复按钮,处理回复消息
'''

from telegram import Update
from telegram.ext import ContextTypes
from utils.language import get_text
from utils.logging import logger
from .transactions import handle_transaction_history
from .balance import handle_balance_history
from .unbind import handle_unbind

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理菜单选择"""
    user_id = update.effective_user.id
    text = update.message.text
    
    try:
        if text == get_text(user_id, 'transaction_prompt'):
            # 处理查询交易明细
            await handle_transaction_history(update, context)
        elif text == get_text(user_id, 'balance_prompt'):
            # 处理查询余额明细
            await handle_balance_history(update, context)
        elif text == '查看报价':
            pass
        elif text == get_text(user_id, 'unbind'):
            # 处理解除绑定
            await handle_unbind(update, context)
        logger.info(f"Menu selection '{text}' handled for user {user_id}")
    except Exception as e:
        logger.error(f"Error handling menu selection for user {user_id}: {str(e)}")
        await update.message.reply_text("An error occurred. Please try again.") 