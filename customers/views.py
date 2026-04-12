from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import HttpResponse
from .models import Customer, CustomerNote, CustomerActivity
from .models import *
from .forms import CustomerForm, CustomerSearchForm, CustomerNoteForm
from .forms import *
import csv


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
    
    # Statistics
    total_customers = customers.count()
    active_customers = customers.filter(status='active').count()
    total_revenue = customers.aggregate(total=Sum('total_spent'))['total'] or 0
    
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'customers': page_obj,
        'form': form,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'total_revenue': total_revenue,
    }
    return render(request, 'customers/customer_list.html', context)


def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    notes = customer.customer_notes.all()[:5]
    activities = customer.activities.all()[:10]
    
    context = {
        'customer': customer,
        'notes': notes,
        'activities': activities,
    }
    return render(request, 'customers/customer_detail.html', context)


def customer_create(request):
    print("=" * 50)
    print("CUSTOMER CREATE VIEW CALLED")
    print(f"Request Method: {request.method}")
    print("=" * 50)
    
    if request.method == 'POST':
        print("\n--- PROCESSING POST REQUEST ---")
        print(f"POST Data: {request.POST}")
        
        form = CustomerForm(request.POST, request.FILES)
        
        print("\n--- FORM DEBUG ---")
        print(f"Is form bound: {form.is_bound}")
        print(f"Form fields: {form.fields.keys()}")
        print(f"Submitted data keys: {list(request.POST.keys())}")
        
        # Check each required field
        required_fields = ['first_name', 'email', 'phone']
        for field in required_fields:
            if field in request.POST:
                print(f"✓ {field}: {request.POST.get(field)}")
            else:
                print(f"✗ {field}: MISSING from POST data")
        
        if form.is_valid():
            print("\n✓ FORM IS VALID ✓")
            print("Cleaned data:")
            for field, value in form.cleaned_data.items():
                print(f"  {field}: {value}")
            
            try:
                customer = form.save()
                
                print(f"\n✓ Customer saved successfully!")
                print(f"  Customer ID: {customer.customer_id}")
                print(f"  Customer Name: {customer.get_full_name()}")
                
                # Log activity (removed created_by user reference)
                CustomerActivity.objects.create(
                    customer=customer,
                    activity_type='note',
                    description=f'Customer created successfully'
                )
                
                print(f"✓ Activity logged")
                messages.success(request, f'Customer {customer.customer_id} created successfully!')
                print(f"✓ Redirecting to customer list")
                return redirect('customers:customer_list')
                
            except Exception as e:
                print(f"\n✗ ERROR SAVING CUSTOMER: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.error(request, f'Error saving customer: {str(e)}')
        else:
            print("\n✗ FORM IS INVALID ✗")
            print("Form errors:")
            for field, errors in form.errors.items():
                print(f"  {field}: {', '.join(errors)}")
            
            messages.error(request, 'Please correct the errors below.')
    else:
        print("\n--- GET REQUEST ---")
        print("Returning empty form")
        form = CustomerForm()
    
    print("\n--- RENDERING FORM TEMPLATE ---")
    print(f"Template: customers/customer_form.html")
    print(f"Title: Add New Contact")
    print("=" * 50)
    
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Add New Contact'})


def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer {customer.customer_id} updated successfully!')
            return redirect('customers:customer_list')
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Edit Contact', 'customer': customer})


def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer_id = customer.customer_id
        customer_name = customer.get_full_name()
        customer.delete()
        messages.success(request, f'Customer {customer_id} - {customer_name} deleted successfully!')
        return redirect('customers:customer_list')
    
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})


def add_note(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerNoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.customer = customer
            note.save()
            
            messages.success(request, 'Note added successfully!')
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerNoteForm()
    
    return render(request, 'customers/add_note.html', {'form': form, 'customer': customer})


def toggle_status(request, pk):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, pk=pk)
        old_status = customer.status
        customer.status = 'inactive' if customer.status == 'active' else 'active'
        customer.save()
        
        CustomerActivity.objects.create(
            customer=customer,
            activity_type='status_change',
            description=f'Status changed from {old_status} to {customer.status}'
        )
        
        messages.success(request, f'Customer status updated to {customer.get_status_display()}')
        return redirect('customers:customer_detail', pk=customer.pk)
    
    return redirect('customers:customer_list')


def export_customers(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Customer ID', 'Name', 'Email', 'Phone', 'Country', 'Status', 'Total Spent'])
    
    customers = Customer.objects.all()
    for customer in customers:
        writer.writerow([
            customer.customer_id,
            customer.get_full_name(),
            customer.email,
            customer.phone,
            customer.country,
            customer.get_status_display(),
            str(customer.total_spent),
        ])
    
    return response








# Add these views to your existing customers/views.py

def project_list(request):
    projects = Project.objects.all()
    form = ProjectSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        customer = form.cleaned_data.get('customer')
        
        if search:
            projects = projects.filter(
                Q(project_name__icontains=search) |
                Q(project_id__icontains=search)
            )
        if status:
            projects = projects.filter(status=status)
        if priority:
            projects = projects.filter(priority=priority)
        if customer:
            projects = projects.filter(customer=customer)
    
    total_projects = projects.count()
    active_projects = projects.filter(status='in_progress').count()
    completed_projects = projects.filter(status='completed').count()
    total_revenue = projects.aggregate(total=Sum('paid_amount'))['total'] or 0
    
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'projects': page_obj,
        'form': form,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_revenue': total_revenue,
    }
    return render(request, 'customers/project_list.html', context)


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    payments = project.payments.all()
    
    context = {
        'project': project,
        'payments': payments,
    }
    return render(request, 'customers/project_detail.html', context)


def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Project {project.project_id} created successfully!')
            return redirect('customers:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'customers/project_form.html', {'form': form, 'title': 'Create New Project'})


def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project {project.project_id} updated successfully!')
            return redirect('customers:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'customers/project_form.html', {'form': form, 'title': 'Edit Project', 'project': project})


def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        project_id = project.project_id
        project.delete()
        messages.success(request, f'Project {project_id} deleted successfully!')
        return redirect('customers:project_list')
    
    return render(request, 'customers/project_confirm_delete.html', {'project': project})


def add_payment(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.project = project
            payment.save()
            messages.success(request, f'Payment of ${payment.amount} added successfully!')
            return redirect('customers:project_detail', pk=project.pk)
    else:
        form = PaymentForm(initial={'payment_date': timezone.now().date()})
    
    return render(request, 'customers/add_payment.html', {'form': form, 'project': project})