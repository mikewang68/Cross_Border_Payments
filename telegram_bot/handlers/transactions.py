'''
    1.此文件通过api获取后端返回的用户交易记录信息
    2.handle_transaction_history
        post api,获取到返回的json数据
    3.display_transaction_history
        显示规范化的数据
    4.display_transaction_history
        解析json数据

'''

from telegram import Update
from telegram.ext import ContextTypes

from utils.language import get_text
from utils.api import post_request
from ui.keyboards import main_menu_keyboard, combined_keyboard
from utils.language import user_language

ITEMS_PER_PAGE = 2

# 添加业务类型映射
BIZ_TYPE_MAP = {
    'en': {
        'AUTH': 'Payment',
        'CORRECTIVE_AUTH': 'Payment Correction',
        'VERIFICATION': 'Verification',
        'VOID': 'Void',
        'REFUND': 'Refund',
        'SETTLE': 'Settlement',
        'CORRECTIVE_REFUND': 'Refund Correction',
        'CORRECTIVE_REFUND_VOID': 'Refund Correction Void',
        'REFUND_REVERSAL': 'Refund Reversal',
        'SERVICE_FEE': 'Service Fee'
    },
    'jp': {
        'AUTH': '支払い',
        'CORRECTIVE_AUTH': '支払い修正',
        'VERIFICATION': '認証取引',
        'VOID': '取消',
        'REFUND': '返金',
        'SETTLE': '決済',
        'CORRECTIVE_REFUND': '返金修正',
        'CORRECTIVE_REFUND_VOID': '返金修正取消',
        'REFUND_REVERSAL': '返金取消',
        'SERVICE_FEE': 'サービス料'
    },
    'zh_cn': {
        'AUTH': '交易扣款',
        'CORRECTIVE_AUTH': '交易扣款修正',
        'VERIFICATION': '验证交易',
        'VOID': '交易撤单',
        'REFUND': '交易退款',
        'SETTLE': '交易结算',
        'CORRECTIVE_REFUND': '退款修正',
        'CORRECTIVE_REFUND_VOID': '退款修正取消',
        'REFUND_REVERSAL': '撤销退款',
        'SERVICE_FEE': '卡服务费'
    },
    'zh_tw': {
        'AUTH': '交易扣款',
        'CORRECTIVE_AUTH': '交易扣款修正',
        'VERIFICATION': '驗證交易',
        'VOID': '交易撤單',
        'REFUND': '交易退款',
        'SETTLE': '交易結算',
        'CORRECTIVE_REFUND': '退款修正',
        'CORRECTIVE_REFUND_VOID': '退款修正取消',
        'REFUND_REVERSAL': '撤銷退款',
        'SERVICE_FEE': '卡服務費'
    }
}

# 添加状态映射
STATUS_MAP = {
    'en': {
        'PENDING': 'Pending',
        'AUTHORIZED': 'Authorized',
        'SUCCEED': 'Successful',
        'FAILED': 'Failed',
        'VOID': 'Voided',
        'PROCESSING': 'Processing',
        'REJECTED': 'Rejected'
    },
    'jp': {
        'PENDING': '処理待ち',
        'AUTHORIZED': '承認済み',
        'SUCCEED': '成功',
        'FAILED': '失敗',
        'VOID': '取消済み',
        'PROCESSING': '処理中',
        'REJECTED': '拒否'
    },
    'zh_cn': {
        'PENDING': '待处理',
        'AUTHORIZED': '预鉴权',
        'SUCCEED': '交易成功',
        'FAILED': '交易失败',
        'VOID': '交易撤单',
        'PROCESSING': '处理中',
        'REJECTED': '已拒绝'
    },
    'zh_tw': {
        'PENDING': '待處理',
        'AUTHORIZED': '預鑑權',
        'SUCCEED': '交易成功',
        'FAILED': '交易失敗',
        'VOID': '交易撤單',
        'PROCESSING': '處理中',
        'REJECTED': '已拒絕'
    }
}

async def handle_transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理交易记录查询"""
    if isinstance(update, Update):
        message = update.message
        context.user_data['transaction_page'] = 1  # 重置页码
    else:
        message = update
        
    telegram_id = message.chat.id
    page = context.user_data.get('transaction_page', 1)
    
    data, status = await post_request(
        "/query/card/bill/transactions",
        {
            'telegram_id': telegram_id,
            'page': page,
            'limit': ITEMS_PER_PAGE
        }
    )
    
    if status == 200:
        await display_transaction_history(message, context, data)
    else:
        await message.reply_text(get_text(telegram_id, 'transaction_fail'))

async def display_transaction_history(message, context: ContextTypes.DEFAULT_TYPE, data: dict):
    """显示交易记录"""
    user_id = message.chat.id
    transactions = data.get('data', {}).get('transactions', [])
    total_pages = data.get('data', {}).get('total_page', 1)
    current_page = data.get('data', {}).get('page', 1)
    
    if not transactions:
        await message.reply_text(get_text(user_id, 'no_transactions'))
        return
    
    message_text = f"{get_text(user_id, 'transaction_page').format(current_page)}\n\n"
    
    for transaction in transactions:
        message_text += format_transaction(user_id, transaction)
    
    # 发送交易记录和 Inline 分页按钮
    await message.reply_text(
        message_text,
        reply_markup=combined_keyboard(user_id, current_page, total_pages, "trans")
    )
    
    # 发送主菜单
    await message.reply_text(
        get_text(user_id, 'select_operation'),
        reply_markup=main_menu_keyboard(user_id)
    )

def format_transaction(user_id: int, transaction: dict) -> str:
    """格式化单条交易记录"""
    
    lang = user_language.get(user_id, 'en')
    
    message = []
    message.append(f"{get_text(user_id, 'transaction_id')} {transaction.get('transaction_id', '')}")
    if transaction.get('origin_transaction_id'):
        message.append(f"{get_text(user_id, 'related_transaction_id')} {transaction.get('origin_transaction_id')}")
    
    message.append(f"{get_text(user_id, 'card_number')} {transaction.get('mask_card_number', '')}")
    message.append(f"{get_text(user_id, 'transaction_time')} {transaction.get('transaction_time', '')}")
    message.append(f"{get_text(user_id, 'confirmation_time')} {transaction.get('confirm_time', '')}")
    
    # 添加金额信息
    trans_amount = transaction.get('transaction_amount', {})
    acc_amount = transaction.get('accounting_amount', {})
    surcharge = transaction.get('surcharge', {})
    
    message.append(f"{get_text(user_id, 'transaction_amount')} {trans_amount.get('amount', '')} {trans_amount.get('currency', '')}")
    message.append(f"{get_text(user_id, 'accounting_amount')} {acc_amount.get('amount', '')} {acc_amount.get('currency', '')}")
    if surcharge.get('amount'):
        message.append(f"{get_text(user_id, 'surcharge_amount')} {surcharge.get('amount', '')} {surcharge.get('currency', '')}")
    
    # 添加商户信息
    message.append(f"{get_text(user_id, 'merchant_name')} {transaction.get('merchant_name', '')}")
    message.append(f"{get_text(user_id, 'merchant_region')} {transaction.get('merchant_region', '')}")
    
    # 添加业务类型和状态
    biz_type = transaction.get('biz_type', '')
    status = transaction.get('status', '')
    message.append(f"{get_text(user_id, 'business_type')} {BIZ_TYPE_MAP[lang].get(biz_type, biz_type)}")
    message.append(f"{get_text(user_id, 'transaction_status')} {STATUS_MAP[lang].get(status, status)}")
    
    if transaction.get('status_description'):
        message.append(f"{get_text(user_id, 'status_description')} {transaction.get('status_description')}")
    
    message.append(get_text(user_id, 'divider'))
    return "\n".join(message) + "\n\n" 