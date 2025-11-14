from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class GameSession(models.Model):
    """
    Модель для хранения игровых сессий пользователей
    """
    
    # Типы игр
    GAME_CHOICES = [
        ('rps', 'Камень-Ножницы-Бумага'),
        ('hangman', 'Виселица'),
        ('quiz', 'Викторина'),
        ('memory', 'Игра на память'),
    ]
    
    # Результаты игры
    RESULT_CHOICES = [
        ('win', 'Победа'),
        ('lose', 'Поражение'),
        ('draw', 'Ничья'),
    ]
    
    # Связь с пользователем
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    
    # Тип игры
    game_type = models.CharField(
        max_length=20,
        choices=GAME_CHOICES,
        verbose_name="Тип игры"
    )
    
    # Счет игрока
    score = models.IntegerField(
        default=0,
        verbose_name="Счет"
    )
    
    # Результат игры
    result = models.CharField(
        max_length=10,
        choices=RESULT_CHOICES,
        verbose_name="Результат"
    )
    
    # Дополнительные данные игры (JSON поле для гибкости)
    game_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Данные игры"
    )
    
    # Длительность игры в секундах
    duration = models.IntegerField(
        default=0,
        verbose_name="Длительность (сек)"
    )
    
    # Дата и время создания записи
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания"
    )
    
    class Meta:
        verbose_name = "Игровая сессия"
        verbose_name_plural = "Игровые сессии"
        ordering = ['-created_at']  # Сортировка по убыванию даты
        indexes = [
            models.Index(fields=['user', 'game_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        """Строковое представление объекта"""
        return f"{self.user.username} - {self.get_game_type_display()} - {self.get_result_display()} ({self.score})"
    
    @property
    def formatted_duration(self):
        """Форматированное время игры (мм:сс)"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    @classmethod
    def get_user_stats(cls, user, game_type=None):
        """Получение статистики пользователя"""
        queryset = cls.objects.filter(user=user)
        
        if game_type:
            queryset = queryset.filter(game_type=game_type)
        
        total_games = queryset.count()
        wins = queryset.filter(result='win').count()
        losses = queryset.filter(result='lose').count()
        draws = queryset.filter(result='draw').count()
        total_score = queryset.aggregate(models.Sum('score'))['score__sum'] or 0
        
        return {
            'total_games': total_games,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': (wins / total_games * 100) if total_games > 0 else 0,
            'total_score': total_score,
            'average_score': total_score / total_games if total_games > 0 else 0,
        }


class HangmanGame(models.Model):
    """
    Модель для игры 'Виселица'
    """
    
    # Статусы игры
    STATUS_CHOICES = [
        ('active', 'Активная'),
        ('won', 'Выиграна'),
        ('lost', 'Проиграна'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    
    # Загаданное слово
    word = models.CharField(
        max_length=50,
        verbose_name="Загаданное слово"
    )
    
    # Текущий прогресс (например: _ _ _ _ _)
    current_state = models.CharField(
        max_length=100,
        verbose_name="Текущее состояние"
    )
    
    # Использованные буквы
    used_letters = models.CharField(
        max_length=100,
        default="",
        blank=True,
        verbose_name="Использованные буквы"
    )
    
    # Количество ошибок
    mistakes = models.IntegerField(
        default=0,
        verbose_name="Количество ошибок"
    )
    
    # Максимальное количество ошибок
    max_mistakes = models.IntegerField(
        default=6,
        verbose_name="Максимальное количество ошибок"
    )
    
    # Статус игры
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Статус игры"
    )
    
    # Дата создания
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания"
    )
    
    # Дата завершения
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата завершения"
    )
    
    class Meta:
        verbose_name = "Игра в виселицу"
        verbose_name_plural = "Игры в виселицу"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Виселица: {self.user.username} - {self.word} ({self.status})"
    
    @property
    def is_completed(self):
        """Проверка завершена ли игра"""
        return self.status in ['won', 'lost']
    
    @property
    def remaining_attempts(self):
        """Оставшиеся попытки"""
        return self.max_mistakes - self.mistakes


class QuizQuestion(models.Model):
    """
    Модель для вопросов викторины
    """
    
    CATEGORY_CHOICES = [
        ('general', 'Общие знания'),
        ('science', 'Наука'),
        ('history', 'История'),
        ('geography', 'География'),
        ('entertainment', 'Развлечения'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Легкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ]
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="Категория"
    )
    
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        verbose_name="Сложность"
    )
    
    question = models.TextField(
        verbose_name="Вопрос"
    )
    
    # Варианты ответов (храним как JSON)
    options = models.JSONField(
        verbose_name="Варианты ответов"
    )
    
    # Правильный ответ (индекс в options)
    correct_answer = models.IntegerField(
        verbose_name="Индекс правильного ответа"
    )
    
    # Объяснение ответа
    explanation = models.TextField(
        blank=True,
        verbose_name="Объяснение"
    )
    
    # Активен ли вопрос
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активный"
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания"
    )
    
    class Meta:
        verbose_name = "Вопрос викторины"
        verbose_name_plural = "Вопросы викторины"
        ordering = ['category', 'difficulty']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.question[:50]}..."


class QuizSession(models.Model):
    """
    Модель для сессии викторины
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    
    # Категория викторины
    category = models.CharField(
        max_length=20,
        choices=QuizQuestion.CATEGORY_CHOICES,
        verbose_name="Категория"
    )
    
    # Сложность
    difficulty = models.CharField(
        max_length=10,
        choices=QuizQuestion.DIFFICULTY_CHOICES,
        verbose_name="Сложность"
    )
    
    # Текущий счет
    score = models.IntegerField(
        default=0,
        verbose_name="Счет"
    )
    
    # Количество вопросов
    total_questions = models.IntegerField(
        default=0,
        verbose_name="Всего вопросов"
    )
    
    # Правильные ответы
    correct_answers = models.IntegerField(
        default=0,
        verbose_name="Правильные ответы"
    )
    
    # Текущий вопрос
    current_question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Текущий вопрос"
    )
    
    # Прогресс (вопросы которые уже были)
    completed_questions = models.JSONField(
        default=list,
        verbose_name="Завершенные вопросы"
    )
    
    # Статус сессии
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активная сессия"
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата завершения"
    )
    
    class Meta:
        verbose_name = "Сессия викторины"
        verbose_name_plural = "Сессии викторины"
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Активная" if self.is_active else "Завершенная"
        return f"Викторина: {self.user.username} - {self.score} очков ({status})"
    
    @property
    def accuracy(self):
        """Точность ответов в процентах"""
        if self.total_questions > 0:
            return (self.correct_answers / self.total_questions) * 100
        return 0
    
    @property
    def progress(self):
        """Прогресс в процентах"""
        if self.total_questions > 0:
            return (len(self.completed_questions) / self.total_questions) * 100
        return 0