from applications.extensions import db
from datetime import datetime

class Wallet(db.Model):
    __tablename__ = 'wallet'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    local_currency = db.Column(db.String(50), nullable=False)  # 本地货币，对应region表的currency
    amount = db.Column(db.Numeric(15, 5), default=0)  # 账户金额，最大支持15位数，5位小数
    platform_name = db.Column(db.String(255))  # 平台名称
    insert_time = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间

    def __repr__(self):
        return f"<Wallet {self.id}:{self.local_currency}>" 