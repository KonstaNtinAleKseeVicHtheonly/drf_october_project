from django.db import models
from django.conf import settings

# Create your models here.
from django.contrib.auth.models import AbstractUser
# Create your models here.


class Comment(models.Model):
    
    """Кастомная модель пользователя"""
    info = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='comments')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    

    class Meta:
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent', '-created_at']),
        ]

    def __str__(self):
        '''вернет комментарий с инфой об авторе коммента, посте и датой создания коммента'''
        return f'Comment by {self.author.username} on {self.post.title}, created_at {self.created_at}'
     
    @property
    def replies_count(self):
        '''подсчет количества комментов к ответу'''
        return self.replies.filter(is_active=True).count()

    @property
    def is_reply(self):
        '''првоерка является ли комментарий ответом на другйо коммент или это изначальынй коммент
        под каким либо постом'''
        return self.parent is not None