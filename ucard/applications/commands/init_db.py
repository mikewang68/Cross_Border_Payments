import click
from flask.cli import with_appcontext
from applications.extensions import db
from applications.models.wallet import Wallet
from applications.models.region import Region
from datetime import datetime

@click.command('init-wallet')
@with_appcontext
def init_wallet_command():
    """初始化钱包数据"""
    try:
        # 检查是否有region数据
        regions = Region.query.all()
        if not regions:
            click.echo('没有找到region数据，请先初始化region表')
            return
        
        # 当前时间
        now = datetime.now()
        
        # 为USD创建钱包，余额为971.32
        usd_wallet = Wallet.query.filter_by(local_currency="USD").first()
        
        if not usd_wallet:
            usd_wallet = Wallet(
                amount=971.32000,
                local_currency="USD",
                platform_name="Default",
                insert_time=now
            )
            db.session.add(usd_wallet)
        else:
            usd_wallet.amount = 971.32000
            usd_wallet.platform_name = "Default"
            usd_wallet.insert_time = now
        
        # 为其他币种创建钱包，余额为0
        for region in regions:
            if region.currency and region.currency != "USD":
                wallet = Wallet.query.filter_by(local_currency=region.currency).first()
                
                if not wallet:
                    wallet = Wallet(
                        amount=0.00000,
                        local_currency=region.currency,
                        platform_name="Default",
                        insert_time=now
                    )
                    db.session.add(wallet)
        
        # 添加一个SGD钱包，匹配图片中的例子
        sgd_wallet = Wallet.query.filter_by(local_currency="SGD").first()
        if sgd_wallet:
            sgd_wallet.amount = 0.00000
            sgd_wallet.platform_name = ""
            sgd_wallet.insert_time = datetime(2025, 3, 9, 20, 51, 12)
        else:
            sgd_wallet = Wallet(
                amount=0.00000,
                local_currency="SGD",
                platform_name="",
                insert_time=datetime(2025, 3, 9, 20, 51, 12)
            )
            db.session.add(sgd_wallet)
        
        db.session.commit()
        click.echo('钱包数据初始化成功')
    except Exception as e:
        db.session.rollback()
        click.echo(f'钱包数据初始化失败: {str(e)}')

def init_app(app):
    app.cli.add_command(init_wallet_command) 