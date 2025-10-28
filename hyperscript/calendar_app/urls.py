from django.urls import path
from . import views

urlpatterns = [
    path('', views.year_calendar, name='year_calendar'),
    path('month/<int:year>/<int:month>/', views.month_calendar, name='month_calendar'),
]