'''
    1.此文件用于用户最后的解绑操作
    2.handle_unbind:
        用户点击解除绑定后,移除查询菜单,清空user_data中的数据
'''

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from utils.language import get_text
from utils.api import post_request

async def handle_unbind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理解除绑定"""
    telegram_id = update.effective_user.id
    
    data, status = await post_request(
        "/un_login",
        {'telegram_id': telegram_id}
    )
    
    if status == 200:
        await update.message.reply_text(
            get_text(telegram_id, 'unbind_success'),
            reply_markup = ReplyKeyboardRemove()
        )
        # 清除用户数据
        context.user_data.clear()
    else:
        await update.message.reply_text(get_text(telegram_id, 'unbind_fail')) 