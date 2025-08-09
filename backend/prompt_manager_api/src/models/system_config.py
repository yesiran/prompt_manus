"""
系统配置模型

定义了系统配置的数据结构和相关方法。
用于存储系统级别的配置信息，支持动态配置管理。
"""

from sqlalchemy import Column, String, Text, Boolean
from src.models.base import BaseModel


class SystemConfig(BaseModel):
    """
    系统配置模型类
    
    存储系统级别的配置信息，支持不同类型的配置值。
    设计理念：灵活的配置管理，支持运行时动态修改。
    """
    
    __tablename__ = 'system_configs'
    
    # === 配置字段 ===
    config_key = Column(
        String(100),
        nullable=False,
        unique=True,
        comment='配置键，必须唯一'
    )
    
    config_value = Column(
        Text,
        nullable=False,
        comment='配置值，支持长文本'
    )
    
    config_type = Column(
        String(20),
        nullable=False,
        default='string',
        comment='配置类型：string, json, number, boolean'
    )
    
    description = Column(
        String(500),
        nullable=True,
        comment='配置描述，说明配置的用途'
    )
    
    is_public = Column(
        Boolean,
        nullable=False,
        default=False,
        comment='是否为公开配置，公开配置可被前端访问'
    )
    
    # === 类型转换方法 ===
    def get_value(self):
        """
        根据配置类型返回正确的值
        
        Returns:
            配置值的正确类型
        """
        if self.config_type == 'boolean':
            return self.config_value.lower() in ('true', '1', 'yes', 'on')
        elif self.config_type == 'number':
            try:
                if '.' in self.config_value:
                    return float(self.config_value)
                else:
                    return int(self.config_value)
            except ValueError:
                return 0
        elif self.config_type == 'json':
            import json
            try:
                return json.loads(self.config_value)
            except json.JSONDecodeError:
                return {}
        else:  # string
            return self.config_value
    
    def set_value(self, value):
        """
        设置配置值
        
        Args:
            value: 要设置的值
        """
        if self.config_type == 'json':
            import json
            self.config_value = json.dumps(value, ensure_ascii=False)
        else:
            self.config_value = str(value)
    
    def __repr__(self):
        """系统配置的字符串表示"""
        return f"<SystemConfig(key='{self.config_key}', type='{self.config_type}')>"

