from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import IncomeForm, ExpenceForm
from .models import Income, Expense
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q, Sum
from decimal import Decimal
from django.db.models.functions import Coalesce
from .models import IncomeSource, ExpenseCategory
from .forms import IncomeSourceForm, ExpenseCategoryForm



# === Income Views ===

def income_list(request):
    incomes = Income.objects.select_related('source').all().order_by('-date', '-id')
    sources = IncomeSource.objects.filter(is_active=True).order_by('name')

    search = request.GET.get('search')
    source = request.GET.get('source')
    currency = request.GET.get('currency')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if search:
        incomes = incomes.filter(title__icontains=search)

    if source:
        incomes = incomes.filter(source_id=source)

    if currency:
        incomes = incomes.filter(currency=currency)

    if from_date:
        incomes = incomes.filter(date__gte=from_date)

    if to_date:
        incomes = incomes.filter(date__lte=to_date)

    total_afn = incomes.filter(currency='AFN').aggregate(total=Sum('amount'))['total'] or 0
    total_usd = incomes.filter(currency='USD').aggregate(total=Sum('amount'))['total'] or 0

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'finance/search_income.html',
            {'incomes': incomes},
            request=request
        )
        return JsonResponse({
            'html': html,
            'total_afn': str(total_afn),
            'total_usd': str(total_usd),
        })

    return render(request, 'finance/income_list.html', {
        'incomes': incomes,
        'sources': sources,
        'total_afn': total_afn,
        'total_usd': total_usd,
    })

def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income was saved successfully!')
            return redirect('finance:income_list')
    else:
        form = IncomeForm()
    return render(request, 'finance/income_form.html', {'form': form, 'title': 'New Income'})

def income_update(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income was updated successfully!')
            return redirect('finance:income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'finance/income_edit_form.html', {'form': form, 'title': 'Edit Income'})

def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk)
    income.delete()
    messages.warning(request, 'Expense was delete successfully!')
    return redirect('finance:income_list')



# === Expense Views ===

def expense_list(request):
    expenses = Expense.objects.select_related('category').all().order_by('-date', '-id')
    categories = ExpenseCategory.objects.filter(is_active=True).order_by('name')

    search = request.GET.get('search')
    category = request.GET.get('category')
    currency = request.GET.get('currency')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if search:
        expenses = expenses.filter(title__icontains=search)

    if category:
        expenses = expenses.filter(category_id=category)

    if currency:
        expenses = expenses.filter(currency=currency)

    if from_date:
        expenses = expenses.filter(date__gte=from_date)

    if to_date:
        expenses = expenses.filter(date__lte=to_date)

    total_afn = expenses.filter(currency='AFN').aggregate(total=Sum('amount'))['total'] or 0
    total_usd = expenses.filter(currency='USD').aggregate(total=Sum('amount'))['total'] or 0

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'finance/search_expense.html',
            {'expenses': expenses},
            request=request
        )
        return JsonResponse({
            'html': html,
            'total_afn': str(total_afn),
            'total_usd': str(total_usd),
        })

    return render(request, 'finance/expense_list.html', {
        'expenses': expenses,
        'categories': categories,
        'total_afn': total_afn,
        'total_usd': total_usd,
    })

def expense_create(request):
    if request.method == 'POST':
        form = ExpenceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense was saved successfully!')
            return redirect('finance:expense_list')
    else:
        form = ExpenceForm()
    return render(request, 'finance/expense_form.html', {'form': form, 'title': 'New Expense'})

def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenceForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense was updated successfully!')
            return redirect('finance:expense_list')
    else:
        form = ExpenceForm(instance=expense)
    return render(request, 'finance/expense_edit_form.html', {'form': form, 'title': 'Edit Expense'})

def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()
    messages.warning(request, 'Expense was delete successfully!')
    return redirect('finance:expense_list')



# # === Dashboard (Independent View) ===
# def dashboard(request):
#     # Latest 5 incomes and expenses
#     recent_incomes = Income.objects.all()[:5]
#     recent_expenses = Expense.objects.all()[:5]
    
#     # Total income and expense in different currencies
#     total_income_afn = sum(i.amount for i in Income.objects.filter(currency='AFN'))
#     total_income_usd = sum(i.amount for i in Income.objects.filter(currency='USD'))
#     total_expense_afn = sum(e.amount for e in Expense.objects.filter(currency='AFN'))
#     total_expense_usd = sum(e.amount for e in Expense.objects.filter(currency='USD'))
    
#     # Net income (separately for each currency)
#     net_afn = total_income_afn - total_expense_afn
#     net_usd = total_income_usd - total_expense_usd
    
#     context = {
#         'recent_incomes': recent_incomes,
#         'recent_expenses': recent_expenses,
#         'total_income_afn': total_income_afn,
#         'total_income_usd': total_income_usd,
#         'total_expense_afn': total_expense_afn,
#         'total_expense_usd': total_expense_usd,
#         'net_afn': net_afn,
#         'net_usd': net_usd,
#     }
#     return render(request, 'dashboard.html', context)





def finance_dashboard(request):
    incomes = Income.objects.all().order_by('-date', '-id')
    expenses = Expense.objects.all().order_by('-date', '-id')

    # AFN
    total_income_afn = Income.objects.filter(currency='AFN').aggregate(
        total=Coalesce(Sum('amount'), Decimal('0.00'))
    )['total']

    total_expense_afn = Expense.objects.filter(currency='AFN').aggregate(
        total=Coalesce(Sum('amount'), Decimal('0.00'))
    )['total']

    balance_afn = total_income_afn - total_expense_afn

    # USD
    total_income_usd = Income.objects.filter(currency='USD').aggregate(
        total=Coalesce(Sum('amount'), Decimal('0.00'))
    )['total']

    total_expense_usd = Expense.objects.filter(currency='USD').aggregate(
        total=Coalesce(Sum('amount'), Decimal('0.00'))
    )['total']

    balance_usd = total_income_usd - total_expense_usd

    # latest records
    latest_incomes = incomes[:5]
    latest_expenses = expenses[:5]

    # status
    if balance_afn > 0:
        afn_status = 'profit'
        afn_status_text = 'You are in profit (AFN)'
    elif balance_afn < 0:
        afn_status = 'loss'
        afn_status_text = 'You are in loss (AFN)'
    else:
        afn_status = 'equal'
        afn_status_text = 'Income and expense are equal (AFN)'

    if balance_usd > 0:
        usd_status = 'profit'
        usd_status_text = 'You are in profit (USD)'
    elif balance_usd < 0:
        usd_status = 'loss'
        usd_status_text = 'You are in loss (USD)'
    else:
        usd_status = 'equal'
        usd_status_text = 'Income and expense are equal (USD)'

    context = {
        'total_income_afn': total_income_afn,
        'total_expense_afn': total_expense_afn,
        'balance_afn': balance_afn,

        'total_income_usd': total_income_usd,
        'total_expense_usd': total_expense_usd,
        'balance_usd': balance_usd,

        'latest_incomes': latest_incomes,
        'latest_expenses': latest_expenses,

        'afn_status': afn_status,
        'afn_status_text': afn_status_text,

        'usd_status': usd_status,
        'usd_status_text': usd_status_text,
    }
    return render(request, 'finance/dashboard.html', context)





def income_source_list(request):
    sources = IncomeSource.objects.all().order_by('name')
    return render(request, 'finance/income_source_list.html', {
        'sources': sources,
    })


def income_source_create(request):
    if request.method == 'POST':
        form = IncomeSourceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income source was created successfully!')
            return redirect('finance:income_source_list')
    else:
        form = IncomeSourceForm()

    return render(request, 'finance/income_source_form.html', {
        'form': form,
        'title': 'Add Income Source'
    })


def income_source_update(request, pk):
    source = get_object_or_404(IncomeSource, pk=pk)

    if request.method == 'POST':
        form = IncomeSourceForm(request.POST, instance=source)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income source was updated successfully!')
            return redirect('finance:income_source_list')
    else:
        form = IncomeSourceForm(instance=source)

    return render(request, 'finance/income_source_form.html', {
        'form': form,
        'title': 'Edit Income Source'
    })


def income_source_delete(request, pk):
    source = get_object_or_404(IncomeSource, pk=pk)
    source.delete()
    messages.warning(request, 'Income source was deleted successfully!')
    return redirect('finance:income_source_list')


# =========================
# Expense Category Views
# =========================

def expense_category_list(request):
    categories = ExpenseCategory.objects.all().order_by('name')
    return render(request, 'finance/expense_category_list.html', {
        'categories': categories,
    })


def expense_category_create(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense category was created successfully!')
            return redirect('finance:expense_category_list')
    else:
        form = ExpenseCategoryForm()

    return render(request, 'finance/expense_category_form.html', {
        'form': form,
        'title': 'Add Expense Category'
    })


def expense_category_update(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)

    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense category was updated successfully!')
            return redirect('finance:expense_category_list')
    else:
        form = ExpenseCategoryForm(instance=category)

    return render(request, 'finance/expense_category_form.html', {
        'form': form,
        'title': 'Edit Expense Category'
    })


def expense_category_delete(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)
    category.delete()
    messages.warning(request, 'Expense category was deleted successfully!')
    return redirect('finance:expense_category_list')



def income_print(request):
    incomes = Income.objects.select_related('source').all().order_by('-date', '-id')
    sources = IncomeSource.objects.filter(is_active=True).order_by('name')

    search = request.GET.get('search')
    source = request.GET.get('source')
    currency = request.GET.get('currency')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if search:
        incomes = incomes.filter(title__icontains=search)

    if source:
        incomes = incomes.filter(source_id=source)

    if currency:
        incomes = incomes.filter(currency=currency)

    if from_date:
        incomes = incomes.filter(date__gte=from_date)

    if to_date:
        incomes = incomes.filter(date__lte=to_date)

    total_afn = incomes.filter(currency='AFN').aggregate(total=Sum('amount'))['total'] or 0
    total_usd = incomes.filter(currency='USD').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'incomes': incomes,
        'total_afn': total_afn,
        'total_usd': total_usd,
        'search': search,
        'selected_source': source,
        'selected_currency': currency,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, 'finance/income_print.html', context)



def expense_print(request):
    expenses = Expense.objects.select_related('category').all().order_by('-date', '-id')
    categories = ExpenseCategory.objects.filter(is_active=True).order_by('name')

    search = request.GET.get('search')
    category = request.GET.get('category')
    currency = request.GET.get('currency')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if search:
        expenses = expenses.filter(title__icontains=search)

    if category:
        expenses = expenses.filter(category_id=category)

    if currency:
        expenses = expenses.filter(currency=currency)

    if from_date:
        expenses = expenses.filter(date__gte=from_date)

    if to_date:
        expenses = expenses.filter(date__lte=to_date)

    total_afn = expenses.filter(currency='AFN').aggregate(total=Sum('amount'))['total'] or 0
    total_usd = expenses.filter(currency='USD').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'expenses': expenses,
        'total_afn': total_afn,
        'total_usd': total_usd,
        'search': search,
        'selected_category': category,
        'selected_currency': currency,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, 'finance/expense_print.html', context)


def finance_dashboard_print(request):
    incomes = Income.objects.select_related('source').all().order_by('-date', '-id')
    expenses = Expense.objects.select_related('category').all().order_by('-date', '-id')

    total_income_afn = Income.objects.filter(currency='AFN').aggregate(
        total=Coalesce(Sum('amount'), Decimal('0.00'))
    )['total']

    total_expense_afn = Expense.objects.filter(currency='AFN').aggregate(
        total=Coalesce(Sum('amount'), Decimal('0.00'))
    )['total']

    balance_afn = total_income_afn - total_expense_afn

    total_income_usd = Income.objects.filter(currency='USD').aggregate(
        total=Coalesce(Sum('amount'), Decimal('0.00'))
    )['total']

    total_expense_usd = Expense.objects.filter(currency='USD').aggregate(
        total=Coalesce(Sum('amount'), Decimal('0.00'))
    )['total']

    balance_usd = total_income_usd - total_expense_usd

    latest_incomes = incomes[:10]
    latest_expenses = expenses[:10]

    if balance_afn > 0:
        afn_status_text = 'You are in profit (AFN)'
    elif balance_afn < 0:
        afn_status_text = 'You are in loss (AFN)'
    else:
        afn_status_text = 'Income and expense are equal (AFN)'

    if balance_usd > 0:
        usd_status_text = 'You are in profit (USD)'
    elif balance_usd < 0:
        usd_status_text = 'You are in loss (USD)'
    else:
        usd_status_text = 'Income and expense are equal (USD)'

    context = {
        'total_income_afn': total_income_afn,
        'total_expense_afn': total_expense_afn,
        'balance_afn': balance_afn,

        'total_income_usd': total_income_usd,
        'total_expense_usd': total_expense_usd,
        'balance_usd': balance_usd,

        'latest_incomes': latest_incomes,
        'latest_expenses': latest_expenses,

        'afn_status_text': afn_status_text,
        'usd_status_text': usd_status_text,
    }
    return render(request, 'finance/dashboard_print.html', context)