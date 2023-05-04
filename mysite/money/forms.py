from django import forms
from .models import Budget
from .models import Goal

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'start_date', 'end_date']


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['category', 'title', 'target_amount', 'target_date'] # Include the category field
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
        }
class UpdateGoalProgressForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['current_amount']
