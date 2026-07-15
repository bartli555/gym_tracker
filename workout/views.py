from django.shortcuts import render, redirect
from .models import Workout
from .forms import WorkoutForm

def dashboard(request):
    # Wyciągamy z bazy wszystkie treningi, posortowane od najnowszego
    all_workouts = Workout.objects.all().order_by('-date')
    # Pakujemy je w paczkę (słownik), żeby przekazać do HTML-a
    context = {
        'workouts': all_workouts
    }
    # Przekazujemy paczkę do szablonu, który zaraz stworzymy
    return render(request, 'workout/dashboard.html', context)

def add_workout(request):
    # Jeśli ktoś kliknął przycisk "Zapisz" (wysłał dane formularzem)
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            form.save() # Zapisujemy do bazy sql
            return redirect('dashboard') # Wróc na stronę gówną
        # Jeśli ktoś po prostu wszedł na stronę (żeby zobaczyć formularz)
    else:
            form = WorkoutForm()

    return render(request, 'workout/add_workout.html', {'form': form})