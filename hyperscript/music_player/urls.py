from django.urls import path
from . import views

urlpatterns = [
    path('', views.music_player, name='music_player'),
    path('delete/<int:track_id>/', views.delete_track, name='delete_track'),
]