"""
数据库配置模块

定义了数据库连接和管理的相关配置。
这个模块体现了数据库管理的艺术：连接池优化、事务管理、错误处理。
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import sqlite3

# 全局数据库实例
db = SQLAlchemy()
migrate = Migrate()


class DatabaseConfig:
    """
    数据库配置类
    
    负责数据库的初始化、连接管理和性能优化。
    设计理念：高性能、高可用、易维护。
    """
    
    def __init__(self, app=None):
        """
        初始化数据库配置
        
        Args:
            app: Flask应用实例
        """
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        初始化Flask应用的数据库配置
        
        Args:
            app: Flask应用实例
        """
        # 初始化SQLAlchemy
        db.init_app(app)
        
        # 初始化数据库迁移
        migrate.init_app(app, db)
        
        # 配置数据库事件监听器
        self._setup_event_listeners(app)
        
        # 注册应用上下文处理器
        self._register_context_processors(app)
    
    def _setup_event_listeners(self, app):
        """
        设置数据库事件监听器
        
        用于性能监控、连接管理等。
        
        Args:
            app: Flask应用实例
        """
        from src.config.logger import get_logger
        logger = get_logger('database')
        
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """SQL执行前的监听器"""
            context._query_start_time = time.time()
            
            # 在调试模式下记录SQL语句
            if app.config.get('DEBUG'):
                logger.debug(f"SQL Query: {statement}")
                if parameters:
                    logger.debug(f"Parameters: {parameters}")
        
        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """SQL执行后的监听器"""
            total_time = time.time() - context._query_start_time
            
            # 记录慢查询
            if total_time > 0.5:  # 超过500ms的查询
                logger.warning(f"Slow Query ({total_time:.3f}s): {statement[:100]}...")
            elif app.config.get('DEBUG'):
                logger.debug(f"Query Time: {total_time:.3f}s")
        
        # SQLite特殊配置
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """SQLite连接时的配置"""
            if isinstance(dbapi_connection, sqlite3.Connection):
                cursor = dbapi_connection.cursor()
                # 启用外键约束
                cursor.execute("PRAGMA foreign_keys=ON")
                # 设置WAL模式提高并发性能
                cursor.execute("PRAGMA journal_mode=WAL")
                # 设置同步模式
                cursor.execute("PRAGMA synchronous=NORMAL")
                # 设置缓存大小
                cursor.execute("PRAGMA cache_size=10000")
                cursor.close()
    
    def _register_context_processors(self, app):
        """
        注册应用上下文处理器
        
        Args:
            app: Flask应用实例
        """
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            """应用上下文结束时清理数据库会话"""
            db.session.remove()
    
    def create_tables(self, app):
        """
        创建数据库表
        
        Args:
            app: Flask应用实例
        """
        with app.app_context():
            # 导入所有模型以确保表被创建
            from src.models import (
                User, Prompt, PromptVersion, Tag, PromptTag,
                PromptCollaborator, TestRecord, SystemConfig, OperationLog
            )
            
            # 创建所有表
            db.create_all()
            
            # 创建初始数据
            self._create_initial_data()
    
    def _create_initial_data(self):
        """
        创建初始数据
        
        包括系统配置、默认用户等。
        """
        from src.models.system_config import SystemConfig
        from src.models.user import User
        from src.config.logger import get_logger
        
        logger = get_logger('database')
        
        try:
            # 创建默认系统配置
            default_configs = [
                {
                    'config_key': 'system.version',
                    'config_value': '1.0.0',
                    'config_type': 'string',
                    'description': '系统版本号',
                    'is_public': True
                },
                {
                    'config_key': 'system.name',
                    'config_value': 'Prompt Manager',
                    'config_type': 'string',
                    'description': '系统名称',
                    'is_public': True
                },
                {
                    'config_key': 'ui.theme',
                    'config_value': 'light',
                    'config_type': 'string',
                    'description': '默认UI主题',
                    'is_public': True
                },
                {
                    'config_key': 'features.collaboration',
                    'config_value': 'true',
                    'config_type': 'boolean',
                    'description': '是否启用协作功能',
                    'is_public': True
                },
                {
                    'config_key': 'features.ai_testing',
                    'config_value': 'true',
                    'config_type': 'boolean',
                    'description': '是否启用AI测试功能',
                    'is_public': True
                }
            ]
            
            for config_data in default_configs:
                existing = SystemConfig.query.filter_by(
                    config_key=config_data['config_key']
                ).first()
                
                if not existing:
                    config = SystemConfig(**config_data)
                    db.session.add(config)
            
            # 提交系统配置
            db.session.commit()
            logger.info("初始系统配置创建完成")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建初始数据失败: {str(e)}")
            raise
    
    def drop_tables(self, app):
        """
        删除所有数据库表
        
        Args:
            app: Flask应用实例
        """
        with app.app_context():
            db.drop_all()
    
    def reset_database(self, app):
        """
        重置数据库
        
        删除所有表并重新创建。
        
        Args:
            app: Flask应用实例
        """
        self.drop_tables(app)
        self.create_tables(app)
    
    def get_database_info(self):
        """
        获取数据库信息
        
        Returns:
            dict: 数据库信息
        """
        try:
            # 获取数据库连接信息
            engine = db.engine
            
            info = {
                'database_url': str(engine.url).replace(engine.url.password or '', '***'),
                'driver': engine.dialect.name,
                'pool_size': engine.pool.size(),
                'checked_in': engine.pool.checkedin(),
                'checked_out': engine.pool.checkedout(),
                'overflow': engine.pool.overflow(),
                'invalid': engine.pool.invalid()
            }
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def health_check(self):
        """
        数据库健康检查
        
        Returns:
            dict: 健康检查结果
        """
        try:
            # 执行简单查询测试连接
            result = db.session.execute('SELECT 1').scalar()
            
            if result == 1:
                return {
                    'status': 'healthy',
                    'message': '数据库连接正常',
                    'database_info': self.get_database_info()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': '数据库查询异常'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'数据库连接失败: {str(e)}'
            }


# 全局数据库配置实例
database_config = DatabaseConfig()


def init_database(app):
    """
    初始化数据库
    
    Args:
        app: Flask应用实例
    """
    database_config.init_app(app)


def get_db():
    """
    获取数据库实例
    
    Returns:
        SQLAlchemy: 数据库实例
    """
    return db


def create_tables(app):
    """创建数据库表的便捷函数"""
    database_config.create_tables(app)


def reset_database(app):
    """重置数据库的便捷函数"""
    database_config.reset_database(app)

