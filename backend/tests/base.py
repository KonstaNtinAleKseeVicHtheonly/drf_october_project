# модели для проекта
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

class User(AbstractUser):
    """
    Пользователь. Связи указываются через related_name в других моделях.
    """
    bio = models.TextField('Биография', blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.username
    
    # Методы для работы с участием в событиях
    def get_events_as_organizer(self):
        return self.events.filter(eventparticipant__is_organizer=True)
    
    def get_events_as_participant(self):
        return self.events.filter(eventparticipant__is_organizer=False)
    
    def is_organizer_of(self, event):
        return self.events.filter(pk=event.pk, eventparticipant__is_organizer=True).exists()


class Category(models.Model):
    """
    Категория событий (один ко многим с Event)
    """
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL', unique=True, blank=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    """
    Событие. Связано с User через EventParticipant (many-to-many)
    """
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', unique=True, blank=True)
    description = models.TextField('Описание', blank=True)
    date = models.DateTimeField('Дата проведения')
    location = models.CharField('Место', max_length=255)
    
    # Связь с Category (one-to-many)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',  # ← category.events
        verbose_name='Категория'
    )
    
    # Связь с User через EventParticipant (many-to-many)
    participants = models.ManyToManyField(
        User,
        through='EventParticipant',
        through_fields=('event', 'user'),
        related_name='events',  # ← user.events
        verbose_name='Участники'
    )
    
    class Meta:
        db_table = 'events'
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        ordering = ['-date']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    # Методы для работы с участниками
    def get_organizers(self):
        return User.objects.filter(
            eventparticipant__event=self,
            eventparticipant__is_organizer=True
        )
    
    def get_participants(self):
        return User.objects.filter(
            eventparticipant__event=self,
            eventparticipant__is_organizer=False
        )
    
    def add_participant(self, user, is_organizer=False):
        return EventParticipant.objects.get_or_create(
            event=self,
            user=user,
            defaults={'is_organizer': is_organizer}
        )
    
    # Методы для работы с комментариями
    def get_comments(self):
        return self.comments.select_related('user').all()
    
    def has_user_commented(self, user):
        return self.comments.filter(user=user).exists()


class EventParticipant(models.Model):
    """
    Промежуточная модель для many-to-many связи User и Event.
    Содержит флаг is_organizer.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='participant_relations',
        verbose_name='Пользователь'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participant_relations',
        verbose_name='Событие'
    )
    is_organizer = models.BooleanField('Организатор', default=False)
    joined_at = models.DateTimeField('Дата присоединения', auto_now_add=True)
    
    class Meta:
        db_table = 'event_participants'
        verbose_name = 'Участник события'
        verbose_name_plural = 'Участники событий'
        unique_together = ('user', 'event')  # один пользователь = одна запись на событие
    
    def __str__(self):
        role = 'Организатор' if self.is_organizer else 'Участник'
        return f'{self.user.username} - {self.event.title} ({role})'


class Comment(models.Model):
    """
    Комментарий пользователя к событию.
    Один пользователь = один комментарий на событие.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',  # ← user.comments
        verbose_name='Автор'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='comments',  # ← event.comments
        verbose_name='Событие'
    )
    text = models.TextField('Текст комментария', max_length=2000)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)
    
    class Meta:
        db_table = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        unique_together = ('user', 'event')  # один комментарий на пару (user, event)
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} -> {self.event.title}: {self.text[:50]}'