from django.shortcuts import render

# Create your views here.

def add_income(request):
    return render(request, 'finance/income.html')