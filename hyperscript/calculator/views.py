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
                    total_points += float(grade) * float(weight)
                    total_weight += float(weight)
            
            if total_weight > 0:
                average_grade = total_points / total_weight
                result = {
                    'success': True,
                    'average_grade': round(average_grade, 2),
                    'total_weight': total_weight
                }
            else:
                result = {'success': False, 'error': 'Введите оценки и веса'}
                
        except ValueError:
            result = {'success': False, 'error': 'Некорректные данные'}
        
        return JsonResponse(result)
    
    # GET запрос - показываем форму
    return render(request, 'calculator/calculator.html')