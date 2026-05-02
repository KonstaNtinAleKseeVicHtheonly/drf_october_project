# core/base_repository.py
from typing import Optional, List, TypeVar, Generic
from django.db import models

T = TypeVar('T', bound=models.Model)

class BaseRepository(Generic[T]):
    """Базовый репозиторий с общими CRUD операциями"""
    
    def __init__(self, model_class: type[T]):
        self.model_class = model_class
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Получить запись по ID"""
        try:
            return self.model_class.objects.get(id=id)
        except self.model_class.DoesNotExist:
            return None
    def get_by_params(self, **params:dict):
        '''ищет по параметрам в бд строку Возвращает QuerySet (может быть пустым)'''
        
        return self.model_class.objects.filter(**params)
        
    def get_all(self) -> List[T]:
        """Получить все записи"""
        return list(self.model_class.objects.all())
    
    def create(self, **kwargs) -> T:
        """Создать запись"""
        return self.model_class.objects.create(**kwargs)
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Обновить запись"""
        instance = self.get_by_id(id)
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, id: int) -> bool:
        """Удалить запись"""
        instance = self.get_by_id(id)
        if instance:
            instance.delete()
            return True
        return False
    
    def filter(self, **kwargs) -> List[T]:
        """Фильтрация записей"""
        return list(self.model_class.objects.filter(**kwargs))
    
    def persist(self, object):
        '''метод для сохранения объекта и возвращения его'''
        object.save()
        return object