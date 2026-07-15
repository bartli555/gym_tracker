from django import forms
from .models import Workout

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['date', 'target_muscle']
        # Bootstrap prosto z pytona
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'target_muscle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Łydki i pięty'})
        }