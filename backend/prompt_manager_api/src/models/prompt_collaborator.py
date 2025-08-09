"""
提示词协作者模型

定义了提示词协作关系的数据结构和相关方法。
支持多用户协作编辑提示词，包含权限管理功能。
"""

from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class PromptCollaborator(BaseModel):
    """
    提示词协作者模型类
    
    管理提示词的协作关系，支持不同角色和权限。
    设计理念：灵活的权限控制，支持未来扩展。
    """
    
    __tablename__ = 'prompt_collaborators'
    
    # === 关联字段 ===
    prompt_id = Column(
        Integer,
        ForeignKey('prompts.id', ondelete='CASCADE'),
        nullable=False,
        comment='提示词ID'
    )
    
    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment='协作者用户ID'
    )
    
    # === 权限字段 ===
    role = Column(
        Integer,
        nullable=False,
        default=2,
        comment='角色：1-所有者，2-编辑者，3-查看者'
    )
    
    permissions = Column(
        JSON,
        nullable=True,
        comment='详细权限配置，JSON格式'
    )
    
    # === 邀请信息字段 ===
    invited_by = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment='邀请者用户ID'
    )
    
    invited_at = Column(
        'invited_at',
        nullable=False,
        comment='邀请时间'
    )
    
    accepted_at = Column(
        'accepted_at',
        nullable=True,
        comment='接受邀请时间'
    )
    
    # === 状态字段 ===
    status = Column(
        Integer,
        nullable=False,
        default=1,
        comment='状态：1-正常，0-待接受，-1-已拒绝'
    )
    
    # === 关系定义 ===
    prompt = relationship(
        'Prompt',
        back_populates='collaborators'
    )
    
    user = relationship(
        'User',
        foreign_keys=[user_id],
        back_populates='collaborated_prompts'
    )
    
    inviter = relationship(
        'User',
        foreign_keys=[invited_by]
    )
    
    # === 角色权限方法 ===
    def is_owner(self):
        """是否为所有者"""
        return self.role == 1
    
    def is_editor(self):
        """是否为编辑者"""
        return self.role == 2
    
    def is_viewer(self):
        """是否为查看者"""
        return self.role == 3
    
    def can_edit(self):
        """是否有编辑权限"""
        return self.role <= 2
    
    def can_view(self):
        """是否有查看权限"""
        return self.role <= 3
    
    # === 状态管理方法 ===
    def is_active(self):
        """是否为活跃状态"""
        return self.status == 1
    
    def is_pending(self):
        """是否为待接受状态"""
        return self.status == 0
    
    def is_rejected(self):
        """是否已拒绝"""
        return self.status == -1
    
    def accept(self):
        """接受邀请"""
        self.status = 1
        from datetime import datetime
        self.accepted_at = datetime.utcnow()
    
    def reject(self):
        """拒绝邀请"""
        self.status = -1
    
    def __repr__(self):
        """协作者模型的字符串表示"""
        return (f"<PromptCollaborator(prompt_id={self.prompt_id}, "
                f"user_id={self.user_id}, role={self.role})>")

