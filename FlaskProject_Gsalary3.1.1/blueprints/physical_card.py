from anyio import sleep
from flask import request, jsonify, current_app
from flask import Blueprint
from sqlalchemy import false

from comm.db_api import query_database, update_database
from comm.test import physical_card_test
from gsalary_api import GSalaryAPI

gsalary = GSalaryAPI()

bp = Blueprint("physical_card", __name__, url_prefix="/physical")


# 视图函数：分配实体卡
@bp.route("/card/assign", methods=["POST"])
def assign_card():
    """分配实体卡给指定用户"""
    # 获取并验证请求参数
    telegram_id = request.json.get('telegram_id')
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400

    try:
        # 1. 查询符合条件的用户
        active_users = get_active_users(telegram_id)
        if not active_users:
            return jsonify({"code": 404, "msg": "No active users found"}), 404

        # 2. 检查用户是否有实体卡
        check_code = check_physical_cards(active_users)

        if check_code == 1:
            available_cards = get_available_cards(active_users)
            if not available_cards:
                return jsonify({"code": 200, "msg": "No available new cards"}), 200

            # 3. 处理第一张可用卡片
            first_card = available_cards[0]
            system_id = active_users[0].get('version')  # 从用户信息中获取系统ID
            return process_card_assignment(first_card, system_id)
        else:
            return jsonify({"code": 404, "msg": "User does not have physical card"})

    except Exception as e:
        # 捕获所有未处理的异常，避免服务崩溃
        current_app.logger.error(f"Error assigning card: {str(e)}")
        return jsonify({"code": 500, "msg": "Internal server error"}), 500


def get_active_users(telegram_id):
    """查询指定telegram_id的活跃用户"""
    user_condition = {
        'telegram_id': telegram_id,
        'user_login': "1"  # 已登录的活跃用户
    }
    return query_database('card_holder', user_condition)


def check_physical_cards(users):
    """检查用户是否被分配实体卡"""
    # 提取所有活跃用户的card_holder_id
    card_holder_ids = [user.get('card_holder_id') for user in users if user.get('card_holder_id')]
    if not card_holder_ids:
        return 0  # 修复：返回0而非空列表

    # 查询这些用户的未分配卡片
    card_condition = {'card_holder_id': card_holder_ids}
    cards = query_database('physical_cards', card_condition)

    return 1 if cards else 0


def get_available_cards(users):
    """获取用户的未分配(new)实体卡"""
    # 提取所有活跃用户的card_holder_id
    card_holder_ids = [user.get('card_holder_id') for user in users if user.get('card_holder_id')]
    if not card_holder_ids:
        return []

    # 查询这些用户的未分配卡片
    card_condition = {'card_holder_id': card_holder_ids, 'status': "new"}
    return query_database('physical_cards', card_condition)


def process_card_assignment(card, system_id):
    """处理卡片分配逻辑：调用外部服务并更新卡片状态"""
    card_info = {
        'card_holder_id': card.get('card_holder_id'),
        'card_number': card.get('card_number'),
        'card_currency': card.get('card_currency'),
    }

    try:
        # 调用外部分配服务并确保解析为JSON
        response = gsalary.assign_card(system_id=system_id, data=card_info)
        # 假设gsalary返回的是响应对象，需要解析JSON
        response_data = response.json() if hasattr(response, 'json') else response
    except Exception as e:
        return jsonify({"code": 503, "msg": f"Failed to call assignment service: {str(e)}"}), 503

    # 处理服务响应
    if response_data.get("result"):
        result = response_data['result']
        if result.get('code') in ('SUCCESS', 'S'):
            # 更新卡片状态为已分配
            update_database(
                table_name='physical_cards',
                set_columns_values={"status": 'assigned'},
                where_conditions={
                    "card_holder_id": card.get('card_holder_id'),
                    "card_number": card.get('card_number')
                }
            )
            return jsonify({"code": 200, "msg": "Card assigned successfully"})
        else:
            return jsonify({
                "code": 400,
                "msg": f"Assignment failed: {result.get('message', 'Unknown error')}"
            })
    elif response_data.get('message') == 'Card number is already assigned':
        return jsonify({"code": 200, "msg": "Card number is already assigned"})
    else:
        return jsonify({
            "code": 400,
            "msg": f"Invalid response: {response_data.get('message', 'No message')}"
        })


# 视图函数：激活实体卡
@bp.route("/card/active", methods=["POST"])
def active_card():
    """激活用户的实体卡"""
    # 获取请求参数
    telegram_id = request.json.get('telegram_id')
    activation_code = request.json.get('activation_code')
    pin = request.json.get('pin')

    # 参数验证
    if not telegram_id:
        return jsonify({"error": "Telegram_id parameter is required"}), 400
    if not activation_code:
        return jsonify({"error": "Activation_code parameter is required"}), 400
    if not pin:
        return jsonify({"error": "Pin parameter is required"}), 400

    try:
        users = get_active_users(telegram_id)
        if not users:
            return jsonify({"code": 404, "msg": "No active users found"}), 404

        # 获取用户的card_holder_id
        card_holder_ids = [user.get('card_holder_id') for user in users if user.get('card_holder_id')]
        if not card_holder_ids:
            return jsonify({"code": 404, "msg": "User has no card holder information"}), 404

        # 查询用户的VISA卡片
        card_condition = {'card_holder_id': card_holder_ids}
        cards = query_database('cards', card_condition)
        visa_card_ids = [card.get('card_id') for card in cards if card.get('brand_code') == "VISA"]

        if not visa_card_ids:
            return jsonify({"code": 404, "msg": "No VISA cards found for user"}), 404

        # 准备激活数据
        first_card_id = visa_card_ids[0]
        system_id = users[0].get('version')
        data = {
            'activation_code': activation_code,
            'pin': pin,
        }

        # 调用激活服务
        response = gsalary.active_card(system_id=system_id, card_id=first_card_id, data=data)
        response_data = response.json() if hasattr(response, 'json') else response

        # 处理激活响应
        if response_data.get("result"):
            result = response_data['result']
            if result.get('code') in ('SUCCESS', 'S'):
                # 查找对应的实体卡并更新状态
                physical_card = query_database(
                    'physical_cards',
                    {'card_holder_id': card_holder_ids[0], 'card_id': first_card_id}
                )

                if physical_card:
                    update_database(
                        table_name='physical_cards',
                        set_columns_values={"active_status": 'active'},
                        where_conditions={"id": physical_card[0].get('id')}
                    )

                return jsonify({"code": 200, "msg": "Card activated successfully"})
            else:
                return jsonify({
                    "code": 400,
                    "msg": f"Activation failed: {result.get('message', 'Unknown error')}"
                })
        elif response_data.get('message') == 'Bank card status is not inactive.':
            return jsonify({"code": 404, "msg": "Bank card status is not inactive"})
        else:
            return jsonify({
                "code": 400,
                "msg": f"Invalid response: {response_data.get('message', 'No message')}"
            })

    except Exception as e:
        current_app.logger.error(f"Error activating card: {str(e)}")
        return jsonify({"code": 500, "msg": "Internal server error"}), 500
