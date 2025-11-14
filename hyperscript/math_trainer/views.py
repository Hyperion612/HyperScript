from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import random
import json
from .models import MathScore

@login_required
def math_trainer(request):
    return render(request, 'math_trainer/trainer.html')

@login_required
def math_operation(request, operation):
    difficulties = {
        'easy': (1, 10),
        'medium': (10, 50),
        'hard': (50, 100)
    }
    
    difficulty = request.GET.get('difficulty', 'easy')
    min_val, max_val = difficulties.get(difficulty, (1, 10))
    
    if operation == 'addition':
        a = random.randint(min_val, max_val)
        b = random.randint(min_val, max_val)
        question = f"{a} + {b}"
        answer = a + b
    elif operation == 'subtraction':
        a = random.randint(min_val, max_val)
        b = random.randint(min_val, a)
        question = f"{a} - {b}"
        answer = a - b
    elif operation == 'multiplication':
        a = random.randint(1, min(10, max_val))
        b = random.randint(1, min(10, max_val))
        question = f"{a} × {b}"
        answer = a * b
    elif operation == 'division':
        b = random.randint(1, 10)
        a = b * random.randint(1, 10)
        question = f"{a} ÷ {b}"
        answer = a // b
    else:
        return JsonResponse({'error': 'Invalid operation'})
    
    return JsonResponse({
        'question': question,
        'answer': answer,
        'difficulty': difficulty
    })

@login_required
def save_math_score(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        operation = data.get('operation')
        difficulty = data.get('difficulty')
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)
        correct_answers = data.get('correct_answers', 0)
        time_spent = data.get('time_spent', 0)
        
        math_score = MathScore.objects.create(
            user=request.user,
            operation=operation,
            difficulty=difficulty,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers,
            time_spent=time_spent
        )
        
        return JsonResponse({'status': 'success', 'score_id': math_score.id})
    
    return JsonResponse({'status': 'error'})

@login_required
def math_stats(request):
    """Статистика пользователя"""
    scores = MathScore.objects.filter(user=request.user).order_by('-created_at')[:10]
    stats = []
    
    for score in scores:
        stats.append({
            'operation': score.operation,
            'difficulty': score.difficulty,
            'score': score.score,
            'accuracy': f"{score.accuracy:.1f}%",
            'date': score.created_at.strftime('%d.%m.%Y %H:%M')
        })
    
    return JsonResponse({'stats': stats})