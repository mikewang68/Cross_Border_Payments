from flask import Blueprint, render_template, session, jsonify, request
from blueprint.auth import login_required
from sqlalchemy import func
from comm.gsalay_api import GSalaryAPI

from comm.db_api import query_all_from_table

main_bp = Blueprint('main', __name__)



@main_bp.route('/')
@login_required
def index():
    # 从会话中获取用户名
    user_account = session.get('user_account', '')
    return render_template('main/index.html', user_account=user_account)

@main_bp.route('/wallet')
@login_required
def wallet():
    # 从会话中获取用户名
    user_account = session.get('user_account', '')
    return render_template('main/wallet.html', user_account=user_account)

@main_bp.route('/recharge')
@login_required
def recharge():
    return render_template('main/recharge.html')

@main_bp.route('/salary')
@login_required
def salary():
    return render_template('main/salary.html')

@main_bp.route('/card_users')
@login_required
def card_users():
    try:
        # 查询用卡人数据
        card_holders = query_all_from_table('card_holder')
        # 打印调试信息
        print(f"查询到 {len(card_holders) if card_holders else 0} 条用卡人记录")
        return render_template('main/card_users.html', card_holders=card_holders)
    except Exception as e:
        print(f"查询用卡人数据时出错: {str(e)}")
        # 返回空列表，避免模板渲染错误
        return render_template('main/card_users.html', card_holders=[])
    
# 添加用卡人表单页面路由
@main_bp.route('/card_holders/add')
def card_holder_add():
    return render_template('main/card_user_add.html')

@main_bp.route('/transactions')
@login_required
def transactions():
    transactions = query_all_from_table('card_transactions')

    # 打印一下查询结果，检查是否有数据返回
    print(f"查询到 {len(transactions) if transactions else 0} 条交易记录")

    # 将所有结果传递给模板，让前端处理分页
    return render_template('main/card_transactions.html', transactions=transactions)

#查看额度明细
@main_bp.route('/balance_history')
@login_required
def balance_history():
    balance_history = query_all_from_table('balance_history')

    print(f"查询到 {len(balance_history) if balance_history else 0} 条额度明细记录")

    return render_template('main/balance_history.html', balance_history=balance_history)


@main_bp.route('/all_cards')
@login_required
def all_cards():
    return render_template('main/all_cards.html')

@main_bp.route('/statistics')
@login_required
def statistics():
    return render_template('main/statistics.html')

@main_bp.route('/system')
@login_required
def system():
    return render_template('main/system.html')

@main_bp.route('/exchange_rate')
@login_required
def exchange_rate():
    return render_template('main/exchange_rate.html')

@main_bp.route('/card_holders/create', methods=['POST'])
@login_required
def create_card_holder():
    try:
        # 获取表单数据
        data = request.get_json()
        # 创建API实例
        gsalary_api = GSalaryAPI()
        
        # 调用API创建用卡人
        result = gsalary_api.create_card_holder("J1", data)  # 替换实际的system_id
        if result['result']['result'] == 'S':
            return jsonify({
                "code": 0,
                "msg": "添加用卡人成功",
                "data": result
            })
        else:
            return jsonify({
                "code": 1,
                "msg": "添加用卡人失败",
                "data": None
            })
    except Exception as e:
        return jsonify({
            "code": 1,
            "msg": f"发生错误: {str(e)}",
            "data": None
        })
