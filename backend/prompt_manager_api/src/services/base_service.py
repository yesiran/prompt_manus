"""
基础服务类

定义了所有业务服务的基类，包含通用的CRUD操作和事务管理。
这个类体现了服务层设计的艺术：抽象、复用、优雅。
"""

from typing import Type, List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query

from src.config.database import db
from src.config.logger import get_logger, log_database_operation, log_user_action
from src.models.base import BaseModel


class ServiceException(Exception):
    """
    业务服务异常类
    
    用于封装业务逻辑中的异常情况。
    """
    
    def __init__(self, message: str, code: str = None, details: Dict = None):
        self.message = message
        self.code = code or 'SERVICE_ERROR'
        self.details = details or {}
        super().__init__(self.message)


class BaseService:
    """
    基础服务类
    
    提供通用的CRUD操作、事务管理、日志记录等功能。
    所有具体的业务服务都应该继承这个类。
    
    设计理念：
    - DRY原则：避免重复的CRUD代码
    - 事务安全：自动处理数据库事务
    - 日志记录：记录所有重要操作
    - 异常处理：统一的错误处理机制
    """
    
    def __init__(self, model_class: Type[BaseModel]):
        """
        初始化基础服务
        
        Args:
            model_class: 对应的数据模型类
        """
        self.model_class = model_class
        self.logger = get_logger(f'service.{model_class.__name__.lower()}')
        self.table_name = model_class.__tablename__
    
    # === 基础CRUD操作 ===
    
    def create(self, data: Dict[str, Any], user_id: int = None) -> BaseModel:
        """
        创建新记录
        
        Args:
            data: 创建数据
            user_id: 操作用户ID
            
        Returns:
            BaseModel: 创建的模型实例
            
        Raises:
            ServiceException: 创建失败时抛出
        """
        try:
            # 创建模型实例
            instance = self.model_class(**data)
            
            # 保存到数据库
            db.session.add(instance)
            db.session.commit()
            
            # 记录日志
            log_database_operation('CREATE', self.table_name, instance.id, data)
            if user_id:
                log_user_action(user_id, 'CREATE', self.table_name, instance.id, data)
            
            self.logger.info(f"创建{self.table_name}记录成功: ID={instance.id}")
            return instance
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"创建{self.table_name}记录失败: {str(e)}")
            raise ServiceException(f"创建记录失败: {str(e)}", 'CREATE_FAILED')
    
    def get_by_id(self, record_id: int) -> Optional[BaseModel]:
        """
        根据ID获取记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            BaseModel: 模型实例，如果不存在则返回None
        """
        try:
            instance = self.model_class.query.get(record_id)
            
            if instance:
                log_database_operation('READ', self.table_name, record_id)
            
            return instance
            
        except SQLAlchemyError as e:
            self.logger.error(f"查询{self.table_name}记录失败: {str(e)}")
            raise ServiceException(f"查询记录失败: {str(e)}", 'QUERY_FAILED')
    
    def get_by_id_or_404(self, record_id: int) -> BaseModel:
        """
        根据ID获取记录，如果不存在则抛出异常
        
        Args:
            record_id: 记录ID
            
        Returns:
            BaseModel: 模型实例
            
        Raises:
            ServiceException: 记录不存在时抛出
        """
        instance = self.get_by_id(record_id)
        if not instance:
            raise ServiceException(f"记录不存在: ID={record_id}", 'RECORD_NOT_FOUND')
        return instance
    
    def update(self, record_id: int, data: Dict[str, Any], user_id: int = None) -> BaseModel:
        """
        更新记录
        
        Args:
            record_id: 记录ID
            data: 更新数据
            user_id: 操作用户ID
            
        Returns:
            BaseModel: 更新后的模型实例
            
        Raises:
            ServiceException: 更新失败时抛出
        """
        try:
            instance = self.get_by_id_or_404(record_id)
            
            # 记录更新前的数据
            old_data = instance.to_dict()
            
            # 更新字段
            instance.update_from_dict(data)
            
            # 保存到数据库
            db.session.commit()
            
            # 记录日志
            update_details = {
                'old_data': old_data,
                'new_data': data
            }
            log_database_operation('UPDATE', self.table_name, record_id, update_details)
            if user_id:
                log_user_action(user_id, 'UPDATE', self.table_name, record_id, update_details)
            
            self.logger.info(f"更新{self.table_name}记录成功: ID={record_id}")
            return instance
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"更新{self.table_name}记录失败: {str(e)}")
            raise ServiceException(f"更新记录失败: {str(e)}", 'UPDATE_FAILED')
    
    def delete(self, record_id: int, user_id: int = None, soft_delete: bool = True) -> bool:
        """
        删除记录
        
        Args:
            record_id: 记录ID
            user_id: 操作用户ID
            soft_delete: 是否软删除
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            ServiceException: 删除失败时抛出
        """
        try:
            instance = self.get_by_id_or_404(record_id)
            
            if soft_delete and hasattr(instance, 'soft_delete'):
                # 软删除
                instance.soft_delete()
                operation = 'SOFT_DELETE'
            else:
                # 硬删除
                db.session.delete(instance)
                operation = 'DELETE'
            
            db.session.commit()
            
            # 记录日志
            log_database_operation(operation, self.table_name, record_id)
            if user_id:
                log_user_action(user_id, operation, self.table_name, record_id)
            
            self.logger.info(f"{operation}{self.table_name}记录成功: ID={record_id}")
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"删除{self.table_name}记录失败: {str(e)}")
            raise ServiceException(f"删除记录失败: {str(e)}", 'DELETE_FAILED')
    
    def list(self, page: int = 1, per_page: int = 20, filters: Dict = None, 
             order_by: str = None) -> Dict[str, Any]:
        """
        分页查询记录列表
        
        Args:
            page: 页码
            per_page: 每页数量
            filters: 过滤条件
            order_by: 排序字段
            
        Returns:
            dict: 包含数据和分页信息的字典
        """
        try:
            query = self.model_class.query
            
            # 应用过滤条件
            if filters:
                query = self._apply_filters(query, filters)
            
            # 应用排序
            if order_by:
                query = self._apply_ordering(query, order_by)
            
            # 分页查询
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # 记录日志
            log_database_operation('LIST', self.table_name, None, {
                'page': page,
                'per_page': per_page,
                'total': pagination.total
            })
            
            return {
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
            
        except SQLAlchemyError as e:
            self.logger.error(f"查询{self.table_name}列表失败: {str(e)}")
            raise ServiceException(f"查询列表失败: {str(e)}", 'LIST_FAILED')
    
    def _apply_filters(self, query: Query, filters: Dict) -> Query:
        """
        应用过滤条件
        
        Args:
            query: SQLAlchemy查询对象
            filters: 过滤条件字典
            
        Returns:
            Query: 应用过滤条件后的查询对象
        """
        for field, value in filters.items():
            if hasattr(self.model_class, field):
                column = getattr(self.model_class, field)
                
                # 处理不同类型的过滤条件
                if isinstance(value, dict):
                    # 复杂过滤条件，如 {'gt': 10}, {'like': '%test%'}
                    for op, op_value in value.items():
                        if op == 'gt':
                            query = query.filter(column > op_value)
                        elif op == 'gte':
                            query = query.filter(column >= op_value)
                        elif op == 'lt':
                            query = query.filter(column < op_value)
                        elif op == 'lte':
                            query = query.filter(column <= op_value)
                        elif op == 'like':
                            query = query.filter(column.like(op_value))
                        elif op == 'in':
                            query = query.filter(column.in_(op_value))
                else:
                    # 简单等值过滤
                    query = query.filter(column == value)
        
        return query
    
    def _apply_ordering(self, query: Query, order_by: str) -> Query:
        """
        应用排序
        
        Args:
            query: SQLAlchemy查询对象
            order_by: 排序字段，支持 'field' 或 '-field' (降序)
            
        Returns:
            Query: 应用排序后的查询对象
        """
        if order_by.startswith('-'):
            # 降序
            field = order_by[1:]
            if hasattr(self.model_class, field):
                column = getattr(self.model_class, field)
                query = query.order_by(column.desc())
        else:
            # 升序
            if hasattr(self.model_class, order_by):
                column = getattr(self.model_class, order_by)
                query = query.order_by(column.asc())
        
        return query
    
    # === 事务管理 ===
    
    def execute_in_transaction(self, func, *args, **kwargs):
        """
        在事务中执行函数
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            ServiceException: 事务执行失败时抛出
        """
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"事务执行失败: {str(e)}")
            raise ServiceException(f"事务执行失败: {str(e)}", 'TRANSACTION_FAILED')
    
    # === 批量操作 ===
    
    def bulk_create(self, data_list: List[Dict], user_id: int = None) -> List[BaseModel]:
        """
        批量创建记录
        
        Args:
            data_list: 创建数据列表
            user_id: 操作用户ID
            
        Returns:
            List[BaseModel]: 创建的模型实例列表
        """
        try:
            instances = []
            for data in data_list:
                instance = self.model_class(**data)
                instances.append(instance)
                db.session.add(instance)
            
            db.session.commit()
            
            # 记录日志
            log_database_operation('BULK_CREATE', self.table_name, None, {
                'count': len(instances)
            })
            if user_id:
                log_user_action(user_id, 'BULK_CREATE', self.table_name, None, {
                    'count': len(instances)
                })
            
            self.logger.info(f"批量创建{self.table_name}记录成功: 数量={len(instances)}")
            return instances
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"批量创建{self.table_name}记录失败: {str(e)}")
            raise ServiceException(f"批量创建失败: {str(e)}", 'BULK_CREATE_FAILED')
    
    def count(self, filters: Dict = None) -> int:
        """
        统计记录数量
        
        Args:
            filters: 过滤条件
            
        Returns:
            int: 记录数量
        """
        try:
            query = self.model_class.query
            
            if filters:
                query = self._apply_filters(query, filters)
            
            return query.count()
            
        except SQLAlchemyError as e:
            self.logger.error(f"统计{self.table_name}记录数量失败: {str(e)}")
            raise ServiceException(f"统计失败: {str(e)}", 'COUNT_FAILED')

