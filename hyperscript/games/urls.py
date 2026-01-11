from django.urls import path
from . import views

urlpatterns = [
    path('', views.games_index, name='games_index'),
    path('rock-paper-scissors/', views.rock_paper_scissors, name='rock_paper_scissors'),
    path('play-rps/', views.play_rps, name='play_rps'),
    path('hangman/', views.hangman, name='hangman'),
    path('2048/', views.game_2048, name='game_2048'),
]