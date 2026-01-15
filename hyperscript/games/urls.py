from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    # Главная страница игр
    path('', views.games_index, name='games_index'),
    
    # Камень-Ножницы-Бумага
    path('rock-paper-scissors/', views.rock_paper_scissors, name='rock_paper_scissors'),
    
    # Виселица
    path('hangman/', views.hangman, name='hangman'),
    path('hangman/guess/', views.hangman_guess, name='hangman_guess'),
    path('hangman/new/', views.hangman_new, name='hangman_new'),
    
    # 2048
    path('2048/', views.game_2048, name='game_2048'),
    path('2048/move/', views.game_2048_move, name='game_2048_move'),
    path('2048/new/', views.game_2048_new, name='game_2048_new'),
    
    # Старые маршруты для совместимости (если были)
    path('play-rps/', views.rock_paper_scissors, name='play_rps'),
]