from telegram import Update
from telegram.ext import ContextTypes
from utils.logging import logger
import re 
from utils.api import post_request
from utils.language import get_text
from ui.keyboards import main_menu_keyboard, binding_email_keyboard

async def check_login_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''检查用户的登录状态'''
    telegram_id = update.effective_user.id

    logger.info(f"Checking login status for user {telegram_id}")
    data, status = await post_request("/check/login", {'telegram_id': telegram_id})

    print(f"API Response Status Code: {status}")
    print(f"API Response Content: {data}")

    if status == 200:
        user_login = data.get('data', {}).get('user_login', "0")
        print(user_login)
        logger.info(f"User {telegram_id} login status: {user_login}")

        if user_login == "0":
            logger.info(f"User {telegram_id} not logged in, prompting for email")
            context.user_data['waiting_for_email'] = False
            await prompt_email(update, context)
        else:
            # 如果用户保留了一个绑卡按钮没执行,又通过start完成绑卡操作后,用户点击之前保留的按钮,存在逻辑冲突,故在此添加操作
            logger.info(f"User {telegram_id} already logged in, showing main menu")
            await update.callback_query.edit_message_text(
                get_text(telegram_id, 'login_persistence')
            )
            await show_main_menu(update, context)
    else:
        logger.error(f"Failed to check login status for user {telegram_id}")
        await prompt_email(update, context)

async def prompt_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """提示用户输入邮箱"""
    '''
        2.14 修改 by mwh
        获取内嵌按钮的callback_query,用户点击登录查询按钮后验证登录状态，进行提示输入邮箱
    '''
    # print(update.message) 
    # print(update.callback_query.message)
    message = update.callback_query.message
    user_id = update.callback_query.from_user.id
    try:
        if update.callback_query:
            logger.info(f"User {user_id} not logged in, prompting for email")
        else:
            return 
    except Exception as e:
        logger.error(f"Error in prompt_email: {str(e)}")
        await message.reply_text("An error occurred when clicking the button.") 

    
    await update.callback_query.edit_message_text(get_text(user_id, 'email_prompt'))
    # await binding_email_keyboard(update, context, user_id)

    context.user_data['waiting_for_email'] = True


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示主菜单"""
    user_id = update.effective_user.id
    await update.message.reply_text(
        get_text(user_id, 'login_success'),
        # 登录成功获取主功能界面，可进行查询数据操作
        reply_markup=main_menu_keyboard(user_id)
    ) 



async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
        1.此函数用于处理用户输入邮箱的格式:
            如果格式正确想邮箱发送请求获取数据和状态，否则重试

    '''
    if not context.user_data.get('waiting_for_email'):
        return
        
    email = update.message.text
    user_id = update.effective_user.id
    
    context.user_data['invalid_email'] = False
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        context.user_data['invalid_email'] = True

        await binding_email_keyboard(update, context, user_id)
        
        # await update.message.reply_text(get_text(user_id, 'invalid_email'))
        # await prompt_email(update, context)
        return
    
    data, status = await post_request("/send/email", {'email': email})
    
    if status == 200:
        context.user_data['email'] = email
        context.user_data['waiting_for_email'] = False
        context.user_data['waiting_for_verification'] = True
        
        # await binding_email_keyboard(update, context, user_id)
        await update.message.reply_text(get_text(user_id, 'verification_sent'))
    else:
        # 发送验证码失败，请重试。
        '''
            2.16 修改 by mwh
        '''
        await binding_email_keyboard(update, context, user_id)
        # await update.message.reply_text(get_text(user_id, 'verification_fail'))
        # await prompt_email(update, context)

async def handle_verification_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理验证码输入"""
    if not context.user_data.get('waiting_for_verification'):
        return
        
    verification_code = update.message.text
    telegram_id = update.effective_user.id
    email = context.user_data.get('email')
    user_id = update.effective_user.id
    
    data, status = await post_request("/check/key", {
        'email': email,
        'key': verification_code,
        'telegram_id': telegram_id
    })
    
    print(f"Verification API Response Status: {status}")
    print(f"Verification API Response Content: {data}")

    if status == 200:
        context.user_data['waiting_for_verification'] = False
        await show_main_menu(update, context)
    else:
        await binding_email_keyboard(update, context, user_id)
        # await update.message.reply_text(get_text(user_id, 'verification_error'))
        # await prompt_email(update, context)