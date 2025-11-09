from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import MusicTrack
from .forms import MusicUploadForm
import os

@login_required
def music_player(request):
    tracks = MusicTrack.objects.filter(uploaded_by=request.user)
    
    if request.method == 'POST':
        form = MusicUploadForm(request.POST, request.FILES)
        if form.is_valid():
            track = form.save(commit=False)
            track.uploaded_by = request.user
            track.save()
            return redirect('music_player')
    else:
        form = MusicUploadForm()
    
    return render(request, 'music_player/player.html', {
        'tracks': tracks,
        'form': form
    })

@login_required
def delete_track(request, track_id):
    track = MusicTrack.objects.get(id=track_id, uploaded_by=request.user)
    if os.path.exists(track.audio_file.path):
        os.remove(track.audio_file.path)
    track.delete()
    return redirect('music_player')
# Create your views here.
