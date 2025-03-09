from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from applications.models.admins import Admin
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# 登录路由
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        account = request.form.get('account')
        password = request.form.get('password')
        
        # 查询用户
        admin = Admin.query.filter_by(admin_account=account).first()
        
        # 直接比较密码（假设数据库中存储的是明文密码）
        if admin and admin.admin_password == password:
            # 登录成功，保存用户信息到会话
            session['user_id'] = admin.admin_id
            session['user_account'] = admin.admin_account
            
            # 重定向到首页
            return redirect(url_for('main.index'))
        else:
            error = '账号或密码不正确'
    
    return render_template('auth/login.html', error=error)

# 退出登录路由
@auth_bp.route('/logout')
def logout():
    # 清除会话
    session.pop('user_id', None)
    session.pop('user_account', None)
    
    # 重定向到登录页
    return redirect(url_for('auth.login')) 