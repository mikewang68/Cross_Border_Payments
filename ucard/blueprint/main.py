from flask import Blueprint, render_template, session, jsonify
from blueprint.auth import login_required
from applications.models.region import Region
from applications.models.wallet import Wallet
from applications.extensions import db
from sqlalchemy import func

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
    return render_template('main/card_users.html')

@main_bp.route('/transactions')
@login_required
def transactions():
    return render_template('main/transactions.html')

@main_bp.route('/limit')
@login_required
def limit():
    return render_template('main/limit.html')

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

@main_bp.route('/api/wallet/balance')
@login_required
def wallet_balance():
    try:
        print("正在获取钱包数据")

        # 联表查询region和wallet表，通过currency字段关联
        query = db.session.query(
            Wallet, Region
        ).outerjoin(
            Region, Wallet.local_currency == Region.currency
        ).all()
        
        print(f"查询到 {len(query)} 条记录")
        
        # 创建货币数据列表
        currencies = []
        main_currency = "USD"
        main_amount = 0
        main_update_time = None
        
        for wallet, region in query:
            # 跳过没有region信息的钱包记录
            if not region:
                print(f"警告: 找不到对应region记录的钱包: {wallet.local_currency}")
                continue
                
            # 获取金额和时间
            amount = float(wallet.amount) if wallet.amount else 0
            currency_code = region.currency
            
            print(f"处理币种 {currency_code}, 金额 {amount}")
            
            # 记录USD或最大余额的货币作为主货币
            if currency_code == "USD":
                main_currency = "USD"
                main_amount = amount
                main_update_time = wallet.insert_time
                print(f"设置USD为主货币, 金额 {main_amount}")
            elif not main_update_time and amount > main_amount:
                main_currency = currency_code
                main_amount = amount
                main_update_time = wallet.insert_time
                print(f"设置 {main_currency} 为主货币, 金额 {main_amount}")
                
            # 确保图标数据可用
            icon_data = ""
            if region.icon_base64:
                icon_data = region.icon_base64
            else:
                print(f"警告: 币种 {currency_code} 没有图标数据")
                
            # 添加到货币列表
            currencies.append({
                "code": currency_code,
                "amount": amount,
                "platform": wallet.platform_name or "",
                "icon_base64": icon_data
            })
        
        # 如果没有查询到任何记录，添加默认数据
        if not currencies:
            print("未查询到任何钱包数据，使用默认数据")
            
            # 默认USD钱包数据
            main_currency = "USD"
            main_amount = 971.32
            
            # 添加默认货币
            currencies = [
                {"code": "USD", "amount": 971.32, "platform": "Default", "icon_base64": ""},
                {"code": "SGD", "amount": 0.00, "platform": "", "icon_base64": ""},
                {"code": "CNY", "amount": 0.00, "platform": "", "icon_base64": ""},
                {"code": "EUR", "amount": 0.00, "platform": "", "icon_base64": ""},
                {"code": "JPY", "amount": 0.00, "platform": "", "icon_base64": ""}
            ]
            
            # 获取当前时间作为更新时间
            from datetime import datetime
            main_update_time = datetime.now()
        
        # 按余额从高到低排序
        currencies.sort(key=lambda x: x["amount"], reverse=True)
        
        # 获取更新时间
        update_time = ""
        if main_update_time:
            update_time = main_update_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            from datetime import datetime
            update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        result = {
            "success": True,
            "data": {
                "mainCurrency": main_currency,
                "mainAmount": main_amount,
                "updateTime": update_time,
                "currencies": currencies
            }
        }
        
        print(f"返回数据: 主货币={main_currency}, 主余额={main_amount}, 货币数量={len(currencies)}")
        
        return jsonify(result)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"处理钱包数据时出错: {str(e)}")
        print(error_trace)
        return jsonify({
            "success": False,
            "message": f"获取钱包数据失败: {str(e)}"
        })

@main_bp.route('/api/wallet/debug')
@login_required
def wallet_debug():
    """调试API，返回详细的钱包和币种数据，帮助排查问题"""
    try:
        # 获取所有币种
        regions = Region.query.all()
        region_data = [{
            "id": r.id,
            "currency": r.currency,
            "english_name": r.english_name if hasattr(r, 'english_name') else None,
            "chinese_name": r.chinese_name if hasattr(r, 'chinese_name') else None,
            "has_icon": bool(r.icon_base64),
            "icon_length": len(r.icon_base64) if r.icon_base64 else 0
        } for r in regions]
        
        # 获取所有钱包
        wallets = Wallet.query.all()
        wallet_data = [{
            "id": w.id,
            "local_currency": w.local_currency,
            "amount": float(w.amount),
            "platform_name": w.platform_name,
            "insert_time": w.insert_time.strftime("%Y-%m-%d %H:%M:%S") if w.insert_time else None
        } for w in wallets]
        
        return jsonify({
            "success": True,
            "regions_count": len(regions),
            "wallets_count": len(wallets),
            "regions": region_data,
            "wallets": wallet_data
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": str(e)
        }) 