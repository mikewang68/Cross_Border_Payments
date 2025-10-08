from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from comm.db_api import query_database
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
        
        # 获取数据，判断数据是否存在
        data = query_database('admins', 'admin_account', str(account))
        
        # 检查是否有查询结果
        if not data:
            error = '账号或密码不正确'
            return render_template('auth/login.html', error=error)
            
        # 验证密码
        try:
            if account == data[0]['admin_account'] and data[0]['admin_password'] == password:
                # 登录成功，保存用户信息到会话
                session['user_id'] = data[0]['admin_id']
                session['user_account'] = data[0]['admin_account']
                
                # 重定向到首页
                return redirect(url_for('main.index'))
            else:
                error = '账号或密码不正确'
        except (IndexError, KeyError) as e:
            print(f"登录验证出错: {str(e)}")
            error = '系统错误，请联系管理员'
    
    return render_template('auth/login.html', error=error)

# 退出登录路由
@auth_bp.route('/logout')
def logout():
    # 清除会话
    session.pop('user_id', None)
    session.pop('user_account', None)
    
    # 重定向到登录页
    return redirect(url_for('auth.login')) 