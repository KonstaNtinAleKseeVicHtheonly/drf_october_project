from core.base_repo import BaseRepository
from apps.accounts.models import User
from django.db.models import Count

class AccountRepo(BaseRepository):
    
    def __init__(self):
        # Передаем модель в базовый класс
        super().__init__(User)
        
        
    def create_new_user(self, validated_data:dict):
        
        new_user = self.model_class.objects.create_user(**validated_data)
        return new_user
    
    def count_user_posts(self, user_id:int):
        
        
        user_posts = self.model.objects.annotate(
        posts_count=Count('posts', distinct=True),#  Считает посты
        ).get(id=user_id)
        return user_posts.count
    
    def count_user_comments(self, user_id:int):
        user_comments = self.model.objects.annotate(
        comments_count=Count('comments', distinct=True),#  Считает коменты
        ).get(id=user_id)
        return user_comments.count
    
    
    
