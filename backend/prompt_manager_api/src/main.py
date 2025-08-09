"""
Prompt Manager API 主应用文件

这是整个应用的入口点，负责初始化Flask应用、配置数据库、注册路由等。
体现了应用架构的艺术：清晰的结构、优雅的初始化、完整的错误处理。
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# 导入配置
from src.config import config
from src.config.database import init_database, create_tables
from src.config.logger import init_logger, get_logger

# 导入所有模型以确保表被创建
from src.models import (
    User, Prompt, PromptVersion, Tag, PromptTag,
    PromptCollaborator, TestRecord, SystemConfig, OperationLog
)


def create_app(config_object=None):
    """
    应用工厂函数
    
    创建并配置Flask应用实例。
    这个函数体现了工厂模式的优雅：灵活、可测试、可扩展。
    
    Args:
        config_object: 配置对象，如果为None则使用默认配置
        
    Returns:
        Flask: 配置好的Flask应用实例
    """
    # 创建Flask应用实例
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # 加载配置
    if config_object is None:
        config_object = config
    
    app.config.from_object(config_object)
    
    # 验证配置
    is_valid, errors = config_object.validate_config()
    if not is_valid:
        print("配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        if not config_object.DEBUG:
            sys.exit(1)
    
    # 初始化日志系统
    init_logger(config_object)
    logger = get_logger()
    logger.info("应用启动中...")
    
    # 初始化数据库
    init_database(app)
    
    # 配置CORS（跨域资源共享）
    CORS(app, origins=getattr(config_object, 'CORS_ORIGINS', ['*']))
    
    # 注册蓝图（路由）
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册请求处理器
    register_request_handlers(app)
    
    # 注册静态文件路由
    register_static_routes(app)
    
    # 创建数据库表
    with app.app_context():
        try:
            create_tables(app)
            logger.info("数据库表创建完成")
        except Exception as e:
            logger.error(f"数据库表创建失败: {str(e)}")
            if not config_object.DEBUG:
                sys.exit(1)
    
    logger.info("应用初始化完成")
    return app


def register_blueprints(app):
    """
    注册蓝图（路由模块）
    
    Args:
        app: Flask应用实例
    """
    # 导入并注册用户相关路由
    try:
        from src.routes.user import user_bp
        app.register_blueprint(user_bp, url_prefix='/api/users')
    except ImportError:
        # 如果路由模块不存在，创建基础路由
        from flask import Blueprint
        user_bp = Blueprint('user', __name__)
        
        @user_bp.route('/', methods=['GET'])
        def list_users():
            return jsonify({'message': '用户列表接口待实现'})
        
        app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # 注册其他路由模块
    # TODO: 添加prompt、tag、version等路由模块


def register_error_handlers(app):
    """
    注册错误处理器
    
    Args:
        app: Flask应用实例
    """
    logger = get_logger()
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """处理HTTP异常"""
        logger.warning(f"HTTP异常: {e.code} - {e.description}")
        return jsonify({
            'error': True,
            'code': e.code,
            'message': e.description
        }), e.code
    
    @app.errorhandler(Exception)
    def handle_general_exception(e):
        """处理一般异常"""
        logger.error(f"未处理的异常: {str(e)}", exc_info=True)
        
        if app.config.get('DEBUG'):
            # 调试模式下返回详细错误信息
            return jsonify({
                'error': True,
                'code': 500,
                'message': str(e),
                'type': type(e).__name__
            }), 500
        else:
            # 生产模式下返回通用错误信息
            return jsonify({
                'error': True,
                'code': 500,
                'message': '服务器内部错误'
            }), 500


def register_request_handlers(app):
    """
    注册请求处理器
    
    Args:
        app: Flask应用实例
    """
    from src.config.logger import log_request
    
    @app.before_request
    def before_request():
        """请求前处理"""
        # 记录请求开始时间
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """请求后处理"""
        # 计算响应时间
        if hasattr(request, 'start_time'):
            response_time = (time.time() - request.start_time) * 1000
            log_request(request, response.status_code, response_time)
        
        return response


def register_static_routes(app):
    """
    注册静态文件路由
    
    Args:
        app: Flask应用实例
    """
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_static(path):
        """服务静态文件"""
        static_folder_path = app.static_folder
        
        if static_folder_path is None:
            return jsonify({'error': '静态文件夹未配置'}), 404
        
        # 如果请求的是具体文件且存在，直接返回
        if path and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        
        # 否则返回index.html（用于SPA应用）
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        
        # 如果index.html也不存在，返回API信息
        return jsonify({
            'name': 'Prompt Manager API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'users': '/api/users',
                'prompts': '/api/prompts',
                'tags': '/api/tags',
                'health': '/api/health'
            }
        })


# 创建应用实例
app = create_app()


# 健康检查路由
@app.route('/api/health')
def health_check():
    """健康检查接口"""
    from src.config.database import database_config
    
    # 检查数据库连接
    db_health = database_config.health_check()
    
    # 检查配置
    config_health = {
        'status': 'healthy',
        'features': config.get_feature_flags()
    }
    
    overall_status = 'healthy' if db_health['status'] == 'healthy' else 'unhealthy'
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_health,
        'config': config_health,
        'version': '1.0.0'
    })

if __name__ == '__main__':
    import time
    from datetime import datetime
    
    logger = get_logger()
    
    # 启动信息
    logger.info(f"启动Prompt Manager API服务")
    logger.info(f"环境: {config.DATABASE_TYPE}")
    logger.info(f"调试模式: {config.DEBUG}")
    logger.info(f"监听地址: {config.HOST}:{config.PORT}")
    
    # 启动Flask开发服务器
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        threaded=True
    )

