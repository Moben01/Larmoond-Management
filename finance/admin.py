from django.contrib import admin
from .models import Expense, Income


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'amount', 'date', 'created_at']
    list_filter = ['category', 'date']
    search_fields = ['title', 'note']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'amount', 'date', 'created_at']
    list_filter = ['source', 'date']
    search_fields = ['title', 'note']