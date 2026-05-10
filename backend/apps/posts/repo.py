from core.base_repo import BaseRepository
from apps.posts.models import Post
from django.db.models import Count

class PostRepo(BaseRepository):
    
    def __init__(self):
        # Передаем модель в базовый класс
        super().__init__(Post)
        
    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()
    
        
    def create_post(self, **kwargs):
        """Создать запись"""
        return self.model_class.create(**kwargs)