from django.db import models
from django.contrib.auth.models import User

class MusicTrack(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название трека')
    artist = models.CharField(max_length=200, verbose_name='Исполнитель', blank=True)
    audio_file = models.FileField(upload_to='music/', verbose_name='Аудио файл')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.artist}"

