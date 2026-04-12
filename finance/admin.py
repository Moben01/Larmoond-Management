from django.contrib import admin
from .models import Income, Expense, IncomeSource, ExpenseCategory


@admin.register(IncomeSource)
class IncomeSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'amount', 'currency', 'date']
    list_filter = ['currency', 'source', 'date']
    search_fields = ['title', 'note']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'amount', 'currency', 'date']
    list_filter = ['currency', 'category', 'date']
    search_fields = ['title', 'note']