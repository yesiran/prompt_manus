"""
提示词标签关联模型

定义了提示词和标签之间的多对多关联关系。
"""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class PromptTag(BaseModel):
    """
    提示词标签关联模型类
    
    实现提示词和标签之间的多对多关联关系。
    这个模型虽然简单，但是多对多关系的核心。
    """
    
    __tablename__ = 'prompt_tags'
    
    # === 关联字段 ===
    prompt_id = Column(
        Integer,
        ForeignKey('prompts.id', ondelete='CASCADE'),
        nullable=False,
        comment='提示词ID'
    )
    
    tag_id = Column(
        Integer,
        ForeignKey('tags.id', ondelete='CASCADE'),
        nullable=False,
        comment='标签ID'
    )
    
    # === 关系定义 ===
    prompt = relationship(
        'Prompt',
        back_populates='tag_associations'
    )
    
    tag = relationship(
        'Tag',
        back_populates='prompt_associations'
    )
    
    def __repr__(self):
        """关联模型的字符串表示"""
        return f"<PromptTag(prompt_id={self.prompt_id}, tag_id={self.tag_id})>"

