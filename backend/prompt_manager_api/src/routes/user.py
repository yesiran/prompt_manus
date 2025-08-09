"""
用户API路由

定义了用户相关的API接口，包括注册、登录、用户管理等。
这个模块体现了RESTful API设计的艺术。
"""

from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest

from src.services.user_service import UserService, ServiceException
from src.config.logger import get_logger

# 创建用户蓝图
user_bp = Blueprint('user', __name__)

# 初始化服务和日志
user_service = UserService()
logger = get_logger('api.user')


@user_bp.route('/', methods=['GET'])
def list_users():
    """
    获取用户列表
    
    支持分页和过滤参数：
    - page: 页码（默认1）
    - per_page: 每页数量（默认20）
    - status: 用户状态过滤
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', type=int)
        
        # 构建过滤条件
        filters = {}
        if status is not None:
            filters['status'] = status
        
        # 查询用户列表
        result = user_service.list(
            page=page,
            per_page=per_page,
            filters=filters,
            order_by='-created_at'
        )
        
        # 过滤敏感信息
        for item in result['items']:
            item.pop('password_hash', None)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ServiceException as e:
        logger.error(f"获取用户列表失败: {e.message}")
        return jsonify({
            'success': False,
            'error': e.code,
            'message': e.message
        }), 400
    
    except Exception as e:
        logger.error(f"获取用户列表异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500


@user_bp.route('/', methods=['POST'])
def create_user():
    """
    创建用户（注册）
    
    请求体参数：
    - username: 用户名（必需）
    - email: 邮箱（必需）
    - password: 密码（必需）
    - display_name: 显示名称（可选）
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            raise BadRequest("请求体不能为空")
        
        # 验证必需字段
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                raise BadRequest(f"缺少必需字段: {field}")
        
        # 注册用户
        user = user_service.register(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            display_name=data.get('display_name')
        )
        
        # 返回用户信息（不包含敏感数据）
        user_data = user.to_dict(exclude_fields=['password_hash'])
        
        return jsonify({
            'success': True,
            'data': user_data,
            'message': '用户注册成功'
        }), 201
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': 'INVALID_REQUEST',
            'message': str(e)
        }), 400
    
    except ServiceException as e:
        logger.error(f"用户注册失败: {e.message}")
        return jsonify({
            'success': False,
            'error': e.code,
            'message': e.message
        }), 400
    
    except Exception as e:
        logger.error(f"用户注册异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500


@user_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    
    请求体参数：
    - username_or_email: 用户名或邮箱（必需）
    - password: 密码（必需）
    """
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("请求体不能为空")
        
        username_or_email = data.get('username_or_email')
        password = data.get('password')
        
        if not username_or_email or not password:
            raise BadRequest("用户名/邮箱和密码不能为空")
        
        # 用户登录
        user = user_service.login(username_or_email, password)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'INVALID_CREDENTIALS',
                'message': '用户名/邮箱或密码错误'
            }), 401
        
        # 返回用户信息（实际项目中应该返回JWT token）
        user_data = user.to_dict(exclude_fields=['password_hash'])
        
        return jsonify({
            'success': True,
            'data': user_data,
            'message': '登录成功'
        })
        
    except BadRequest as e:
        return jsonify({
            'success': False,
            'error': 'INVALID_REQUEST',
            'message': str(e)
        }), 400
    
    except ServiceException as e:
        return jsonify({
            'success': False,
            'error': e.code,
            'message': e.message
        }), 400
    
    except Exception as e:
        logger.error(f"用户登录异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500

