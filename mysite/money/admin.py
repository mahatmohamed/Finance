from django.contrib import admin
from .models import Category, Income, Expense, Subcategory

# Register your models here.
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Income)
admin.site.register(Expense)
