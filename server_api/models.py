from exts import db

class UserModel(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}  # 确保它不会试图创建新表
    user_code = db.Column(db.String,primary_key=True)  # 用户代码,主键
    user_id = db.Column(db.String(255), unique=True, nullable=False)  # 用户id，唯一
    user_name = db.Column(db.String(255))  # 用户姓名
    region = db.Column(db.String(255))  # 所属地区
    birth = db.Column(db.Date)  # 生日
    mobile = db.Column(db.String(20))  # 联系电话
    email = db.Column(db.String(255), unique=True)  # 联系邮箱，唯一
    country = db.Column(db.String(255))  # 国家/地区
    state = db.Column(db.String(255))  # 省/州
    city = db.Column(db.String(255))  # 城市
    address = db.Column(db.Text)  # 详细地址
    postcode = db.Column(db.String(20))  # 邮政编码
    create_time = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间，默认当前时间
    user_key = db.Column(db.String(255))  # 用户密钥
    status = db.Column(db.String(20))  # 用户状态
    qd_id = db.Column(db.String(255))  # 渠道ID
    qd_name = db.Column(db.String(255))  # 渠道名称
    telegram_id = db.Column(db.String(255))  # 电报号
    user_login = db.Column(db.String(255))  # 登录状态 0未登录 1登录

class CardModel(db.Model):
    __tablename__ = 'card'
    __table_args__ = {'extend_existing': True}  # 确保它不会试图创建新表
    card_id = db.Column(db.String(255), primary_key=True)  # 卡ID，主键
    pan = db.Column(db.String(255))  # 带掩码卡号
    expire_date = db.Column(db.String(255))  # 过期日期
    cvv = db.Column(db.String(255))  # CVV
    status = db.Column(db.String(255))  # 状态
    brand_code = db.Column(db.String(255))  # 卡品牌
    create_time = db.Column(db.String(255))  # 创建时间
    limit_per_transaction = db.Column(db.String(255))  # 每笔交易限额
    limit_per_day = db.Column(db.String(255))  # 每日交易限额
    limit_per_month = db.Column(db.String(255))  # 每月交易限额
    user_id = db.Column(db.String(255))  # 用户ID
    user_code = db.Column(db.String(255))  # 用户代码
    user_name = db.Column(db.String(255))  # 用户名