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
from django.contrib import admin
from django.contrib import admin
from django.urls import path, include
from calculator.views import grade_calculator, register
from django.contrib.auth import views as auth_views
from calculator.views import custom_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('todo.urls')),
    path('calendar/', include('calendar_app.urls')),
    path('calculator/', grade_calculator, name='grade_calculator'),
    path('accounts/register/', register, name='register'),
    
    # ✅ ЕДИНСТВЕННЫЙ путь для выхода:
    path('accounts/logout/', custom_logout, name='logout'),
    
    # Остальные auth URLs
    path('accounts/', include('django.contrib.auth.urls')),
]