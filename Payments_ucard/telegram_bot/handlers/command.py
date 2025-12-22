from telegram import Update
from telegram.ext import ContextTypes
from utils.logging import logger
from ui.keyboards import language_selection_keyboard
from utils.api import post_request
from utils.language import get_text

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
        215 修改 by mwh
            程序入口/start
            通过输入/start,弹出内嵌按钮选择语言文本

        218 增加 by mwh
            持久化验证，防止用户在绑卡状态下再次调用/start
    '''
    telegram_id = update.effective_user.id
    logger.info(f"Checking login status for user {telegram_id}")
    data, status = await post_request("/check/login", {'telegram_id': telegram_id})

    try:
        if data.get('data', {}).get('user_login', "0") == "1":
            user_id = update.effective_user.id    
            await update.message.reply_text(
                get_text(user_id, 'login_persistence')
            )
            return
        
        await language_selection_keyboard(update, context)
        logger.info(f"Start command received from user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await update.message.reply_text("An error occurred. Please try again.")