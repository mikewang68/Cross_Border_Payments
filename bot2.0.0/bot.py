from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from telegram.request import HTTPXRequest
import requests
import re

# 配置
# TOKEN = '7720717885:AAE2OkulcRjOvXMGn65H4s64NI0CSNhFR0U'
# API_URL = "http://8.213.144.235:5001"
TOKEN = '8386991105:AAFjfoaEzxqY-rlhpp2vt--NissyOyL-zfo'
API_URL = "http://62.234.37.216:5001"
PROXY = "http://127.0.0.1:7897"  # 改用 http 代理，端口号要根据你的实际代理软件设置
ITEMS_PER_PAGE = 5  # 每页显示5条数据

# 通过代理构建请求，以避免在受限网络下与 Telegram 连接超时
request = HTTPXRequest(proxy=PROXY)
app = Application.builder().token(TOKEN).request(request).build()
# 存储用户语言选择
user_language = {}
# 存储用户当前页码
user_page = {}


# 语言模板
language_templates = {
    'en': {
        'start': "Welcome to the U Card Bot! Please choose your language to begin.",
        'email_prompt': "Please enter your email to bind your U card:",
        'login_success': "Login successful! Please select an option below:",
        'transaction_prompt': "View Transaction History",
        'transaction_fail': "Failed to get transactions. Please try again later.",
        'transaction_page': "Transaction History (Page {}):",
        'transaction_time': "🕒 Transaction Time:",
        'transaction_id': "🆔 Transaction ID:",
        'related_transaction_id': "🔗 Related Transaction ID:",
        'confirmation_time': "⌚ Confirmation Time:",
        'transaction_amount': "💰 Transaction Amount:",
        'accounting_amount': "💵 Settlement Amount:",
        'surcharge_amount': "💸 Surcharge:",
        'merchant_name': "🏢 Merchant Name:",
        'merchant_region': "🌍 Merchant Region:",
        'business_type': "📝 Business Type:",
        'transaction_status': "✓ Transaction Status:",
        'status_description': "📋 Status Description:",
        'card_number': "💳 Card Number:",
        'balance_prompt': "View Balance History",
        'balance_fail': "Failed to get balance history. Please try again later.",
        'balance_page': "Balance History (Page {}):",
        'balance_after': "💰 Balance After:",
        'next_page': "Next →",
        'prev_page': "← Back",
        'choose_language': "Please select your language:",
        'invalid_email': "Invalid email format. Please try again.",
        'verification_sent': "Verification code has been sent to your email. Please enter the code:",
        'verification_fail': "Failed to send verification code. Please try again.",
        'verification_error': "Incorrect verification code. Please enter your email again:",
        'unbind_success': "Successfully unbound! Please use /start command to start using the bot.",
        'unbind_fail': "Failed to unbind. Please try again later.",
        'select_operation': "Please select an operation:",
        'no_transactions': "No transaction records found.",
        'no_balance_records': "No balance records found.",
        'unbind': "Unbind",
        'divider': "=" * 30,
        'activate':"activate a physical card",
        'waiting_for_pin_code':"Please input your pin(6-digit pure number, which will be used as your physical card password)",
        'active_prompt': "Please check your email and input your active code",
        'active_error':"Please correct your active code",
        'active_success':"Your card has been successfully activated",
        'assign_error': "Activation code sending failed, please contact the administrator",

    },
    'jp': {
        'start': "Uカードボットへようこそ！言語を選択してください。",
        'email_prompt': "Uカードをバインドするためにメールアドレスを入力してください:",
        'login_success': "ログイン成功！以下のオプションから選択してください:",
        'transaction_prompt': "取引履歴を表示",
        'transaction_fail': "取引履歴の取得に失敗しました。後でもう一度お試しください。",
        'transaction_page': "取引履歴（ページ {}）:",
        'transaction_time': "🕒 時間:",
        'amount_local': None,
        'amount_usd': None,
        'merchant': None,
        'status': None,
        'next_page': "次へ →",
        'prev_page': "← 戻る",
        'choose_language': "言語を選択してください:",
        'invalid_email': "メールアドレスの形式が無効です。もう一度お試しください。",
        'balance_prompt': "残高履歴を表示",
        'balance_fail': "残高履歴の取得に失敗しました。後でもう一度お試しください。",
        'balance_after': "💰 残高:",
        'card_number': "💳 カード番号:",
        'balance_page': "残高履歴（ページ {}）:",
        'verification_sent': "認証コードをメールに送信しました。コードを入力してください:",
        'verification_fail': "認証コードの送信に失敗しました。もう一度お試しください。",
        'verification_error': "認証コードが間違っています。メールアドレスを再入力してください:",
        'unbind_success': "バインド解除に成功しました！ /start コマンドでボットの使用を開始してください。",
        'unbind_fail': "バインド解除に失敗しました。後でもう一度お試しください。",
        'select_operation': "操作を選択してください:",
        'no_transactions': "取引記録が見つかりません。",
        'no_balance_records': "残高記録が見つかりません。",
        'unbind': "バインド解除",
        'business_type': "📝 取引種類:",
        'confirmation_time': "⌚ Confirmation Time:",
        'surcharge': None,
        'region': None,
        'status_description': "📋 Status Description:",
        'transaction_id': "🆔 取引ID:",
        'related_transaction_id': "🔗 関連取引ID:",
        'transaction_time': "🕒 取引時間:",
        'confirmation_time': "⌚ 決済時間:",
        'transaction_amount': "💰 取引金額:",
        'accounting_amount': "💵 決済金額:",
        'surcharge_amount': "💸 手数料:",
        'merchant_name': "🏢 加盟店名:",
        'merchant_region': "🌍 加盟店地域:",
        'transaction_status': "✓ 取引状態:",
        'status_description': "📋 状態詳細:",
        'card_number': "💳 カード番号:",
        'divider': "=" * 30,
        'activate':"実体カードを活性化する",
        "waiting_for_pin_code": "ピンコードを入力してください（6桁の数字だけで、これが実体カードのパスワードとなります）",
        "active_prompt": "メールを確認し、活性化コードを入力してください",
        "active_error": "活性化コードを修正してください",
        "active_success": "カードの活性化が正常に完了しました",
        "assign_error": "活性化コードの送信に失敗しました。管理者にご連絡ください"
    },
    'zh_cn': {
        'start': "欢迎使用 U Card Bot！请选择您的语言以开始。",
        'email_prompt': "请输入您的邮箱以绑定 U 卡：",
        'password_prompt': "请输入您的密码：",
        'login_success': "登录成功！请选择以下选项：",
        'login_fail': "密码错误。请重试。",
        'transaction_prompt': "查看交易记录",
        'transaction_fail': "获取交易记录失败。请稍后再试。",
        'Loading': "加载中...",
        'bind_first': "请先通过点击 /start 绑定您的 U 卡。",
        'click_start': "请点击 /start 开始。",
        'records_found': "找到 {} 条记录：",
        'transaction_page': "交易记录（第 {} 页）：",
        'transaction_time': "🕒 时间：",
        'amount_local': None,
        'amount_usd': None,
        'type': " 类型：",
        'status': None,
        'merchant': None,
        'region': None,
        'surcharge': None,
        'next_page': "下一页 →",
        'prev_page': "← 上一页",
        'choose_language': "请选择您的语言 / 言語を選択してください:",
        'invalid_email': "邮箱格式无效。请重试。",
        'balance_prompt': "查看余额记录",
        'balance_fail': "获取余额记录失败。请稍后再试。",
        'balance_result': "当前余额：{} 美元",
        'balance_after': "💰 余额:",
        'card_number': "💳 卡号：",
        'transaction_type': " 类型：",
        'business_type': "📝 业务类型:",
        'balance_page': "余额记录（第 {} 页）：",
        'verification_sent': "验证码已发送到您的邮箱，请输入验证码：",
        'verification_fail': "发送验证码失败，请重试。",
        'verification_error': "验证码错误，请重新输入邮箱：",
        'unbind_success': "解绑成功！请重新使用 /start 命令开始使用机器人。",
        'unbind_fail': "解绑失败，请稍后重试。",
        'select_operation': "请选择操作：",
        'no_transactions': "没有找到交易记录",
        'no_balance_records': "没有找到余额记录",
        'unbind': "解除绑定",
        'business_type': "📝 Business Type:",
        'confirmation_time': "⌚ Confirmation Time:",
        'surcharge': None,
        'region': None,
        'status_description': "📋 Status Description:",
        'transaction_id': "🆔 交易ID:",
        'related_transaction_id': "🔗 关联交易ID:",
        'transaction_time': "🕒 交易时间:",
        'confirmation_time': "⌚ 入账时间:",
        'transaction_amount': "💰 交易金额:",
        'accounting_amount': "💵 入账金额:",
        'surcharge_amount': "💸 手续费:",
        'merchant_name': "🏢 商户名称:",
        'merchant_region': "🌍 商户地区:",
        'transaction_status': "✓ 交易状态:",
        'status_description': "📋 状态描述:",
        'card_number': "💳 卡号:",
        'divider': "=" * 30,
        'activate': "激活实体卡",
        "waiting_for_pin_code": "请输入您的PIN码（6位纯数字，这将作为你的实体卡密码）",
        "active_prompt": "请查看您的邮件并输入激活码",
        "active_error": "请更正您的激活码",
        "active_success": "您的卡片已成功激活",
        "assign_error": "激活码发送失败，请联系管理员"
    },
    'zh_tw': {
        'start': "歡迎使用 U Card Bot！請選擇您的語言以開始。",
        'email_prompt': "請輸入您的電子郵件以綁定 U 卡：",
        'password_prompt': "請輸入您的密碼：",
        'login_success': "登入成功！請選擇以下選項：",
        'login_fail': "密碼錯誤。請重試。",
        'transaction_prompt': "查看交易記錄",
        'transaction_fail': "取得交易記錄失敗。請稍後再試。",
        'Loading': "載入中...",
        'bind_first': "請先通過點擊 /start 綁定您的 U 卡。",
        'click_start': "請點擊 /start 開始。",
        'records_found': "找到 {} 條記錄：",
        'transaction_page': "交易記錄（第 {} 頁）：",
        'transaction_time': "🕒 時間：",
        'amount_local': None,
        'amount_usd': None,
        'type': " 種類：",
        'status': None,
        'merchant': None,
        'region': None,
        'surcharge': None,
        'next_page': "下一頁 →",
        'prev_page': "← 上一頁",
        'choose_language': "請選擇您的語言 / 言語を選択してください:",
        'invalid_email': "電子郵件格式無效。請重試。",
        'balance_prompt': "查看餘額記錄",
        'balance_fail': "獲取餘額記錄失敗，請稍後重試",
        'balance_after': "💰 餘額:",
        'card_number': "💳 卡號:",
        'transaction_type': " 種類：",
        'business_type': "📝 業務類型:",
        'balance_page': "餘額記錄（第 {} 頁）：",
        'verification_sent': "驗證碼已發送到您的郵箱，請輸入驗證碼：",
        'verification_fail': "發送驗證碼失敗，請重試。",
        'verification_error': "驗證碼錯誤，請重新輸入郵箱：",
        'unbind_success': "解綁成功！請重新使用 /start 命令開始使用機器人。",
        'unbind_fail': "解綁失敗，請稍後重試。",
        'select_operation': "請選擇操作：",
        'no_transactions': "沒有找到交易記錄",
        'no_balance_records': "沒有找到餘額記錄",
        'unbind': "解除綁定",
        'business_type': "📝 Business Type:",
        'confirmation_time': "⌚ Confirmation Time:",
        'surcharge': None,
        'region': None,
        'status_description': "📋 Status Description:",
        'transaction_id': "🆔 交易ID:",
        'related_transaction_id': "🔗 關聯交易ID:",
        'transaction_time': "🕒 交易時間:",
        'confirmation_time': "⌚ 入賬時間:",
        'transaction_amount': "💰 交易金額:",
        'accounting_amount': "💵 入賬金額:",
        'surcharge_amount': "💸 手續費:",
        'merchant_name': "🏢 商戶名稱:",
        'merchant_region': "🌍 商戶地區:",
        'transaction_status': "✓ 交易狀態:",
        'status_description': "📋 狀態描述:",
        'card_number': "💳 卡號:",
        'divider': "=" * 30,
        'activate': "激活實體卡",
        "waiting_for_pin_code": "請輸入您的PIN碼（6位純數字，這將作為你的實體卡密碼）",
        "active_prompt": "請查看您的郵件並輸入激活碼",
        "active_error": "請更正您的激活碼",
        "active_success": "您的卡片已成功激活",
        "assign_error": "激活碼發送失敗，請聯繫管理員"
    }
}

def get_text(user_id, key):
    """获取对应语言的文本"""
    lang = user_language.get(user_id, 'en')
    return language_templates[lang][key]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理开始命令"""
    keyboard = [
        [KeyboardButton('English'), KeyboardButton('日本語')],
        [KeyboardButton('简体中文'), KeyboardButton('繁體中文')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please select your language / 言語を選択してください / 请选择语言:",
        reply_markup=reply_markup
    )

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理语言选择"""
    message_text = update.message.text
    language_map = {
        'English': 'en',
        '日本語': 'jp',
        '简体中文': 'zh_cn',
        '繁體中文': 'zh_tw'
    }
    
    if message_text not in language_map:
        return
    
    user_id = update.effective_user.id
    user_language[user_id] = language_map[message_text]
    
    # 检查用户登录状态
    await check_login_status(update, context)

async def check_login_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """检查用户登录状态"""
    telegram_id = update.effective_user.id
    response = requests.post(f"{API_URL}/check/login", json={'telegram_id': telegram_id})
    
    print(f"API Response Status Code: {response.status_code}")
    print(f"API Response Content: {response.text}")
    
    if response.status_code == 200:
        # 解析响应数据
        data = response.json()
        user_login = data.get('data', {}).get('user_login', "0")  # 获取字符串类型的 user_login
        print(f"User Login Status: {user_login}")
        
        if user_login == "0":  # 使用字符串比较
            print("User not logged in, prompting for email")
            # user_login 为 "0" 表示未登录状态，需要邮箱验证
            await prompt_email(update, context)
        else:
            print("User logged in, showing main menu")
            # user_login 不为 "0" 表示已登录状态，显示主菜单
            await show_main_menu(update, context)
    else:
        print(f"API request failed with status code: {response.status_code}")
        # API 请求失败，视为未登录状态
        await prompt_email(update, context)

async def prompt_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """提示用户输入邮箱"""
    user_id = update.effective_user.id
    await update.message.reply_text(get_text(user_id, 'email_prompt'))
    context.user_data['waiting_for_email'] = True

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理邮箱输入"""
    if not context.user_data.get('waiting_for_email'):
        return
        
    email = update.message.text
    user_id = update.effective_user.id
    
    # 打印日志
    print(f"Processing email input: {email}")
    
    # 验证邮箱格式
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print(f"Invalid email format: {email}")
        await update.message.reply_text(get_text(user_id, 'invalid_email'))
        await prompt_email(update, context)
        return
    
    # 发送验证邮件
    print(f"Sending verification email to: {email}")
    response = requests.post(
        f"{API_URL}/send/email",
        json={'email': email}
    )
    
    print(f"Email API Response Status: {response.status_code}")
    print(f"Email API Response Content: {response.text}")
    
    if response.status_code == 200:
        # 保存邮箱并等待验证码
        context.user_data['email'] = email
        context.user_data['waiting_for_email'] = False
        context.user_data['waiting_for_verification'] = True
        await update.message.reply_text(get_text(user_id, 'verification_sent'))
        print(f"Verification email sent successfully to: {email}")
    else:
        # 发送失败处理
        await update.message.reply_text(get_text(user_id, 'verification_fail'))
        await prompt_email(update, context)
        print(f"Failed to send verification email to: {email}")

async def handle_verification_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理验证码输入"""
    if not context.user_data.get('waiting_for_verification'):
        return
        
    verification_code = update.message.text
    telegram_id = update.effective_user.id
    email = context.user_data.get('email')
    user_id = update.effective_user.id
    
    # 打印日志
    print(f"Verifying code for email: {email}")
    print(f"Verification code received: {verification_code}")
    
    # 验证验证码
    response = requests.post(
        f"{API_URL}/check/key",
        json={
            'email': email,
            'key': verification_code,
            'telegram_id': telegram_id
        }
    )
    
    print(f"Verification API Response Status: {response.status_code}")
    print(f"Verification API Response Content: {response.text}")
    
    if response.status_code == 200:
        print("Verification successful")
        context.user_data['waiting_for_verification'] = False
        await show_main_menu(update, context)
    else:
        print("Verification failed")
        await update.message.reply_text(get_text(user_id, 'verification_error'))
        await prompt_email(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示主菜单"""
    user_id = update.effective_user.id
    keyboard = [
        [KeyboardButton(get_text(user_id, 'transaction_prompt')), 
         KeyboardButton(get_text(user_id, 'balance_prompt'))],
        [KeyboardButton(get_text(user_id, 'activate')),
         KeyboardButton(get_text(user_id, 'unbind'))],
        [KeyboardButton('/start')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text(user_id, 'login_success'),
        reply_markup=reply_markup
    )

async def handle_transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理交易明细查询"""
    telegram_id = update.effective_user.id
    page = context.user_data.get('transaction_page', 1)
    
    print(f"Fetching transaction history page {page}")  # 添加日志
    
    response = requests.post(
        f"{API_URL}/query/card/bill/transactions",
        json={
            'telegram_id': telegram_id,
            'page': page,
            'limit': ITEMS_PER_PAGE
        }
    )
    
    print(f"Transaction API Response: {response.text}")  # 添加日志
    
    if response.status_code == 200:
        await display_transaction_history(update, context, response.json())
    else:
        await update.message.reply_text(get_text(telegram_id, 'transaction_fail'))

async def handle_balance_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理余额明细查询"""
    telegram_id = update.effective_user.id
    page = context.user_data.get('balance_page', 1)
    
    print(f"Fetching balance history page {page}")  # 添加日志
    
    response = requests.post(
        f"{API_URL}/query/card/bill/balance_history",
        json={
            'telegram_id': telegram_id,
            'page': page,
            'limit': ITEMS_PER_PAGE
        }
    )
    
    print(f"Balance API Response: {response.text}")  # 添加日志
    
    if response.status_code == 200:
        await display_balance_history(update, context, response.json())
    else:
        await update.message.reply_text(get_text(telegram_id, 'balance_fail'))

# --------------------------------实体卡 start------------------------------------------------------

async def prompt_active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """提示用户输入激活码"""
    user_id = update.effective_user.id
    await update.message.reply_text(get_text(user_id, 'active_prompt'))
    # 调用分配接口实现分配并发送激活码
    response = requests.post(
        f"{API_URL}/physical/card/assign",
        json={
            'telegram_id': user_id
        }
    )
    result = response.json()

    if result['code'] == 200:
        print("激活码发送成功")
        print(result)
        context.user_data['waiting_for_active_code'] = True
    else:
        print("激活码发送失败")
        await update.message.reply_text(get_text(user_id, 'assign_error'))
        context.user_data.clear()

async def handle_active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理激活码"""
    if not context.user_data.get('waiting_for_active_code'):
        return

    activation_code = update.message.text
    user_id = update.effective_user.id
    context.user_data['active_code'] = activation_code
    context.user_data['waiting_for_active_code'] = False
    context.user_data['waiting_for_pin_code'] = True
    await update.message.reply_text(get_text(user_id, 'waiting_for_pin_code'))


async def handle_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理pin码"""
    if not context.user_data.get('waiting_for_pin_code'):
        return

    pin = update.message.text
    telegram_id = update.effective_user.id
    activation_code = context.user_data.get('active_code')
    user_id = update.effective_user.id

    # 打印日志
    print(f"Verifying code for pin_code: {pin}")
    print(f"Verification code active: {activation_code}")

    # 验证激活码
    response = requests.post(
        f"{API_URL}/physical/card/active",
        json={
            'pin': pin,
            'activation_code': activation_code,
            'telegram_id': telegram_id
        }
    )

    print(f"Verification API Response Status: {response.status_code}")
    print(f"Verification API Response Content: {response.text}")
    result = response.json()

    if result['code'] != 200 :
        print("Verification failed")
        await update.message.reply_text(get_text(user_id, 'active_error'))
        await update.message.reply_text(result['msg'])
        context.user_data.clear()
    else:
        print("Verification successful")
        context.user_data['waiting_for_active'] = False
        await update.message.reply_text(get_text(user_id, 'active_success'))
        context.user_data.clear()

    context.user_data.clear()

#--------------------------------实体卡 end---------------------------------------------------------------

async def handle_unbind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理解除绑定"""
    telegram_id = update.effective_user.id
    
    response = requests.post(
        f"{API_URL}/un_login",
        json={'telegram_id': telegram_id}
    )
    
    if response.status_code == 200:
        await update.message.reply_text(get_text(update.effective_user.id, 'unbind_success'))
        # 清除用户数据
        context.user_data.clear()
    else:
        await update.message.reply_text(get_text(update.effective_user.id, 'unbind_fail'))

async def display_transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict):
    """显示交易记录"""
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    
    # 业务类型映射
    biz_type_map = {
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
    
    # 状态映射
    status_map = {
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
    
    transactions = data.get('data', {}).get('transactions', [])
    total_pages = data.get('data', {}).get('total_page', 1)
    current_page = data.get('data', {}).get('page', 1)
    
    if not transactions:
        await update.message.reply_text(get_text(user_id, 'no_transactions'))
        return
    
    # 构建消息文本
    message_text = f"{get_text(user_id, 'transaction_page').format(current_page)}\n\n"
    
    for transaction in transactions:
        # 交易ID和关联信息
        message_text += f"{get_text(user_id, 'transaction_id')} {transaction.get('transaction_id', '')}\n"
        if transaction.get('origin_transaction_id'):
            message_text += f"{get_text(user_id, 'related_transaction_id')} {transaction.get('origin_transaction_id')}\n"
        
        # 卡信息
        message_text += f"{get_text(user_id, 'card_number')} {transaction.get('mask_card_number', '')}\n"
        
        # 时间信息
        message_text += (
            f"{get_text(user_id, 'transaction_time')} {transaction.get('transaction_time', '')}\n"
            f"{get_text(user_id, 'confirmation_time')} {transaction.get('confirm_time', '')}\n"
        )
        
        # 金额信息
        trans_amount = transaction.get('transaction_amount', {})
        acc_amount = transaction.get('accounting_amount', {})
        surcharge = transaction.get('surcharge', {})
        
        message_text += (
            f"{get_text(user_id, 'transaction_amount')} {trans_amount.get('amount', '')} {trans_amount.get('currency', '')}\n"
            f"{get_text(user_id, 'accounting_amount')} {acc_amount.get('amount', '')} {acc_amount.get('currency', '')}\n"
        )
        
        if surcharge.get('amount'):
            message_text += f"{get_text(user_id, 'surcharge_amount')} {surcharge.get('amount', '')} {surcharge.get('currency', '')}\n"
        
        # 商户信息
        message_text += (
            f"{get_text(user_id, 'merchant_name')} {transaction.get('merchant_name', '')}\n"
            f"{get_text(user_id, 'merchant_region')} {transaction.get('merchant_region', '')}\n"
        )
        
        # 交易类型和状态
        biz_type = transaction.get('biz_type', '')
        status = transaction.get('status', '')
        message_text += (
            f"{get_text(user_id, 'business_type')} {biz_type_map[lang].get(biz_type, biz_type)}\n"
            f"{get_text(user_id, 'transaction_status')} {status_map[lang].get(status, status)}\n"
        )
        
        # 状态描述
        if transaction.get('status_description'):
            message_text += f"{get_text(user_id, 'status_description')} {transaction.get('status_description')}\n"
        
        message_text += "\n" + get_text(user_id, 'divider') + "\n\n"
    
    # 发送交易记录
    await update.message.reply_text(message_text)
    
    # 分页按钮和功能菜单组合
    keyboard = []
    # 第一行：分页按钮
    pagination_row = []
    if current_page > 1:
        pagination_row.append(KeyboardButton(get_text(user_id, 'prev_page')))
    if current_page < total_pages:
        pagination_row.append(KeyboardButton(get_text(user_id, 'next_page')))
    if pagination_row:
        keyboard.append(pagination_row)
    
    # 第二行：功能菜单
    keyboard.append([
        KeyboardButton(get_text(user_id, 'transaction_prompt')),
        KeyboardButton(get_text(user_id, 'balance_prompt'))
    ])
    keyboard.append([KeyboardButton(get_text(user_id, 'activate')),
                     KeyboardButton(get_text(user_id, 'unbind'))])
    keyboard.append([KeyboardButton("/start")])
    
    reply_markup = ReplyKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(user_id, 'select_operation'), reply_markup=reply_markup)

async def display_balance_history(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict):
    """显示余额记录"""
    user_id = update.effective_user.id
    lang = user_language.get(user_id, 'en')
    
    history = data.get('data', {}).get('history', [])
    total_pages = data.get('data', {}).get('total_page', 1)
    current_page = data.get('data', {}).get('page', 1)
    
    if not history:
        await update.message.reply_text(get_text(user_id, 'no_balance_records'))
        return
    
    # 构建消息文本
    message_text = f"{get_text(user_id, 'balance_page').format(current_page)}\n\n"
    
    for record in history:
        # 交易ID和卡信息
        message_text += (
            f"{get_text(user_id, 'transaction_id')} {record.get('transaction_id', '')}\n"
            f"{get_text(user_id, 'card_number')} {record.get('mask_card_number', '')}\n"
        )
        
        # 时间信息
        message_text += (
            f"{get_text(user_id, 'transaction_time')} {record.get('transaction_time', '')}\n"
            f"{get_text(user_id, 'confirmation_time')} {record.get('confirm_time', '')}\n"
        )
        
        # 金额信息
        amount = record.get('amount', {})
        balance = record.get('balance_after_transaction', {})
        message_text += (
            f"{get_text(user_id, 'transaction_amount')} {amount.get('amount', '')} {amount.get('currency', '')}\n"
            f"{get_text(user_id, 'balance_after')} {balance.get('amount', '')} {balance.get('currency', '')}\n"
        )
        
        message_text += "\n" + get_text(user_id, 'divider') + "\n\n"
    
    await update.message.reply_text(message_text)
    
    # 分页按钮和功能菜单组合
    keyboard = []
    # 第一行：分页按钮
    pagination_row = []
    if current_page > 1:
        pagination_row.append(KeyboardButton(get_text(user_id, 'prev_page')))
    if current_page < total_pages:
        pagination_row.append(KeyboardButton(get_text(user_id, 'next_page')))
    if pagination_row:
        keyboard.append(pagination_row)
    
    # 第二行：功能菜单
    keyboard.append([
        KeyboardButton(get_text(user_id, 'transaction_prompt')),
        KeyboardButton(get_text(user_id, 'balance_prompt'))
    ])
    keyboard.append([KeyboardButton(get_text(user_id, 'activate')),
                     KeyboardButton(get_text(user_id, 'unbind'))])
    keyboard.append([KeyboardButton("/start")])
    
    reply_markup = ReplyKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(user_id, 'select_operation'), reply_markup=reply_markup)


def main():
    """启动机器人"""
    print("正在启动机器人...")
    try:
        # 添加处理程序
        app.add_handler(CommandHandler("start", start))

        # 语言选择处理
        app.add_handler(MessageHandler(
            filters.TEXT & filters.Regex('^(English|日本語|简体中文|繁體中文)$'),
            handle_language_selection
        ))

        async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """处理所有消息"""
            text = update.message.text
            user_id = update.effective_user.id

            # 邮箱和验证码处理
            if context.user_data.get('waiting_for_email'):
                await handle_email(update, context)
            elif context.user_data.get('waiting_for_verification'):
                await handle_verification_code(update, context)
            elif context.user_data.get('waiting_for_active_code'):
                await handle_active(update, context)
            elif context.user_data.get('waiting_for_pin_code'):
                await handle_pin(update, context)

            elif text == get_text(user_id, 'next_page'):
                # 处理下一页
                if context.user_data.get('viewing_transaction'):
                    context.user_data['transaction_page'] = context.user_data.get('transaction_page', 1) + 1
                    await handle_transaction_history(update, context)
                elif context.user_data.get('viewing_balance'):
                    context.user_data['balance_page'] = context.user_data.get('balance_page', 1) + 1
                    await handle_balance_history(update, context)
            elif text == get_text(user_id, 'prev_page'):
                # 处理上一页
                if context.user_data.get('viewing_transaction'):
                    context.user_data['transaction_page'] = max(1, context.user_data.get('transaction_page', 1) - 1)
                    await handle_transaction_history(update, context)
                elif context.user_data.get('viewing_balance'):
                    context.user_data['balance_page'] = max(1, context.user_data.get('balance_page', 1) - 1)
                    await handle_balance_history(update, context)
            elif text == get_text(user_id, 'transaction_prompt'):
                # 重置交易记录页码并查询
                context.user_data['transaction_page'] = 1
                context.user_data['viewing_transaction'] = True
                context.user_data['viewing_balance'] = False
                await handle_transaction_history(update, context)
            elif text == get_text(user_id, 'balance_prompt'):
                # 重置余额记录页码并查询
                context.user_data['balance_page'] = 1
                context.user_data['viewing_balance'] = True
                context.user_data['viewing_transaction'] = False
                await handle_balance_history(update, context)
            elif text == get_text(user_id, 'unbind'):
                await handle_unbind(update, context)
            # 处理激活实体卡
            elif text == get_text(user_id, 'activate'):
                await prompt_active(update, context)
            else:
                await update.message.reply_text("请使用 /start 命令开始使用机器人。")

        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        ))

        print(f"机器人启动成功！")
        print(f"Bot Token: {TOKEN}")
        print(f"API URL: {API_URL}")
        print("机器人正在运行中...")

        # 启动机器人
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )

    except Exception as e:
        print(f"机器人启动失败！错误信息：{str(e)}")
        raise e

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n检测到 Ctrl+C，正在关闭机器人...")
    except Exception as e:
        print(f"发生错误：{str(e)}")
    finally:
        print("机器人已关闭。") 