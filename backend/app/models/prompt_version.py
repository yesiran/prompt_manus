"""
提示词版本模型

定义了提示词版本的数据结构和相关方法。
版本模型是版本控制系统的核心，记录了提示词的每一次变更历史。
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class PromptVersion(BaseModel):
    """
    提示词版本模型类
    
    记录提示词的版本历史，支持完整的版本控制功能。
    这个模型设计参考了Git的版本管理理念，每个版本都是完整的快照。
    
    核心功能：
    1. 版本快照 - 完整记录每个版本的内容
    2. 版本树 - 支持分支和合并（通过parent_version_id）
    3. 变更追踪 - 记录变更摘要和作者
    4. 版本切换 - 支持回滚和版本对比
    
    设计理念：
    - 不可变性：版本一旦创建就不能修改
    - 完整性：每个版本都包含完整的内容快照
    - 可追溯：清晰的版本链和变更记录
    """
    
    __tablename__ = 'prompt_versions'
    
    # === 关联字段 ===
    prompt_id = Column(
        Integer,
        ForeignKey('prompts.id', ondelete='CASCADE'),
        nullable=False,
        comment='所属提示词ID，外键关联prompts表'
    )
    
    # === 版本信息字段 ===
    version_number = Column(
        Integer,
        nullable=False,
        comment='版本号，从1开始递增'
    )
    
    title = Column(
        String(200),
        nullable=False,
        comment='版本标题，记录当时的标题'
    )
    
    content = Column(
        Text,
        nullable=False,
        comment='版本内容，完整的内容快照'
    )
    
    content_hash = Column(
        String(64),
        nullable=False,
        comment='内容哈希值，用于快速比较版本差异'
    )
    
    change_summary = Column(
        String(500),
        nullable=True,
        comment='变更摘要，描述本次修改的主要内容'
    )
    
    # === 作者信息字段 ===
    author_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment='版本作者ID，记录是谁创建了这个版本'
    )
    
    # === 版本树字段 ===
    parent_version_id = Column(
        Integer,
        ForeignKey('prompt_versions.id', ondelete='SET NULL'),
        nullable=True,
        comment='父版本ID，用于构建版本树结构'
    )
    
    # === 状态字段 ===
    is_current = Column(
        Boolean,
        nullable=False,
        default=False,
        comment='是否为当前版本，每个提示词只能有一个当前版本'
    )
    
    # === 关系定义 ===
    # 多对一：多个版本属于一个提示词
    prompt = relationship(
        'Prompt',
        back_populates='versions'
    )
    
    # 多对一：多个版本由一个用户创建
    author = relationship(
        'User',
        foreign_keys=[author_id]
    )
    
    # 自引用：版本树结构
    parent_version = relationship(
        'PromptVersion',
        remote_side=[BaseModel.id],  # 指向自己的id字段
        backref='child_versions'
    )
    
    # 一对多：一个版本可能有多个测试记录
    test_records = relationship(
        'TestRecord',
        back_populates='prompt_version',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    # === 版本比较方法 ===
    def compare_with(self, other_version):
        """
        与另一个版本进行比较
        
        Args:
            other_version (PromptVersion): 要比较的版本
            
        Returns:
            dict: 比较结果，包含差异信息
        """
        if not isinstance(other_version, PromptVersion):
            raise ValueError("比较对象必须是PromptVersion实例")
        
        result = {
            'is_same': self.content_hash == other_version.content_hash,
            'version_diff': self.version_number - other_version.version_number,
            'title_changed': self.title != other_version.title,
            'content_changed': self.content != other_version.content,
            'author_changed': self.author_id != other_version.author_id
        }
        
        return result
    
    def get_content_diff(self, other_version):
        """
        获取与另一个版本的内容差异
        
        这个方法可以扩展为使用difflib等库来生成详细的差异信息。
        
        Args:
            other_version (PromptVersion): 要比较的版本
            
        Returns:
            dict: 内容差异信息
        """
        import difflib
        
        # 按行分割内容
        self_lines = self.content.splitlines(keepends=True)
        other_lines = other_version.content.splitlines(keepends=True)
        
        # 生成统一差异格式
        diff = list(difflib.unified_diff(
            other_lines,
            self_lines,
            fromfile=f'版本 {other_version.version_number}',
            tofile=f'版本 {self.version_number}',
            lineterm=''
        ))
        
        return {
            'diff_lines': diff,
            'added_lines': len([line for line in diff if line.startswith('+') and not line.startswith('+++')]),
            'removed_lines': len([line for line in diff if line.startswith('-') and not line.startswith('---')]),
            'has_changes': len(diff) > 0
        }
    
    # === 版本树方法 ===
    def get_ancestors(self):
        """
        获取所有祖先版本
        
        Returns:
            list: 祖先版本列表，按时间倒序排列
        """
        ancestors = []
        current = self.parent_version
        
        while current:
            ancestors.append(current)
            current = current.parent_version
        
        return ancestors
    
    def get_descendants(self):
        """
        获取所有后代版本
        
        Returns:
            list: 后代版本列表
        """
        descendants = []
        
        def collect_descendants(version):
            for child in version.child_versions:
                descendants.append(child)
                collect_descendants(child)
        
        collect_descendants(self)
        return descendants
    
    def is_ancestor_of(self, other_version):
        """
        检查是否为另一个版本的祖先
        
        Args:
            other_version (PromptVersion): 要检查的版本
            
        Returns:
            bool: 是否为祖先版本
        """
        current = other_version.parent_version
        
        while current:
            if current.id == self.id:
                return True
            current = current.parent_version
        
        return False
    
    def is_descendant_of(self, other_version):
        """
        检查是否为另一个版本的后代
        
        Args:
            other_version (PromptVersion): 要检查的版本
            
        Returns:
            bool: 是否为后代版本
        """
        return other_version.is_ancestor_of(self)
    
    # === 版本状态方法 ===
    def set_as_current(self):
        """
        将此版本设置为当前版本
        
        注意：这个方法只设置标志，实际的业务逻辑（如更新其他版本的状态）
        应该在服务层处理。
        """
        self.is_current = True
    
    def unset_as_current(self):
        """取消当前版本状态"""
        self.is_current = False
    
    # === 统计方法 ===
    def get_test_count(self):
        """
        获取此版本的测试次数
        
        Returns:
            int: 测试次数
        """
        return self.test_records.count()
    
    def get_latest_test(self):
        """
        获取最新的测试记录
        
        Returns:
            TestRecord: 最新的测试记录，如果没有则返回None
        """
        return self.test_records.order_by('created_at desc').first()
    
    # === 验证方法 ===
    def validate_version_number(self):
        """
        验证版本号的有效性
        
        Returns:
            bool: 版本号是否有效
        """
        if self.version_number <= 0:
            return False
        
        # 检查是否与同一提示词的其他版本冲突
        if self.prompt:
            existing = self.prompt.versions.filter_by(
                version_number=self.version_number
            ).filter(PromptVersion.id != self.id).first()
            
            return existing is None
        
        return True
    
    def validate_content_hash(self):
        """
        验证内容哈希值是否正确
        
        Returns:
            bool: 哈希值是否正确
        """
        import hashlib
        expected_hash = hashlib.sha256(self.content.encode('utf-8')).hexdigest()
        return self.content_hash == expected_hash
    
    # === 序列化方法 ===
    def to_dict(self, include_content=True, include_relations=False, exclude_fields=None):
        """
        将版本模型转换为字典
        
        Args:
            include_content (bool): 是否包含内容字段
            include_relations (bool): 是否包含关联数据
            exclude_fields (list): 需要排除的字段列表
            
        Returns:
            dict: 版本数据字典
        """
        if exclude_fields is None:
            exclude_fields = []
        
        # 根据参数决定是否排除内容
        if not include_content:
            exclude_fields.extend(['content'])
        
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 添加关联数据
        if include_relations:
            result['author'] = self.author.to_dict(exclude_fields=['password_hash'])
            result['prompt'] = self.prompt.to_dict(include_content=False, include_relations=False)
            
            if self.parent_version:
                result['parent_version'] = self.parent_version.to_dict(
                    include_content=False, 
                    include_relations=False
                )
        
        # 添加计算字段
        result['test_count'] = self.get_test_count()
        result['is_valid'] = self.validate_content_hash()
        
        return result
    
    def __repr__(self):
        """版本模型的字符串表示"""
        return (f"<PromptVersion(id={self.id}, prompt_id={self.prompt_id}, "
                f"version_number={self.version_number}, is_current={self.is_current})>")

