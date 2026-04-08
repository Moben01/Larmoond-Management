from django import forms
from django.core.exceptions import ValidationError
from .models import Customer, CustomerNote

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