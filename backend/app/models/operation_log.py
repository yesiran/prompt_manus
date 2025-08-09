"""
操作日志模型

定义了操作日志的数据结构和相关方法。
记录用户在系统中的重要操作，用于审计和问题追踪。
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class OperationLog(BaseModel):
    """
    操作日志模型类
    
    记录用户的重要操作，支持审计和问题追踪。
    设计理念：完整记录操作信息，便于后续分析和问题定位。
    """
    
    __tablename__ = 'operation_logs'
    
    # === 用户信息字段 ===
    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        comment='操作用户ID，可为空（系统操作）'
    )
    
    # === 操作信息字段 ===
    operation_type = Column(
        String(50),
        nullable=False,
        comment='操作类型，如CREATE、UPDATE、DELETE等'
    )
    
    resource_type = Column(
        String(50),
        nullable=False,
        comment='资源类型，如prompt、user、tag等'
    )
    
    resource_id = Column(
        Integer,
        nullable=True,
        comment='资源ID，具体操作的资源标识'
    )
    
    operation_detail = Column(
        JSON,
        nullable=True,
        comment='操作详情，JSON格式存储具体的操作信息'
    )
    
    # === 请求信息字段 ===
    ip_address = Column(
        String(45),
        nullable=True,
        comment='IP地址，支持IPv6'
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment='用户代理字符串'
    )
    
    # === 关系定义 ===
    user = relationship(
        'User',
        foreign_keys=[user_id]
    )
    
    # === 操作类型常量 ===
    OPERATION_CREATE = 'CREATE'
    OPERATION_UPDATE = 'UPDATE'
    OPERATION_DELETE = 'DELETE'
    OPERATION_VIEW = 'VIEW'
    OPERATION_LOGIN = 'LOGIN'
    OPERATION_LOGOUT = 'LOGOUT'
    OPERATION_TEST = 'TEST'
    
    # === 资源类型常量 ===
    RESOURCE_USER = 'user'
    RESOURCE_PROMPT = 'prompt'
    RESOURCE_TAG = 'tag'
    RESOURCE_VERSION = 'version'
    RESOURCE_COLLABORATOR = 'collaborator'
    RESOURCE_TEST = 'test'
    
    # === 便捷创建方法 ===
    @classmethod
    def create_log(cls, user_id, operation_type, resource_type, 
                   resource_id=None, operation_detail=None, 
                   ip_address=None, user_agent=None):
        """
        创建操作日志
        
        Args:
            user_id (int): 用户ID
            operation_type (str): 操作类型
            resource_type (str): 资源类型
            resource_id (int): 资源ID
            operation_detail (dict): 操作详情
            ip_address (str): IP地址
            user_agent (str): 用户代理
            
        Returns:
            OperationLog: 日志实例
        """
        return cls(
            user_id=user_id,
            operation_type=operation_type,
            resource_type=resource_type,
            resource_id=resource_id,
            operation_detail=operation_detail,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    # === 查询方法 ===
    def get_operation_summary(self):
        """
        获取操作摘要
        
        Returns:
            str: 操作摘要字符串
        """
        user_name = self.user.username if self.user else 'System'
        return f"{user_name} {self.operation_type} {self.resource_type}"
    
    def get_detail_value(self, key, default=None):
        """
        获取操作详情中的特定值
        
        Args:
            key (str): 详情键
            default: 默认值
            
        Returns:
            操作详情值
        """
        if self.operation_detail is None:
            return default
        return self.operation_detail.get(key, default)
    
    # === 序列化方法 ===
    def to_dict(self, include_relations=False, exclude_fields=None):
        """
        将操作日志转换为字典
        
        Args:
            include_relations (bool): 是否包含关联数据
            exclude_fields (list): 需要排除的字段列表
            
        Returns:
            dict: 操作日志数据字典
        """
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 添加关联数据
        if include_relations and self.user:
            result['user'] = self.user.to_dict(exclude_fields=['password_hash'])
        
        # 添加计算字段
        result['operation_summary'] = self.get_operation_summary()
        
        return result
    
    def __repr__(self):
        """操作日志的字符串表示"""
        return (f"<OperationLog(id={self.id}, user_id={self.user_id}, "
                f"operation='{self.operation_type}', resource='{self.resource_type}')>")

