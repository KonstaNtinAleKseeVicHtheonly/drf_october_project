import os
from typing import List, Optional, Union
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache 

load_dotenv()



class ProjectSettings(BaseSettings):
    """
    Настройки проекта с загрузкой из .env файла
    """
    
    # ========== БАЗОВЫЕ НАСТРОЙКИ ==========
    APP_NAME: str = "FastAPI E STORE"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    APP_PORT : int = 8000
    
    # ========== БАЗА ДАННЫХ ==========
    DB_POSTGRES_HOST: str = "localhost"
    DB_POSTGRES_PORT: int = 5432
    DB_POSTGRES_NAME: str = "project_name"
    DB_POSTGRES_USER: str = "postgres"
    DB_POSTGRES_PASSWORD: str = "password"
    
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    @property
    def DATABASE_URL(self) -> str:
        """URL для подключения к PostgreSQL"""
        return f"postgresql+asyncpg://{self.DB_POSTGRES_USER}:{self.DB_POSTGRES_PASSWORD}@{self.DB_POSTGRES_HOST}:{self.DB_POSTGRES_PORT}/{self.DB_POSTGRES_NAME}"
    
    @property
    def TEST_DATABASE_URL(self) -> str:
        """URL для тестовой БД"""
        return "sqlite+aiosqlite:///:memory:"
    
    # ========== БЕЗОПАСНОСТЬ ==========
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ========== REDIS ==========
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        """URL для подключения к Redis"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    
    # ========== CORS ==========
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:5173", "http://localhost:8001","http://0.0.0.0:8000"]
    ALLOWED_METHODS: List[str] = ['*']
    ALLOWED_HEADERS: List[str] = ["*"]
    
    STATIC_DIR : str  = 'backend/static'
    IMAGES_DIR : str = 'backend/static/images'
    # ========== ЗАГРУЗКА ФАЙЛОВ ==========
    MAX_UPLOAD_SIZE: int = 10_485_760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".pdf"]
    UPLOAD_DIR: str = "uploads"
    
    # ========== ПАГИНАЦИЯ ==========
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"   # ← игнорировать лишние переменные
    
@lru_cache()# Декоратор кэширует результат первого вызова
def get_settings() -> ProjectSettings:
    return ProjectSettings() # вызов экз класса с данными конфигурации из env.

# Создаем глобальный объект настроек
project_settings = ProjectSettings()