# core/base_service.py
from typing import Optional, List, Dict, Any, TypeVar, Generic
from django.db import models

T = TypeVar('T', bound=models.Model)

class BaseService(Generic[T]):
    """Базовый сервис с общей бизнес-логикой"""
    
    def __init__(self, repository):
        self.repository = repository
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Получить запись по ID"""
        return self.repository.get_by_id(id)
    
    def get_all(self) -> List[T]:
        """Получить все записи"""
        return self.repository.get_all()
    
    def create(self, **kwargs) -> T:
        """Создать запись (можно переопределить)"""
        return self.repository.create(**kwargs)
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Обновить запись (можно переопределить)"""
        return self.repository.update(id, **kwargs)
    
    def delete(self, id: int) -> bool:
        """Удалить запись"""
        return self.repository.delete(id)