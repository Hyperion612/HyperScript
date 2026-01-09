from django.urls import path
from .views import calendar_view

urlpatterns = [
    path('calendar/', calendar_view, name='calendar_year'),          # весь год
    path('calendar/<int:year>/', calendar_view, name='calendar_year'),  # весь год конкретного года
    path('calendar/<int:year>/<int:month>/', calendar_view, name='calendar_month'),  # один месяц
]
