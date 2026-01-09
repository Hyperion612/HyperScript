from django.shortcuts import render
import calendar
from datetime import datetime

def calendar_view(request, year=None, month=None):
    """
    Показывает календарь.
    Если month указан — показывается только этот месяц.
    Если month не указан — показывается весь год.
    """
    today = datetime.today()
    year = int(year) if year else today.year
    month = int(month) if month else None

    cal = {}
    if month:  # Отдельный месяц
        month_cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        cal[month_name] = month_cal
    else:  # Весь год
        for m in range(1, 13):
            month_cal = calendar.monthcalendar(year, m)
            month_name = calendar.month_name[m]
            cal[month_name] = month_cal

    context = {
        'calendar': cal,
        'year': year,
        'month': month,
    }
    return render(request, 'calendar.html', context)
