from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone

class Customer(models.Model):
    # Customer Type Choices
    CUSTOMER_TYPE = [
        ('individual', 'Individual'),
        ('business', 'Business'),
        ('government', 'Government'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]
    
    # Basic Information
    customer_id = models.CharField(max_length=50, unique=True, editable=False)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE, default='individual')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    
    # Business Information
    company_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Address Information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    
    # Financial Information
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Tags
    tags = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated tags")
    
    # Owner
   
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Business Metrics
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Comments (renamed from 'notes' to avoid conflict)
    comments = models.TextField(blank=True, null=True)
    
    # Audit Fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        if self.company_name:
            return f"{self.customer_id} - {self.company_name}"
        return f"{self.customer_id} - {self.first_name} {self.last_name or ''}"
    
    def save(self, *args, **kwargs):
        if not self.customer_id:
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
    
    def get_tag_list(self):
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []


class CustomerNote(models.Model):
    # Changed related_name to 'customer_notes' to avoid conflict with Customer.notes field
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_notes')
    title = models.CharField(max_length=200)
    note = models.TextField()
    attachment = models.FileField(upload_to='customer_notes/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class CustomerActivity(models.Model):
    ACTIVITY_TYPES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note Added'),
        ('status_change', 'Status Change'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)