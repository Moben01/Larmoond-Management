from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
  
    # عاید
    path('incomes/', views.income_list, name='income_list'),
    path('incomes/create/', views.income_create, name='income_create'),
    path('incomes/<int:pk>/update/', views.income_update, name='income_update'),
    path('incomes/<int:pk>/delete/', views.income_delete, name='income_delete'),
    
    # لګښت
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/update/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    path('finance/dashboard/', views.finance_dashboard, name='dashboard'),
    path('income/print/', views.income_print, name='income_print'),
    path('expense/print/', views.expense_print, name='expense_print'),
    path('dashboard/print/', views.finance_dashboard_print, name='dashboard_print'),

    # income sources
    path('income-sources/', views.income_source_list, name='income_source_list'),
    path('income-sources/create/', views.income_source_create, name='income_source_create'),
    path('income-sources/<int:pk>/update/', views.income_source_update, name='income_source_update'),
    path('income-sources/<int:pk>/delete/', views.income_source_delete, name='income_source_delete'),

    # expense category
    path('expense-categories/', views.expense_category_list, name='expense_category_list'),
    path('expense-categories/create/', views.expense_category_create, name='expense_category_create'),
    path('expense-categories/<int:pk>/update/', views.expense_category_update, name='expense_category_update'),
    path('expense-categories/<int:pk>/delete/', views.expense_category_delete, name='expense_category_delete'),

]