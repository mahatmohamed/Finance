from django.shortcuts import render, redirect
from .models import Income, Category, Expense
import pandas as pd
from django.db.models import Sum
from django.template import loader
import pdfkit
from django.http import HttpResponse


def add_income(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        # Process the submitted form data here
        amount = request.POST.get('amount', '')
        date = request.POST.get('date', '')
        frequency = request.POST.get('frequency', '')
        income = Income(user=request.user, amount=amount, date=date, frequency=frequency)
        income.save()

        # Redirect to the data_analysis page after successfully saving the income
        return redirect('data_analysis')
    return render(request, 'money/income.html')


def add_expense(request):
    if request.method == 'POST':
        amount = request.POST.get('amount', '')
        date = request.POST.get('date', '')
        category_id = request.POST.get('category', '')
        frequency = request.POST.get('frequency', '')

        category = Category.objects.get(id=category_id)

        expense = Expense(
            user=request.user,
            amount=amount,
            date=date,
            category=category,
            frequency=frequency
        )
        expense.save()

        # Redirect to the data_analysis page after successfully saving the expense
        return redirect('data_analysis')

    else:
        categories = Category.objects.all()
        return render(request, 'money/expense.html', {'categories': categories})


def get_analysis_data(user):
    income_qs = Income.objects.filter(user=user)
    expense_qs = Expense.objects.filter(user=user)

    total_income = income_qs.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = expense_qs.aggregate(total=Sum('amount'))['total'] or 0
    savings = total_income - total_expenses

    if expense_qs.exists():
        expense_df = pd.DataFrame(list(expense_qs.values('amount', 'category_id')))
        category_df = pd.DataFrame(list(Category.objects.all().values()))
        expense_df = expense_df.merge(category_df, left_on='category_id', right_on='id', how='left')
        expense_df = expense_df.groupby(['name'])['amount'].sum().reset_index()
    else:
        expense_df = pd.DataFrame(columns=['name', 'amount'])

    income_list = income_qs.values()
    expense_list = expense_qs.values('id', 'amount', 'date', 'frequency', 'category__name')
    category_list = Category.objects.all().values()

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
