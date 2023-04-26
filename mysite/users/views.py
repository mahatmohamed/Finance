from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import RegistrationForm
from .forms import UserProfileForm
from .models import UserProfile
from money.views import get_analysis_data

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user object
            print("User saved:", user)  # Debugging message
            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcome {username}! Your are Logged in!.')
            login(request, user)  # Pass the 'user' object instead of 'username'
            return redirect('login')
        else:
            print("Form is not valid:", form.errors)  # Debugging message
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})




def user_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = UserProfile.objects.get(user=request.user)

    context = get_analysis_data(request.user)

    total_income = context['total_income']
    total_expenses = context['total_expenses']
    savings = context['savings']

    if total_income > 0:
        income_percentage = (total_income / (total_income + total_expenses + savings)) * 100
        expense_percentage = (total_expenses / (total_income + total_expenses + savings)) * 100
        savings_percentage = (savings / (total_income + total_expenses + savings)) * 100
    else:
        income_percentage = 0
        expense_percentage = 0
        savings_percentage = 0

    context.update({
        'income_percentage': income_percentage,
        'expense_percentage': expense_percentage,
        'savings_percentage': savings_percentage,
    })

    return render(request, 'users/user_profile.html', context)