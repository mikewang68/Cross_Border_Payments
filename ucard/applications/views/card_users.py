from flask import Blueprint, render_template, jsonify, request, current_app
from applications.models.card_holder import card_holder
from sqlalchemy.exc import SQLAlchemyError
import traceback
import uuid
from datetime import datetime

# 创建蓝图
card_users_bp = Blueprint('card_users', __name__, url_prefix='/api')

@card_users_bp.route('/card_holders')
def get_card_holders():
    """
    获取用卡人数据API
    """
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # 查询用卡人数据
        query = card_holder.query
        
        # 获取搜索参数
        name = request.args.get('name', '')
        card_no = request.args.get('card_no', '')
        
        # 应用搜索过滤
        if name:
            query = query.filter(card_holder.user_name.like(f'%{name}%'))
        if card_no:
            query = query.filter(card_holder.user_id.like(f'%{card_no}%'))
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * limit
        card_users = query.offset(offset).limit(limit).all()
        
        # 准备数据
        data = []
        for user in card_users:
            data.append({
                'id': user.user_code,
                'name': user.user_name,
                'card_no': user.user_id,
                'phone': user.mobile,
                'email': user.email,
                'country': user.country,
                'state': user.state,
                'city': user.city,
                'address': user.address,
                'postcode': '',
                'birth_date': '',
                'balance': 0.0,  # 这里可以从其他表获取余额
                'status': 1  # 这里可以从其他表获取状态
            })
        
        # 返回JSON数据
        return jsonify({
            'code': 0,  # Layui table要求的成功状态码为0
            'msg': '',
            'count': total,
            'data': data
        })
    except SQLAlchemyError as e:
        # 记录数据库错误
        current_app.logger.error(f'Database error in get_card_holders: {str(e)}\n{traceback.format_exc()}')
        return jsonify({
            'code': 500,
            'msg': '数据库错误，请联系管理员',
            'count': 0,
            'data': []
        })
    except Exception as e:
        # 记录其他错误
        current_app.logger.error(f'Unexpected error in get_card_holders: {str(e)}\n{traceback.format_exc()}')
        return jsonify({
            'code': 500,
            'msg': '服务器错误，请联系管理员',
            'count': 0,
            'data': []
        })

# 添加用卡人表单页面路由
@card_users_bp.route('/card_holders/add', methods=['GET'])
def add_card_holder_form():
    """
    渲染添加用卡人表单页面
    """
    return render_template('main/card_user_add.html')

# 添加用卡人API
@card_users_bp.route('/card_holders', methods=['POST'])
def add_card_holder():
    """
    添加用卡人API
    """
    try:
        # 获取表单数据
        data = request.json
        
        # 生成用户编码
        user_code = f"UC{uuid.uuid4().hex[:8].upper()}"
        
        # 提取出必要字段，或使用默认值
        user_id = data.get('user_id')
        user_name = data.get('user_name')
        email = data.get('email')
        mobile = data.get('mobile', '')
        country = data.get('country', 'USA')
        state = data.get('state', 'California')
        city = data.get('city', 'Los Angeles')
        address = data.get('address', '1234 Main St')
        region = data.get('region', 'USA')
        
        # 创建新用卡人（注意：移除了不在数据库中的字段）
        new_user = card_holder(
            user_code=user_code,
            user_id=user_id,
            user_name=user_name,
            region=region,
            mobile=mobile,
            email=email,
            country=country,
            state=state,
            city=city,
            address=address
        )
        
        # 保存到数据库
        from applications.extensions import db
        db.session.add(new_user)
        db.session.commit()
        
        # 返回成功信息
        return jsonify({
            'code': 200,
            'msg': '添加用卡人成功',
            'data': {
                'user_code': user_code
            }
        })
    except SQLAlchemyError as e:
        # 回滚事务
        from applications.extensions import db
        db.session.rollback()
        # 记录数据库错误
        current_app.logger.error(f'Database error in add_card_holder: {str(e)}\n{traceback.format_exc()}')
        return jsonify({
            'code': 500,
            'msg': f'数据库错误，请联系管理员: {str(e)}',
            'data': None
        })
    except Exception as e:
        # 记录其他错误
        current_app.logger.error(f'Unexpected error in add_card_holder: {str(e)}\n{traceback.format_exc()}')
        return jsonify({
            'code': 500,
            'msg': f'服务器错误，请联系管理员: {str(e)}',
            'data': None
        }) 