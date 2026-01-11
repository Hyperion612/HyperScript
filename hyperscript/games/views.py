from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import random
import json
# Добавьте в начало views.py
from django.db.models import Count, Sum
from django.contrib.auth.models import User

@login_required
def games_index(request):
    """Главная страница игр со статистикой"""
    # Получаем статистику для авторизованного пользователя
    user_stats = {}
    
    if request.user.is_authenticated:
        # Здесь можно добавить реальную статистику из базы данных
        # Пока используем сессионные данные
        user_stats = {
            'rps_wins': request.session.get('rps_wins', 0),
            'hangman_wins': request.session.get('hangman_wins', 0),
            'game_2048_high_score': request.session.get('2048_high_score', 0),
            'total_games': request.session.get('total_games_played', 0),
        }
    
    context = {
        'user_games_stats': user_stats if request.user.is_authenticated else None,
    }
    return render(request, 'games/index.html', context)

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
@login_required
def hangman(request):
    """Игра Виселица"""
    # Слова для игры (можно расширить)
    words = [
        'ПРОГРАММИРОВАНИЕ', 'КОМПЬЮТЕР', 'АЛГОРИТМ', 
        'БАЗАДАННЫХ', 'ИНТЕРНЕТ', 'ПРИЛОЖЕНИЕ',
        'ФРЕЙМВОРК', 'ШАБЛОН', 'ПЕРЕМЕННАЯ'
    ]
    
    # Инициализация или получение состояния игры из сессии
    if 'hangman' not in request.session:
        request.session['hangman'] = {
            'word': random.choice(words),
            'guessed': [],
            'wrong_guesses': 0,
            'game_over': False,
            'won': False
        }
    
    game_state = request.session['hangman']
    
    # Обработка угадывания буквы
    if request.method == 'POST' and not game_state['game_over']:
        letter = request.POST.get('letter', '').upper()
        
        if letter and len(letter) == 1 and letter.isalpha():
            if letter not in game_state['guessed']:
                game_state['guessed'].append(letter)
                
                if letter not in game_state['word']:
                    game_state['wrong_guesses'] += 1
                
                # Проверка победы
                if all(l in game_state['guessed'] for l in game_state['word']):
                    game_state['game_over'] = True
                    game_state['won'] = True
                
                # Проверка поражения (максимум 7 ошибок)
                if game_state['wrong_guesses'] >= 7:
                    game_state['game_over'] = True
                    game_state['won'] = False
                
                request.session['hangman'] = game_state
    
    # Новая игра
    if request.method == 'POST' and request.POST.get('new_game'):
        request.session['hangman'] = {
            'word': random.choice(words),
            'guessed': [],
            'wrong_guesses': 0,
            'game_over': False,
            'won': False
        }
        game_state = request.session['hangman']
    
    # Подготовка данных для отображения
    display_word = ''
    for letter in game_state['word']:
        if letter in game_state['guessed']:
            display_word += letter + ' '
        else:
            display_word += '_ '
    
    # Буквы для выбора
    alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    
    context = {
        'display_word': display_word.strip(),
        'guessed_letters': ', '.join(game_state['guessed']),
        'wrong_guesses': game_state['wrong_guesses'],
        'max_wrong': 7,
        'game_over': game_state['game_over'],
        'won': game_state['won'],
        'alphabet': alphabet,
        'word_length': len(game_state['word']),
        'remaining_letters': [l for l in alphabet if l not in game_state['guessed']],
    }
    
    return render(request, 'games/hangman.html', context)

@login_required
def game_2048(request):
    """Игра 2048"""
    # Инициализация игрового поля
    if 'game_2048' not in request.session:
        request.session['game_2048'] = {
            'grid': [[0, 0, 0, 0] for _ in range(4)],
            'score': 0,
            'game_over': False,
            'won': False,
            'moves': 0
        }
        # Добавляем 2 начальные клетки
        add_new_tile(request.session['game_2048'])
        add_new_tile(request.session['game_2048'])
    
    game_state = request.session['game_2048']
    
    # Обработка хода
    if request.method == 'POST' and not game_state['game_over']:
        direction = request.POST.get('direction')
        
        if direction in ['up', 'down', 'left', 'right']:
            old_grid = [row[:] for row in game_state['grid']]
            
            if move_tiles(game_state, direction):
                game_state['moves'] += 1
                add_new_tile(game_state)
                
                # Проверка победы (достигли 2048)
                if not game_state['won']:
                    for row in game_state['grid']:
                        if 2048 in row:
                            game_state['won'] = True
                            break
                
                # Проверка поражения (нет возможных ходов)
                if not can_move(game_state['grid']):
                    game_state['game_over'] = True
            
            request.session['game_2048'] = game_state
    
    # Новая игра
    if request.method == 'POST' and request.POST.get('new_game'):
        request.session['game_2048'] = {
            'grid': [[0, 0, 0, 0] for _ in range(4)],
            'score': 0,
            'game_over': False,
            'won': False,
            'moves': 0
        }
        game_state = request.session['game_2048']
        add_new_tile(game_state)
        add_new_tile(game_state)
    
    context = {
        'grid': game_state['grid'],
        'score': game_state['score'],
        'high_score': request.session.get('2048_high_score', 0),
        'game_over': game_state['game_over'],
        'won': game_state['won'],
        'moves': game_state['moves'],
    }
    
    # Обновление рекорда
    if game_state['score'] > request.session.get('2048_high_score', 0):
        request.session['2048_high_score'] = game_state['score']
        context['high_score'] = game_state['score']
    
    return render(request, 'games/2048.html', context)

# Вспомогательные функции для игры 2048

def add_new_tile(game_state):
    """Добавляет новую плитку (2 или 4) на свободное место"""
    empty_cells = []
    for i in range(4):
        for j in range(4):
            if game_state['grid'][i][j] == 0:
                empty_cells.append((i, j))
    
    if empty_cells:
        i, j = random.choice(empty_cells)
        game_state['grid'][i][j] = 2 if random.random() < 0.9 else 4
        return True
    return False

def move_tiles(game_state, direction):
    """Перемещает плитки в указанном направлении"""
    grid = game_state['grid']
    moved = False
    score_add = 0
    
    if direction == 'left':
        for i in range(4):
            row, added_score = merge_row(grid[i])
            if row != grid[i]:
                moved = True
            grid[i] = row
            score_add += added_score
    
    elif direction == 'right':
        for i in range(4):
            row, added_score = merge_row(grid[i][::-1])
            if row != grid[i][::-1]:
                moved = True
            grid[i] = row[::-1]
            score_add += added_score
    
    elif direction == 'up':
        for j in range(4):
            column = [grid[i][j] for i in range(4)]
            new_col, added_score = merge_row(column)
            if new_col != column:
                moved = True
            for i in range(4):
                grid[i][j] = new_col[i]
            score_add += added_score
    
    elif direction == 'down':
        for j in range(4):
            column = [grid[i][j] for i in range(4)]
            new_col, added_score = merge_row(column[::-1])
            if new_col != column[::-1]:
                moved = True
            new_col = new_col[::-1]
            for i in range(4):
                grid[i][j] = new_col[i]
            score_add += added_score
    
    game_state['score'] += score_add
    return moved

def merge_row(row):
    """Объединяет плитки в строке"""
    new_row = [x for x in row if x != 0]
    added_score = 0
    
    i = 0
    while i < len(new_row) - 1:
        if new_row[i] == new_row[i + 1]:
            new_row[i] *= 2
            added_score += new_row[i]
            new_row.pop(i + 1)
        i += 1
    
    # Заполняем нулями до длины 4
    new_row += [0] * (4 - len(new_row))
    return new_row, added_score

def can_move(grid):
    """Проверяет, есть ли возможные ходы"""
    # Проверка пустых клеток
    for i in range(4):
        for j in range(4):
            if grid[i][j] == 0:
                return True
    
    # Проверка возможных слияний по горизонтали
    for i in range(4):
        for j in range(3):
            if grid[i][j] == grid[i][j + 1]:
                return True
    
    # Проверка возможных слияний по вертикали
    for j in range(4):
        for i in range(3):
            if grid[i][j] == grid[i + 1][j]:
                return True
    
    return False