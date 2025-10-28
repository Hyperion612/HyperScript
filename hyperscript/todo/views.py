from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from .forms import TaskForm

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'todo/task_list.html', {'tasks': tasks})

@login_required
def add_task(request):
    if request.method == 'POST':
        # Создаем форму из данных запроса
        form_data = {
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
            'priority': request.POST.get('priority', 'medium'),
            'due_date': request.POST.get('due_date') or None
        }
        
        # Простая валидация
        if not form_data['title']:
            messages.error(request, 'Название задачи обязательно!')
            return render(request, 'todo/add_task.html')
        
        # Создаем задачу
        task = Task(
            user=request.user,
            title=form_data['title'],
            description=form_data['description'],
            priority=form_data['priority'],
            due_date=form_data['due_date']
        )
        task.save()
        
        messages.success(request, 'Задача успешно добавлена!')
        return redirect('task_list')
    
    # GET запрос - показываем пустую форму
    return render(request, 'todo/add_task.html')

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = not task.completed
    task.save()
    
    status = "выполнена" if task.completed else "возвращена в работу"
    messages.success(request, f'Задача "{task.title}" {status}!')
    return redirect('task_list')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task_title = task.title
    task.delete()
    
    messages.success(request, f'Задача "{task_title}" удалена!')
    return redirect('task_list')