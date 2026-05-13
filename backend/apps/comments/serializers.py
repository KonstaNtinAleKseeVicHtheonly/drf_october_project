from rest_framework import serializers
from apps.comments.models import Comment
from apps.posts.models import Post


class CommentSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для комментариев"""
    author_info = serializers.SerializerMethodField()
    replies_count = serializers.ReadOnlyField()
    is_reply = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'author_info', 'parent',
            'is_active', 'replies_count', 'is_reply',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'is_active']