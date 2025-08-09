"""
提示词模型

定义了提示词实体的数据结构和相关方法。
提示词是系统的核心业务实体，承载了内容管理、版本控制、协作编辑等核心功能。
"""

import hashlib
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Prompt(BaseModel):
    """
    提示词模型类
    
    代表系统中的提示词实体，是整个系统的核心业务对象。
    这个模型设计考虑了以下核心功能：
    1. 内容管理 - 标题、描述、内容
    2. 版本控制 - 内容哈希、版本计数
    3. 权限管理 - 所有者、可见性
    4. 协作支持 - 多用户编辑
    5. 分类管理 - 标签系统
    6. 测试集成 - AI模型测试
    
    设计哲学：
    - 高内聚：提示词相关的核心属性都在这个模型中
    - 低耦合：通过外键和关系与其他模型连接
    - 扩展性：预留了多个扩展字段
    """
    
    __tablename__ = 'prompts'
    
    # === 基本信息字段 ===
    title = Column(
        String(200),
        nullable=False,
        comment='提示词标题，用于显示和搜索'
    )
    
    description = Column(
        Text,
        nullable=True,
        comment='提示词描述，详细说明用途和使用方法'
    )
    
    content = Column(
        Text,
        nullable=False,
        comment='提示词内容，核心的prompt文本'
    )
    
    content_hash = Column(
        String(64),
        nullable=False,
        comment='内容哈希值，用于版本对比和去重'
    )
    
    # === 所有权和权限字段 ===
    owner_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment='创建者用户ID，外键关联users表'
    )
    
    visibility = Column(
        Integer,
        nullable=False,
        default=1,
        comment='可见性：1-私有，2-协作者可见，3-公开'
    )
    
    # === 分类和元数据字段 ===
    category = Column(
        String(50),
        nullable=True,
        comment='分类名称，用于组织和筛选'
    )
    
    language = Column(
        String(10),
        nullable=False,
        default='zh-CN',
        comment='语言代码，如zh-CN、en-US'
    )
    
    model_type = Column(
        String(50),
        nullable=True,
        comment='适用的AI模型类型，如GPT-4、Claude等'
    )
    
    # === 状态和统计字段 ===
    status = Column(
        Integer,
        nullable=False,
        default=1,
        comment='状态：1-正常，0-草稿，-1-软删除'
    )
    
    version_count = Column(
        Integer,
        nullable=False,
        default=1,
        comment='版本数量，用于统计和显示'
    )
    
    test_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment='测试次数，用于统计使用频率'
    )
    
    last_tested_at = Column(
        'last_tested_at',
        nullable=True,
        comment='最后测试时间'
    )
    
    # === 关系定义 ===
    # 多对一：多个提示词属于一个用户
    owner = relationship(
        'User',
        foreign_keys=[owner_id],
        back_populates='owned_prompts'
    )
    
    # 一对多：一个提示词有多个版本
    versions = relationship(
        'PromptVersion',
        back_populates='prompt',
        cascade='all, delete-orphan',
        lazy='dynamic',
        order_by='PromptVersion.version_number.desc()'  # 按版本号降序排列
    )
    
    # 多对多：提示词和标签的关联
    tag_associations = relationship(
        'PromptTag',
        back_populates='prompt',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    # 一对多：一个提示词有多个协作者
    collaborators = relationship(
        'PromptCollaborator',
        back_populates='prompt',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    # 一对多：一个提示词有多个测试记录
    test_records = relationship(
        'TestRecord',
        back_populates='prompt',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    # === 内容管理方法 ===
    def update_content(self, new_content, author_id, change_summary=None):
        """
        更新提示词内容
        
        这个方法不仅更新内容，还会创建新的版本记录。
        体现了版本控制的核心逻辑。
        
        Args:
            new_content (str): 新的内容
            author_id (int): 修改者ID
            change_summary (str): 变更摘要
            
        Returns:
            PromptVersion: 新创建的版本对象
        """
        # 计算新内容的哈希值
        new_hash = self._calculate_content_hash(new_content)
        
        # 如果内容没有变化，不创建新版本
        if new_hash == self.content_hash:
            return None
        
        # 导入PromptVersion（避免循环导入）
        from .prompt_version import PromptVersion
        
        # 创建新版本
        new_version = PromptVersion(
            prompt_id=self.id,
            version_number=self.version_count + 1,
            title=self.title,
            content=new_content,
            content_hash=new_hash,
            change_summary=change_summary,
            author_id=author_id,
            is_current=True
        )
        
        # 更新当前提示词
        self.content = new_content
        self.content_hash = new_hash
        self.version_count += 1
        
        return new_version
    
    def _calculate_content_hash(self, content):
        """
        计算内容哈希值
        
        使用SHA-256算法计算内容的哈希值，用于版本对比。
        
        Args:
            content (str): 要计算哈希的内容
            
        Returns:
            str: 十六进制的哈希值
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    # === 版本管理方法 ===
    def get_current_version(self):
        """
        获取当前版本
        
        Returns:
            PromptVersion: 当前版本对象，如果没有则返回None
        """
        return self.versions.filter_by(is_current=True).first()
    
    def get_version_by_number(self, version_number):
        """
        根据版本号获取版本
        
        Args:
            version_number (int): 版本号
            
        Returns:
            PromptVersion: 版本对象，如果没有则返回None
        """
        return self.versions.filter_by(version_number=version_number).first()
    
    def rollback_to_version(self, version_number, author_id):
        """
        回滚到指定版本
        
        Args:
            version_number (int): 目标版本号
            author_id (int): 操作者ID
            
        Returns:
            bool: 是否成功回滚
        """
        target_version = self.get_version_by_number(version_number)
        if not target_version:
            return False
        
        # 创建新版本（基于目标版本的内容）
        self.update_content(
            target_version.content,
            author_id,
            f"回滚到版本 {version_number}"
        )
        
        return True
    
    # === 权限管理方法 ===
    def is_owner(self, user_id):
        """
        检查用户是否为所有者
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            bool: 是否为所有者
        """
        return self.owner_id == user_id
    
    def is_collaborator(self, user_id):
        """
        检查用户是否为协作者
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            bool: 是否为协作者
        """
        if self.is_owner(user_id):
            return True
        
        return self.collaborators.filter_by(
            user_id=user_id,
            status=1
        ).first() is not None
    
    def can_edit(self, user_id):
        """
        检查用户是否有编辑权限
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            bool: 是否有编辑权限
        """
        if self.is_owner(user_id):
            return True
        
        collaborator = self.collaborators.filter_by(
            user_id=user_id,
            status=1
        ).first()
        
        if not collaborator:
            return False
        
        # 角色：1-所有者，2-编辑者，3-查看者
        return collaborator.role <= 2
    
    def can_view(self, user_id):
        """
        检查用户是否有查看权限
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            bool: 是否有查看权限
        """
        # 公开的提示词所有人都可以查看
        if self.visibility == 3:
            return True
        
        # 私有的只有所有者可以查看
        if self.visibility == 1:
            return self.is_owner(user_id)
        
        # 协作者可见的，协作者可以查看
        if self.visibility == 2:
            return self.is_collaborator(user_id)
        
        return False
    
    # === 标签管理方法 ===
    def add_tag(self, tag):
        """
        添加标签
        
        Args:
            tag (Tag): 标签对象
        """
        # 导入PromptTag（避免循环导入）
        from .prompt_tag import PromptTag
        
        # 检查是否已经存在关联
        existing = self.tag_associations.filter_by(tag_id=tag.id).first()
        if existing:
            return
        
        # 创建新的关联
        association = PromptTag(prompt_id=self.id, tag_id=tag.id)
        return association
    
    def remove_tag(self, tag):
        """
        移除标签
        
        Args:
            tag (Tag): 标签对象
        """
        association = self.tag_associations.filter_by(tag_id=tag.id).first()
        if association:
            # 这里需要在session中删除
            return association
    
    def get_tags(self):
        """
        获取所有标签
        
        Returns:
            list: 标签列表
        """
        return [assoc.tag for assoc in self.tag_associations.all()]
    
    # === 状态管理方法 ===
    def is_active(self):
        """检查是否为活跃状态"""
        return self.status == 1
    
    def is_draft(self):
        """检查是否为草稿状态"""
        return self.status == 0
    
    def is_deleted(self):
        """检查是否已被软删除"""
        return self.status == -1
    
    def publish(self):
        """发布提示词（从草稿变为正常）"""
        self.status = 1
    
    def set_draft(self):
        """设置为草稿状态"""
        self.status = 0
    
    def soft_delete(self):
        """软删除提示词"""
        self.status = -1
    
    # === 测试相关方法 ===
    def increment_test_count(self):
        """增加测试次数"""
        self.test_count += 1
        # last_tested_at 会在创建测试记录时更新
    
    # === 序列化方法 ===
    def to_dict(self, include_content=True, include_relations=False, exclude_fields=None):
        """
        将提示词模型转换为字典
        
        Args:
            include_content (bool): 是否包含内容字段
            include_relations (bool): 是否包含关联数据
            exclude_fields (list): 需要排除的字段列表
            
        Returns:
            dict: 提示词数据字典
        """
        if exclude_fields is None:
            exclude_fields = []
        
        # 根据参数决定是否排除内容
        if not include_content:
            exclude_fields.extend(['content', 'content_hash'])
        
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 添加关联数据
        if include_relations:
            result['owner'] = self.owner.to_dict(exclude_fields=['password_hash'])
            result['tags'] = [tag.to_dict() for tag in self.get_tags()]
            result['current_version'] = self.get_current_version().to_dict() if self.get_current_version() else None
        
        return result
    
    def __repr__(self):
        """提示词模型的字符串表示"""
        return f"<Prompt(id={self.id}, title='{self.title}', owner_id={self.owner_id})>"

