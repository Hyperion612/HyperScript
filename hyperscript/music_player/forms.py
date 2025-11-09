from django import forms
from .models import MusicTrack

class MusicUploadForm(forms.ModelForm):
    class Meta:
        model = MusicTrack
        fields = ['title', 'artist', 'audio_file']