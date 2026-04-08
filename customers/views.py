from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Customer, CustomerInteraction
from .forms import CustomerForm, CustomerSearchForm, CustomerInteractionForm


def customer_list(request):
    customers = Customer.objects.all()
    form = CustomerSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        customer_type = form.cleaned_data.get('customer_type')
        country = form.cleaned_data.get('country')
        
        if search:
            customers = customers.filter(
                Q(customer_id__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(company_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        if status:
            customers = customers.filter(status=status)
        
        if customer_type:
            customers = customers.filter(customer_type=customer_type)
        
        if country:
            customers = customers.filter(country__icontains=country)
    
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'customers': page_obj,
        'form': form,
        'total_customers': customers.count(),
        'active_customers': customers.filter(status='active').count(),
    }
    return render(request, 'customers/customer_list.html', context)



def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    interactions = customer.interactions.all()[:10]
    
    context = {
        'customer': customer,
        'interactions': interactions,
    }
    return render(request, 'customers/customer_detail.html', context)



def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()
            messages.success(request, f'Customer {customer.customer_id} created successfully!')
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Create Customer'})



def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_by = request.user
            customer.save()
            messages.success(request, f'Customer {customer.customer_id} updated successfully!')
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Edit Customer', 'customer': customer})



def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer_id = customer.customer_id
        customer.delete()
        messages.success(request, f'Customer {customer_id} deleted successfully!')
        return redirect('customers:customer_list')
    
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})



def add_interaction(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk)
    
    if request.method == 'POST':
        form = CustomerInteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.customer = customer
            interaction.handled_by = request.user
            interaction.save()
            messages.success(request, 'Interaction recorded successfully!')
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerInteractionForm()
    
    return render(request, 'customers/add_interaction.html', {'form': form, 'customer': customer})



def toggle_customer_status(request, pk):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, pk=pk)
        if customer.status == 'active':
            customer.status = 'inactive'
        else:
            customer.status = 'active'
        customer.save()
        messages.success(request, f'Customer status updated to {customer.get_status_display()}')
        return redirect('customers:customer_detail', pk=customer.pk)
    
    return redirect('customers:customer_list')