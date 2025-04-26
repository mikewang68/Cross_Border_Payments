from flask import Flask, render_template
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# 创建Flask应用
app = Flask(__name__)


# 设置session密钥
app.secret_key = os.urandom(24)


# 注册蓝图
def register_blueprints(app):
    from blueprint.main import main_bp
    from blueprint.auth import auth_bp
    # from views.card_users import card_users_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    # app.register_blueprint(card_users_bp)
    

# 注册蓝图
register_blueprints(app)

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500


# 在应用上下文中运行初始化
# with app.app_context():
#     initialize_database()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
