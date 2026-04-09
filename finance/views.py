from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import IncomeForm, ExpenceForm
from .models import Income, Expense
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q, Sum

# === د عاید لیدونه ===


def income_list(request):
    incomes = Income.objects.all().order_by('-date', '-id')

    # filters
    search = request.GET.get('search')
    source = request.GET.get('source')
    currency = request.GET.get('currency')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if search:
        incomes = incomes.filter(title__icontains=search)

    if source:
        incomes = incomes.filter(source=source)

    if currency:
        incomes = incomes.filter(currency=currency)

    if from_date:
        incomes = incomes.filter(date__gte=from_date)

    if to_date:
        incomes = incomes.filter(date__lte=to_date)

    total_afn = incomes.filter(currency='AFN').aggregate(total=Sum('amount'))['total'] or 0
    total_usd = incomes.filter(currency='USD').aggregate(total=Sum('amount'))['total'] or 0

    # 🔥 AJAX response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('finance/search_income.html', {'incomes': incomes})
        return JsonResponse({'html': html})

    return render(request, 'finance/income_list.html', {
        'incomes': incomes,
        'total_afn': total_afn,
        'total_usd': total_usd,
    })


def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'عاید په بریالیتوب سره ثبت شو!')
            return redirect('finance/income_list')
    else:
        form = IncomeForm()
    return render(request, 'finance/income_form.html', {'form': form, 'title': 'نوی عاید'})

def income_update(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'عاید په بریالیتوب سره سم شو!')
            return redirect('finance:income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'finance/income_edit_form.html', {'form': form, 'title': 'عاید سمول'})

def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk)
    income.delete()
    return redirect('finance:income_list')



# === د لګښت لیدونه ===
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Sum

def expense_list(request):
    expenses = Expense.objects.all().order_by('-date', '-id')

    search = request.GET.get('search')
    category = request.GET.get('category')
    currency = request.GET.get('currency')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if search:
        expenses = expenses.filter(title__icontains=search)

    if category:
        expenses = expenses.filter(category=category)

    if currency:
        expenses = expenses.filter(currency=currency)

    if from_date:
        expenses = expenses.filter(date__gte=from_date)

    if to_date:
        expenses = expenses.filter(date__lte=to_date)

    total_afn = expenses.filter(currency='AFN').aggregate(total=Sum('amount'))['total'] or 0
    total_usd = expenses.filter(currency='USD').aggregate(total=Sum('amount'))['total'] or 0

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('finance/search_expense.html', {'expenses': expenses}, request=request)
        return JsonResponse({
            'html': html,
            'total_afn': str(total_afn),
            'total_usd': str(total_usd),
        })

    return render(request, 'finance/expense_list.html', {
        'expenses': expenses,
        'total_afn': total_afn,
        'total_usd': total_usd,
    })


def expense_create(request):
    if request.method == 'POST':
        form = ExpenceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'لګښت په بریالیتوب سره ثبت شو!')
            return redirect('finance:expense_list')
    else:
        form = ExpenceForm()
    return render(request, 'finance/expense_form.html', {'form': form, 'title': 'نوی لګښت'})

def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenceForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'لګښت په بریالیتوب سره سم شو!')
            return redirect('finance:expense_list')
    else:
        form = ExpenceForm(instance=expense)
    return render(request, 'finance/expense_edit_form.html', {'form': form, 'title': 'لګښت سمول'})

def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()
    return redirect('finance:expense_list')

# === ډشبورډ (د خپلواک لید) ===
def dashboard(request):
    # وروستي 5 عایدونه او لګښتونه
    recent_incomes = Income.objects.all()[:5]
    recent_expenses = Expense.objects.all()[:5]
    
    # مجموعي عاید او لګښت په بیلابیلو اسعارو
    total_income_afn = sum(i.amount for i in Income.objects.filter(currency='AFN'))
    total_income_usd = sum(i.amount for i in Income.objects.filter(currency='USD'))
    total_expense_afn = sum(e.amount for e in Expense.objects.filter(currency='AFN'))
    total_expense_usd = sum(e.amount for e in Expense.objects.filter(currency='USD'))
    
    # خالص عاید (په هر اسعار کې جلا)
    net_afn = total_income_afn - total_expense_afn
    net_usd = total_income_usd - total_expense_usd
    
    context = {
        'recent_incomes': recent_incomes,
        'recent_expenses': recent_expenses,
        'total_income_afn': total_income_afn,
        'total_income_usd': total_income_usd,
        'total_expense_afn': total_expense_afn,
        'total_expense_usd': total_expense_usd,
        'net_afn': net_afn,
        'net_usd': net_usd,
    }
    return render(request, 'dashboard.html', context)