from django import forms
from .models import Discipline


class DisciplineForm(forms.ModelForm):

    class Meta:
        model = Discipline
        fields = [
            'discipline',
            'weight_1',
            'weight_2',
            'weight_3',
            'weight_4',
            'weight_5',
            'weight_6',
            'weight_7',
            'weight_8',
            'weight_9',
            'weight_10',
            'times_1',
            'times_2',
            'times_3',
            'times_4',
            'times_5',
            'times_6',
            'times_7',
            'times_8',
            'times_9',
            'times_10',
            'remarks',
        ]
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }
