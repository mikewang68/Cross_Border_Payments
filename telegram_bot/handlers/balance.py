from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.language import get_text
from utils.api import post_request
from ui.keyboards import main_menu_keyboard, combined_keyboard

ITEMS_PER_PAGE = 2

async def handle_balance_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理余额记录查询"""
    if isinstance(update, Update):
        message = update.message
        context.user_data['balance_page'] = 1  # 重置页码
    else:
        message = update
        
    telegram_id = message.chat.id
    page = context.user_data.get('balance_page', 1)
    
    data, status = await post_request(
        "/query/card/bill/balance_history",
        {
            'telegram_id': telegram_id,
            'page': page,
            'limit': ITEMS_PER_PAGE
        }
    )
    
    if status == 200:
        await display_balance_history(message, context, data)
    else:
        await message.reply_text(get_text(telegram_id, 'balance_fail'))

async def display_balance_history(message, context: ContextTypes.DEFAULT_TYPE, data: dict):
    """显示余额记录"""
    user_id = message.chat.id
    history = data.get('data', {}).get('history', [])
    total_pages = data.get('data', {}).get('total_page', 1)
    current_page = data.get('data', {}).get('page', 1)
    
    if not history:
        await message.reply_text(get_text(user_id, 'no_balance_records'))
        return
    
    # 'balance_page': "余额记录（第 {} 页）："
    message_text = f"{get_text(user_id, 'balance_page').format(current_page)}\n\n"
    
    for record in history:
        message_text += format_balance_record(user_id, record)
    
    # 发送余额记录和 Inline 分页按钮
    await message.reply_text(
        message_text,
        reply_markup=combined_keyboard(user_id, current_page, total_pages, "balance")
    )
    
    # 发送主菜单
    await message.reply_text(
        get_text(user_id, 'select_operation'),
        reply_markup=main_menu_keyboard(user_id)
    )

def format_balance_record(user_id: int, record: dict) -> str:
    """格式化单条余额记录"""
    message = []
    message.append(f"{get_text(user_id, 'transaction_id')} {record.get('transaction_id', '')}")
    message.append(f"{get_text(user_id, 'card_number')} {record.get('mask_card_number', '')}")
    message.append(f"{get_text(user_id, 'transaction_time')} {record.get('transaction_time', '')}")
    message.append(f"{get_text(user_id, 'confirmation_time')} {record.get('confirm_time', '')}")
    
    amount = record.get('amount', {})
    balance = record.get('balance_after_transaction', {})
    message.append(f"{get_text(user_id, 'transaction_amount')} {amount.get('amount', '')} {amount.get('currency', '')}")
    message.append(f"{get_text(user_id, 'balance_after')} {balance.get('amount', '')} {balance.get('currency', '')}")
    
    message.append(get_text(user_id, 'divider'))
    return "\n".join(message) + "\n\n" 