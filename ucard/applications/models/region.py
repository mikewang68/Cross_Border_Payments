from applications.extensions import db
from datetime import datetime

class Region(db.Model):
    __tablename__ = 'region'  # 根据图片中的"region @gtest"提示建议的表名

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    english_name = db.Column(db.String(255))
    chinese_name = db.Column(db.String(255))
    abbreviation = db.Column(db.String(10))
    currency = db.Column(db.String(50))
    icon_base64 = db.Column(db.Text)  # 存储base64编码的图标
    is_referenced = db.Column(db.SmallInteger, nullable=False, default=0)  # 对应tinyint(1)
    insert_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)