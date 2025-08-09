"""
业务服务层包

这个包包含了所有的业务逻辑服务类。
服务层是连接API层和数据层的桥梁，负责实现具体的业务逻辑。

设计理念：
1. 单一职责 - 每个服务类负责一个业务领域
2. 依赖注入 - 通过构造函数注入依赖
3. 事务管理 - 在服务层处理数据库事务
4. 异常处理 - 统一的业务异常处理
"""

from .base_service import BaseService
from .user_service import UserService
from .prompt_service import PromptService
from .version_service import VersionService
from .tag_service import TagService
from .collaboration_service import CollaborationService
from .test_service import TestService

__all__ = [
    'BaseService',
    'UserService',
    'PromptService', 
    'VersionService',
    'TagService',
    'CollaborationService',
    'TestService'
]

