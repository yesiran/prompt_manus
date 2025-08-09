"""
基础模型类

这个模块定义了所有数据模型的基类，包含了通用的字段和方法。
遵循DRY原则，避免在每个模型中重复定义相同的字段。
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr

# 创建基础模型类
Base = declarative_base()


class BaseModel(Base):
    """
    基础模型类
    
    所有数据模型的基类，包含了通用的字段和方法。
    这个设计体现了代码复用和一致性的原则。
    
    通用字段：
    - id: 主键，使用BIGINT类型支持大量数据
    - created_at: 创建时间，自动设置
    - updated_at: 更新时间，自动更新
    """
    
    # 这个装饰器确保每个子类都有自己的表名
    # 而不是继承父类的表名
    __abstract__ = True
    
    # 主键字段，使用BIGINT支持大量数据
    id = Column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True,
        comment='唯一标识符，主键'
    )
    
    # 创建时间，自动设置为当前时间
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.current_timestamp(),
        comment='记录创建时间'
    )
    
    # 更新时间，创建时设置为当前时间，更新时自动更新
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment='记录最后更新时间'
    )
    
    def to_dict(self, exclude_fields=None):
        """
        将模型实例转换为字典
        
        这个方法用于序列化模型数据，方便API返回JSON格式。
        
        Args:
            exclude_fields (list): 需要排除的字段列表
            
        Returns:
            dict: 模型数据的字典表示
        """
        if exclude_fields is None:
            exclude_fields = []
            
        result = {}
        
        # 遍历所有列，将值添加到字典中
        for column in self.__table__.columns:
            field_name = column.name
            
            # 跳过需要排除的字段
            if field_name in exclude_fields:
                continue
                
            field_value = getattr(self, field_name)
            
            # 处理datetime类型，转换为ISO格式字符串
            if isinstance(field_value, datetime):
                field_value = field_value.isoformat()
                
            result[field_name] = field_value
            
        return result
    
    def update_from_dict(self, data, allowed_fields=None):
        """
        从字典更新模型实例
        
        这个方法用于批量更新模型字段，常用于API接收数据后更新模型。
        
        Args:
            data (dict): 包含更新数据的字典
            allowed_fields (list): 允许更新的字段列表，None表示允许所有字段
        """
        if allowed_fields is None:
            # 如果没有指定允许的字段，则获取所有列名
            allowed_fields = [column.name for column in self.__table__.columns]
        
        # 遍历数据字典，更新对应字段
        for field_name, field_value in data.items():
            # 检查字段是否存在且允许更新
            if (hasattr(self, field_name) and 
                field_name in allowed_fields and 
                field_name != 'id'):  # 主键不允许更新
                setattr(self, field_name, field_value)
    
    def __repr__(self):
        """
        模型的字符串表示
        
        用于调试和日志输出，显示模型的类名和ID。
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    @declared_attr
    def __tablename__(cls):
        """
        自动生成表名
        
        将类名转换为下划线命名的表名。
        例如：UserProfile -> user_profile
        """
        import re
        # 将驼峰命名转换为下划线命名
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class TimestampMixin:
    """
    时间戳混入类
    
    为不继承BaseModel的类提供时间戳字段。
    这是一个混入类(Mixin)，体现了组合优于继承的设计原则。
    """
    
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.current_timestamp(),
        comment='记录创建时间'
    )
    
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment='记录最后更新时间'
    )

