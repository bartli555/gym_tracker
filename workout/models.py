from django.db import models

# To zastępuje naszą pierwszą tabelę "workouts"
class Workout(models.Model):
    date = models.DateField()
    target_muscle = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.date} - {self.target_muscle}"

    @property
    def total_tonnage(self):
        # Pyta wyciąga wszystkie serie, mnoży ciężar przez powtórzenia i sumuje całość
        return sum(seria.weight * seria.reps for seria in self.sets.all())

# To zastępuje naszą tabelę "training_sets"
class TrainingSet(models.Model):
    # Klucz obcy (FOREIGN KEY) - łączy serię z konkretnym treningiem
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='sets')
    exercise = models.CharField(max_length=100, default="Nieznane")
    set_number = models.PositiveIntegerField(default=1, verbose_name="Numer serii")
    weight = models.FloatField()
    reps = models.IntegerField()

    def __str__(self):
        return f"{self.weight} kg x {self.reps} powt."

class DailyMetrics(models.Model):
    date = models.DateField(unique=True, verbose_name="Data pomiaru")
    weight = models.DecimalField(max_digits=5, decimal_places=2,verbose_name="Masa ciała (kg)")
    calories = models.PositiveIntegerField(verbose_name="Spożyte kalorie (kcal)", null=True, blank=True)
    protein = models.PositiveIntegerField(verbose_name="Białko (g)", null=True, blank=True)
    carbs = models.PositiveIntegerField(verbose_name="Węglowodany (g)", null=True, blank=True)
    fats = models.PositiveIntegerField(verbose_name="Tłuszcze (g)", null=True, blank=True)

    def __str__(self):
        return f"{self.date} - {self.weight} kg"

class ExerciseMapping(models.Model):
    exercise_name = models.CharField(max_length=255, unique=True, verbose_name="Nazwa Ćwiczenia (Hevy)")
    target_muscle = models.CharField(max_length=100, verbose_name="Partia mięśniowa")

    def __str__(self):
        return f"{self.exercise_name} -> {self.target_muscle}" 