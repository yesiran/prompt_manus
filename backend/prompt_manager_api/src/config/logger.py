"""
日志配置模块

定义了应用的日志配置和管理功能。
这个模块体现了日志管理的艺术：既要详细记录又要性能优化。
"""

import os
import logging
import logging.handlers
from datetime import datetime


class LoggerConfig:
    """
    日志配置类
    
    负责配置和管理应用的日志系统。
    设计理念：分级记录、文件持久化、自动切分、性能优化。
    """
    
    def __init__(self, config):
        """
        初始化日志配置
        
        Args:
            config: 应用配置对象
        """
        self.config = config
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """
        设置日志器
        
        配置日志的格式、级别、处理器等。
        这个方法体现了日志配置的完整性和专业性。
        """
        # 创建主日志器
        self.logger = logging.getLogger('prompt_manager')
        self.logger.setLevel(getattr(logging, self.config.LOG_LEVEL.upper()))
        
        # 避免重复添加处理器
        if self.logger.handlers:
            return
        
        # 创建日志格式器
        formatter = self._create_formatter()
        
        # 添加控制台处理器（用于开发调试）
        if self.config.DEBUG:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 添加文件处理器（用于持久化存储）
        file_handler = self._create_file_handler()
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 添加错误日志处理器（单独记录错误）
        error_handler = self._create_error_handler()
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def _create_formatter(self):
        """
        创建日志格式器
        
        定义日志的输出格式，包含时间、级别、模块、消息等信息。
        
        Returns:
            logging.Formatter: 格式器对象
        """
        # 详细的日志格式，便于调试和问题追踪
        log_format = (
            '%(asctime)s - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
        )
        
        # 时间格式
        date_format = '%Y-%m-%d %H:%M:%S'
        
        return logging.Formatter(log_format, date_format)
    
    def _create_file_handler(self):
        """
        创建文件处理器
        
        配置日志文件的轮转和大小限制。
        
        Returns:
            logging.Handler: 文件处理器
        """
        # 确保日志目录存在
        log_dir = os.path.dirname(self.config.LOG_FILE_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 生成带日期的日志文件名
        log_file = self._generate_log_filename(self.config.LOG_FILE_PATH)
        
        # 创建轮转文件处理器
        # 当文件大小超过限制时自动创建新文件
        handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=self.config.LOG_MAX_SIZE,
            backupCount=self.config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        
        handler.setLevel(getattr(logging, self.config.LOG_LEVEL.upper()))
        
        return handler
    
    def _create_error_handler(self):
        """
        创建错误日志处理器
        
        单独记录ERROR级别以上的日志，便于快速定位问题。
        
        Returns:
            logging.Handler: 错误日志处理器
        """
        # 生成错误日志文件名
        error_log_file = self._generate_log_filename(
            self.config.LOG_FILE_PATH, 
            suffix='_error'
        )
        
        # 创建错误日志处理器
        handler = logging.handlers.RotatingFileHandler(
            filename=error_log_file,
            maxBytes=self.config.LOG_MAX_SIZE,
            backupCount=self.config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        
        # 只记录ERROR级别以上的日志
        handler.setLevel(logging.ERROR)
        
        return handler
    
    def _generate_log_filename(self, base_path, suffix=''):
        """
        生成带日期的日志文件名
        
        按照要求的格式生成日志文件名：prompt_project_log.YYYY/MM/DD
        
        Args:
            base_path (str): 基础路径
            suffix (str): 文件名后缀
            
        Returns:
            str: 完整的日志文件路径
        """
        # 获取当前日期
        now = datetime.now()
        date_str = now.strftime('%Y/%m/%d')
        
        # 分离路径和文件名
        dir_path = os.path.dirname(base_path)
        base_name = os.path.splitext(os.path.basename(base_path))[0]
        
        # 构建新的文件名
        new_filename = f"{base_name}{suffix}.{date_str.replace('/', '_')}.log"
        
        return os.path.join(dir_path, new_filename)
    
    def get_logger(self, name=None):
        """
        获取日志器实例
        
        Args:
            name (str): 日志器名称，如果为None则返回主日志器
            
        Returns:
            logging.Logger: 日志器实例
        """
        if name:
            return logging.getLogger(f'prompt_manager.{name}')
        return self.logger
    
    def log_request(self, request, response_status=None, response_time=None):
        """
        记录HTTP请求日志
        
        专门用于记录API请求的详细信息。
        
        Args:
            request: Flask请求对象
            response_status (int): 响应状态码
            response_time (float): 响应时间（毫秒）
        """
        # 构建请求日志信息
        log_data = {
            'method': request.method,
            'url': request.url,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'content_length': request.content_length or 0
        }
        
        if response_status:
            log_data['status'] = response_status
        
        if response_time:
            log_data['response_time'] = f"{response_time:.2f}ms"
        
        # 根据状态码选择日志级别
        if response_status and response_status >= 400:
            self.logger.warning(f"HTTP Request: {log_data}")
        else:
            self.logger.info(f"HTTP Request: {log_data}")
    
    def log_database_operation(self, operation, table, record_id=None, details=None):
        """
        记录数据库操作日志
        
        专门用于记录数据库CRUD操作。
        
        Args:
            operation (str): 操作类型（CREATE, READ, UPDATE, DELETE）
            table (str): 表名
            record_id: 记录ID
            details (dict): 操作详情
        """
        log_data = {
            'operation': operation,
            'table': table,
            'record_id': record_id,
            'details': details or {}
        }
        
        self.logger.info(f"Database Operation: {log_data}")
    
    def log_ai_request(self, model, prompt_length, response_length=None, 
                      response_time=None, error=None):
        """
        记录AI模型请求日志
        
        专门用于记录AI模型调用的详细信息。
        
        Args:
            model (str): 模型名称
            prompt_length (int): 提示词长度
            response_length (int): 响应长度
            response_time (float): 响应时间（毫秒）
            error (str): 错误信息
        """
        log_data = {
            'model': model,
            'prompt_length': prompt_length,
            'response_length': response_length,
            'response_time': f"{response_time:.2f}ms" if response_time else None
        }
        
        if error:
            log_data['error'] = error
            self.logger.error(f"AI Request Failed: {log_data}")
        else:
            self.logger.info(f"AI Request: {log_data}")
    
    def log_user_action(self, user_id, action, resource_type, resource_id=None, details=None):
        """
        记录用户操作日志
        
        专门用于记录用户的重要操作，便于审计。
        
        Args:
            user_id (int): 用户ID
            action (str): 操作类型
            resource_type (str): 资源类型
            resource_id: 资源ID
            details (dict): 操作详情
        """
        log_data = {
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or {}
        }
        
        self.logger.info(f"User Action: {log_data}")


# 全局日志器实例
_logger_config = None


def init_logger(config):
    """
    初始化全局日志器
    
    Args:
        config: 应用配置对象
    """
    global _logger_config
    _logger_config = LoggerConfig(config)


def get_logger(name=None):
    """
    获取日志器实例
    
    Args:
        name (str): 日志器名称
        
    Returns:
        logging.Logger: 日志器实例
    """
    if _logger_config is None:
        # 如果没有初始化，创建一个基础的日志器
        logger = logging.getLogger('prompt_manager')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    return _logger_config.get_logger(name)


def log_request(*args, **kwargs):
    """记录HTTP请求日志的便捷函数"""
    if _logger_config:
        _logger_config.log_request(*args, **kwargs)


def log_database_operation(*args, **kwargs):
    """记录数据库操作日志的便捷函数"""
    if _logger_config:
        _logger_config.log_database_operation(*args, **kwargs)


def log_ai_request(*args, **kwargs):
    """记录AI请求日志的便捷函数"""
    if _logger_config:
        _logger_config.log_ai_request(*args, **kwargs)


def log_user_action(*args, **kwargs):
    """记录用户操作日志的便捷函数"""
    if _logger_config:
        _logger_config.log_user_action(*args, **kwargs)

