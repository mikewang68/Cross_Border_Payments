# 项目扩展文件
# extentions.py:这个文件存在的意义就是为了解决循环应用的问题
from flask_sqlalchemy import SQLAlchemy

# 数据库对象
db = SQLAlchemy()

def init_plugs(app):
    db.init_app(app)


