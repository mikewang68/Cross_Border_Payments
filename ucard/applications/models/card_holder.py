# 项目模型文件
from applications.extensions import db
from datetime import datetime


# 创建一个模型 (如果你想使用 ORM)
class card_holder(db.Model):
    __tablename__ = 'card_holder'  # 假设表名为user

    # 主键字段（根据"键"列标记推断）
    user_code = db.Column(db.String(255), primary_key=True)  # 长度255，主键
    
    # 必填字段（根据"不是null"列勾选推断）
    user_id = db.Column(db.String(255), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(255))
    # 注意：birth_date在实际数据库中不存在，因此注释掉
    # birth_date = db.Column(db.String(255))
    mobile = db.Column(db.String(255), nullable=True)  # 手机号设为可空
    email = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255))
    state = db.Column(db.String(255))
    city = db.Column(db.String(255))
    address = db.Column(db.String(255))
    # 注意：postcode在实际数据库中不存在，因此注释掉
    # postcode = db.Column(db.String(255))
    # create_time = db.Column(db.String(255))
    # user_key = db.Column(db.String(255))
    # status = db.Column(db.String(255))
    # qd_id = db.Column(db.String(255))
    # qd_name = db.Column(db.String(255))
    # telegram_id = db.Column(db.String(255))
    # user_login = db.Column(db.String(255), nullable=False)
