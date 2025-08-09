"""
数据模型包

这个包包含了所有的数据模型类，每个模型都对应数据库中的一个表。
模型设计遵循以下原则：
1. 高内聚，低耦合 - 每个模型职责单一
2. 扩展性优先 - 预留扩展字段和方法
3. 代码美学 - 优雅的命名和结构
4. 完整注释 - 每个字段和方法都有详细说明
"""

from .base import BaseModel
from .user import User
from .prompt import Prompt
from .prompt_version import PromptVersion
from .tag import Tag
from .prompt_tag import PromptTag
from .prompt_collaborator import PromptCollaborator
from .test_record import TestRecord
from .system_config import SystemConfig
from .operation_log import OperationLog

# 导出所有模型类，方便其他模块导入
__all__ = [
    'BaseModel',
    'User',
    'Prompt',
    'PromptVersion',
    'Tag',
    'PromptTag',
    'PromptCollaborator',
    'TestRecord',
    'SystemConfig',
    'OperationLog'
]

