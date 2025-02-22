from telegram import Update
from telegram.ext import ContextTypes
from utils.language import get_text
from utils.logging import logger
from handlers.login import handle_email, handle_verification_code
from handlers.transactions import handle_transaction_history
from handlers.balance import handle_balance_history
from handlers.unbind import handle_unbind

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理所有消息"""
    text = update.message.text
    user_id = update.effective_user.id
    
    try:
        if context.user_data.get('waiting_for_email'):
            await handle_email(update, context)
        elif context.user_data.get('waiting_for_verification'):
            await handle_verification_code(update, context)
        elif text == get_text(user_id, 'transaction_prompt'):
            context.user_data['transaction_page'] = 1
            context.user_data['viewing_transaction'] = True
            context.user_data['viewing_balance'] = False
            await handle_transaction_history(update, context)
        elif text == get_text(user_id, 'balance_prompt'):
            context.user_data['balance_page'] = 1
            context.user_data['viewing_balance'] = True
            context.user_data['viewing_transaction'] = False
            await handle_balance_history(update, context)
        elif text == get_text(user_id, 'next_page'):
            if context.user_data.get('viewing_transaction'):
                context.user_data['transaction_page'] = context.user_data.get('transaction_page', 1) + 1
                await handle_transaction_history(update, context)
            elif context.user_data.get('viewing_balance'):
                context.user_data['balance_page'] = context.user_data.get('balance_page', 1) + 1
                await handle_balance_history(update, context)
        elif text == get_text(user_id, 'prev_page'):
            if context.user_data.get('viewing_transaction'):
                context.user_data['transaction_page'] = max(1, context.user_data.get('transaction_page', 1) - 1)
                await handle_transaction_history(update, context)
            elif context.user_data.get('viewing_balance'):
                context.user_data['balance_page'] = max(1, context.user_data.get('balance_page', 1) - 1)
                await handle_balance_history(update, context)
        elif text == get_text(user_id, 'unbind'):
            await handle_unbind(update, context)
        else:
            await update.message.reply_text(get_text(user_id, 'click_start'))
            
        logger.info(f"Message '{text}' handled for user {user_id}")
    except Exception as e:
        logger.error(f"Error handling message for user {user_id}: {str(e)}")
        await update.message.reply_text("An error occurred. Please try again.")
