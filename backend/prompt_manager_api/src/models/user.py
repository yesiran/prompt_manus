"""
用户模型

定义了用户实体的数据结构和相关方法。
用户是系统的核心实体，承载了身份认证、个人信息等功能。
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, JSON
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.base import BaseModel


class User(BaseModel):
    """
    用户模型类
    
    代表系统中的用户实体，包含了用户的基本信息、认证信息和偏好设置。
    这个模型设计考虑了扩展性，预留了JSON字段用于存储灵活的用户偏好。
    
    主要功能：
    1. 用户身份认证（用户名/邮箱 + 密码）
    2. 用户基本信息管理
    3. 用户偏好设置
    4. 用户状态管理
    """
    
    # 表名显式指定，体现清晰的命名
    __tablename__ = 'users'
    
    # === 认证相关字段 ===
    username = Column(
        String(50),
        nullable=False,
        unique=True,
        comment='用户名，用于登录，必须唯一'
    )
    
    email = Column(
        String(100),
        nullable=False,
        unique=True,
        comment='邮箱地址，用于登录和通知，必须唯一'
    )
    
    password_hash = Column(
        String(255),
        nullable=False,
        comment='密码哈希值，使用werkzeug加密'
    )
    
    # === 个人信息字段 ===
    display_name = Column(
        String(100),
        nullable=False,
        comment='显示名称，用于界面展示'
    )
    
    avatar_url = Column(
        String(500),
        nullable=True,
        comment='头像URL地址'
    )
    
    bio = Column(
        Text,
        nullable=True,
        comment='个人简介，支持长文本'
    )
    
    # === 系统相关字段 ===
    preferences = Column(
        JSON,
        nullable=True,
        comment='用户偏好设置，JSON格式存储，支持灵活扩展'
    )
    
    status = Column(
        Integer,
        nullable=False,
        default=1,
        comment='用户状态：1-正常，0-禁用，-1-软删除'
    )
    
    last_login_at = Column(
        'last_login_at',
        nullable=True,
        comment='最后登录时间'
    )
    
    # === 关系定义 ===
    # 一个用户可以拥有多个提示词
    owned_prompts = relationship(
        'Prompt',
        foreign_keys='Prompt.owner_id',
        back_populates='owner',
        cascade='all, delete-orphan',
        lazy='dynamic'  # 延迟加载，提高性能
    )
    
    # 一个用户可以协作编辑多个提示词
    collaborated_prompts = relationship(
        'PromptCollaborator',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    # 一个用户可以创建多个标签
    created_tags = relationship(
        'Tag',
        back_populates='creator',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    # 一个用户可以有多个测试记录
    test_records = relationship(
        'TestRecord',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    # === 密码相关方法 ===
    def set_password(self, password):
        """
        设置用户密码
        
        使用werkzeug的安全哈希算法加密密码。
        这个方法确保密码以安全的方式存储。
        
        Args:
            password (str): 明文密码
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        验证用户密码
        
        将输入的明文密码与存储的哈希值进行比较。
        
        Args:
            password (str): 待验证的明文密码
            
        Returns:
            bool: 密码是否正确
        """
        return check_password_hash(self.password_hash, password)
    
    # === 状态相关方法 ===
    def is_active(self):
        """
        检查用户是否处于活跃状态
        
        Returns:
            bool: 用户是否可以正常使用系统
        """
        return self.status == 1
    
    def is_deleted(self):
        """
        检查用户是否已被软删除
        
        Returns:
            bool: 用户是否已被标记为删除
        """
        return self.status == -1
    
    def activate(self):
        """激活用户账户"""
        self.status = 1
    
    def deactivate(self):
        """停用用户账户"""
        self.status = 0
    
    def soft_delete(self):
        """软删除用户账户"""
        self.status = -1
    
    # === 偏好设置相关方法 ===
    def get_preference(self, key, default=None):
        """
        获取用户偏好设置
        
        Args:
            key (str): 偏好设置的键
            default: 默认值
            
        Returns:
            偏好设置的值或默认值
        """
        if self.preferences is None:
            return default
        return self.preferences.get(key, default)
    
    def set_preference(self, key, value):
        """
        设置用户偏好
        
        Args:
            key (str): 偏好设置的键
            value: 偏好设置的值
        """
        if self.preferences is None:
            self.preferences = {}
        
        # 创建新的字典以触发SQLAlchemy的变更检测
        new_preferences = dict(self.preferences)
        new_preferences[key] = value
        self.preferences = new_preferences
    
    def remove_preference(self, key):
        """
        移除用户偏好设置
        
        Args:
            key (str): 要移除的偏好设置键
        """
        if self.preferences is None:
            return
        
        # 创建新的字典以触发SQLAlchemy的变更检测
        new_preferences = dict(self.preferences)
        new_preferences.pop(key, None)
        self.preferences = new_preferences
    
    # === 统计相关方法 ===
    def get_prompt_count(self):
        """
        获取用户拥有的提示词数量
        
        Returns:
            int: 提示词数量
        """
        return self.owned_prompts.filter_by(status=1).count()
    
    def get_collaboration_count(self):
        """
        获取用户参与协作的提示词数量
        
        Returns:
            int: 协作提示词数量
        """
        return self.collaborated_prompts.filter_by(status=1).count()
    
    # === 序列化方法 ===
    def to_dict(self, include_sensitive=False, exclude_fields=None):
        """
        将用户模型转换为字典
        
        重写基类方法，增加敏感信息控制。
        
        Args:
            include_sensitive (bool): 是否包含敏感信息（如密码哈希）
            exclude_fields (list): 需要排除的字段列表
            
        Returns:
            dict: 用户数据字典
        """
        if exclude_fields is None:
            exclude_fields = []
        
        # 默认排除敏感字段
        if not include_sensitive:
            exclude_fields.extend(['password_hash'])
        
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 添加计算字段
        result['prompt_count'] = self.get_prompt_count()
        result['collaboration_count'] = self.get_collaboration_count()
        result['is_active'] = self.is_active()
        
        return result
    
    def __repr__(self):
        """用户模型的字符串表示"""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

