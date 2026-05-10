from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
# сервисы
from apps.posts.service import PostService
from apps.posts.models import Category, Post
from apps.posts.serializers import (
    CategorySerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer
)
from apps.posts.permissions import IsAuthorOrReadOnly
#openapi свагер
from drf_spectacular.utils import extend_schema
tags = ["Accounts"]





class CategoryListCreateView(generics.ListCreateAPIView):
    """API endpoint для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] # филтрация в query запросе
    search_fields = ['name', 'description'] # query запрос на поиск
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint для конкретной категории"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug' # поиск в запросе по slug вместо id /category/sport-nutrition

class PostListCreateView(generics.ListCreateAPIView): # есть и post и get методы
    """
    API endpoint для постов c поддержкой закрепленных постов.
    Закрепленные посты отображаются первыми в порядке закрепления.
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'status']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'title']
    ordering = ['-created_at']
    
    
    def get_queryset(self): # определяет логику вывода инфы при гет запросе
        """Возвращает посты с учетом прав доступа"""

        # ✅ КЛЮЧЕВОЕ исправление - проверка на Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()  # Возвращаем пустой queryset для схемы
        queryset = Post.objects.select_related('author', 'category')

        # фильрация по правам доступа
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        else:
            queryset = queryset.filter(
                Q(status='published') | Q(author=self.request.user)
            )

        # # Проверяем, нужна ли сортировка с учетом закрепленных постов
        # ordering = self.request.query_params.get('ordering', '')
        # show_pinned_first = not ordering or ordering in ['-created_at', 'created_at']
        
        # if show_pinned_first:
        #     return Post.get_posts_for_feed().filter(
        #         Q(status='published') | (
        #             Q(author=self.request.user) if self.request.user.is_authenticated else Q()
        #         )
        #     )

        return queryset
    
    def get_serializer_class(self): # каким сериализатором пользоваться в зависимости от типа запроса
        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostListSerializer
    
    
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
        '''коннтролле для выывода детальной инфы об опред посте'''
        queryset = Post.objects.select_related('author', 'category')# уже срощенная таблицы поста с ифной об автое и категории из других таблиц
        serializer_class = PostDetailSerializer
        permission_classes = [IsAuthorOrReadOnly]
        lookup_field = 'slug'
        
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.post_service = PostService()  #  Внедряем сервис
            
        
        def get_serializer_class(self): # каким сериализатором пользоваться в зависимости от типа запроса
            if self.request.method in ['PUT', 'PATCH']:
                return PostCreateUpdateSerializer
            return PostListSerializer
        
        
        def retrieve(self, request, *args, **kwargs):
            """Увеличивает счетчик просмотров при GET запросе"""
            current_post = self.get_object()

            if request.method == 'GET':
                self.post_service.increment_views(current_post)

            serializer = self.get_serializer(current_post)
            return Response(serializer.data)
                
class MyPostsView(generics.ListAPIView):
    """API endpoint для постов текущего пользователя"""
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        # ✅ КЛЮЧЕВОЕ исправление - проверка на Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()  # Возвращаем пустой queryset для схемы
        return Post.objects.filter(
            author=self.request.user
        ).select_related('author', 'category')
        
        
        
        
@extend_schema(
    summary="Get posts by category", 
    description="""
        Вывод постов опред категории
    """,
    tags=tags,
    responses={200: PostListSerializer(many=True)} 
)  
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def post_by_category(request, category_slug):
    """Вывод Постов определенной категории"""
    current_category = get_object_or_404(Category, slug=category_slug)
    
    posts = Post.objects.with_subscription_info().filter(
        category=current_category,
        status='published')
    serializer = PostListSerializer(posts, many=True, context={'request': request}) # валидация найденных постов
    
    return Response({'category':CategorySerializer(current_category).data,
                     'posts' : serializer.data})
    
    
@extend_schema(
    summary="Get top 10 popular posts", 
    description="""
        Вывод 10 самых просматриваемых постов
    """,
    tags=tags,
    responses={200: PostListSerializer(many=True)} 
)  
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def popular_posts(request):
    """10 самых популярных постов"""
    posts = Post.objects.with_subscription_info().filter(
        status='published'
    ).order_by('-views_count')[:10] # первый 10 по количествам просмотров
    
    serializer = PostListSerializer(
        posts, 
        many=True, 
        context={'request': request}
    )
    return Response(serializer.data)


@extend_schema(
    summary="Get top 10 fresh posts", 
    description="""
        Вывод 10 самых новых постов(по дате)
    """,
    responses={200: PostListSerializer(many=True)},
    tags=tags, 
)  
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recent_posts(request):
    """10 последних опубликованных постов"""
    posts = Post.objects.with_subscription_info().filter(
        status='published'
    ).order_by('-created_at')[:10]
    
    serializer = PostListSerializer(
        posts, 
        many=True, 
        context={'request': request}
    )
    return Response(serializer.data)


@extend_schema(
    summary="Get pinned posts only",
    description="Returns list of all pinned posts",
    responses={200: PostListSerializer(many=True)},
    tags=tags
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def pinned_posts_only(request):
    """Только закрепленные посты"""
    posts = Post.objects.pinned_posts()
    serializer = PostListSerializer(
        posts,
        many=True,
        context={'request': request}
    )
    return Response({
        'count': posts.count(),
        'results': serializer.data
    })