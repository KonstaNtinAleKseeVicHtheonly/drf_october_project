from django.utils import timezone

from core.base_service import BaseService
from apps.accounts.repo import AccountRepo
from rest_framework.exceptions import ValidationError
from django.db.models import Count
from apps.accounts.models import User
from core.project_logging import get_logger


logger = get_logger(__name__)



class AccountService(BaseService):
    
    def __init__(self):
        # Инициализируем с конкретным репозиторием
        repository = AccountRepo()
        super().__init__(repository)
        
    def create_user(self, validated_data:dict):
        '''по проавалидированным данным из сериализатора
        через репозитория создает нового юзера в БД'''
        
        validated_data.pop('password_confirm', None)
        existed_user = self.repository.get_by_params(**validated_data).exists()
        if existed_user:
            raise ValidationError({"email": "User with this email already exists"})
        
        new_user = self.repository.create_new_user(validated_data)
        new_user.save()
        return new_user
    
    def check_active_user(self,user_id:int):
        current_user = self.get_current_user(user_id)
        if not current_user or not current_user.is_active:
            return False
        return current_user
    
    def login_user(self,user_id:int, request=None):
        # Проверки
        if not request:
            raise ValueError("Request object is required for login")
        current_user = self.check_active_user(user_id)
        if not current_user:
            raise ValidationError({"message" : 'Current user doesnt exist'})
        # 3. Обновление last_login
        current_user.last_login = timezone.now()
        current_user.save(update_fields=['last_login'])
        # 3. Логирование с IP (если есть request) - можно убрать по возможнсот
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        if ip:
            ip = ip.split(',')[0] if ',' in ip else ip
        logger.info(f"User {user_id} logged in from IP {ip}")
        
        # 4. Возвращаем пользователя для генерации токенов
        return current_user
        
        return current_user
        
    def _get_client_ip(self, request):
        '''системны мметод для логина юзера'''
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def get_current_user(self, user_id:int)->User|None:
        '''проверяет сущестует ли юзер по указанному id'''
        return self.repository.get_by_id(user_id)
    
    def get_user_posts(self,user_id:int):
        
        current_user = self.get_current_user(user_id)
        if not current_user:
            raise ValidationError({"message" : 'Current user doesnt exist'})
            
        user_posts = self.repository.count_user_posts(user_id)
        return user_posts
    
    def count_user_comments(self, user_id:int):
        current_user = self.get_current_user(user_id)
        if not current_user:
            raise ValidationError({"message" : 'Current user doesnt exist'})
        
        user_comments = self.repository.count_user_comments(user_id)
        return user_comments

    def update_current_user(self, user_id, updated_data:dict):
        '''по указанному id обновляет данные юзера'''
        current_user = self.get_current_user(user_id)
        if not current_user:
            raise ValidationError({"message" : 'Current user doesnt exist'})
        try:
            updated_user = self.repository.update(user_id,**updated_data)
            return updated_user
        except Exception as err:
            raise ValidationError({'message' : f"ошибка при обновлении : {err}"})
        
    def validated_new_password(self, old_password, new_password):
        ''''''
        if old_password == new_password:
            raise ValidationError({"message" : 'Old password is incorrect.'})
        
    # def validate_new_password(self, password_confirm, new_password_confirm)->bool:
    #     '''при первичном и повторном вводе пароля проверяет что бы они совпадали'''
    #     if password_confirm != new_password_confirm:
    #         raise ValidationError({'message' : "пароь введенный первый и второй раз не совпадают, повторите еще раз"})
    #     return True
    
    
    def change_password(self, user_id: int, old_password: str, new_password: str):
        """Смена пароля"""
    
        current_user = self.check_active_user(user_id)
        if not current_user:
            raise ValidationError({"message": "Current user doesnt exist"})
        
        # 2. Проверка старого пароля (открытый пароль от пользователя)
        if not current_user.check_password(old_password):  # 👈 old_password от пользователя
            raise ValidationError({"old_password": "Wrong password"})
        
        # 3. Проверка что новый пароль не совпадает со старым
        if old_password == new_password:
            raise ValidationError({"new_password": "New password must be different"})
        
        # 4. Установка нового пароля
        current_user.set_password(new_password)
        current_user.save()
        return True