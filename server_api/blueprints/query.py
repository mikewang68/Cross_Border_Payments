from flask import request, jsonify
from flask import Blueprint
from secure_info import query_secure_info
from balance_history import query_balance_history
from card_transactions import query_card_transactions
from models import UserModel, CardModel

bp = Blueprint("query", __name__, url_prefix="/query")
User = UserModel
Card = CardModel

# 视图函数：获取卡片的安全信息
@bp.route("/card/info", methods=["POST"])  # 指定为 POST 请求
def get_card_secure_info():
    # 获取 POST 请求体中的 'telegram_id'（假设请求体是 JSON 格式）
    telegram_id = request.json.get('telegram_id')

    # 如果没有提供 'telegram_id' 参数，返回 400 错误
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400

    # 根据 telegram_id 查找用户
    user = User.query.filter_by(telegram_id=telegram_id).first()

    # 如果没有找到用户，返回404
    if not user:
        return jsonify({"error": f"No user found with telegram_id {telegram_id}"}), 404

    # 获取用户的 id
    user_id = user.user_id

    # 根据 user_id 查找卡片信息
    card = Card.query.filter_by(user_id=user_id).first()  # 根据 user_id 查找对应的卡
    if not card:
        return jsonify({"error": f"No card found for user with ID {user_id}"}), 404

    # 获取卡片的 id
    id = card.card_id

    # 调用查询函数并返回结果
    return query_secure_info(id)

# 视图函数：获取卡片的余额明细
@bp.route("/card/bill/balance_history", methods=["POST"])  # 修改为 POST 请求
def get_card_bill_balance_history():
    # 获取 POST 请求体中的 'mobile'
    telegram_id = request.json.get('telegram_id')
    page = request.json.get('page')
    limit = request.json.get('limit')

    # 如果没有提供 'telegram_id' 参数，返回 400 错误
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400

    # 根据 email 查找用户
    user = User.query.filter_by(telegram_id=telegram_id).first()  # 根据 mobile 查找用户

    # 如果没有找到用户，返回404
    if not user:
        return jsonify({"error": f"No user found with telegram_id {telegram_id}"}), 404

    # 获取用户的 id
    user_id = user.user_id

    # 根据 user_id 查找卡片信息
    card = Card.query.filter_by(user_id=user_id).first()  # 根据 user_id 查找对应的卡
    if not card:
        return jsonify({"error": f"No card found for user with ID {user_id}"}), 404

    id = card.card_id

    # 调用查询函数并返回结果
    return query_balance_history(id,page,limit)


# 视图函数：获取卡片的交易明细
@bp.route("/card/bill/transactions", methods=["POST"])  # 修改为 POST 请求
def get_card_transactions():
    # 获取 POST 请求体中的 'mobile'
    telegram_id = request.json.get('telegram_id')
    page = request.json.get('page')
    limit = request.json.get('limit')

    # 如果没有提供 'telegram_id' 参数，返回 400 错误
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400

    # 根据 email 查找用户
    user = User.query.filter_by(telegram_id=telegram_id).first()

    # 如果没有找到用户，返回404
    if not user:
        return jsonify({"error": f"No user found with telegram_id {telegram_id}"}), 404

    # 获取用户的 id
    user_id = user.user_id

    # 根据 user_id 查找卡片信息
    card = Card.query.filter_by(user_id=user_id).first()
    if not card:
        return jsonify({"error": f"No card found for user with ID {user_id}"}), 404

    id = card.card_id

    # 调用查询函数并返回结果
    return query_card_transactions(id,page,limit)