from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for
from ucard.blueprint.auth import login_required
from comm.gsalay_api import GSalaryAPI
from datetime import datetime
from comm.db_api import insert_database, query_all_from_table, update_database, create_db_connection, query_database,delete_single_data
from sync.realtime import realtime_card_info_update, modify_response_data_insert,realtime_insert_payers_info,realtime_insert_payers,realtime_update_payers
from comm.db_api import batch_update_database

import time
import uuid


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
    
def wallet_balance_transform(data):
    result = {}
    for item in data:
        available = item.get('available')
        if available is None:
            continue  # 跳过available为None的条目
        version = item['version']
        currency = item['currency']
        amount = item['amount']
        
        # 转换为字符串
        amount_str = str(amount)
        available_str = str(available)

        currency_info = {
            'amount': amount_str,
            'available': available_str
        }
        # 更新到结果字典中
        if version not in result:
            result[version] = {}
        result[version][currency] = currency_info
    return result


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
    
@main_bp.route('/exchange_usdt')
@login_required
def exchange_usdt():
    try:
        # 查询汇率
        exchange_usdt = query_all_from_table('exchange_usdt')
        regions = query_all_from_table('region')
        rate_ctrl = query_all_from_table('rate_ctrl')
        exchange_merchants = query_all_from_table('exchange_merchants')
        
        # 打印调试信息
        print(f"查询到 {len(exchange_usdt) if exchange_usdt else 0} 条汇率记录")
        print(f"查询到 {len(regions) if regions else 0} 条地区记录")
        print(f"查询到 {len(exchange_merchants) if exchange_merchants else 0} 条兑换商记录")
        
        # 如果数据为空，添加测试数据（仅用于测试前端显示）
        if not exchange_usdt or len(exchange_usdt) == 0:
            # 添加测试数据，仅用于开发阶段
            print("未找到钱包余额数据，使用测试数据")
        
        # 将数据转换为JSON并返回给前端
        return render_template('main/exchange_usdt.html', exchange_usdt=exchange_usdt, regions=regions, rate_ctrl=rate_ctrl, exchange_merchants=exchange_merchants)
    except Exception as e:
        print(f"查询汇率数据时出错: {str(e)}")
        # 返回空列表，避免模板渲染错误
        return render_template('main/exchange_usdt.html', exchange_usdt=[], regions=[], rate_ctrl=[], exchange_merchants=[])
    
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
        print(f"查询到 {len(wallet_transactions) if wallet_transactions else 0} 条交易明细记录")
        
        # 如果数据为空，添加测试数据（仅用于测试前端显示）
        if not wallet_balances or len(wallet_balances) == 0:
            # 添加测试数据，仅用于开发阶段
            print("未找到钱包余额数据，使用测试数据")
            wallet_balances = [
                {"currency": "USD", "amount": 936.12, "user_id": "test_user", "update_time": "2023-03-13 18:48:52"}
            ]
           
        # 将数据转换为JSON并返回给前端
        return render_template('main/wallet_transactions.html', wallet_balances=wallet_balances, wallet_transactions=wallet_transactions, regions=regions)
    except Exception as e:
        print(f"查询钱包数据时出错: {str(e)}")
        # 返回空列表，避免模板渲染错误
        return render_template('main/wallet_transactions.html', wallet_balances=[], wallet_transactions=[], regions=[])

@main_bp.route('/daily')
@login_required
def daily():
    try:
        # 查询钱包交易记录
        wallet_transactions = query_all_from_table('wallet_transactions')
        # 查询钱包余额
        wallet_balances = query_all_from_table('wallet_balance')
        # 
        cards = query_all_from_table('cards')
        # 
        balance_history = query_all_from_table('balance_history')
        card_transactions = query_all_from_table('card_transactions')     
        # 打印调试信息
        print(f"查询到 {len(cards) if cards else 0} 条卡记录")
        print(f"查询到 {len(balance_history) if balance_history else 0} 条交易明细记录")
        print(f"查询到 {len(card_transactions) if card_transactions else 0} 条卡交易明细记录")
        # 如果数据为空，添加测试数据（仅用于测试前端显示）
        if not cards or len(cards) == 0:
            # 添加测试数据，仅用于开发阶段
            print("未找到卡数据，使用测试数据")
                    
        # 将数据转换为JSON并返回给前端
        return render_template('main/daily.html', cards=cards, balance_history=balance_history, card_transactions=card_transactions, wallet_transactions=wallet_transactions, wallet_balances=wallet_balances)
    except Exception as e:
        print(f"查询钱包数据时出错: {str(e)}")
        # 返回空列表，避免模板渲染错误
        return render_template('main/daily.html', cards=[], balance_history=[], card_transactions=[],wallet_transactions=[],wallet_balances=[])
    
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
    # 对列表进行排序，按 transaction_time 倒序排列
    sorted_balance_history = sorted(balance_history, key=lambda x: convert_time(x["transaction_time"]), reverse=True)
    return render_template('main/balance_history.html', balance_history=sorted_balance_history)


@main_bp.route('/all_cards')
@login_required
def all_cards():
    return render_template('main/all_cards.html')

@main_bp.route('/statistics')
@login_required
def statistics():
    return render_template('main/statistics.html')


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
@login_required
def card_holder_edit_page():
    """渲染用卡人编辑页面"""
    return render_template('main/card_user_edit.html')

@main_bp.route('/card_holders/edit', methods=['PUT']) 
@login_required
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
        cards_all_info = query_all_from_table('cards_all_info')
        card_holders = query_all_from_table('card_holder')
        wallet_balance = query_all_from_table('wallet_balance')
        transform_wallet_balance = wallet_balance_transform(wallet_balance)
        sorted_cards_all_info = sorted(cards_all_info, key=lambda x: convert_time(x["create_time"]), reverse=True)      
        # 打印调试信息
        print(f"查询到 {len(cards_all_info) if cards_all_info else 0} 条卡记录")
        print(f"查询到 {len(card_holders) if card_holders else 0} 条用卡人记录")
        return render_template('main/cards.html', cards_all_info=sorted_cards_all_info, card_holders=card_holders, wallet_balance=transform_wallet_balance)
    except Exception as e:
        print(f"查询卡数据时出错: {str(e)}")
        # 返回空列表，避免模板渲染错误
        return render_template('main/cards.html', cards_all_info=[], card_holders=[])
    
# 开卡页面路由
@main_bp.route('/cards/cards_apply')
def cards_apply():
    card_holders = query_all_from_table('card_holder')
    cards_product = query_all_from_table('cards_product')
    wallet_balance = query_all_from_table('wallet_balance')
    transform_wallet_balance = wallet_balance_transform(wallet_balance)

    return render_template('main/cards_apply.html', card_holders=card_holders, cards_product=cards_product, wallet_balance=transform_wallet_balance)

@main_bp.route('/cards/newcard', methods=['POST'])
@login_required
def apply_new_card():
    try:
        # 获取表单数据
        data = request.get_json()
        request_id = str(uuid.uuid4())
        # {'currency': 'USD', 'card_holder_id': '2025031513232401010010302501', 'init_balance': '0', 'limit_per_day': '', 'limit_per_month': '', 'limit_per_transaction': '', 'product_code': 'G68796'}
        version = data.pop('platform')
        data['request_id'] = request_id
        print(data)
        # 创建API实例
        gsalary_api = GSalaryAPI()
        
        # 调用API创建用卡人
        result = gsalary_api.apply_new_card(version, data)
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
    
# 冻结或者解冻卡片
@main_bp.route('/cards/freeze_unfreeze', methods=['PUT'])
@login_required
def cards_freeze_unfreeze():
    try:
        # 获取表单数据
        data = request.get_json()
        card_id = data.pop('card_id')
        version = data.pop('version')
        gsalary_api = GSalaryAPI()
        # 调用API进行冻结或者解冻
        result = gsalary_api.freeze_unfreeze_card(system_id=version, card_id=card_id, data= data)
        if data['freeze']:
            if result['result']['result'] == 'S':
                time.sleep(15)
                realtime_card_info_update(version, card_id)
                return jsonify({
                    "code": 0,
                    "msg": "冻结成功",
                    "data": result
                })
            else:
                return jsonify({
                    "code": 1,
                    "msg": "冻结失败",
                    "data": None
                })
        else:
            if result['result']['result'] == 'S':
                time.sleep(15)
                realtime_card_info_update(version, card_id)
                return jsonify({
                    "code": 0,
                    "msg": "解冻成功",
                    "data": result
                })
            else:
                return jsonify({
                    "code": 1,
                    "msg": "解冻失败",
                    "data": None
                })
    except Exception as e:
        return jsonify({
            "code": 1,
            "msg": f"发生错误: {str(e)}",
            "data": None
        })
    
# 冻结或者解冻卡片
@main_bp.route('/cards/cancel_card', methods=['DELETE'])
@login_required
def cancel_card():
    try:
        # 获取表单数据
        data = request.get_json()
        print(data)
        card_id = data.pop('card_id')
        version = data.pop('version')
        gsalary_api = GSalaryAPI()
        result = gsalary_api.cancel_card(system_id=version, card_id=card_id)
        
        if result['result']['result'] == 'S':
            time.sleep(15)
            realtime_card_info_update(version, card_id)
            return jsonify({
                "code": 0,
                "msg": "销卡成功",
                "data": result
            })
        else:
            return jsonify({
                "code": 1,
                "msg": "销卡失败",
                "data": None
            })
    except Exception as e:
        return jsonify({
            "code": 1,
            "msg": f"发生错误: {str(e)}",
            "data": None
        })

@main_bp.route('/cards/modify_card_balance')
@login_required
def modify_card_balance():
    return render_template('main/modify_card_balance.html')

# 调额
@main_bp.route('/cards/modify_card', methods=['POST'])
@login_required
def modify_card():
    try:
        # 获取表单数据
        data = request.get_json()
        request_id = str(uuid.uuid4())
        data['request_id'] = request_id
        version = data.pop('version')
        gsalary_api = GSalaryAPI()
        result = gsalary_api.modify_card_balance(system_id=version, data = data)
        if result['result']['result'] == 'S':
            modify_response_data_insert(version = version, result = result)
            if result['data']['status'] == 'SUCCESS':
                return jsonify({
                    "code": 0,
                    "msg": "调额成功",
                    "data": result
                })
            else:
                return jsonify({
                "code": 1,
                "msg": "调额失败",
                "data": None
            })
        else:
            return jsonify({
                "code": 1,
                "msg": "服务器访问出错，调额失败",
                "data": None
            })
    except Exception as e:
        return jsonify({
            "code": 1,
            "msg": f"发生错误: {str(e)}",
            "data": None
        })


@main_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """管理员密码修改功能"""
    if request.method == 'GET':
        # 渲染密码修改页面，并在页面中显示当前登录的用户名
        user_account = session.get('user_account', '')
        print(f"当前登录用户: {user_account}")
        return render_template('main/change_password.html')
    
    # 处理POST请求，接收JSON数据
    data = request.get_json()
    
    if not data:
        return jsonify({
            'code': 1,
            'msg': '请求数据无效'
        })
    
    # 获取表单数据
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    # 验证数据完整性
    if not all([old_password, new_password, confirm_password]):
        return jsonify({
            'code': 1,
            'msg': '请填写所有必填字段'
        })
    
    # 验证新密码与确认密码是否一致
    if new_password != confirm_password:
        return jsonify({
            'code': 1,
            'msg': '两次输入的新密码不一致'
        })
    
    try:
        # 获取当前登录的管理员账号
        admin_account = session.get('user_account')
        
        print(f"获取到的管理员账号: {admin_account}")
        
        if not admin_account:
            return jsonify({
                'code': 1,
                'msg': '无法获取当前登录信息，请重新登录'
            })
        
        # 查询管理员信息，验证原密码
        admin_list = query_all_from_table('admins')
        print(f"管理员列表: {admin_list}")
        
        current_admin = None
        for admin in admin_list:
            if admin.get('admin_account') == admin_account:
                current_admin = admin
                break
        
        if not current_admin:
            return jsonify({
                'code': 1,
                'msg': '当前管理员账号不存在'
            })
        
        # 验证原密码是否正确
        if current_admin.get('admin_password') != old_password:
            return jsonify({
                'code': 1,
                'msg': '原密码不正确'
            })
        
        # 更新密码
        update_data = [{
            'admin_account': admin_account,
            'admin_password': new_password
        }]
        
        # 正确调用batch_update_database方法
        result = batch_update_database('admins', update_data, 'admin_account')
        
        if result:
            # 更新成功
            return jsonify({
                'code': 0,
                'msg': '密码修改成功'
            })
        else:
            # 更新失败
            return jsonify({
                'code': 1,
                'msg': '密码修改失败，请稍后重试'
            })
            
    except Exception as e:
        # 记录错误日志
        print(f"修改密码时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}'
        })


@main_bp.route('/add_system')
@login_required
def add_system():
    """添加平台页面"""
    return render_template('main/add_system.html')

@main_bp.route('/api/add_system', methods=['POST'])
@login_required
def api_add_system():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 1,
                'msg': '请求数据为空'
            })
            
        appid = data.get('appid')
        key = data.get('key')
        system = data.get('system')
        
        print(f"收到平台添加请求: appid={appid}, system={system}")
        
        if not appid or not key or not system:
            print("平台信息不完整")
            return jsonify({
                'code': 1,
                'msg': '平台信息不完整，请填写所有必填项'
            })
        
        # 检查是否已存在相同的平台
        existing_system = query_database('system_key', 'system', system)
        print(f"查询现有平台结果: {existing_system}")
        
        if existing_system:
            print(f"平台 {system} 已存在")
            return jsonify({
                'code': 1,
                'msg': '该平台已存在'
            })
        
        try:
            conn = create_db_connection()
            if conn is None:
                print("数据库连接失败")
                return jsonify({
                    'code': 1,
                    'msg': '数据库连接失败'
                })
                
            cursor = conn.cursor()
            
            # 先获取最大的ID值
            try:
                cursor.execute("SELECT MAX(id) FROM system_key")
                max_id = cursor.fetchone()[0]
                if max_id is None:
                    new_id = 1
                else:
                    new_id = max_id + 1
            except Exception as e:
                print(f"获取最大ID时出错: {str(e)}")
                new_id = 1  # 如果查询失败，默认使用1作为ID
                
            print(f"使用新ID: {new_id}")
            
            # 手动构建插入SQL，包含id字段
            sql = "INSERT INTO system_key (id, appid, `key`, system) VALUES (%s, %s, %s, %s)"
            val = (new_id, appid, key, system)
            
            print(f"执行SQL: {sql}, 参数: {val}")
            
            cursor.execute(sql, val)
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"成功插入平台 {system}")
                return jsonify({
                    'code': 0,
                    'msg': '添加平台成功'
                })
            else:
                print("插入失败，没有行受影响")
                return jsonify({
                    'code': 1,
                    'msg': '添加平台失败，没有数据被插入'
                })
                
        except Exception as e:
            print(f"插入数据时出错: {str(e)}")
            return jsonify({
                'code': 1,
                'msg': f'添加平台失败: {str(e)}'
            })
            
    except Exception as e:
        print(f"添加平台时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}'
        })



    
# 修改卡信息包括卡昵称和每日限额，每月限额，单笔交易限额
@main_bp.route('/cards/modify_card_info', methods=['PUT'])
@login_required
def modify_card_info():
    try:
        # 获取表单数据
        data = request.get_json()
        version = data.pop('version')
        card_id = data.pop('card_id')
        type = data.pop('type')
        if type == 'nickname':
            msg = '卡昵称'
        elif type == 'limit':
            msg = '限额'
            
        gsalary_api = GSalaryAPI()
        result = gsalary_api.modify_card(system_id=version, card_id=card_id, data = data)
        if result['result']['result'] == 'S':
            time.sleep(15)
            realtime_card_info_update(version, card_id)
            return jsonify({
                "code": 0,
                "msg": f"{msg}修改成功",
                "data": result
            })
        else:
            return jsonify({
                "code": 1,
                "msg": f"{msg}修改失败",
                "data": None
            })
    except Exception as e:
        return jsonify({
            "code": 1,
            "msg": f"发生错误: {str(e)}",
            "data": None
        })

@main_bp.route('/api/get_all_systems', methods=['GET'])
@login_required
def api_get_all_systems():
    try:
        # 查询所有平台数据
        systems = query_all_from_table('system_key')
        
        # 确保返回的数据是列表格式
        if systems is None:
            systems = []
        
        # 直接返回系统列表，不做额外处理
        print(f"查询到 {len(systems)} 条平台数据: {systems}")
        
        return jsonify({
            'code': 0,  # 成功码为0
            'msg': '获取平台列表成功',
            'count': len(systems),
            'data': systems
        })
    except Exception as e:
        print(f"获取平台列表时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}',
            'count': 0,
            'data': []
        })




@main_bp.route('/api/update_system', methods=['POST'])
@login_required
def api_update_system():
    try:
        data = request.get_json()
        system_id = data.get('id')
        
        if not system_id:
            return jsonify({
                'code': 1,
                'msg': '平台ID不能为空'
            })
        
        # 更新数据，使用反引号转义key字段
        update_data = {
            'appid': data.get('appid'),
            '`key`': data.get('key'),  # 使用反引号转义key字段
            'system': data.get('system')
        }
        
        # 更新平台数据
        result = update_database('system_key', {'id': system_id}, update_data)
        
        if result:
            return jsonify({
                'code': 0,
                'msg': '更新平台成功'
            })
        else:
            return jsonify({
                'code': 1,
                'msg': '更新平台失败'
            })
    except Exception as e:
        print(f"更新平台时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}'
        })

@main_bp.route('/api/delete_system', methods=['POST'])
@login_required
def api_delete_system():
    try:
        data = request.get_json()
        system_id = data.get('id')
        
        if not system_id:
            return jsonify({
                'code': 1,
                'msg': '平台ID不能为空'
            })
        
        # 直接删除平台数据
        conn = create_db_connection()
        if conn is None:
            return jsonify({
                'code': 1,
                'msg': '数据库连接失败'
            })
            
        cursor = conn.cursor()
        try:
            # 构建删除SQL语句
            sql = "DELETE FROM system_key WHERE id = %s"
            cursor.execute(sql, (system_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return jsonify({
                    'code': 0,
                    'msg': '删除平台成功'
                })
            else:
                return jsonify({
                    'code': 1,
                    'msg': '未找到要删除的平台'
                })
        except Exception as e:
            conn.rollback()
            print(f"删除平台时出错: {str(e)}")
            return jsonify({
                'code': 1,
                'msg': f'系统错误: {str(e)}'
            })
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"删除平台时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}'
        })
@main_bp.route('/payees')
@login_required
def payees():
    try: 
        # 查询所有卡数据
        payees_info_data = query_all_from_table('payees_info')
        available_payment_methods = query_all_from_table('payees_availpay_methods')     
        print(available_payment_methods)
        print(payees_info_data)
        # 打印调试信息
        print(f"查询到 {len(payees_info_data) if payees_info_data else 0} 条收款人数据")
        print(f"查询到 {len(available_payment_methods) if available_payment_methods else 0} 条可用付款方式数据")
        return render_template('main/payees.html', payees_info_data=payees_info_data, available_payment_methods=available_payment_methods)
    except Exception as e:
        print(f"查询收款人或付款方式数据时出错: {str(e)}")
        # 返回空列表，避免模板渲染错误
        return render_template('main/payees.html', payees_info_data=[], available_payment_methods=[])
    
# 付款人页面路由
@main_bp.route('/payers',)
@login_required
def payers():
    try: 
        payers_info_data = query_all_from_table('payers_info')
        # 打印调试信息
        print(f"查询到 {len(payers_info_data) if payers_info_data else 0} 条付款人数据")
        return render_template('main/payers.html', payers_info_data=payers_info_data)
    except Exception as e:
        print(f"查询付款人数据时出错: {str(e)}")
        # 返回空列表，避免模板渲染错误
        return render_template('main/payers.html', payers_info_data=[])

# 添加付款人页面路由
@main_bp.route('/payers/add_page')
@login_required
def payer_add_page():
    """渲染添加付款人页面"""
    # 返回完整的HTML页面，适用于iframe加载
    return render_template('main/payer_add.html')
    
@main_bp.route('/payers/upload_file', methods=['POST'])
@login_required
def payers_upload_file():
    try:
        # 获取表单数据
        print('-------------------------------------------------this is upload file-------------------------------------------------')
        data = request.get_json()
        version = data.pop('version')
        print(data) 
        print(version)
        gsalary_api = GSalaryAPI()
        result = gsalary_api.upload_payer_file(system_id=version, data=data)
        print(result)
        if result['result']['result'] == 'S':
            print('-------------------------------------------------this is upload file success end-------------------------------------------------')
            return jsonify({
                "code": 0,
                "msg": "上传成功",
                "data": result
            })
        else:
            return jsonify({
                "code": 1,
                "msg": "上传失败",
                "data": None
            })
    except Exception as e:
        return jsonify({
            "code": 1,
            "msg": f"发生错误: {str(e)}",
            "data": None
        })
    
@main_bp.route('/payers/add', methods=['POST'])
@login_required
def payers_add():
    try:
        print('-------------------------------------------------this is add payer-------------------------------------------------')
        data = request.get_json()
        print(data)
        version = data.pop('version')
        gsalary_api = GSalaryAPI()
        result = gsalary_api.create_payer(system_id=version, data=data)
        if result['result']['result'] == 'S':
            print('-------------------------------------------------this is add payer insert database-------------------------------------------------')
            print(result)
            realtime_insert_payers(version)
            realtime_insert_payers_info(version, result)
            print('数据更新成功')
            print('-------------------------------------------------this is add payer success end-------------------------------------------------')
            return jsonify({
                "code": 0,
                "msg": "创建成功",
                "data": result
            })
        else:
            return jsonify({
                "code": 1,  
                "msg": "创建失败",
                "data": None
            })
    except Exception as e:
        return jsonify({
            "code": 1,  
            "msg": f"发生错误: {str(e)}",
            "data": None
        })

@main_bp.route('/payers/delete', methods=['DELETE'])
@login_required
def payers_delete():
    try:
        data = request.get_json()
        version = data.pop('version')
        payer_id = data.pop('payer_id')
        conditions = {
            'payer_id': payer_id,
            'version': version
        }
        gsalary_api = GSalaryAPI()
        result = gsalary_api.delete_payer(system_id=version, payer_id=payer_id)
        if result['result']['result'] == 'S':
            delete_payers_info_result = delete_single_data('payers_info', conditions)
            delete_payers_result = delete_single_data('payers', conditions)
            if delete_payers_info_result and delete_payers_result:
                print('-------------------------------------------------this is delete payer success end-------------------------------------------------')
                return jsonify({
                    "code": 0,
                    "msg": "官方和本地数据删除成功",
                    "data": result
                })
            else:
                return jsonify({
                    "code": 1,
                    "msg": "官方和本地数据删除失败",
                    "data": None
                })
        else:
            return jsonify({
                "code": 1,
                "msg": "官方删除失败",
                "data": None
            })
    except Exception as e:
        return jsonify({
            "code": 1,
            "msg": f"发生错误: {str(e)}",
            "data": None
        })

@main_bp.route('/wallet_manage')
@login_required
def wallet_manage():
    try:
        # 查询钱包管理数据
        percent_data = query_all_from_table('percent')
        
        # 打印调试信息
        print(f"查询到 {len(percent_data) if percent_data else 0} 条钱包管理记录")
        
        # 将数据转换为JSON并返回给前端
        return render_template('main/wallet_manage.html', percent_data=percent_data)
    except Exception as e:
        print(f"查询钱包管理数据时出错: {str(e)}")
        # 返回空列表，避免模板渲染错误
        return render_template('main/wallet_manage.html', percent_data=[])

@main_bp.route('/api/wallet_manage/list', methods=['GET'])
@login_required
def api_wallet_manage_list():
    try:
        # 查询钱包管理数据
        percent_data = query_all_from_table('percent')
        
        # 打印调试信息
        print(f"API查询到 {len(percent_data) if percent_data else 0} 条钱包管理记录")
        
        return jsonify({
            'code': 0,
            'msg': '获取钱包管理数据成功',
            'count': len(percent_data),
            'data': percent_data
        })
    except Exception as e:
        print(f"获取钱包管理数据时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'获取钱包管理数据失败: {str(e)}',
            'count': 0,
            'data': []
        })

@main_bp.route('/api/wallet_manage/add', methods=['POST'])
@login_required
def api_wallet_manage_add():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 1,
                'msg': '请求数据为空'
            })
        
        # 构建插入数据
        insert_data = [data]  # 封装成列表，适配insert_database方法
        
        print(f"准备插入钱包管理数据: {insert_data}")
        
        try:
            # 执行插入操作
            insert_database('percent', insert_data)
            
            # 如果没有抛出异常，则视为插入成功
            print("钱包管理数据插入成功")
            return jsonify({
                'code': 0,
                'msg': '添加钱包管理数据成功'
            })
        except Exception as e:
            print(f"钱包管理数据插入过程中出错: {str(e)}")
            return jsonify({
                'code': 1,
                'msg': f'添加钱包管理数据失败: {str(e)}'
            })
            
    except Exception as e:
        print(f"添加钱包管理数据时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}'
        })

@main_bp.route('/api/wallet_manage/update', methods=['POST'])
@login_required
def api_wallet_manage_update():
    try:
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({
                'code': 1,
                'msg': '请求数据无效或缺少ID'
            })
        
        # 提取ID作为条件
        record_id = data.pop('id')
        condition = {'id': record_id}
        
        print(f"准备更新钱包管理数据: ID={record_id}, 数据={data}")
        
        try:
            # 执行更新操作
            update_database('percent', condition, data)
            
            # 如果没有抛出异常，则视为更新成功
            print(f"钱包管理数据 ID={record_id} 更新成功")
            return jsonify({
                'code': 0,
                'msg': '更新钱包管理数据成功'
            })
        except Exception as e:
            print(f"钱包管理数据更新过程中出错: {str(e)}")
            return jsonify({
                'code': 1,
                'msg': f'更新钱包管理数据失败: {str(e)}'
            })
            
    except Exception as e:
        print(f"更新钱包管理数据时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}'
        })

@main_bp.route('/api/wallet_manage/delete', methods=['POST'])
@login_required
def api_wallet_manage_delete():
    try:
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({
                'code': 1,
                'msg': '请求数据无效或缺少ID'
            })
        
        record_id = data['id']
        
        # 通过数据库连接直接删除数据
        conn = create_db_connection()
        if conn is None:
            return jsonify({
                'code': 1,
                'msg': '数据库连接失败'
            })
            
        cursor = conn.cursor()
        try:
            # 构建删除SQL语句
            sql = "DELETE FROM percent WHERE id = %s"
            cursor.execute(sql, (record_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return jsonify({
                    'code': 0,
                    'msg': '删除钱包管理数据成功'
                })
            else:
                return jsonify({
                    'code': 1,
                    'msg': '未找到要删除的数据'
                })
        except Exception as e:
            conn.rollback()
            print(f"删除钱包管理数据时出错: {str(e)}")
            return jsonify({
                'code': 1,
                'msg': f'系统错误: {str(e)}'
            })
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"删除钱包管理数据时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}'
        })
@main_bp.route('/payers/update', methods=['PUT'])
@login_required
def payers_update():
    try:
        data = request.get_json()
        version = data.pop('version')
        payer_id = data.pop('payer_id')
        gsalary_api = GSalaryAPI()
        result = gsalary_api.update_payer(system_id=version, payer_id=payer_id, data=data)
        if result['result']['result'] == 'S':
            realtime_update_payers(version, payer_id, result)
            return jsonify({
                "code": 0,
                "msg": "更新成功",
                "data": result
            })
        else:
            return jsonify({
                "code": 1,
                "msg": "更新失败",
                "data": None
            })
    except Exception as e:
        return jsonify({
            "code": 1,
            "msg": f"发生错误: {str(e)}",
            "data": None
        })
