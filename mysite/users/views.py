from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import RegistrationForm
from .forms import UserProfileForm
from .models import UserProfile
from money.views import get_analysis_data
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after successful registration.
            login(request, user)
            messages.success(request, 'You have successfully registered and are now logged in.')
            return redirect('data_analysis')
        else:
            if User.objects.filter(username=form.data['username']).exists():
                messages.warning(request, 'This username is already registered. Please choose another username.')
            if form.data['password1'] != form.data['password2']:
                messages.error(request, 'Passwords do not match. Please enter the same password in both fields.')
    else:
        form = RegistrationForm()

    return render(request, 'users/register.html', {'form': form})




@login_required
def user_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile, created = UserProfile.objects.get_or_create(user=request.user)

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

@login_required
def edit_profile(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'users/edit_profile.html', {'form': form})