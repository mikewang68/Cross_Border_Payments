from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name or 'default'])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 注册蓝图
    from blueprint.auth import auth_bp
    from blueprint.main import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # 注册命令
    from applications.commands import init_commands
    init_commands(app)
    
    return app 