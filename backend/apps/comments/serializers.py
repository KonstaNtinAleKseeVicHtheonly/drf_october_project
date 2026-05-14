from rest_framework import serializers
from apps.comments.models import Comment
from apps.posts.models import Post





class CommentSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для комментариев"""
    author_info = serializers.SerializerMethodField() # поле вычисляется в сериализаторе а не модели
    replies_count = serializers.ReadOnlyField()
    is_reply = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = [
            'id', 'info', 'author', 'author_info', 'parent',
            'is_active', 'replies_count', 'is_reply',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'is_active']
        
    def get_author_info(self, obj):
        '''выводит инфу об авторе коммента'''
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'full_name': obj.author.full_name,
            'avatar': obj.author.avatar.url if obj.author.avatar else None # если аватарки нет то None
        }
        
        
class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментариев"""
    
    class Meta:
        model = Comment
        fields = ['post', 'parent', 'info']

    def validate_post(self, value):
        '''проверка поста с указанными параметрами на публикацию и существование'''
        if not Post.objects.filter(id=value.id, status='published').exists():
            raise serializers.ValidationError('Post not found')
        return value

    def validate_parent(self, value):
        if value:
            # Получаем пост из валидированных данных или из initial_data
            post_data = self.initial_data.get('post')
            if post_data:
                # Сравниваем ID поста родительского комментария с переданным ID поста
                if value.post.id != int(post_data):
                    raise serializers.ValidationError(
                        'Parent comment must belong to the same post.'
                    )
        return value
    
    def create(self, validated_data):
        '''созадние коммента с добавлением инфы о его авторе'''
        # данные в self(сериализатор) поступают из View, в котором мы в serializer_class указали данные сериализатор
        validated_data['author'] = self.context['request'].user # в дату на запись передаем инфу о юзере
        return super().create(validated_data)
    
    
class CommentUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления комментариев"""
    
    class Meta:
        model = Comment
        fields = ['info'] # менять можно только текст коммента
        
        
class CommentDetailSerializer(CommentSerializer):
    '''детальный сериализатор для комментария с ответами'''
    replies = serializers.SerializerMethodField() # ответы на комменты
    
    def get_replies(self, obj):
        '''вернет ответы на комментарии'''

        if obj.parent is None:# ответы только на основные комменты а не вложенные
                comment_replies = obj.replies.filter(is_active=True).order_by('-created_at')
                return CommentSerializer(comment_replies, many=True, context=self.context).data
        return []# если коммент вложенный то не нужно на него ответы возвращать
    
    class Meta:
        model = Comment
        fields = ('id', 'info', 'author', 'created_at', 'replies')  # НЕТ replies