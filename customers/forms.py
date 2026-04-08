from django import forms
from django.core.exceptions import ValidationError
from .models import Customer, CustomerInteraction
import re

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'customer_type', 'salutation', 'first_name', 'last_name',
            'email', 'phone', 'mobile', 'fax', 'website',
            'company_name', 'tax_id', 'registration_number',
            'address_line1', 'address_line2', 'city', 'state_province',
            'postal_code', 'country',
            'shipping_address_same', 'shipping_address_line1', 'shipping_address_line2',
            'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country',
            'credit_limit', 'payment_terms_days', 'discount_percentage',
            'tax_exempt', 'tax_exemption_number',
            'preferred_contact_method', 'send_notifications', 'send_promotions',
            'notes'
        ]
        widgets = {
            'address_line1': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'address_line2': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'shipping_address_line1': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'shipping_address_line2': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Customer.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('A customer with this email already exists.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and Customer.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise ValidationError('A customer with this phone number already exists.')
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        shipping_same = cleaned_data.get('shipping_address_same')
        
        if not shipping_same:
            required_shipping_fields = [
                'shipping_address_line1', 'shipping_city', 'shipping_postal_code', 'shipping_country'
            ]
            for field in required_shipping_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'This field is required when shipping address is different.')
        
        return cleaned_data


class CustomerSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search by name, email, phone, or customer ID...'
    }))
    status = forms.ChoiceField(required=False, choices=[('', 'All Status')] + Customer.STATUS_CHOICES)
    customer_type = forms.ChoiceField(required=False, choices=[('', 'All Types')] + Customer.CUSTOMER_TYPE)
    country = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Country'
    }))


class CustomerInteractionForm(forms.ModelForm):
    class Meta:
        model = CustomerInteraction
        fields = ['interaction_type', 'subject', 'description', 'follow_up_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }