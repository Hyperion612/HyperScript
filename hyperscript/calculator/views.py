from django.shortcuts import render
from django.http import JsonResponse

def grade_calculator(request):
    if request.method == 'POST':
        # Обработка данных из формы
        grades = request.POST.getlist('grades[]')
        weights = request.POST.getlist('weights[]')
        
        try:
            total_points = 0
            total_weight = 0
            
            for grade, weight in zip(grades, weights):
                if grade and weight:
                    grade_val = float(grade)
                    weight_val = float(weight)
                    
                    # Проверяем что оценка от 2 до 5
                    if 2 <= grade_val <= 5:
                        total_points += grade_val * weight_val
                        total_weight += weight_val
                    else:
                        return JsonResponse({
                            'success': False, 
                            'error': f'Оценка {grade_val} должна быть от 2 до 5'
                        })
            
            if total_weight > 0:
                average_grade = total_points / total_weight
                result = {
                    'success': True,
                    'average_grade': round(average_grade, 2),
                    'total_weight': total_weight,
                    'qualitative_grade': get_qualitative_grade(average_grade)
                }
            else:
                result = {'success': False, 'error': 'Введите оценки и веса'}
                
        except ValueError:
            result = {'success': False, 'error': 'Некорректные данные'}
        
        return JsonResponse(result)
    
    # GET запрос - показываем форму
    return render(request, 'calculator/calculator.html')

def get_qualitative_grade(grade):
    """Возвращает качественную оценку"""
    if grade >= 4.5:
        return "Отлично"
    elif grade >= 3.5:
        return "Хорошо"
    elif grade >= 2.5:
        return "Удовлетворительно"
    else:
        return "Неудовлетворительно"

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Аккаунт создан для {username}!')
            return redirect('task_list')
        else:
            # Покажем ошибки формы
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})