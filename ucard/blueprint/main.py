from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for
from ucard.blueprint.auth import login_required
from comm.gsalay_api import GSalaryAPI
from datetime import datetime
from comm.db_api import query_all_from_table

main_bp = Blueprint('main', __name__)

# 定义一个函数将字符串转换为 datetime 对象
def convert_time(time_str):
    try:
        # 尝试使用包含毫秒的格式解析
        if len(time_str) > 0:
            return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            return '--'
    except ValueError:
        # 如果失败，使用不包含毫秒的格式解析
            return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')

@main_bp.route('/')
@login_required
def index():
    # 从会话中获取用户名
    user_account = session.get('user_account', '')
    return render_template('main/index.html', user_account=user_account)

@main_bp.route('/wallet')
@login_required
def wallet_redirect():
    return redirect(url_for('main.wallet_balance'))

@main_bp.route('/wallet_balance')
@login_required
def wallet_balance():
    try:
        # 查询钱包余额数据
        wallet_balances = query_all_from_table('wallet_balance')
        # 查询地区数据（包含国旗图标）
        regions = query_all_from_table('region')
        
        # 打印调试信息
        print(f"查询到 {len(wallet_balances) if wallet_balances else 0} 条钱包余额记录")
        print(f"查询到 {len(regions) if regions else 0} 条地区记录")
        
        # 如果数据为空，添加测试数据（仅用于测试前端显示）
        if not wallet_balances or len(wallet_balances) == 0:
            # 添加测试数据，仅用于开发阶段
            print("未找到钱包余额数据，使用测试数据")
            wallet_balances = [
                {"currency": "USD", "amount": 936.12, "user_id": "test_user", "update_time": "2023-03-13 18:48:52"}
            ]
        
        # 将数据转换为JSON并返回给前端
        return render_template('main/wallet_balance.html', wallet_balances=wallet_balances, regions=regions)
    except Exception as e:
        print(f"查询钱包数据时出错: {str(e)}")
        # 返回空列表，避免模板渲染错误
        return render_template('main/wallet_balance.html', wallet_balances=[], regions=[])
    
@main_bp.route('/wallet_transactions')
@login_required
def wallet_transactions():
    try:
        # 查询钱包交易记录
        wallet_transactions = query_all_from_table('wallet_transactions')
        # 查询钱包余额
        wallet_balances = query_all_from_table('wallet_balance')
        regions = query_all_from_table('region')
        
        # 打印调试信息
        print(f"查询到 {len(wallet_balances) if wallet_balances else 0} 条钱包余额记录")
        print(f"查询到 {len(wallet_transactions) if wallet_transactions else 0} 条地区记录")
        
        # 如果数据为空，添加测试数据（仅用于测试前端显示）
        if not wallet_balances or len(wallet_balances) == 0:
            # 添加测试数据，仅用于开发阶段
            print("未找到钱包余额数据，使用测试数据")
            wallet_balances = [
                {"currency": "USD", "amount": 936.12, "user_id": "test_user", "update_time": "2023-03-13 18:48:52"}
            ]
        # if not wallet_transactions or len(wallet_transactions) == 0:
        #     # 添加测试数据，仅用于开发阶段
        #     print("未找到钱包交易记录，使用测试数据")
        #     wallet_transactions = [
        #         {"insert_time": "2023-03-13 18:48:52""currency": "USD", "amount": 936.12, "user_id": "test_user", }
        #     ]
        
        # 将数据转换为JSON并返回给前端
        return render_template('main/wallet_transactions.html', wallet_balances=wallet_balances, wallet_transactions=wallet_transactions, regions=regions)
    except Exception as e:
        print(f"查询钱包数据时出错: {str(e)}")
        # 返回空列表，避免模板渲染错误
        return render_template('main/wallet_transactions.html', wallet_balances=[], wallet_transactions=[], regions=[])

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
        
        # 对列表进行排序，按 transaction_time 倒序排列
        sorted_card_holders = sorted(card_holders, key=lambda x: convert_time(x["create_time"]), reverse=True)
        return render_template('main/card_users.html', card_holders=sorted_card_holders)
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
    # 对列表进行排序，按 transaction_time 倒序排列
    sorted_transactions = sorted(transactions, key=lambda x: convert_time(x["transaction_time"]), reverse=True)
    # 将所有结果传递给模板，让前端处理分页
    return render_template('main/card_transactions.html', transactions=sorted_transactions)

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
        version_data = data.pop('version') # 删除json['platform']并将其赋值给platform_data
        # 创建API实例
        gsalary_api = GSalaryAPI()
        
        # 调用API创建用卡人
        result = gsalary_api.create_card_holder(version_data, data)  # 替换实际的system_id
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

@main_bp.route('/card_holders/edit_page')
def card_holder_edit_page():
    """渲染用卡人编辑页面"""
    return render_template('main/card_user_edit.html')

@main_bp.route('/card_holders/edit', methods=['PUT']) 
def card_holder_edit():
    """处理用卡人编辑请求"""
    try:
        # 获取JSON数据
        data = request.get_json()
        card_holder_id = data.pop('card_holder_id')  # 删除json['card_holder_id']并将其赋值给card_holder_id
        version = data.pop('version')  # 删除json['version']并将其赋值给version
        # print(data)
        # print(card_holder_id)
        # print(version)
        # 创建API实例
        gsalary_api = GSalaryAPI()
        # 调用API创建用卡人
        result = gsalary_api.update_card_holder(system_id = version, holder_id=card_holder_id, data=data)  # 替换实际的system_id
        if result['result']['result'] == 'S':
            return jsonify({
                "code": 0,
                "msg": "修改成功",
                "data": result
            })
        else:
            return jsonify({
                "code": 1,
                "msg": "修改失败",
                "data": None
            })
    except Exception as e:
        return jsonify({
            "code": 1,
            "msg": f"发生错误: {str(e)}",
            "data": None
        })

# API endpoints
@main_bp.route('/api/wallet/balance', methods=['GET'])
@login_required
def api_wallet_balance():
    try:
        # 查询钱包余额数据
        wallet_balances = query_all_from_table('wallet_balance')
        # 查询地区数据
        regions = query_all_from_table('region')
        
        # 构建响应数据
        balances = []
        for balance in wallet_balances:
            balances.append({
                'currency': balance.get('currency', ''),
                'amount': float(balance.get('amount', 0)),
            })
        
        # 获取更新时间（取第一条记录的更新时间）
        update_time = wallet_balances[0].get('update_time', '') if wallet_balances else ''
        
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': {
                'balances': balances,
                'updateTime': update_time
            }
        })
    except Exception as e:
        print(f"获取钱包余额数据时出错: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': f'获取钱包余额数据失败: {str(e)}',
            'data': None
        })

@main_bp.route('/api/wallet_data', methods=['GET'])
@login_required
def api_wallet_data():
    """返回钱包数据的API端点，用于调试和标签页加载"""
    try:
        # 查询钱包余额数据
        wallet_balances = query_all_from_table('wallet_balance')
        # 查询地区数据（包含国旗图标）
        regions = query_all_from_table('region')
        
        # 打印调试信息
        print(f"API查询到 {len(wallet_balances) if wallet_balances else 0} 条钱包余额记录")
        print(f"API查询到 {len(regions) if regions else 0} 条地区记录")
        
        # 如果数据为空，添加测试数据
        if not wallet_balances or len(wallet_balances) == 0:
            print("API未找到钱包余额数据，使用测试数据")
            wallet_balances = [
                {"currency": "USD", "amount": 936.12, "user_id": "test_user", "update_time": "2023-03-13 18:48:52"}
            ]
        
        return jsonify({
            'status': 'success',
            'data': {
                'wallet_balances': wallet_balances,
                'regions': regions  # 返回完整的region数据，包括图标
            }
        })
    except Exception as e:
        print(f"API获取钱包数据时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# 所有卡
@main_bp.route('/cards')
@login_required
def cards():
    try: 
        # 查询所有卡数据
        cards= query_all_from_table('cards')
        card_holders = query_all_from_table('card_holder')
        # 打印调试信息
        print(f"查询到 {len(cards) if cards else 0} 条卡记录")
        print(f"查询到 {len(card_users) if card_users else 0} 条用卡人记录")
        return render_template('main/cards.html', cards=cards, card_holders=card_holders)
    except Exception as e:
        print(f"查询卡数据时出错: {str(e)}")
        # 返回空列表，避免模板渲染错误
        return render_template('main/cards.html', cards=[], card_holders=[])