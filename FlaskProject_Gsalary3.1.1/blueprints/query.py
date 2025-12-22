from flask import request, jsonify
from flask import Blueprint
from balance_history import query_balance_history
from card_transactions import query_card_transactions
from comm.db_api import query_database

bp = Blueprint("query", __name__, url_prefix="/query")

# 视图函数：获取卡片的余额明细
@bp.route("/card/bill/balance_history", methods=["POST"])  # 修改为 POST 请求
def get_card_bill_balance_history():
    # 获取 POST
    telegram_id = request.json.get('telegram_id')
    page = request.json.get('page')
    limit = request.json.get('limit')

    # 如果没有提供 'telegram_id' 参数，返回 400 错误
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400

    # 根据 telegram_id 查找用户
    user_condition = {'telegram_id': telegram_id,'user_login': "1"}
    users = query_database('card_holder', user_condition)

    card_id_list = []
    card_holder_id_list = []
    # 通过card_holder_id查找card_id形成列表
    for user in users :
        card_holder_id = user.get('card_holder_id')
        card_holder_id_list.append(card_holder_id)

    card_condition = {'card_holder_id': card_holder_id_list}
    cards = query_database('cards',card_condition)
    for card in cards :
        card_id = card.get('card_id')
        card_id_list.append(card_id)

    balance_history = query_balance_history(card_id_list,page=page,limit=limit)

    return balance_history


# 视图函数：获取卡片的交易明细
@bp.route("/card/bill/transactions", methods=["POST"])
def get_card_transactions():
    # 获取 POST
    telegram_id = request.json.get('telegram_id')
    page = request.json.get('page')
    limit = request.json.get('limit')

    # 如果没有提供 'telegram_id' 参数，返回 400 错误
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400

    # 根据 telegram_id 查找用户
    user_condition = {'telegram_id': telegram_id,'user_login': "1"}
    users = query_database('card_holder', user_condition)

    card_id_list = []
    card_holder_id_list = []
    # 通过card_holder_id查找card_id形成列表
    for user in users :
        card_holder_id = user.get('card_holder_id')
        card_holder_id_list.append(card_holder_id)

    card_condition = {'card_holder_id': card_holder_id_list}
    cards = query_database('cards',card_condition)
    for card in cards :
        card_id = card.get('card_id')
        card_id_list.append(card_id)

    card_transactions = query_card_transactions(card_id_list,page=page,limit=limit)

    return card_transactions