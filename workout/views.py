from django.shortcuts import render
from .models import Workout

def dashboard(request):
    # Wyciągamy z bazy wszystkie treningi, posortowane od najnowszego
    all_workouts = Workout.objects.all().order_by('-date')

    # Pakujemy je w paczkę (słownik), żeby przekazać do HTML-a
    context = {
        'workouts': all_workouts
    }

    # Przekazujemy paczkę do szablonu, który zaraz stworzymy
    return render(request, 'workout/dashboard.html', context)