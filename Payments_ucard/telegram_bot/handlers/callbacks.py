from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.language import user_language
from utils.logging import logger
from handlers.login import check_login_status
from utils.api import post_request
from utils.language import get_text
from ui.keyboards import  confirm_language_selection, language_selection_keyboard, after_language_selection, combined_keyboard

ITEMS_PER_PAGE = 2

async def language_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
        215 增加 by mwh
        处理语言选择的callback_query
    '''
    query = update.callback_query
    user_id = update.effective_user.id
    # 调用 query.answer() 会立即清除这个动画，告知客户端“操作已收到，无需继续等待”。
    query.answer()

    # debug
    # print('handlers.callback:' + query.data)

    if query.data.startswith('language_'):
        if query.data == 'language_en_button':
            user_language[user_id] = 'en'
        elif query.data == 'language_jp_button':
            user_language[user_id] = 'jp'
        elif query.data == 'language_zhcn_button':
            user_language[user_id] = 'zh_cn'
        elif query.data == 'language_zhtw_button':
            user_language[user_id] = 'zh_tw' 
        
        await confirm_language_selection(update, context, user_id)

    # 处理重新选择
    elif query.data == "back_language_select":
        # 重新显示语言选择界面
        await language_selection_keyboard(update, context)

    # 处理继续操作
    elif query.data == "proceed":
        await after_language_selection(update, context, user_id)
 
    logger.info(f"User {user_id} selected language: {user_language[user_id]}")
    # await after_language_selection(update, context, user_id)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    
    # 进行的是绑卡操作,实则不是登录操作
    if query.data == "login_button":
        await check_login_status(update, context) 
    elif query.data == "about_button":
        await query.message.edit_text("这是一个示例机器人，用于演示按钮功能。")

async def binding_email_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    if query.data == "failed_after_language_selection":
        await after_language_selection(update, context, user_id) 
    elif query.data == "verification_after_language_selection":
        context.user_data['waiting_for_email'] = False
        await after_language_selection(update, context)

    
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理回调查询"""
    query = update.callback_query
    data = query.data
    message = query.message
    
    # 解析回调数据
    parts = data.split('_')
    if len(parts) != 3:
        return
    
    data_type, action, current_page = parts
    page = int(current_page)
    telegram_id = message.chat.id
    
    # 更新页码并获取新数据
    if data_type == "trans":
        # 获取新的交易记录
        data, status = await post_request(
            "/query/card/bill/transactions",
            {
                'telegram_id': telegram_id,
                'page': page,
                'limit': ITEMS_PER_PAGE
            }
        )
        
        if status == 200:
            transactions = data.get('data', {}).get('transactions', [])
            total_pages = data.get('data', {}).get('total_page', 1)
            current_page = data.get('data', {}).get('page', 1)
            
            # 构建新消息文本
            message_text = f"{get_text(telegram_id, 'transaction_page').format(current_page)}\n\n"
            for transaction in transactions:
                from .transactions import format_transaction
                message_text += format_transaction(telegram_id, transaction)
            
            # 更新消息
            await message.edit_text(
                message_text,
                reply_markup=combined_keyboard(telegram_id, current_page, total_pages, "trans")
            )
            
    elif data_type == "balance":
        # 获取新的余额记录
        data, status = await post_request(
            "/query/card/bill/balance_history",
            {
                'telegram_id': telegram_id,
                'page': page,
                'limit': ITEMS_PER_PAGE
            }
        )
        
        if status == 200:
            history = data.get('data', {}).get('history', [])
            total_pages = data.get('data', {}).get('total_page', 1)
            current_page = data.get('data', {}).get('page', 1)
            
            # 构建新消息文本
            message_text = f"{get_text(telegram_id, 'balance_page').format(current_page)}\n\n"
            for record in history:
                from .balance import format_balance_record
                message_text += format_balance_record(telegram_id, record)
            
            # 更新消息
            await message.edit_text(
                message_text,
                reply_markup=combined_keyboard(telegram_id, current_page, total_pages, "balance")
            )
    
    # 应答回调查询
    await query.answer() 

