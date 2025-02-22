# 项目模型文件
from exts import db
from datetime import datetime


# 创建一个模型 (如果你想使用 ORM)

class ExchangeUSDT(db.Model):
    __tablename__ = 'exchange_usdt'
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(10))
    official_rate = db.Column(db.Float)
    exchange_provider = db.Column(db.String(50))
    fee = db.Column(db.Float)
    usdt_cost = db.Column(db.Float)
    index_quote = db.Column(db.Float)
    percentage = db.Column(db.Float)
    percentage_quote = db.Column(db.Float)

    def __repr__(self):
        return f"<ExchangeUSDT {self.currency}>"
