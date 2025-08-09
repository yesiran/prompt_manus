"""
应用配置类

定义了应用的各种配置类，支持不同环境的配置管理。
这个模块体现了配置管理的艺术：既要灵活又要安全。
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量文件
# 首先尝试加载 .env 文件，如果不存在则使用系统环境变量
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)


class Config:
    """
    基础配置类
    
    包含所有环境共同的配置项。
    这个类体现了配置管理的基础原则：安全、灵活、可扩展。
    """
    
    # === 应用基础配置 ===
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes', 'on')
    TESTING = False
    
    # === 服务器配置 ===
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # === 数据库配置 ===
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20)),
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600))
    }
    
    # === JWT配置 ===
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 24)))
    JWT_ALGORITHM = 'HS256'
    
    # === 安全配置 ===
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 8))
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    ACCOUNT_LOCKOUT_MINUTES = int(os.getenv('ACCOUNT_LOCKOUT_MINUTES', 30))
    
    # === 文件上传配置 ===
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_UPLOAD_SIZE', 10)) * 1024 * 1024  # MB转字节
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'txt,md,json').split(','))
    UPLOAD_FOLDER = os.getenv('UPLOAD_PATH', 'uploads')
    
    # === AI模型配置 ===
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_API_BASE = os.getenv('CLAUDE_API_BASE', 'https://api.anthropic.com')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-opus-20240229')
    
    # === 日志配置 ===
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/prompt_manager.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10)) * 1024 * 1024  # MB转字节
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # === Redis配置 ===
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # === 邮件配置 ===
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ('true', '1', 'yes', 'on')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # === 功能开关配置 ===
    ENABLE_REGISTRATION = os.getenv('ENABLE_REGISTRATION', 'true').lower() in ('true', '1', 'yes', 'on')
    REQUIRE_EMAIL_VERIFICATION = os.getenv('REQUIRE_EMAIL_VERIFICATION', 'false').lower() in ('true', '1', 'yes', 'on')
    DEFAULT_USER_ROLE = os.getenv('DEFAULT_USER_ROLE', 'user')
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """
        动态生成数据库连接URI
        
        根据配置的数据库类型生成相应的连接字符串。
        这个属性方法体现了配置的灵活性。
        """
        if self.DATABASE_TYPE.lower() == 'mysql':
            host = os.getenv('MYSQL_HOST', 'localhost')
            port = os.getenv('MYSQL_PORT', '3306')
            user = os.getenv('MYSQL_USER', 'root')
            password = os.getenv('MYSQL_PASSWORD', '')
            database = os.getenv('MYSQL_DATABASE', 'prompt_manager_db')
            
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
        
        elif self.DATABASE_TYPE.lower() == 'postgresql':
            host = os.getenv('POSTGRES_HOST', 'localhost')
            port = os.getenv('POSTGRES_PORT', '5432')
            user = os.getenv('POSTGRES_USER', 'postgres')
            password = os.getenv('POSTGRES_PASSWORD', '')
            database = os.getenv('POSTGRES_DATABASE', 'prompt_manager_db')
            
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        else:  # 默认使用SQLite
            sqlite_path = os.getenv('SQLITE_PATH', 'database/app.db')
            # 确保路径是绝对路径
            if not os.path.isabs(sqlite_path):
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                sqlite_path = os.path.join(base_dir, sqlite_path)
            
            return f"sqlite:///{sqlite_path}"
    
    @property
    def REDIS_URL(self):
        """Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def validate_config(self):
        """
        验证配置的有效性
        
        检查关键配置项是否正确设置。
        这个方法体现了配置管理的安全性考虑。
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # 检查必需的配置项
        if not self.SECRET_KEY or self.SECRET_KEY == 'dev-secret-key-change-in-production':
            if not self.DEBUG:
                errors.append("生产环境必须设置安全的SECRET_KEY")
        
        # 检查AI API密钥
        if not self.OPENAI_API_KEY and not self.CLAUDE_API_KEY:
            errors.append("至少需要配置一个AI模型的API密钥")
        
        # 检查数据库配置
        if self.DATABASE_TYPE.lower() == 'mysql':
            required_mysql_vars = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
            for var in required_mysql_vars:
                if not os.getenv(var):
                    errors.append(f"MySQL配置缺少必需的环境变量: {var}")
        
        return len(errors) == 0, errors
    
    def get_feature_flags(self):
        """
        获取功能开关配置
        
        Returns:
            dict: 功能开关字典
        """
        return {
            'registration_enabled': self.ENABLE_REGISTRATION,
            'email_verification_required': self.REQUIRE_EMAIL_VERIFICATION,
            'ai_testing_enabled': bool(self.OPENAI_API_KEY or self.CLAUDE_API_KEY),
            'file_upload_enabled': True,
            'collaboration_enabled': True,
            'version_control_enabled': True
        }


class DevelopmentConfig(Config):
    """
    开发环境配置
    
    针对开发环境的特殊配置，注重调试和开发便利性。
    """
    DEBUG = True
    TESTING = False
    
    # 开发环境使用更详细的日志
    LOG_LEVEL = 'DEBUG'
    
    # 开发环境允许所有来源的跨域请求
    CORS_ORIGINS = ['*']
    
    # 开发环境使用较短的JWT过期时间便于测试
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)


class ProductionConfig(Config):
    """
    生产环境配置
    
    针对生产环境的安全和性能优化配置。
    """
    DEBUG = False
    TESTING = False
    
    # 生产环境使用更严格的日志级别
    LOG_LEVEL = 'WARNING'
    
    # 生产环境限制跨域请求来源
    CORS_ORIGINS = []  # 需要根据实际前端域名配置
    
    # 生产环境使用更长的JWT过期时间
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # 生产环境启用更多安全特性
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """
    测试环境配置
    
    针对单元测试和集成测试的配置。
    """
    DEBUG = True
    TESTING = True
    
    # 测试环境使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # 测试环境禁用CSRF保护
    WTF_CSRF_ENABLED = False
    
    # 测试环境使用更短的JWT过期时间
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    
    # 测试环境禁用邮件发送
    MAIL_SUPPRESS_SEND = True

