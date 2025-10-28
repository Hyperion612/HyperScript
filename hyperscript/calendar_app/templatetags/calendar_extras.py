from django import template

register = template.Library()

@register.filter
def month_name(month_number):
    """Возвращает название месяца по номеру"""
    months = [
        '', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]
    return months[month_number] if 1 <= month_number <= 12 else ''