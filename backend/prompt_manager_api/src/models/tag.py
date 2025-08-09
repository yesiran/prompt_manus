"""
标签模型

定义了标签实体的数据结构和相关方法。
标签用于对提示词进行分类和组织，支持灵活的标签系统。
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class Tag(BaseModel):
    """
    标签模型类
    
    用于对提示词进行分类和标记的标签系统。
    设计理念：简单而强大，支持颜色标记和使用统计。
    """
    
    __tablename__ = 'tags'
    
    # === 基本信息字段 ===
    name = Column(
        String(50),
        nullable=False,
        unique=True,
        comment='标签名称，必须唯一'
    )
    
    color = Column(
        String(7),
        nullable=True,
        comment='标签颜色，HEX格式如#FF5733'
    )
    
    description = Column(
        String(200),
        nullable=True,
        comment='标签描述，说明标签的用途'
    )
    
    # === 统计字段 ===
    usage_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment='使用次数，用于统计标签热度'
    )
    
    # === 创建者字段 ===
    created_by = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment='创建者用户ID'
    )
    
    # === 关系定义 ===
    # 多对一：多个标签由一个用户创建
    creator = relationship(
        'User',
        back_populates='created_tags'
    )
    
    # 多对多：标签和提示词的关联
    prompt_associations = relationship(
        'PromptTag',
        back_populates='tag',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    # === 使用统计方法 ===
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
    
    def decrement_usage(self):
        """减少使用次数"""
        if self.usage_count > 0:
            self.usage_count -= 1
    
    # === 颜色管理方法 ===
    def set_color(self, color_hex):
        """
        设置标签颜色
        
        Args:
            color_hex (str): HEX格式的颜色值
        """
        if color_hex and not color_hex.startswith('#'):
            color_hex = '#' + color_hex
        self.color = color_hex
    
    def get_color_rgb(self):
        """
        获取RGB格式的颜色值
        
        Returns:
            tuple: (r, g, b) 或 None
        """
        if not self.color:
            return None
        
        hex_color = self.color.lstrip('#')
        if len(hex_color) != 6:
            return None
        
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return None
    
    # === 关联管理方法 ===
    def get_prompts(self):
        """
        获取使用此标签的所有提示词
        
        Returns:
            list: 提示词列表
        """
        return [assoc.prompt for assoc in self.prompt_associations.all()]
    
    def get_active_prompts(self):
        """
        获取使用此标签的活跃提示词
        
        Returns:
            list: 活跃提示词列表
        """
        return [assoc.prompt for assoc in self.prompt_associations.all() 
                if assoc.prompt.is_active()]
    
    # === 序列化方法 ===
    def to_dict(self, include_relations=False, exclude_fields=None):
        """
        将标签模型转换为字典
        
        Args:
            include_relations (bool): 是否包含关联数据
            exclude_fields (list): 需要排除的字段列表
            
        Returns:
            dict: 标签数据字典
        """
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 添加关联数据
        if include_relations:
            result['creator'] = self.creator.to_dict(exclude_fields=['password_hash'])
            result['prompt_count'] = self.prompt_associations.count()
        
        # 添加计算字段
        result['color_rgb'] = self.get_color_rgb()
        
        return result
    
    def __repr__(self):
        """标签模型的字符串表示"""
        return f"<Tag(id={self.id}, name='{self.name}', usage_count={self.usage_count})>"

