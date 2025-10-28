from django.shortcuts import render
from django.http import HttpResponse

def note_list(request):
    return HttpResponse("Приложение Заметки в разработке")

# Create your views here.
