import csv
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Workout, TrainingSet, DailyMetrics
from .forms import WorkoutForm, TrainingSetForm
from django.db.models import Max, Sum, F
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
    tonnage = []

    if target_exercise:
         qs = TrainingSet.objects.filter(exercise__icontains=target_exercise) \
                                .values('workout__date') \
                                .annotate(
                                     max_weight = Max('weight'),
                                     total_tonnage = Sum(F('weight') *F('reps'))
                                ) \
                                .order_by('workout__date')
         
         dates = [str(entry['workout__date']) for entry in qs]
         weights = [float(entry['max_weight'] or 0) for entry in qs]
         tonnage = [float(entry['total_tonnage'] or 0) for entry in qs]                       

    context = {
        'workouts': all_workouts,
        'unique_exercises': uniqe_exercises,
        'target_exercise': target_exercise,
        'dates_json': json.dumps(dates),
        'weights_json': json.dumps(weights),
        'tonnage_json': json.dumps(tonnage),
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

@login_required
def upload_hevy_csv(request):
     if request.method == 'POST':
          csv_file = request.FILES.get('csv_file')

          # Proste zabezpieczenie, żeby ktoś nie wrzucił tam np. zdjęcia
          if not csv_file or not csv_file.name.endswtih('.csv'):
               messages.error(request, "EEE, to nie jest plik CSV.")
               return redirect('dashboard')
          
          # Odczytujemy plik w pamięci, linijka po linijce
          file_data = csv_file.read().decode('utf-8').splitlines()
          reader = csv.DictReader(file_data)

          workouts_created = 0
          sets_created = 0

          for row in reader:
               # Hevy dorzuca backslashe do nagłówków (np. start\_time)
               # Czyścimy klucze słownika ze znaków '\', żeby wygodnie wyciągać dane
               clean_row = {k.replace('\\', ''): v for k, v in row.items()}

               # Pobieramy datę z kolumny start_time (format z Hevy: "1 Aug 2026, 12:46")
               try:
                    date_obj = datetime.strptime(clean_row['start_time'], '%d %b %Y, %H:%M')
                    workout_date = date_obj.date()
               except (ValueError, KeyError):
                    # Jeśli wiersz jest uszkodzony lub pusty, lecimy do następnego
                    continue     

               exercise_name = clean_row['exercise_title']

               # Zabezpieczenie przed pustymi wartościami, np. przy ćwiczeniach z masą ciała
               weight = float(clean_row['weight_kg']) if clean_row.get('weight_kg') else 0.0
               reps = int(clean_row['reps']) if clean_row.get('reps') else 0
               set_number = int(clean_row['set_index']) if clean_row.get('set_index') else 0 

               # 1. Krok pierwszy: Szukamy (lub tworzymy) Trening dla danego dnia
               workout, w_created = Workout.objects.get_or_create(
                    date = workout_date,
                    defaults={
                         'target_muscle': 'Import z Hevy' # Domyślna partia dla całego dnia
                    }
               )
               if w_created:
                    workouts_created += 1

               # 2. Krok drugi: Szukamy (lub tworzymy) konkretną serię (Set)
               # Dzięki temu nie dodamy dwa razy tej samej serii z tego samego pliku
               t_set, s_created = TrainingSet.objects.get_or_create(
                    workout = workout,
                    exercise = exercise_name,
                    set_number = set_number,
                    defaults={
                         'weight': weight,
                         'reps': reps
                    }
               )
               if s_created:
                    sets_created += 1

          messages.succes(request, f"Import zakończony! Utworzono {workouts_created} nowych treningów i {sets_created} serii")
          return redirect('dashboard')

     return render(request, 'workout/upload_csv.html')