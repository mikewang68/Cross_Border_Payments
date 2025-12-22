'''
    1.此文件存放ui设置,即各种各种的键盘样式
    2.language_selection_keyboard: 
        在执行start命令后,弹出四种语言选择按钮
    3.confirm_language_selection: 
        用户选择完语言后,进入一步确认操作
    4.after_language_selection: 
        用户确定选择的语言后,可进行绑卡操作
    5.binding_email_keyboard: 
        在用户输入邮箱无效、邮箱未注册、验证码错误时,用于返回after_language_selection
    6.main_menu_keyboard: 
        用户绑卡成功后,弹出回复按钮菜单
    7.combined_keyboard: 
        用户选择查看交易记录或者余额记录时用于翻页
'''

from telegram import (
    Update,
    InlineKeyboardButton, 
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes,
    CallbackContext
)
from utils.language import get_text

async def language_selection_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    "语言选择,内嵌键盘"
    inline_keyboard = [
        [
            InlineKeyboardButton('English', callback_data="language_en_button"),
            InlineKeyboardButton('日本語', callback_data="language_jp_button")
        ],
        [
            InlineKeyboardButton('简体中文', callback_data='language_zhcn_button'),
            InlineKeyboardButton('繁體中文', callback_data='language_zhtw_button')
        ]
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)

    # query = update.callback_query
    # print('..................................')
    # print(query)

    if  update.callback_query == None:
        await update.message.reply_text(
            "Please select your language / 言語を選択してください / 请选择语言:",
            reply_markup=inline_markup
        )
    else:
        await update.callback_query.edit_message_text(
            "Please select your language / 言語を選択してください / 请选择语言:",
            reply_markup=inline_markup
        )

    

async def confirm_language_selection(update: Update, context: CallbackContext, user_id):
    # 创建新的按钮布局
    # print('confirm_language_selection:' + 'before')
    query = update.callback_query
    # print('confirm_language_selection:' + 'after')
    new_keyboard = [
        [
            InlineKeyboardButton("⬅️", callback_data="back_language_select"),
            InlineKeyboardButton("➡️", callback_data="proceed")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(new_keyboard)
    await query.edit_message_text(
        get_text(user_id, 'confirm_language_selection') + 
        '\n \n' +
        'Change language, click⬅️\n' + 
        '言語を変更して、クリックします⬅️\n'+
        '更换语言，点击⬅️\n',
        reply_markup = reply_markup
    )


async def after_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    "选择语言后跳出的内嵌按钮"
    # print('after_language_selection' + '已进入')
    inline_keyboard = [
        [
            InlineKeyboardButton( get_text(user_id, 'InlineKeyboardButton_loginsearch'), callback_data="login_button"),
            # InlineKeyboardButton( get_text(user_id, 'InlineKeyboardButton_help'), callback_data="help_button")
        ],
        # [InlineKeyboardButton(get_text(user_id, 'InlineKeyboardButton_url'), url='https://example.com')],
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    # 最后发送内联键盘按钮
    # await update.message.reply_text("菜单选项如下：\n"+
    #                                 "登录查询ℹ️ - 登录后查询交易余额记录\n" +
    #                                 "帮助🔭 - 本机器人的应用方向\n" + 
    #                                 "访问网址🔗 - 官网地址,供您使用\n" 
    # , reply_markup=inline_markup)
    await update.callback_query.edit_message_text(
        get_text(user_id, 'after_language_selection_menu'), 
        reply_markup=inline_markup
    )

'''
    2.16 增加 by mwh
'''
async def binding_email_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    failed_email_keyboard = [
        [
            InlineKeyboardButton(get_text(user_id, 'back_bind'),callback_data='failed_after_language_selection')
        ] 
    ]
    # inline_verification_keyboard = [
    #     [
    #         InlineKeyboardButton('放弃绑定，返回菜单',callback_data='verification_after_language_selection')
    #     ]
    # ]
    failed_email_keyboard = InlineKeyboardMarkup(failed_email_keyboard)
    # inline_verification_mark = InlineKeyboardMarkup(inline_verification_keyboard)
    if context.user_data['invalid_email'] == True:
        await update.message.reply_text(
            get_text(user_id, 'invalid_email'),
            reply_markup=failed_email_keyboard
        )
    elif context.user_data['invalid_email'] == False:
        await update.message.reply_text(
            get_text(user_id, 'verification_fail'),
            reply_markup=failed_email_keyboard
        )
    elif context.user_data['waiting_for_verification'] == True:
        context.user_data['waiting_for_verification'] == False
        await update.message.reply_text(
            get_text(user_id, 'verification_fail'),
            reply_markup=failed_email_keyboard
        )
    else:
        return



def main_menu_keyboard(user_id: int):
    """主菜单键盘"""
    return ReplyKeyboardMarkup([
        [
            KeyboardButton(get_text(user_id, 'transaction_prompt')),
            KeyboardButton(get_text(user_id, 'balance_prompt'))
        ],
        [
            KeyboardButton(get_text(user_id, 'unbind'))
        ]
    ], resize_keyboard=True)


def combined_keyboard(user_id: int, current_page: int, total_pages: int, data_type: str):
    """组合键盘（Inline分页 + 主菜单）"""
    # 创建 Inline 分页按钮
    inline_buttons = []
    if current_page > 1:
        inline_buttons.append(
            InlineKeyboardButton(
                get_text(user_id, 'prev_page'),  # "← Back"
                callback_data=f"{data_type}_page_{current_page-1}"
            )
        )
    if current_page < total_pages:
        inline_buttons.append(
            InlineKeyboardButton(
                get_text(user_id, 'next_page'),  # "Next →"
                callback_data=f"{data_type}_page_{current_page+1}"
            )
        )
    
    inline_keyboard = []
    if inline_buttons:
        inline_keyboard.append(inline_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard)

