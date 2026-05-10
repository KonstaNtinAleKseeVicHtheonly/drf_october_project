from django.utils import timezone

from core.base_service import BaseService
from apps.posts.repo import PostRepo
from rest_framework.exceptions import ValidationError
from django.db.models import Count
from apps.posts.models import Post
from core.project_logging import get_logger
from django.utils.text import slugify


logger = get_logger(__name__)



class PostService(BaseService):
    
    def __init__(self):
        # Инициализируем с конкретным репозиторием
        repository = PostRepo()
        super().__init__(repository)
        
    def create_post(self,post_author:str, new_post_data:dict):
        '''создаст слаг по имнеи поста и создаст его'''
        new_post_data['author'] = slugify(post_author)
        new_post_data['slug'] = slugify(new_post_data['name'])
        return self.repository.create(**new_post_data)
    
    def update(self, instance, validated_data):
        if 'title' in validated_data:
            validated_data['slug'] = slugify(validated_data['title'])
        return self.repository.update(instance.id, **validated_data)
    
    def increment_views(self, current_post):
        '''увеличивает количество просмотров в посе на 1'''
        current_post.views += 1
        current_post.save()
        return current_post
        
        