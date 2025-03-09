from flask import Flask, render_template
from applications.extensions import init_plugs, db
import os
from datetime import datetime

# 创建Flask应用
app = Flask(__name__)

# 加载配置
app.config.from_object('applications.config')

# 设置session密钥
app.secret_key = os.urandom(24)

# 初始化插件（包含数据库初始化）
init_plugs(app)

# 注册蓝图
def register_blueprints(app):
    from blueprint.main import main_bp
    from blueprint.auth import auth_bp
    from applications.views.card_users import card_users_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(card_users_bp)
    
    # 添加用卡人表单页面路由
    @app.route('/card_holders/add')
    def card_holder_add():
        return render_template('main/card_user_add.html')

# 注册蓝图
register_blueprints(app)

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500

# 初始化数据库函数
def initialize_database():
    try:
        from applications.models.wallet import Wallet
        from applications.models.region import Region
        from datetime import datetime
        
        # 当前时间
        now = datetime.now()
        
        # 检查是否有 region 数据
        regions = Region.query.all()
        
        # 检查是否有 wallet 数据
        wallets = Wallet.query.all()
        
        # 如果没有钱包数据，初始化测试数据
        if not wallets:
            # 为USD创建钱包，余额为971.32
            usd_wallet = Wallet(
                amount=971.32000,
                local_currency="USD",
                platform_name="Default",
                insert_time=now
            )
            db.session.add(usd_wallet)
            
            # 为其他币种创建钱包，余额为0
            if regions:
                for region in regions:
                    if region.currency and region.currency != "USD":
                        wallet = Wallet(
                            amount=0.00000,
                            local_currency=region.currency,
                            platform_name="Default",
                            insert_time=now
                        )
                        db.session.add(wallet)
                
                # 特别添加一个SGD钱包示例
                sgd_wallet = Wallet(
                    amount=0.00000,
                    local_currency="SGD",
                    platform_name="",
                    insert_time=datetime(2025, 3, 9, 20, 51, 12)
                )
                db.session.add(sgd_wallet)
                
                db.session.commit()
                print('钱包数据自动初始化成功')
    except Exception as e:
        print(f'钱包数据自动初始化失败: {str(e)}')

# 在应用上下文中运行初始化
with app.app_context():
    initialize_database()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
