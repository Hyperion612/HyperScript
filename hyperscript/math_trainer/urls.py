from django.urls import path
from . import views

urlpatterns = [
    path('', views.math_trainer, name='math_trainer'),
    path('operation/<str:operation>/', views.math_operation, name='math_operation'),
    path('save-score/', views.save_math_score, name='save_math_score'),
    #path('stats/', views.math_stats, name='math_stats'),
]