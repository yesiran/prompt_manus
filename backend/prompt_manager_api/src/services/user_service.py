"""
用户服务类

实现用户相关的业务逻辑，包括注册、登录、用户管理等功能。
这个服务体现了用户管理的完整业务逻辑。
"""

from typing import Optional, Dict, Any
from werkzeug.security import check_password_hash

from src.models.user import User
from src.services.base_service import BaseService, ServiceException
from src.config.logger import get_logger


class UserService(BaseService):
    """
    用户服务类
    
    负责处理用户相关的所有业务逻辑。
    设计理念：安全第一、用户体验优先、扩展性考虑。
    """
    
    def __init__(self):
        super().__init__(User)
        self.logger = get_logger('service.user')
    
    def register(self, username: str, email: str, password: str, 
                display_name: str = None) -> User:
        """
        用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            display_name: 显示名称
            
        Returns:
            User: 创建的用户实例
            
        Raises:
            ServiceException: 注册失败时抛出
        """
        # 验证用户名和邮箱是否已存在
        if self.get_by_username(username):
            raise ServiceException("用户名已存在", 'USERNAME_EXISTS')
        
        if self.get_by_email(email):
            raise ServiceException("邮箱已存在", 'EMAIL_EXISTS')
        
        # 验证密码强度
        self._validate_password(password)
        
        # 创建用户数据
        user_data = {
            'username': username,
            'email': email,
            'display_name': display_name or username,
            'status': 1  # 正常状态
        }
        
        # 创建用户
        user = self.create(user_data)
        
        # 设置密码（单独处理以确保加密）
        user.set_password(password)
        
        # 保存密码
        from src.config.database import db
        db.session.commit()
        
        self.logger.info(f"用户注册成功: {username} ({email})")
        return user
    
    def login(self, username_or_email: str, password: str) -> Optional[User]:
        """
        用户登录
        
        Args:
            username_or_email: 用户名或邮箱
            password: 密码
            
        Returns:
            User: 登录成功的用户实例，失败返回None
        """
        # 查找用户
        user = self.get_by_username_or_email(username_or_email)
        
        if not user:
            self.logger.warning(f"登录失败: 用户不存在 - {username_or_email}")
            return None
        
        # 检查用户状态
        if not user.is_active():
            self.logger.warning(f"登录失败: 用户已被禁用 - {username_or_email}")
            raise ServiceException("账户已被禁用", 'ACCOUNT_DISABLED')
        
        # 验证密码
        if not user.check_password(password):
            self.logger.warning(f"登录失败: 密码错误 - {username_or_email}")
            return None
        
        # 更新最后登录时间
        from datetime import datetime
        user.last_login_at = datetime.utcnow()
        
        from src.config.database import db
        db.session.commit()
        
        self.logger.info(f"用户登录成功: {user.username}")
        return user
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            User: 用户实例，如果不存在则返回None
        """
        return User.query.filter_by(username=username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱
            
        Returns:
            User: 用户实例，如果不存在则返回None
        """
        return User.query.filter_by(email=email).first()
    
    def get_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        """
        根据用户名或邮箱获取用户
        
        Args:
            username_or_email: 用户名或邮箱
            
        Returns:
            User: 用户实例，如果不存在则返回None
        """
        user = self.get_by_username(username_or_email)
        if not user:
            user = self.get_by_email(username_or_email)
        return user
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            bool: 是否修改成功
            
        Raises:
            ServiceException: 修改失败时抛出
        """
        user = self.get_by_id_or_404(user_id)
        
        # 验证旧密码
        if not user.check_password(old_password):
            raise ServiceException("旧密码错误", 'INVALID_OLD_PASSWORD')
        
        # 验证新密码强度
        self._validate_password(new_password)
        
        # 设置新密码
        user.set_password(new_password)
        
        from src.config.database import db
        db.session.commit()
        
        self.logger.info(f"用户修改密码成功: {user.username}")
        return True
    
    def update_profile(self, user_id: int, profile_data: Dict[str, Any]) -> User:
        """
        更新用户资料
        
        Args:
            user_id: 用户ID
            profile_data: 资料数据
            
        Returns:
            User: 更新后的用户实例
        """
        # 过滤允许更新的字段
        allowed_fields = ['display_name', 'bio', 'avatar_url']
        filtered_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
        
        return self.update(user_id, filtered_data, user_id)
    
    def update_preferences(self, user_id: int, preferences: Dict[str, Any]) -> User:
        """
        更新用户偏好设置
        
        Args:
            user_id: 用户ID
            preferences: 偏好设置
            
        Returns:
            User: 更新后的用户实例
        """
        user = self.get_by_id_or_404(user_id)
        
        # 更新偏好设置
        for key, value in preferences.items():
            user.set_preference(key, value)
        
        from src.config.database import db
        db.session.commit()
        
        self.logger.info(f"用户更新偏好设置成功: {user.username}")
        return user
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 统计信息
        """
        user = self.get_by_id_or_404(user_id)
        
        return {
            'prompt_count': user.get_prompt_count(),
            'collaboration_count': user.get_collaboration_count(),
            'created_tags_count': user.created_tags.count(),
            'test_records_count': user.test_records.count(),
            'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
            'account_created_at': user.created_at.isoformat(),
            'is_active': user.is_active()
        }
    
    def _validate_password(self, password: str) -> None:
        """
        验证密码强度
        
        Args:
            password: 密码
            
        Raises:
            ServiceException: 密码不符合要求时抛出
        """
        from src.config import config
        
        min_length = config.PASSWORD_MIN_LENGTH
        
        if len(password) < min_length:
            raise ServiceException(
                f"密码长度不能少于{min_length}位", 
                'PASSWORD_TOO_SHORT'
            )
        
        # 可以添加更多密码强度验证规则
        # 如：必须包含大小写字母、数字、特殊字符等
    
    def deactivate_user(self, user_id: int, operator_id: int) -> User:
        """
        停用用户账户
        
        Args:
            user_id: 用户ID
            operator_id: 操作者ID
            
        Returns:
            User: 更新后的用户实例
        """
        user = self.get_by_id_or_404(user_id)
        user.deactivate()
        
        from src.config.database import db
        db.session.commit()
        
        from src.config.logger import log_user_action
        log_user_action(operator_id, 'DEACTIVATE', 'user', user_id)
        
        self.logger.info(f"用户账户已停用: {user.username}")
        return user
    
    def activate_user(self, user_id: int, operator_id: int) -> User:
        """
        激活用户账户
        
        Args:
            user_id: 用户ID
            operator_id: 操作者ID
            
        Returns:
            User: 更新后的用户实例
        """
        user = self.get_by_id_or_404(user_id)
        user.activate()
        
        from src.config.database import db
        db.session.commit()
        
        from src.config.logger import log_user_action
        log_user_action(operator_id, 'ACTIVATE', 'user', user_id)
        
        self.logger.info(f"用户账户已激活: {user.username}")
        return user

