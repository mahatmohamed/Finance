from django.shortcuts import render, redirect, get_object_or_404
from .models import Income, Category, Expense, Subcategory, Budget,Goal
import pandas as pd
from .models import Category, Expense
from datetime import date
from django.db.models import Sum, F, FloatField
from django.template import loader
import pdfkit
from django.db.models import Q, Sum
from django.contrib import messages
from .forms import BudgetForm,GoalForm, UpdateGoalProgressForm
from django.http import HttpResponse
from dateutil.relativedelta import relativedelta


def add_income(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        # Process the submitted form data here
        source = request.POST.get('source', '')  # Update this line
        amount = request.POST.get('amount', '')
        date = request.POST.get('date', '')
        frequency = request.POST.get('frequency', '')
        income = Income(user=request.user, source=source, amount=amount, date=date, frequency=frequency)  # Update this line
        income.save()

        # Redirect to the data_analysis page after successfully saving the income
        return redirect('data_analysis')
    return render(request, 'money/income.html')

def add_expense(request):
    if request.method == 'POST':
        amount = request.POST.get('amount', '')
        date = request.POST.get('date', '')
        category_id = request.POST.get('category', '')
        subcategory_id = request.POST.get('subcategory', '')
        new_category_name = request.POST.get('new_category', '')  # Get the new category name
        new_subcategory_name = request.POST.get('new_subcategory', '')
        description = request.POST.get('description', '')
        frequency = request.POST.get('frequency', '')

        # Handle the case when the category_id is 'new_category'
        if category_id == 'new_category':
            category = Category.objects.create(name=new_category_name)
        else:
            category = Category.objects.get(id=category_id)

        # Handle the case when the subcategory_id is 'new_subcategory'
        if subcategory_id == 'new_subcategory':
            subcategory = Subcategory.objects.create(name=new_subcategory_name, category=category)
        else:
            subcategory = Subcategory.objects.get(id=subcategory_id)

        expense = Expense(
            user=request.user,
            amount=amount,
            date=date,
            category=category,
            subcategory=subcategory,
            description=description,
            frequency=frequency
        )
        expense.save()

        return redirect('data_analysis')

    else:
        categories = Category.objects.all()
        subcategories = Subcategory.objects.all()
        return render(request, 'money/expense.html', {'categories': categories, 'subcategories': subcategories})



def get_analysis_data(user):
    income_qs = Income.objects.filter(user=user)
    expense_qs = Expense.objects.filter(user=user)

    total_income = income_qs.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = expense_qs.aggregate(total=Sum('amount'))['total'] or 0
    savings = total_income - total_expenses
     # Round the total_expenses and savings to 2 decimal places
    total_expenses = round(total_expenses, 2)
    savings = round(savings, 2)

    category_list = Category.objects.all().values()

    if expense_qs.exists():
        expense_df = pd.DataFrame(list(expense_qs.values('amount', 'category_id')))
        category_df = pd.DataFrame(list(category_list))

        expense_df['category_id'] = expense_df['category_id'].fillna(-1).astype(int)
        category_df['id'] = category_df['id'].astype(int)

        expense_df = expense_df.merge(category_df, left_on='category_id', right_on='id', how='left')
        expense_df = expense_df.groupby(['name'])['amount'].sum().reset_index()

        # Create a dictionary with category names as keys and amounts as values
        category_amounts = dict(zip(expense_df['name'], expense_df['amount']))

        # Add the amount to each category object in the category_list
        for category in category_list:
            category['amount'] = category_amounts.get(category['name'], 0)
    else:
        expense_df = pd.DataFrame(columns=['name', 'amount'])

    income_list = income_qs.values()
    expense_list = expense_qs.values('id', 'amount', 'date', 'frequency', 'category__name', 'subcategory__name')


    income_percentage = 0
    expense_percentage = 0
    savings_percentage = 0

    if total_income > 0:
        income_percentage = (total_income / (total_income + total_expenses)) * 100
        expense_percentage = (total_expenses / (total_income + total_expenses)) * 100
        savings_percentage = 100 - income_percentage - expense_percentage

    return {
        'income_list': income_list,
        'expense_list': expense_list,
        'category_list': category_list,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'savings': savings,
        'expense_df': expense_df.to_dict('records'),
        'income_percentage': income_percentage,
        'expense_percentage': expense_percentage,
        'savings_percentage': savings_percentage,
    }




def data_analysis(request):
    if not request.user.is_authenticated:
        return redirect('login')

    context = get_analysis_data(request.user)
    return render(request, 'money/data_analysis.html', context)

def download_analysis_pdf(request):
    if not request.user.is_authenticated:
        return redirect('login')

    context = get_analysis_data(request.user)
    template = loader.get_template('money/data_analysis.html')
    html = template.render(context)

    # Use pdfkit to convert the HTML string to a PDF file
    pdf_file = pdfkit.from_string(html, False)

    # Return the PDF file as a response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="analysis.pdf"'

    return response

def about(request):
    return render(request, 'money/about.html')

def terms_and_privacy(request):
    return render(request, 'money/terms_and_privacy.html')



def add_budget(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        category_id = request.POST.get('category', '')
        amount = request.POST.get('amount', '')
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')

        category = Category.objects.get(id=category_id)
        budget = Budget(user=request.user, category=category, amount=amount, start_date=start_date, end_date=end_date)
        budget.save()

        return redirect('view_budgets')

    categories = Category.objects.all()
    return render(request, 'money/add_budget.html', {'categories': categories})

def view_budgets(request):
    if not request.user.is_authenticated:
        return redirect('login')

    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'money/view_budgets.html', {'budgets': budgets})

def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, pk=budget_id)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully.')
            return redirect('view_budgets')
        else:
            messages.error(request, 'There was an error updating the budget.')
    else:
        form = BudgetForm(instance=budget)
    
    return render(request, 'money/edit_budget.html', {'form': form, 'budget_id': budget_id})

def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, pk=budget_id)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully.')
        return redirect('view_budgets')
    
    return render(request, 'money/delete_budget.html', {'budget': budget})



def view_bills(request):
    if not request.user.is_authenticated:
        return redirect('login')

    expenses = Expense.objects.filter(user=request.user)
    bills = []

    for expense in expenses:
        next_due_date = expense.date
        today = date.today()

        # Find the next due date
        while next_due_date <= today:
            next_due_date += relativedelta(months=1)

        days_left = (next_due_date - today).days
        bills.append({
            'expense': expense,
            'next_due_date': next_due_date,
            'days_left': days_left
        })

    # Filter bills by category
    category_id = request.GET.get('category')
    if category_id:
        bills = [b for b in bills if b['expense'].category.id == int(category_id)]

    # Filter bills by status
    status = request.GET.get('status')
    if status == 'overdue':
        bills = [b for b in bills if b['days_left'] < 0]
    elif status == 'upcoming':
        bills = [b for b in bills if 0 <= b['days_left'] <= 30]
    elif status == 'paid':
        bills = [b for b in bills if b['expense'].is_paid]

    # Sort bills
    sort_by = request.GET.get('sort_by')
    if sort_by == 'due_date':
        bills = sorted(bills, key=lambda x: x['next_due_date'])
    elif sort_by == 'amount':
        bills = sorted(bills, key=lambda x: x['expense'].amount)
    elif sort_by == 'category':
       bills = sorted([b for b in bills if b['expense'].category], key=lambda x: x['expense'].category.name)


    categories = Category.objects.annotate(
        total_amount=Sum(F('expense__amount'), filter=Q(expense__user=request.user), output_field=FloatField()))

    for category in categories:
        if category.total_amount is not None:
            category.total_amount = round(category.total_amount, 2)

    return render(request, 'money/view_bills.html', {'bills': bills, 'categories': categories, 'status': status, 'sort_by': sort_by})



# Add Goal
def add_goal(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = GoalForm(request.POST)

        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Financial goal added successfully!')
            return redirect('view_goals')
        else:
            messages.error(request, 'Please correct the errors in the form.')

    else:
        form = GoalForm()

    return render(request, 'money/add_goal.html', {'form': form})
# View Goals
def view_goals(request):
    if not request.user.is_authenticated:
        return redirect('login')

    goals = Goal.objects.filter(user=request.user)
    for goal in goals:
        goal.progress = (goal.current_amount / goal.target_amount) * 100
    return render(request, 'money/view_goals.html', {'goals': goals})
def update_goal_progress(request, goal_id):
    if not request.user.is_authenticated:
        return redirect('login')

    goal = get_object_or_404(Goal, id=goal_id, user=request.user)

    if request.method == 'POST':
        form = UpdateGoalProgressForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal progress updated successfully!')
            return redirect('view_goals')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = UpdateGoalProgressForm(instance=goal)

    return render(request, 'money/update_goal_progress.html', {'form': form, 'goal': goal})

def edit_goal(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('view_goals')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'money/edit_goal.html', {'form': form, 'goal': goal})

def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    goal.delete()
    return redirect('view_goals')