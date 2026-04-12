from django import forms
from django.core.exceptions import ValidationError
from .models import Customer, CustomerNote
from .models import *

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'customer_type', 'first_name', 'last_name', 'email', 'phone',
            'company_name', 'address', 'city', 'state', 'pincode', 'country',
            'credit_limit', 'tags','status', 'comments'  # Changed from 'notes' to 'comments'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Street address'}),
            'comments': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any additional notes...'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter tags separated by commas'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ != 'CheckboxInput':
                field.widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Customer.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('A customer with this email already exists.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and Customer.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise ValidationError('A customer with this phone number already exists.')
        return phone


class CustomerNoteForm(forms.ModelForm):
    class Meta:
        model = CustomerNote
        fields = ['title', 'note', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CustomerSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search by name, email, or phone...'
    }))
    status = forms.ChoiceField(required=False, choices=[('', 'All Status')] + Customer.STATUS_CHOICES)
    customer_type = forms.ChoiceField(required=False, choices=[('', 'All Types')] + Customer.CUSTOMER_TYPE)
    country = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Country'
    }))




class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'project_name', 'customer', 'description',
            'total_price', 'paid_amount', 'start_date', 'end_date',
            'status', 'priority', 'progress_percentage', 'notes'
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project name'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Project description'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'progress_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Additional notes'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ not in ['Select', 'Textarea']:
                field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        total_price = cleaned_data.get('total_price', 0)
        paid_amount = cleaned_data.get('paid_amount', 0)
        
        if paid_amount > total_price:
            raise ValidationError('Paid amount cannot be greater than total price.')
        
        return cleaned_data


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_date', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction ID / Check Number'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Payment notes'}),
        }


class ProjectSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search by project name or ID...'
    }))
    status = forms.ChoiceField(required=False, choices=[('', 'All Status')] + Project.STATUS_CHOICES)
    priority = forms.ChoiceField(required=False, choices=[('', 'All Priority')] + Project.PRIORITY_CHOICES)
    customer = forms.ModelChoiceField(required=False, queryset=Customer.objects.all(), empty_label="All Customers")