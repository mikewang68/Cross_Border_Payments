from flask import request, jsonify
from flask import Blueprint, render_template
from flask_mail import Message
from exts import mail, db
from models import UserModel,CardModel
from userLogin import generate_key
from secure_info import query_secure_info
bp = Blueprint("auth", __name__, url_prefix="/")
User = UserModel
Card = CardModel

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route('/send/email', methods=["POST"])  # 修改为 POST 请求
def send_email():
    # 从 POST 请求体中获取邮箱地址
    data = request.json  # 获取 JSON 数据
    email = data.get('email')


    # 如果没有提供 'email' 参数，返回 400 错误
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400


    # 根据 email 查找用户
    user = User.query.filter_by(email=email).first()

    # 如果没有找到用户，返回404
    if not user:
        return jsonify({"error": f"No user found with email {email}"}), 404

    # 获取用户的 id
    user_id = user.user_id

    # 创建密钥，使用 generate_key 动态生成密钥
    user_key = generate_key(email, user_id)  # 生成密钥

    # 使用 try-except 处理数据库操作
    try:
        user.user_key = user_key  # 更新 user_key
        user.user_login = 0  # 更新 user_login 初始化用户登录状态
        db.session.commit()  # 提交更新
        # 如果数据库更新成功，继续发送邮件
        msg = Message(f"GsalaryKey", recipients=[email], body=f"Hello, This is your key: {user_key}, do not share it with others!")
        try:
            # 发送邮件
            mail.send(msg)
            return jsonify({"message": "Email sent successfully!"}), 200
        except Exception as e:
            return jsonify({"error": f"Error sending email: {e}"}), 500

    except Exception as db_error:
        # 如果数据库操作失败，回滚事务并返回错误信息
        db.session.rollback()  # 回滚数据库事务，防止部分更新
        return jsonify({"error": f"Error updating database: {db_error}"}), 500

@bp.route('/check/key', methods=["POST"])  # 修改为 POST 请求
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

    # 根据 email 查找用户
    user = User.query.filter_by(email=email).first()

    # 如果没有找到用户，返回404
    if not user:
        return jsonify({"error": f"No user found with email {email}"}), 404
    # 获取用户密钥
    user_key = user.user_key
    # 比对密钥
    if key != user_key :
        return jsonify({"error": f"Wrong key: {key}"}), 400

    else:
        # 使用 try-except 处理数据库操作
        try:
            user.telegram_id = telegram_id  # 更新 telegram_id
            user.user_login = 1  # 更新 user_login 用户变为绑定状态
            db.session.commit()  # 提交更新

        except Exception as db_error:
            # 如果数据库操作失败，回滚事务并返回错误信息
            db.session.rollback()  # 回滚数据库事务，防止部分更新
            return jsonify({"error": f"Error updating database: {db_error}"}), 500

        # 获取用户的 id
        user_id = user.user_id

        # 根据 user_id 查找卡片信息
        card = Card.query.filter_by(user_id=user_id).first()  # 根据 user_id 查找对应的卡
        if not card:
            return jsonify({"error": f"No card found for user with ID {user_id}"}), 404

        # 获取卡片的 id
        id = card.card_id

        # 调用查询函数并返回结果
        card_data = query_secure_info(id)
        data = card_data.get('data', {})
        pan = data.get('pan')
        expire_year = data.get('expire_year')
        expire_month = data.get('expire_month')
        cvv = data.get('cvv')

        msg = Message(f"Gsalary", recipients=[email], body=f"Hello, This is your card information：number: {pan},expire date：{expire_year}-{expire_month} ，cvv：{cvv},do not share it with others!")
        try:
            # 发送邮件
            mail.send(msg)
            return jsonify({"message": "Email sent successfully!"}), 200
        except Exception as e:
            return jsonify({"error": f"Error sending email: {e}"}), 500


# 检查登录状态
@bp.route('/check/login', methods=["POST"])  # 修改为 POST 请求
def check_login():
    # 从 POST 请求体中获取telegram_id
    data = request.json  # 获取 JSON 数据
    telegram_id = data.get('telegram_id')

    # 如果没有提供 'telegram_id' 参数，返回 400 错误
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400

    # 根据 telegram_id 查找用户
    user = User.query.filter_by(telegram_id=telegram_id).first()  # 根据 key 查找用户

    # 如果没有找到用户，返回404
    if not user:
        return jsonify({"error": f"No user found with key {telegram_id}"}), 404
    else:

        # 获取用户的登录状态
        user_login = user.user_login

        data = {
            "status": "success",
            "message": "Data fetched successfully",
            "data": {"user_login": user_login}
        }

        # 0 未绑定
        # 1 绑定

        if not user_login:
            return jsonify({"message": "Email sent successfully!"}), 400
        else:
            return data


# 解绑
@bp.route('/un_login', methods=["POST"])  # 修改为 POST 请求
def un_login():
    # 从 POST 请求体中获取telegram_id
    data = request.json  # 获取 JSON 数据
    telegram_id = data.get('telegram_id')

    # 如果没有提供 'telegram_id' 参数，返回 400 错误
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400

    # 根据 telegram_id 查找用户
    user = User.query.filter_by(telegram_id=telegram_id).first()  # 根据 key 查找用户

    # 如果没有找到用户，返回404
    if not user:
        return jsonify({"error": f"No user found with key {telegram_id}"}), 404
    else:

        # 获取用户的登录状态
        user_login = user.user_login

        if not user_login:
            return jsonify({"error": "User_login parameter not found"}), 400

        # 使用 try-except 处理数据库操作
        try:
            user.user_login = 0  # 更新 user_login
            db.session.commit()  # 提交更新
            # 如果数据库更新成功，提示解绑成功
            return jsonify({"message": "Logout successfully!"}), 200


        except Exception as db_error:
            # 如果数据库操作失败，回滚事务并返回错误信息
            db.session.rollback()  # 回滚数据库事务，防止部分更新
            return jsonify({"error": f"Error updating database: {db_error}"}), 500




