from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Новая главная страница
    path('tasks/', views.task_list, name='task_list'),  # Задачи теперь по другому пути
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/complete/<int:task_id>/', views.complete_task, name='complete_task'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('profile/', views.profile, name='profile'),
]