from django import forms
from .models import Workout, TrainingSet

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['date', 'target_muscle']
        # Bootstrap prosto z pytona
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'target_muscle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Łydki i pięty'})
        }

class TrainingSetForm(forms.ModelForm):
    class Meta:
        model = TrainingSet
        fields = ['exercise', 'set_number', 'weight', 'reps']

        widgets = {
            'exercise': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Klatka i Niceps'}),
            'set_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}), # Pozwólmy na połowki kilogramów
            'reps': forms.NumberInput(attrs={'class': 'form-control'}),
        }