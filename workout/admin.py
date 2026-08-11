from django.contrib import admin
from .models import Workout, TrainingSet, DailyMetrics, ExerciseMapping

# Tworzymy moduł do wpisywania serii "w linii"
class TrainingSetInline(admin.TabularInline):
    model = TrainingSet
    extra = 3 # Domyślnie pokaże 3 puste pola pod serie (Tutaj np. 3x10)

# Doczepiamy serie bezpośrednio do widoku treningu
class WorkoutAdmin(admin.ModelAdmin):
    inlines = [TrainingSetInline]
    # Przy okazji robimy eleganckie kolumny na liście głównej
    list_display = ('date', 'target_muscle')

# Rejestrujemy z nowymi ustawieniami
admin.site.register(Workout, WorkoutAdmin)
admin.site.register(DailyMetrics)

@admin.register(ExerciseMapping)
class ExerciseMappingAdmin(admin.ModelAdmin):
    list_display = ('exercise_name', 'target_muscle')
    search_fields = ('exercise_name', 'target_muscle')