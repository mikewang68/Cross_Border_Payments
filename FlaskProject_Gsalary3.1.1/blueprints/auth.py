from flask import request, jsonify
from flask import Blueprint, render_template
from comm.email_pusher import EmailPusher
from userLogin import generate_key
from comm.db_api import query_database, update_database, query_field_from_table, query_multiple_fields

bp = Blueprint("auth", __name__, url_prefix="/")
email_pusher = EmailPusher()

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route('/send/email', methods=["POST"])
def send_email():
    # 从 POST 请求体中获取邮箱地址
    data = request.json  # 获取 JSON 数据
    email = data.get('email')

    # 如果没有提供 'email' 参数，返回 400 错误
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    condition = {'email':f'{email}'}

    # 根据 email 查找用户
    users = query_database('card_holder',condition)

    # 如果没有找到用户，返回404
    if not users:
        return jsonify({"error": f"No user found with email {email}"}), 404

    # 创建密钥，使用 generate_key 动态生成密钥
    user_key = generate_key(email)  # 生成密钥

    set_columns = {'user_key':f'{user_key}'}
    where_condition = {'email':f'{email}'}
    update_database('card_holder',set_columns,where_condition)

    body = f"Hello, This is your key: {user_key}, do not share it with others!"
    result = email_pusher.send_email(email,'Galileo',body)

    return result



@bp.route('/check/key', methods=["POST"])
def check_key():
    # 从 POST 请求体中获取邮箱地址
    data = request.json  # 获取 JSON 数据
    email = data.get('email')
    key = data.get('key')
    telegram_id = data.get('telegram_id')
    # 如果没有提供 'email' 参数，返回 400 错误
    if not key:
        return jsonify({"error": "Key parameter is required"}), 400

    # 如果没有提供 'telegram_id' 参数，返回 400 错误
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400

    # 如果没有提供 'email' 参数，返回 400 错误
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    condition = {'email':f'{email}'}
    # 根据 email 查找用户
    user_list = query_database('card_holder',condition)
    print('user_list:',user_list)

    # 如果没有找到用户，返回404
    if not user_list:
        return jsonify({"error": f"No user found with email {email}"}), 404

    # 获取用户密钥
    user_key = ''
    card_holder_id_list = []
    for user in user_list:
        user_key = user.get('user_key')
        card_holder_id = user.get('card_holder_id')
        card_holder_id_list.append(card_holder_id)
        print('card_holder_id_list:',card_holder_id_list)
    # 比对密钥
    if key != user_key :
        return jsonify({"error": f"Wrong key: {key}"}), 400

    else:
        set_columns = {'telegram_id': f'{telegram_id}','user_login': '1'}
        where_columns = {'email': f'{email}'}
        update_database('card_holder', set_columns, where_columns)

        email_body = "Hello, This is your card information:\n" #编辑邮件

        # 根据 user_id 查找卡片信息
        card_condition = {'card_holder_id': card_holder_id_list}
        cards = query_database('cards', card_condition)

        card_id_list = []

        for card in cards :
            card_id = card.get('card_id')
            card_id_list.append(card_id)

        if cards is None:
            return jsonify({"error": f"No card found for user with ID {card_holder_id_list}"}), 404

        card_id_dict = {'card_id': card_id_list}

        secure_info = query_database('cards_secure_info',card_id_dict)

        for data in secure_info :
            pan = data.get('pan')
            expire_year = data.get('expire_year')
            expire_month = data.get('expire_month')
            cvv = data.get('cvv')

            email_body += f"Number: {pan}, Expire Date: {expire_year}-{expire_month}, CVV: {cvv}\n"

        result = email_pusher.send_email(email, 'Galileo', email_body)

        return result


@bp.route('/check/login', methods=["POST"])
def check_login():
    # 从POST请求体中获取telegram_id
    data = request.json
    telegram_id = data.get('telegram_id')

    # 验证参数是否存在
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400

    # 根据telegram_id查找用户
    user_condition = {'telegram_id': telegram_id}
    users = query_database('card_holder', user_condition)

    # 检查用户是否存在
    if not users:
        return jsonify({"error": f"No user found with key {telegram_id}"}), 404

    # 检查是否有任何用户处于登录状态
    has_logged_in_user = any(user.get('user_login') == "1" for user in users)

    # 构建返回数据
    response_data = {
        "status": "success",
        "message": "Data fetched successfully",
        "data": {"user_login": "1" if has_logged_in_user else "0"}
    }

    return jsonify(response_data)


# 解绑
@bp.route('/un_login', methods=["POST"])  # 修改为 POST 请求
def un_login():
    # 从 POST 请求体中获取telegram_id
    data = request.json  # 获取 JSON 数据
    telegram_id = data.get('telegram_id')

    # 如果没有提供 'telegram_id' 参数，返回 400 错误
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400

    set_columns = {'user_login': '0'}
    where_columns = {'telegram_id': f'{telegram_id}'}

    update_database('card_holder', set_columns, where_columns)

    return jsonify({"info": "Un_login successfully"}), 200




