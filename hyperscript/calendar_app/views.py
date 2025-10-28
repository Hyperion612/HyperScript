from django.shortcuts import render
from django.utils import timezone
import calendar
from datetime import datetime

def year_calendar(request):
    current_year = timezone.now().year
    return render(request, 'calendar_app/year_calendar.html', {
        'current_year': current_year,
        'years': range(current_year - 1, current_year + 3)  # -1 прошлый, +2 будущих
    })

def month_calendar(request, year, month):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Получаем текущую дату для выделения
    today = timezone.now().date()
    is_current_month = (today.year == year and today.month == month)
    
    return render(request, 'calendar_app/month_calendar.html', {
        'calendar': cal,
        'year': year,
        'month': month,
        'month_name': month_name,
        'today': today,
        'is_current_month': is_current_month,
    })

