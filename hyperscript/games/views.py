from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import random
import json

@login_required
def games_index(request):
    return render(request, 'games/index.html')

@login_required
def rock_paper_scissors(request):
    return render(request, 'games/rock_paper_scissors.html')

@login_required
def play_rps(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_choice = data.get('choice')
        
        choices = ['rock', 'paper', 'scissors']
        computer_choice = random.choice(choices)
        
        # Определяем победителя
        if user_choice == computer_choice:
            result = 'draw'
            message = 'Ничья!'
        elif (user_choice == 'rock' and computer_choice == 'scissors') or \
             (user_choice == 'scissors' and computer_choice == 'paper') or \
             (user_choice == 'paper' and computer_choice == 'rock'):
            result = 'win'
            message = 'Вы победили! 🎉'
        else:
            result = 'lose'
            message = 'Компьютер победил! 💻'
        
        return JsonResponse({
            'user_choice': user_choice,
            'computer_choice': computer_choice,
            'result': result,
            'message': message
        })
    
    return JsonResponse({'error': 'Invalid request'})

# Аналогично можно добавить views для других игр