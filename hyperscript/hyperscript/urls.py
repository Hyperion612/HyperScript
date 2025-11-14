"""
URL configuration for hyperscript project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from calculator.views import grade_calculator, register, custom_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Главная страница
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Существующие приложения
    path('tasks/', include('todo.urls')),
    path('calendar/', include('calendar_app.urls')),
    path('calculator/', grade_calculator, name='grade_calculator'),
    path('music/', include('music_player.urls')),
    
    # НОВЫЕ ПРИЛОЖЕНИЯ
    path('math/', include('math_trainer.urls')),
    path('games/', include('games.urls')),
    
    # Аутентификация
    path('accounts/register/', register, name='register'),
    path('accounts/logout/', custom_logout, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Дополнительные страницы
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    path('settings/', TemplateView.as_view(template_name='settings.html'), name='settings'),
]

# Serving media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)