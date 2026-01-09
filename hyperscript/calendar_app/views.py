from django.shortcuts import render
from django.utils import timezone
import calendar
import locale

# Русская локаль
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')


def year_calendar(request):
    current_year = timezone.now().year

    months = [
        timezone.datetime(current_year, m, 1).strftime('%B').capitalize()
        for m in range(1, 13)
    ]

    return render(request, 'calendar_app/year_calendar.html', {
        'current_year': current_year,
        'months': enumerate(months, start=1),
    })


def month_calendar(request, year, month):
    year = int(year)
    month = int(month)

    if month < 1 or month > 12:
        month = timezone.now().month

    calendar.setfirstweekday(calendar.MONDAY)
    cal = calendar.monthcalendar(year, month)

    today = timezone.now().date()
    month_name = timezone.datetime(year, month, 1).strftime('%B').capitalize()

    # предыдущий месяц
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    # следующий месяц
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    return render(request, 'calendar_app/month_calendar.html', {
        'calendar': cal,
        'year': year,
        'month': month,
        'month_name': month_name,
        'today': today,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    })


