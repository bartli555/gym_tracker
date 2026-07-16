from django.shortcuts import render, redirect, get_object_or_404
from .models import Workout, TrainingSet
from .forms import WorkoutForm, TrainingSetForm

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

def workout_detail(request, pk):
     # Wyciągamy konkretny trening z bazy na podstawie jego ID (pk - primary key)
     workout = get_object_or_404(Workout, pk=pk)

     if request.method == 'POST':
          form = TrainingSetForm(request.POST)
          if form.is_valid():
               # INŻYNIERYJNY TRIK: Tworzymy paczkę z danymi, ale wstrzymujemy zapis do bazy (commit=False)
               new_set = form.save(commit=False)
               # Ręcznie "przypinamy" tę serię do obecnego treningu
               new_set.workout = workout
               # Dopiero teraz wysyłamy wszystko do bazy SQL
               new_set.save()

               # Przeładowujemy stronę, żeby wyświetlić nową serię
               return redirect('workout_detail', pk=workout.pk)
     else:
          form = TrainingSetForm()

     context = {
          'workout': workout,
          'form': form,
          'sets': workout.sets.all().order_by('id') # Wyciągamy dodane już serie
     }           
     return render(request, 'workout/workout_detail.html', context)       