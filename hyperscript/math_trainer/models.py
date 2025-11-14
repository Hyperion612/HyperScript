from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class MathScore(models.Model):
    """
    Модель для хранения результатов математического тренажера
    """
    
    # Типы математических операций
    OPERATION_CHOICES = [
        ('addition', 'Сложение'),
        ('subtraction', 'Вычитание'),
        ('multiplication', 'Умножение'),
        ('division', 'Деление'),
        ('mixed', 'Смешанные операции'),
    ]
    
    # Уровни сложности
    DIFFICULTY_CHOICES = [
        ('easy', 'Легкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
        ('expert', 'Эксперт'),
    ]
    
    # Связь с пользователем
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='math_scores',
        verbose_name="Пользователь"
    )
    
    # Тип математической операции
    operation = models.CharField(
        max_length=20,
        choices=OPERATION_CHOICES,
        verbose_name="Операция"
    )
    
    # Уровень сложности
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        verbose_name="Сложность"
    )
    
    # Количество очков
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Счет"
    )
    
    # Общее количество вопросов
    total_questions = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Всего вопросов"
    )
    
    # Количество правильных ответов
    correct_answers = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Правильные ответы"
    )
    
    # Затраченное время в секундах
    time_spent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Затраченное время (сек)"
    )
    
    # Среднее время на вопрос
    average_time_per_question = models.FloatField(
        default=0.0,
        verbose_name="Среднее время на вопрос"
    )
    
    # Максимальная серия правильных ответов
    max_streak = models.IntegerField(
        default=0,
        verbose_name="Максимальная серия"
    )
    
    # Дополнительные метрики
    metrics = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Дополнительные метрики"
    )
    
    # Дата и время создания записи
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания"
    )
    
    class Meta:
        verbose_name = "Результат математического тренажера"
        verbose_name_plural = "Результаты математического тренажера"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'operation']),
            models.Index(fields=['user', 'difficulty']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(correct_answers__lte=models.F('total_questions')),
                name='correct_answers_lte_total_questions'
            )
        ]
    
    def __str__(self):
        """Строковое представление объекта"""
        return f"{self.user.username} - {self.get_operation_display()} - {self.accuracy:.1f}%"
    
    def save(self, *args, **kwargs):
        """Переопределение save для вычисления производных полей"""
        # Вычисляем точность
        if self.total_questions > 0:
            self.accuracy = (self.correct_answers / self.total_questions) * 100
        else:
            self.accuracy = 0
        
        # Вычисляем среднее время на вопрос
        if self.total_questions > 0:
            self.average_time_per_question = self.time_spent / self.total_questions
        else:
            self.average_time_per_question = 0
        
        super().save(*args, **kwargs)
    
    @property
    def accuracy(self):
        """Точность ответов в процентах (вычисляемое свойство)"""
        if self.total_questions > 0:
            return (self.correct_answers / self.total_questions) * 100
        return 0
    
    @accuracy.setter
    def accuracy(self, value):
        """Setter для accuracy (нужен для save)"""
        pass  # Вычисляемое свойство, не хранится в БД
    
    @property
    def formatted_time(self):
        """Форматированное время (мм:сс)"""
        minutes = self.time_spent // 60
        seconds = self.time_spent % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def performance_rating(self):
        """Рейтинг производительности (0-100)"""
        accuracy_weight = 0.6
        speed_weight = 0.4
        
        # Базовый рейтинг точности
        accuracy_rating = self.accuracy
        
        # Рейтинг скорости (чем быстрее, тем лучше)
        base_time_per_question = {
            'easy': 10,
            'medium': 15,
            'hard': 20,
            'expert': 25
        }
        
        expected_time = base_time_per_question.get(self.difficulty, 15)
        if self.average_time_per_question > 0:
            speed_rating = max(0, 100 - (self.average_time_per_question / expected_time) * 100)
        else:
            speed_rating = 0
        
        return (accuracy_rating * accuracy_weight) + (speed_rating * speed_weight)
    
    @classmethod
    def get_user_stats(cls, user, operation=None, difficulty=None):
        """Получение статистики пользователя"""
        queryset = cls.objects.filter(user=user)
        
        if operation:
            queryset = queryset.filter(operation=operation)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        total_sessions = queryset.count()
        total_questions = queryset.aggregate(models.Sum('total_questions'))['total_questions__sum'] or 0
        total_correct = queryset.aggregate(models.Sum('correct_answers'))['correct_answers__sum'] or 0
        total_time = queryset.aggregate(models.Sum('time_spent'))['time_spent__sum'] or 0
        best_score = queryset.aggregate(models.Max('score'))['score__max'] or 0
        best_accuracy = queryset.aggregate(models.Max('correct_answers'))['correct_answers__max'] or 0
        
        if total_questions > 0:
            overall_accuracy = (total_correct / total_questions) * 100
            avg_time_per_question = total_time / total_questions
        else:
            overall_accuracy = 0
            avg_time_per_question = 0
        
        return {
            'total_sessions': total_sessions,
            'total_questions': total_questions,
            'total_correct': total_correct,
            'total_time': total_time,
            'best_score': best_score,
            'best_accuracy': best_accuracy,
            'overall_accuracy': overall_accuracy,
            'avg_time_per_question': avg_time_per_question,
        }


class MathSession(models.Model):
    """
    Модель для активных сессий математического тренажера
    """
    
    # Типы сессий
    SESSION_TYPES = [
        ('practice', 'Тренировка'),
        ('timed', 'На время'),
        ('endless', 'Бесконечный режим'),
        ('challenge', 'Испытание'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='math_sessions',
        verbose_name="Пользователь"
    )
    
    # Тип сессии
    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPES,
        default='practice',
        verbose_name="Тип сессии"
    )
    
    # Операция (может быть mixed для смешанных)
    operation = models.CharField(
        max_length=20,
        choices=MathScore.OPERATION_CHOICES,
        verbose_name="Операция"
    )
    
    # Сложность
    difficulty = models.CharField(
        max_length=10,
        choices=MathScore.DIFFICULTY_CHOICES,
        verbose_name="Сложность"
    )
    
    # Текущий счет
    current_score = models.IntegerField(
        default=0,
        verbose_name="Текущий счет"
    )
    
    # Текущий вопрос
    current_question = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Текущий вопрос"
    )
    
    # Правильный ответ на текущий вопрос
    current_answer = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Правильный ответ"
    )
    
    # Количество правильных ответов подряд
    current_streak = models.IntegerField(
        default=0,
        verbose_name="Текущая серия"
    )
    
    # Максимальная серия в этой сессии
    session_max_streak = models.IntegerField(
        default=0,
        verbose_name="Максимальная серия в сессии"
    )
    
    # Время начала сессии
    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время начала"
    )
    
    # Время окончания сессии
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Время окончания"
    )
    
    # Статус сессии
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активная сессия"
    )
    
    # Дополнительные данные сессии
    session_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Данные сессии"
    )
    
    class Meta:
        verbose_name = "Сессия математического тренажера"
        verbose_name_plural = "Сессии математического тренажера"
        ordering = ['-start_time']
    
    def __str__(self):
        status = "Активная" if self.is_active else "Завершенная"
        return f"Сессия: {self.user.username} - {self.get_operation_display()} ({status})"
    
    @property
    def duration(self):
        """Длительность сессии в секундах"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (timezone.now() - self.start_time).total_seconds()
        return 0
    
    @property
    def formatted_duration(self):
        """Форматированная длительность"""
        duration = self.duration
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def complete_session(self, final_score=0):
        """Завершение сессии"""
        self.is_active = False
        self.end_time = timezone.now()
        self.current_score = final_score
        self.save()


class MathChallenge(models.Model):
    """
    Модель для математических испытаний/челленджей
    """
    
    # Типы испытаний
    CHALLENGE_TYPES = [
        ('speed', 'Скоростной'),
        ('accuracy', 'На точность'),
        ('endurance', 'На выносливость'),
        ('combo', 'Комбинированный'),
    ]
    
    # Статусы испытаний
    STATUS_CHOICES = [
        ('active', 'Активное'),
        ('completed', 'Завершено'),
        ('failed', 'Провалено'),
        ('expired', 'Истекло'),
    ]
    
    title = models.CharField(
        max_length=100,
        verbose_name="Название испытания"
    )
    
    description = models.TextField(
        verbose_name="Описание"
    )
    
    challenge_type = models.CharField(
        max_length=20,
        choices=CHALLENGE_TYPES,
        verbose_name="Тип испытания"
    )
    
    operation = models.CharField(
        max_length=20,
        choices=MathScore.OPERATION_CHOICES,
        verbose_name="Операция"
    )
    
    difficulty = models.CharField(
        max_length=10,
        choices=MathScore.DIFFICULTY_CHOICES,
        verbose_name="Сложность"
    )
    
    # Целевые показатели
    target_score = models.IntegerField(
        default=0,
        verbose_name="Целевой счет"
    )
    
    target_accuracy = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Целевая точность (%)"
    )
    
    time_limit = models.IntegerField(
        default=0,
        verbose_name="Лимит времени (сек)"
    )
    
    # Награда за выполнение
    reward_points = models.IntegerField(
        default=0,
        verbose_name="Очки награды"
    )
    
    # Испытание активно
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активное испытание"
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания"
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Действует до"
    )
    
    class Meta:
        verbose_name = "Математическое испытание"
        verbose_name_plural = "Математические испытания"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_challenge_type_display()})"
    
    @property
    def is_expired(self):
        """Проверка истекло ли испытание"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def time_remaining(self):
        """Оставшееся время"""
        if self.expires_at:
            remaining = self.expires_at - timezone.now()
            return max(0, remaining.total_seconds())
        return None


class UserMathProfile(models.Model):
    """
    Профиль пользователя для математического тренажера
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='math_profile',
        verbose_name="Пользователь"
    )
    
    # Общий опыт
    total_experience = models.IntegerField(
        default=0,
        verbose_name="Общий опыт"
    )
    
    # Уровень пользователя
    level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Уровень"
    )
    
    # Текущие очки
    current_points = models.IntegerField(
        default=0,
        verbose_name="Текущие очки"
    )
    
    # Достижения
    achievements = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Достижения"
    )
    
    # Настройки пользователя
    preferences = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Настройки"
    )
    
    # Статистика по операциям
    operation_stats = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Статистика по операциям"
    )
    
    # Дата последней активности
    last_active = models.DateTimeField(
        auto_now=True,
        verbose_name="Последняя активность"
    )
    
    class Meta:
        verbose_name = "Профиль математического тренажера"
        verbose_name_plural = "Профили математического тренажера"
    
    def __str__(self):
        return f"Профиль: {self.user.username} (Уровень {self.level})"
    
    @property
    def experience_to_next_level(self):
        """Опыт до следующего уровня"""
        base_exp = 100
        return base_exp * (self.level ** 2)
    
    @property
    def level_progress(self):
        """Прогресс до следующего уровня в процентах"""
        if self.experience_to_next_level > 0:
            return (self.total_experience / self.experience_to_next_level) * 100
        return 0
    
    def add_experience(self, amount):
        """Добавление опыта и проверка уровня"""
        self.total_experience += amount
        
        # Проверяем повышение уровня
        while self.total_experience >= self.experience_to_next_level:
            self.total_experience -= self.experience_to_next_level
            self.level += 1
        
        self.save()