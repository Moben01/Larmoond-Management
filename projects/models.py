from django.db import models
from django.contrib.auth.models import User
from customers.models import Customer


class Project(models.Model):
    STATUS_CHOICES = [
        ('draft', 'draft'),
        ('pending', 'pending'),
        ('in_progress', 'in_progress'),
        ('on_hold', 'on_hold'),
        ('completed', 'completed'),
        ('cancelled', 'cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'low'),
        ('medium', 'medium'),
        ('high', 'high'),
        ('urgent', 'urgent'),
    ]

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, editable=False)
    client = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    project_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects'
    )
    team_members = models.ManyToManyField(User, blank=True, related_name='project_memberships')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_project_code(self):
        last_project = Project.objects.order_by('-id').first()
        next_id = 1 if not last_project else last_project.id + 1
        return f"PRJ-{next_id:04d}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_project_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    
class ProjectTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_project_tasks'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_project_tasks'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    start_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.title} - {self.project.name}"