"""
测试记录模型

定义了AI测试记录的数据结构和相关方法。
记录提示词在不同AI模型上的测试结果和性能数据。
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class TestRecord(BaseModel):
    """
    测试记录模型类
    
    记录提示词在AI模型上的测试结果，支持性能分析和效果评估。
    设计理念：完整记录测试过程，支持后续分析和优化。
    """
    
    __tablename__ = 'test_records'
    
    # === 关联字段 ===
    prompt_id = Column(
        Integer,
        ForeignKey('prompts.id', ondelete='CASCADE'),
        nullable=False,
        comment='测试的提示词ID'
    )
    
    prompt_version_id = Column(
        Integer,
        ForeignKey('prompt_versions.id', ondelete='SET NULL'),
        nullable=True,
        comment='测试的版本ID，可为空'
    )
    
    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment='执行测试的用户ID'
    )
    
    # === 测试配置字段 ===
    model_name = Column(
        String(50),
        nullable=False,
        comment='AI模型名称，如GPT-4、Claude等'
    )
    
    input_content = Column(
        Text,
        nullable=True,
        comment='输入内容，用于测试的具体输入'
    )
    
    # === 测试结果字段 ===
    output_content = Column(
        Text,
        nullable=True,
        comment='输出内容，AI模型的响应结果'
    )
    
    response_time = Column(
        Integer,
        nullable=True,
        comment='响应时间，单位毫秒'
    )
    
    token_usage = Column(
        JSON,
        nullable=True,
        comment='Token使用情况，JSON格式存储'
    )
    
    # === 评估字段 ===
    rating = Column(
        Integer,
        nullable=True,
        comment='用户评分，1-5分'
    )
    
    notes = Column(
        Text,
        nullable=True,
        comment='测试备注，用户的评价和说明'
    )
    
    # === 状态字段 ===
    status = Column(
        Integer,
        nullable=False,
        default=1,
        comment='测试状态：1-成功，0-失败，2-超时'
    )
    
    error_message = Column(
        Text,
        nullable=True,
        comment='错误信息，测试失败时的详细错误'
    )
    
    # === 关系定义 ===
    prompt = relationship(
        'Prompt',
        back_populates='test_records'
    )
    
    prompt_version = relationship(
        'PromptVersion',
        back_populates='test_records'
    )
    
    user = relationship(
        'User',
        back_populates='test_records'
    )
    
    # === 状态判断方法 ===
    def is_successful(self):
        """测试是否成功"""
        return self.status == 1
    
    def is_failed(self):
        """测试是否失败"""
        return self.status == 0
    
    def is_timeout(self):
        """测试是否超时"""
        return self.status == 2
    
    # === Token使用分析方法 ===
    def get_token_usage(self, key=None):
        """
        获取Token使用情况
        
        Args:
            key (str): 特定的键，如'prompt_tokens', 'completion_tokens'
            
        Returns:
            dict or value: Token使用数据
        """
        if self.token_usage is None:
            return None if key is None else 0
        
        if key is None:
            return self.token_usage
        
        return self.token_usage.get(key, 0)
    
    def get_total_tokens(self):
        """获取总Token数"""
        if self.token_usage is None:
            return 0
        
        return (self.token_usage.get('prompt_tokens', 0) + 
                self.token_usage.get('completion_tokens', 0))
    
    def get_cost_estimate(self, model_pricing=None):
        """
        估算测试成本
        
        Args:
            model_pricing (dict): 模型定价信息
            
        Returns:
            float: 估算成本
        """
        if not model_pricing or self.token_usage is None:
            return 0.0
        
        prompt_tokens = self.token_usage.get('prompt_tokens', 0)
        completion_tokens = self.token_usage.get('completion_tokens', 0)
        
        prompt_cost = prompt_tokens * model_pricing.get('prompt_price_per_token', 0)
        completion_cost = completion_tokens * model_pricing.get('completion_price_per_token', 0)
        
        return prompt_cost + completion_cost
    
    # === 性能分析方法 ===
    def get_response_time_seconds(self):
        """获取响应时间（秒）"""
        if self.response_time is None:
            return None
        return self.response_time / 1000.0
    
    def is_fast_response(self, threshold_ms=5000):
        """
        判断是否为快速响应
        
        Args:
            threshold_ms (int): 阈值，单位毫秒
            
        Returns:
            bool: 是否为快速响应
        """
        if self.response_time is None:
            return False
        return self.response_time <= threshold_ms
    
    # === 评分相关方法 ===
    def set_rating(self, rating, notes=None):
        """
        设置评分
        
        Args:
            rating (int): 评分，1-5分
            notes (str): 评价备注
        """
        if 1 <= rating <= 5:
            self.rating = rating
        if notes:
            self.notes = notes
    
    def is_good_rating(self, threshold=4):
        """
        判断是否为好评
        
        Args:
            threshold (int): 好评阈值
            
        Returns:
            bool: 是否为好评
        """
        if self.rating is None:
            return False
        return self.rating >= threshold
    
    # === 序列化方法 ===
    def to_dict(self, include_relations=False, exclude_fields=None):
        """
        将测试记录转换为字典
        
        Args:
            include_relations (bool): 是否包含关联数据
            exclude_fields (list): 需要排除的字段列表
            
        Returns:
            dict: 测试记录数据字典
        """
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 添加关联数据
        if include_relations:
            result['prompt'] = self.prompt.to_dict(include_content=False, include_relations=False)
            result['user'] = self.user.to_dict(exclude_fields=['password_hash'])
            
            if self.prompt_version:
                result['prompt_version'] = self.prompt_version.to_dict(
                    include_content=False, 
                    include_relations=False
                )
        
        # 添加计算字段
        result['total_tokens'] = self.get_total_tokens()
        result['response_time_seconds'] = self.get_response_time_seconds()
        result['is_successful'] = self.is_successful()
        result['is_good_rating'] = self.is_good_rating()
        
        return result
    
    def __repr__(self):
        """测试记录的字符串表示"""
        return (f"<TestRecord(id={self.id}, prompt_id={self.prompt_id}, "
                f"model='{self.model_name}', status={self.status})>")

