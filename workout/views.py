from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Workout, TrainingSet, DailyMetrics
from .forms import WorkoutForm, TrainingSetForm
from django.db.models import Max
import json

@login_required
def dashboard(request):
    # Wyciągamy z bazy wszystkie treningi, posortowane od najnowszego
    all_workouts = Workout.objects.all().order_by('-date')
    # Wyciągamy ostatni zaraportowany dzień (first() bierze pierwszy wynik z posortowanej listy)
    latest_metrics = DailyMetrics.objects.order_by('-date').first()

    # Łapiemy parametry dat z adresu URL
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    muscle_query = request.GET.get('muscle')

    #Nakładamy filtry na zapytanie do bazy, jeśli daty zostały podane
    if date_from:
         all_workouts = all_workouts.filter(date__gte=date_from) # gte = greater than or equal (od)
    if date_to:
         all_workouts = all_workouts.filter(date__lte=date_to) # lte = less than or equal (do)  
    if muscle_query:
         all_workouts = all_workouts.filter(target_muscle__icontains=muscle_query)        

    # Wyciągamy listę unikalnych nazw ćwiczeń z bazy
    uniqe_exercises = TrainingSet.objects.values_list('exercise', flat=True).distinct()

    # Sprawdzamy, co wybrał użytkownik z menu (parametr w adresie URL)
    target_exercise = request.GET.get('exercise')

    # Jeśli ktoś wszedł na stronę i nic nie wybrał (pierwsze załadowanie), 
    # to ładujemy wykres dla pierwszego ćwiczenia z listy (jeśli jakieś istnieje)
    if not target_exercise and uniqe_exercises:
         target_exercise = uniqe_exercises[0]

    # Filtrujemy dane tylko dla wybranego ćwiczenia (lub domyślnego)
    dates = []
    weights = []

    if target_exercise:
         qs = TrainingSet.objects.filter(exercise__icontains=target_exercise) \
                                .values('workout__date') \
                                .annotate(max_weight = Max('weight')) \
                                .order_by('workout__date')
         dates = [str(entry['workout__date']) for entry in qs]
         weights = [float(entry['max_weight']) for entry in qs]
                                

    context = {
        'workouts': all_workouts,
        'unique_exercises': uniqe_exercises,
        'target_exercise': target_exercise,
        'dates_json': json.dumps(dates),
        'weights_json': json.dumps(weights),
        'latest_metrics': latest_metrics
    }
    # Przekazujemy paczkę do szablonu, który zaraz stworzymy
    return render(request, 'workout/dashboard.html', context)

@login_required
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

@login_required
def workout_detail(request, pk):
     # Wyciągamy konkretny trening z bazy na podstawie jego ID (pk - primary key)
     workout = get_object_or_404(Workout, pk=pk)

     # Wyciągamy listę wszystkich unikalnych ćwiczeń z bazy
     unique_exercises = TrainingSet.objects.values_list('exercise', flat=True).distinct()

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
          'unique_exercises': unique_exercises,
          'form': form,
          'sets': workout.sets.all().order_by('id') # Wyciągamy dodane już serie
     }           
     return render(request, 'workout/workout_detail.html', context)

@login_required
def delete_set(request, set_id):
     # Znajdujemy konkretną serię w bazie
     training_set = get_object_or_404(TrainingSet, id=set_id)
     # Zapisujemy ID treningu, żeby wiedzieć, gdzie wrócić po usunięciu
     workout_id = training_set.workout.id
     # Usuwamy!
     training_set.delete()
     return redirect('workout_detail', pk=workout_id)

@login_required
def edit_set(request, set_id):
    training_set = get_object_or_404(TrainingSet, id=set_id)
    workout_id = training_set.workout.id

    if request.method == "POST":
        # Przekazujemy instance, aby Django nadpisało ten konkretny wpis
        form = TrainingSetForm(request.POST, instance=training_set)
        if form.is_valid():
            form.save()
            return redirect('workout_detail', pk=workout_id)
    else:
            # Ładujemy formularz wypełniony obecnymi danymi z bazy
            form = TrainingSetForm(instance=training_set)   

    return render(request, 'workout/edit_set.html', {'form': form, 'training_set': training_set})

@login_required
def delete_workout(request, pk):
     # Ze względów bezpieczeństwa reagujemy tylko na żądania POST
     if request.method == 'POST':
          workout = get_object_or_404(Workout, pk=pk)
          workout.delete()

     # Po skasowaniu przekierowujemy z powrotem na główny kokpit
     return redirect('dashboard')     

@login_required
def add_daily_metrics(request):
     if request.method == 'POST':
          # Pobieramy dane z formularza. Jeśli pole jest puste, ustawiamy None
          weight = request.POST.get('weight')
          calories = request.POST.get('calories') or None
          protein = request.POST.get('protein') or None
          carbs = request.POST.get('carbs') or None
          fats = request.POST.get('fats') or None

          # update_or_create szuka wpisu z dzisiejszą datą. 
          # Jak nie ma - tworzy nowy. Jak jest - aktualizuje podane pola (defaults)
          DailyMetrics.objects.update_or_create(
               date = date.today(),
               defaults={
                    'weight': weight,
                    'calories': calories,
                    'protein': protein,
                    'carbs': carbs,
                    'fats': fats
               }
          )
     return redirect('dashboard')