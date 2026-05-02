from django.urls import path
from  apps.accounts.views import RegisterView, LoginView, ProfileView, ChangePasswordSerializer, logout_view
from rest_framework_simplejwt.views import TokenRefreshView



app_name = 'all_accounts'


urlpatterns = [
    
    path('/register', RegisterView.as_view(), name='register'),
    path('/login', LoginView.as_view(), name='login'),
    path('/logout', logout_view.as_view(), name='logout'),
    path('/profile', ProfileView.as_view(), name='profile'),
    path('/change-password', ChangePasswordSerializer.as_view(), name='change_password'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh')
    
]
