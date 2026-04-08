from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
import uuid

class Customer(models.Model):
    # Customer Type Choices
    CUSTOMER_TYPE = [
        ('individual', 'Individual'),
        ('business', 'Business'),
        ('government', 'Government'),
        ('non_profit', 'Non-Profit Organization'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('suspended', 'Suspended'),
    ]
    
    # Basic Information
    customer_id = models.CharField(max_length=50, unique=True, editable=False)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE, default='individual')
    salutation = models.CharField(max_length=10, choices=[
        ('mr', 'Mr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('dr', 'Dr.'), ('company', 'Company')
    ], blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Contact Information
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, validators=[RegexValidator(r'^\+?[\d\s-]+$')])
    mobile = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Business Information (Optional)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tax ID/VAT")
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Address Information (Flexible)
    address_line1 = models.TextField()
    address_line2 = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)  # User will enter any country
    
    # Shipping Address (Optional)
    shipping_address_same = models.BooleanField(default=True)
    shipping_address_line1 = models.TextField(blank=True, null=True)
    shipping_address_line2 = models.TextField(blank=True, null=True)
    shipping_city = models.CharField(max_length=100, blank=True, null=True)
    shipping_state = models.CharField(max_length=100, blank=True, null=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True, null=True)
    shipping_country = models.CharField(max_length=100, blank=True, null=True)
    
    # Financial Information
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    payment_terms_days = models.IntegerField(default=30)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_exempt = models.BooleanField(default=False)
    tax_exemption_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Account Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    
    # Business Metrics
    registration_date = models.DateTimeField(auto_now_add=True)
    last_activity_date = models.DateTimeField(auto_now=True)
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    last_order_date = models.DateTimeField(blank=True, null=True)
    
    # Preferences
    preferred_contact_method = models.CharField(max_length=20, choices=[
        ('email', 'Email'), ('phone', 'Phone'), ('whatsapp', 'WhatsApp')
    ], default='email')
    send_notifications = models.BooleanField(default=True)
    send_promotions = models.BooleanField(default=False)
    
    # Internal Notes
    notes = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)  # Staff only
    
    # Audit Fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_customers')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['status']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['company_name']),
        ]
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        if self.company_name:
            return f"{self.customer_id} - {self.company_name}"
        return f"{self.customer_id} - {self.first_name} {self.last_name or ''}"
    
    def save(self, *args, **kwargs):
        if not self.customer_id:
            # Generate unique customer ID: CUST-20240001 format
            current_year = timezone.now().year
            last_customer = Customer.objects.filter(
                customer_id__startswith=f'CUST-{current_year}'
            ).order_by('-customer_id').first()
            
            if last_customer:
                last_number = int(last_customer.customer_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.customer_id = f'CUST-{current_year}-{str(new_number).zfill(6)}'
        
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def get_full_address(self):
        address = f"{self.address_line1}"
        if self.address_line2:
            address += f", {self.address_line2}"
        address += f", {self.city}"
        if self.state_province:
            address += f", {self.state_province}"
        address += f" - {self.postal_code}, {self.country}"
        return address


class CustomerInteraction(models.Model):
    """Track all interactions with customers"""
    INTERACTION_TYPES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('support', 'Support Ticket'),
        ('complaint', 'Complaint'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    interaction_date = models.DateTimeField(default=timezone.now)
    follow_up_date = models.DateField(blank=True, null=True)
    follow_up_completed = models.BooleanField(default=False)
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-interaction_date']
        verbose_name = 'Customer Interaction'
        verbose_name_plural = 'Customer Interactions'
    
    def __str__(self):
        return f"{self.customer} - {self.interaction_type} - {self.interaction_date}"