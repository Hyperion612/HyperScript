from django.shortcuts import render
import calendar
from datetime import datetime
from django.utils import timezone

def year_calendar(request):
    """
    Показывает страницу с выбором года и месяцев
    (для шаблона year_calendar.html)
    """
    today = datetime.today()
    current_year = today.year
    
    # Создаем диапазон лет (текущий год ±2)
    years = range(current_year - 2, current_year + 3)
    
    context = {
        'years': years,
        'current_year': current_year,
    }
    return render(request, 'year_calendar.html', context)

def month_calendar(request, year, month):
    """
    Показывает календарь конкретного месяца
    (для шаблона month_calendar.html)
    """
    year = int(year)
    month = int(month)
    today = datetime.today()
    
    # Получаем календарь на месяц (список недель)
    month_cal = calendar.monthcalendar(year, month)
    
    # Русские названия месяцев (как в вашем шаблоне)
    month_names_ru = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]
    
    # Навигация по месяцам
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
        
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1
    
    context = {
        'year': year,
        'month': month,
        'month_name': month_names_ru[month - 1],
        'calendar': month_cal,  # Это для цикла {% for week in calendar %}
        'today': today.date(),
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    }
    return render(request, 'month_calendar.html', context)