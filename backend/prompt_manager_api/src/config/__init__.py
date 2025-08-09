"""
配置管理包

这个包负责管理应用的所有配置信息，包括环境变量、数据库配置、日志配置等。
设计理念：统一配置管理，支持不同环境的配置切换。
"""

from .config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from .database import DatabaseConfig
from .logger import LoggerConfig

# 根据环境变量选择配置类
import os

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

# 获取当前环境配置
current_env = os.getenv('APP_ENV', 'development')
current_config = config_map.get(current_env, DevelopmentConfig)

# 导出配置实例
config = current_config()

__all__ = [
    'Config',
    'DevelopmentConfig', 
    'ProductionConfig',
    'TestingConfig',
    'DatabaseConfig',
    'LoggerConfig',
    'config'
]

