from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
import random
import json

# ==================== ВИСЕЛИЦА (Hangman) ====================

@login_required
def hangman(request):
    """Главная страница игры Виселица"""
    # Слова для игры
    words = [
        'ПРОГРАММИРОВАНИЕ', 'КОМПЬЮТЕР', 'АЛГОРИТМ', 'БАЗАДАННЫХ',
        'ИНТЕРНЕТ', 'ПРИЛОЖЕНИЕ', 'ФРЕЙМВОРК', 'ШАБЛОН', 'ПЕРЕМЕННАЯ',
        'ФУНКЦИЯ', 'ОБЪЕКТ', 'КЛАСС', 'МЕТОД', 'АТРИБУТ', 'СЕРВЕР'
    ]
    
    # Инициализация игры в сессии
    if 'hangman' not in request.session:
        request.session['hangman'] = {
            'word': random.choice(words),
            'guessed': [],
            'wrong_guesses': 0,
            'game_over': False,
            'won': False
        }
    
    game_state = request.session['hangman']
    
    # Подготовка контекста
    context = prepare_hangman_context(game_state)
    
    # Если это AJAX запрос, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('games/hangman_game.html', context)
        return JsonResponse({
            'html': html,
            'game_state': game_state
        })
    
    # Обычный запрос - полная страница
    return render(request, 'games/hangman.html', context)

@login_required
def hangman_guess(request):
    """AJAX: Угадать букву в Виселице"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            letter = data.get('letter', '').upper().strip()
            
            # Проверяем, что буква валидная
            if not letter or len(letter) != 1 or not letter.isalpha():
                return JsonResponse({'error': 'Некорректная буква'}, status=400)
            
            # Получаем текущее состояние игры
            game_state = request.session.get('hangman', {})
            if not game_state:
                return JsonResponse({'error': 'Игра не инициализирована'}, status=400)
            
            # Если игра уже окончена
            if game_state.get('game_over', False):
                return JsonResponse({'error': 'Игра уже окончена'}, status=400)
            
            # Проверяем, не угадывали ли уже эту букву
            if letter in game_state['guessed']:
                context = prepare_hangman_context(game_state)
                html = render_to_string('games/hangman_game.html', context)
                return JsonResponse({
                    'html': html,
                    'message': f'Буква "{letter}" уже была использована',
                    'status': 'already_used'
                })
            
            # Добавляем букву в угаданные
            game_state['guessed'].append(letter)
            
            # Проверяем, есть ли буква в слове
            if letter not in game_state['word']:
                game_state['wrong_guesses'] += 1
            
            # Проверка условий окончания игры
            message = f'Буква "{letter}" угадана!'
            
            # Проверяем, выиграл ли игрок
            if all(l in game_state['guessed'] for l in game_state['word']):
                game_state['game_over'] = True
                game_state['won'] = True
                message = '🎉 Поздравляем! Вы выиграли!'
            
            # Проверяем, проиграл ли игрок (7 ошибок)
            elif game_state['wrong_guesses'] >= 7:
                game_state['game_over'] = True
                game_state['won'] = False
                message = '💀 Игра окончена! Вы проиграли!'
            
            # Сохраняем обновленное состояние
            request.session['hangman'] = game_state
            
            # Готовим контекст для ответа
            context = prepare_hangman_context(game_state)
            html = render_to_string('games/hangman_game.html', context)
            
            return JsonResponse({
                'html': html,
                'message': message,
                'game_state': game_state,
                'status': 'success'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректный JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@login_required
def hangman_new(request):
    """AJAX: Начать новую игру в Виселицу"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        words = [
            'ПРОГРАММИРОВАНИЕ', 'КОМПЬЮТЕР', 'АЛГОРИТМ', 'БАЗАДАННЫХ',
            'ИНТЕРНЕТ', 'ПРИЛОЖЕНИЕ', 'ФРЕЙМВОРК', 'ШАБЛОН', 'ПЕРЕМЕННАЯ'
        ]
        
        # Создаем новую игру
        game_state = {
            'word': random.choice(words),
            'guessed': [],
            'wrong_guesses': 0,
            'game_over': False,
            'won': False
        }
        
        request.session['hangman'] = game_state
        
        # Готовим контекст
        context = prepare_hangman_context(game_state)
        html = render_to_string('games/hangman_game.html', context)
        
        return JsonResponse({
            'html': html,
            'message': '🚀 Новая игра началась!',
            'game_state': game_state,
            'status': 'new_game'
        })
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

def prepare_hangman_context(game_state):
    """Подготовка контекста для рендеринга Виселицы"""
    display_word = ''
    for letter in game_state['word']:
        if letter in game_state['guessed']:
            display_word += letter + ' '
        else:
            display_word += '_ '
    
    return {
        'display_word': display_word.strip(),
        'guessed_letters': game_state['guessed'],
        'wrong_guesses': game_state['wrong_guesses'],
        'game_over': game_state['game_over'],
        'won': game_state['won'],
        'word_length': len(game_state['word']),
        'full_word': game_state['word'],
        'max_wrong': 7,
    }

# ==================== 2048 ====================

@login_required
def game_2048(request):
    """Главная страница игры 2048"""
    # Инициализация игры
    if 'game_2048' not in request.session:
        request.session['game_2048'] = initialize_2048_game()
    
    game_state = request.session['game_2048']
    
    # Подготовка контекста
    context = prepare_2048_context(game_state, request)
    
    # Если это AJAX запрос
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('games/2048_game.html', context)
        return JsonResponse({
            'html': html,
            'game_state': {
                'grid': game_state['grid'],
                'score': game_state['score'],
                'game_over': game_state['game_over'],
                'won': game_state['won'],
                'moves': game_state['moves']
            }
        })
    
    return render(request, 'games/2048.html', context)

@login_required
def game_2048_move(request):
    """AJAX: Сделать ход в 2048"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            direction = data.get('direction')
            
            if direction not in ['up', 'down', 'left', 'right']:
                return JsonResponse({'error': 'Некорректное направление'}, status=400)
            
            # Получаем текущее состояние
            game_state = request.session.get('game_2048', {})
            if not game_state:
                game_state = initialize_2048_game()
            
            # Если игра окончена
            if game_state.get('game_over', False):
                return JsonResponse({'error': 'Игра уже окончена'}, status=400)
            
            # Делаем ход
            old_grid = [row[:] for row in game_state['grid']]
            moved = move_2048_tiles(game_state, direction)
            
            if moved:
                game_state['moves'] += 1
                add_new_2048_tile(game_state)
                
                # Проверка победы
                if not game_state['won']:
                    for row in game_state['grid']:
                        if 2048 in row:
                            game_state['won'] = True
                            break
                
                # Проверка поражения
                if not can_2048_move(game_state['grid']):
                    game_state['game_over'] = True
            
            # Сохраняем состояние
            request.session['game_2048'] = game_state
            
            # Обновляем рекорд
            if game_state['score'] > request.session.get('2048_high_score', 0):
                request.session['2048_high_score'] = game_state['score']
            
            # Готовим контекст
            context = prepare_2048_context(game_state, request)
            html = render_to_string('games/2048_game.html', context)
            
            return JsonResponse({
                'html': html,
                'game_state': {
                    'grid': game_state['grid'],
                    'score': game_state['score'],
                    'game_over': game_state['game_over'],
                    'won': game_state['won'],
                    'moves': game_state['moves']
                },
                'moved': moved,
                'message': 'Ход сделан!' if moved else 'Ход невозможен!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректный JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@login_required
def game_2048_new(request):
    """AJAX: Новая игра 2048"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Инициализируем новую игру
        game_state = initialize_2048_game()
        request.session['game_2048'] = game_state
        
        # Готовим контекст
        context = prepare_2048_context(game_state, request)
        html = render_to_string('games/2048_game.html', context)
        
        return JsonResponse({
            'html': html,
            'game_state': {
                'grid': game_state['grid'],
                'score': game_state['score'],
                'game_over': game_state['game_over'],
                'won': game_state['won'],
                'moves': game_state['moves']
            },
            'message': '🚀 Новая игра началась!'
        })
    
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

def initialize_2048_game():
    """Инициализация новой игры 2048"""
    game_state = {
        'grid': [[0, 0, 0, 0] for _ in range(4)],
        'score': 0,
        'game_over': False,
        'won': False,
        'moves': 0
    }
    add_new_2048_tile(game_state)
    add_new_2048_tile(game_state)
    return game_state

def add_new_2048_tile(game_state):
    """Добавить новую плитку в 2048"""
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

def move_2048_tiles(game_state, direction):
    """Переместить плитки в 2048"""
    grid = game_state['grid']
    moved = False
    score_add = 0
    
    if direction == 'left':
        for i in range(4):
            row, added_score = merge_2048_row(grid[i])
            if row != grid[i]:
                moved = True
            grid[i] = row
            score_add += added_score
    
    elif direction == 'right':
        for i in range(4):
            row, added_score = merge_2048_row(grid[i][::-1])
            if row != grid[i][::-1]:
                moved = True
            grid[i] = row[::-1]
            score_add += added_score
    
    elif direction == 'up':
        for j in range(4):
            column = [grid[i][j] for i in range(4)]
            new_col, added_score = merge_2048_row(column)
            if new_col != column:
                moved = True
            for i in range(4):
                grid[i][j] = new_col[i]
            score_add += added_score
    
    elif direction == 'down':
        for j in range(4):
            column = [grid[i][j] for i in range(4)]
            new_col, added_score = merge_2048_row(column[::-1])
            if new_col != column[::-1]:
                moved = True
            new_col = new_col[::-1]
            for i in range(4):
                grid[i][j] = new_col[i]
            score_add += added_score
    
    game_state['score'] += score_add
    return moved

def merge_2048_row(row):
    """Объединить плитки в строке для 2048"""
    new_row = [x for x in row if x != 0]
    added_score = 0
    
    i = 0
    while i < len(new_row) - 1:
        if new_row[i] == new_row[i + 1]:
            new_row[i] *= 2
            added_score += new_row[i]
            new_row.pop(i + 1)
        i += 1
    
    new_row += [0] * (4 - len(new_row))
    return new_row, added_score

def can_2048_move(grid):
    """Проверить, есть ли возможные ходы в 2048"""
    # Проверка пустых клеток
    for i in range(4):
        for j in range(4):
            if grid[i][j] == 0:
                return True
    
    # Проверка возможных слияний
    for i in range(4):
        for j in range(3):
            if grid[i][j] == grid[i][j + 1]:
                return True
    
    for j in range(4):
        for i in range(3):
            if grid[i][j] == grid[i + 1][j]:
                return True
    
    return False

def prepare_2048_context(game_state, request):
    """Подготовка контекста для 2048"""
    return {
        'grid': game_state['grid'],
        'score': game_state['score'],
        'high_score': request.session.get('2048_high_score', 0),
        'game_over': game_state['game_over'],
        'won': game_state['won'],
        'moves': game_state['moves'],
    }

# ==================== ОБЩИЕ ФУНКЦИИ ====================

@login_required
def games_index(request):
    """Главная страница всех игр"""
    # Статистика для пользователя
    user_stats = {}
    
    if request.user.is_authenticated:
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
def rock_paper_scissors(request):
    """Игра Камень-Ножницы-Бумага"""
    # Простая версия без AJAX (можно добавить позже)
    if 'rps_stats' not in request.session:
        request.session['rps_stats'] = {'wins': 0, 'losses': 0, 'draws': 0, 'round': 0}
    
    stats = request.session['rps_stats']
    
    if request.method == 'POST':
        if 'choice' in request.POST:
            user_choice = request.POST['choice']
            choices = ['rock', 'paper', 'scissors']
            computer_choice = random.choice(choices)
            
            # Определяем победителя
            if user_choice == computer_choice:
                result = 'draw'
                stats['draws'] += 1
            elif (
                (user_choice == 'rock' and computer_choice == 'scissors') or
                (user_choice == 'scissors' and computer_choice == 'paper') or
                (user_choice == 'paper' and computer_choice == 'rock')
            ):
                result = 'win'
                stats['wins'] += 1
            else:
                result = 'lose'
                stats['losses'] += 1
            
            stats['round'] += 1
            request.session['rps_stats'] = stats
            
            # Сохраняем в сессии для отображения
            request.session['rps_last_game'] = {
                'user_choice': user_choice,
                'computer_choice': computer_choice,
                'result': result
            }
            
            # Обновляем общую статистику побед
            if result == 'win':
                request.session['rps_wins'] = request.session.get('rps_wins', 0) + 1
            
            return render(request, 'games/rock_paper_scissors.html', {
                'wins': stats['wins'],
                'losses': stats['losses'],
                'draws': stats['draws'],
                'round': stats['round'],
                'last_game': request.session.get('rps_last_game', {}),
                'show_result': True
            })
        
        elif 'new_game' in request.POST:
            # Новая игра
            request.session['rps_stats'] = {'wins': 0, 'losses': 0, 'draws': 0, 'round': 0}
            return render(request, 'games/rock_paper_scissors.html', {
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'round': 0,
                'show_result': False
            })
    
    # Первый заход на страницу
    return render(request, 'games/rock_paper_scissors.html', {
        'wins': stats['wins'],
        'losses': stats['losses'],
        'draws': stats['draws'],
        'round': stats['round'],
        'show_result': False
    })