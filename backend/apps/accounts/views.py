from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
#ошибки
from rest_framework.exceptions import ValidationError
#логер
from core.project_logging import get_logger
# модели
from apps.accounts.models import User
# сериализаторы
from apps.accounts.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer)
# сервисы
from apps.accounts.service import AccountService



class RegisterView(generics.CreateAPIView): # метод post уже внутри CreateAPIView
    """Регистрация нового пользователя"""
    queryset = User.objects.all() # инфа о всех юзерах из БД
    serializer_class = UserRegistrationSerializer # сериализатор на регистрацию
    permission_classes = [permissions.AllowAny] # любой может зарегаться

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = AccountService()  #  Внедряем сервис
        
    def create(self, request, *args, **kwargs):
        '''запрос на создание нового юзера'''
        serializer = self.get_serializer(data=request.data) # проверяем входные данные
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        new_user = self.user_service.create_user(validated_data)

        # при регитсрации лучше убрать рефреш токен ибо юзер может не подтвердить почту и слиться
        # refresh = RefreshToken.for_user(new_user) # даем refresh токен 
        
        # выдаем инфу юзеру при успешном создании
        return Response({
            'user': UserProfileSerializer(new_user).data,
            # 'refresh': str(refresh),
            # 'access': str(refresh.access_token),
            'message': 'User regirstered successfully'
        }, status=status.HTTP_201_CREATED)
    

class LoginView(generics.GenericAPIView): # метод post определить самому
    """Вход пользователя"""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny] # для любого
    
    def __init__(self, **kwargs):  # 👈 Создаем сервис
        super().__init__(**kwargs)
        self.auth_service = AccountService()  # 

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # login(request, user)# если в севрсие метод не будет рабоатьт
        authenticated_user = self.auth_service.login_user(user.id, request)
        
  
        refresh = RefreshToken.for_user(authenticated_user) # даем refresh токен 
        
        return Response({
            'user': UserProfileSerializer(authenticated_user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User login successfully'
        }, status=status.HTTP_200_OK)
    

class ProfileView(generics.RetrieveUpdateAPIView):
    """Просмотр и обновление профиля"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserProfileSerializer
    

class ChangePasswordView(generics.UpdateAPIView):
    """Смена пароля"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated] # пароль меняют только авторизированные юзеры


    def __init__(self, **kwargs):  # 👈 Создаем сервис
        super().__init__(**kwargs)
        self.auth_service = AccountService()  # 

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 3. Меняем пароль через сервис
        try:
            self.auth_service.change_password(
                user=request.user.id,
                old_password=serializer.validated_data['old_password'],
                new_password=serializer.validated_data['new_password']
            )
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
    
# логика разлогина
@api_view(['POST'])# тольок для post запросов
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Выход пользователя"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            # при разлогине старый рефреш токен выносим в блэклист
            token.blacklist() # тогда юзеру нужно будет заново логиниться
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception:# при поытке вернуть левый токен
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)