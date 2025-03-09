from applications.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(db.Model):
    __tablename__ = 'admins'

    # 主键字段
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    
    # 登录凭证字段
    admin_account = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 添加唯一索引
    admin_password = db.Column(db.String(255), nullable=False)  # 密码哈希存储

    # 密码安全方法
    def set_password(self, password):
        self.admin_password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.admin_password, password)

    def __repr__(self):
        return f'<Admin {self.admin_account}>'