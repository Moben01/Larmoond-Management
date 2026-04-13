from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal


class Employee(models.Model):

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    ROLE_CHOICES = [
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('manager', 'Manager'),
        ('qa', 'QA'),
        ('hr', 'HR'),
        ('other', 'Other'),
    ]

    # 🔹 معلومات شخصی
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

    # 🔹 معلومات کاری
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='developer')
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    join_date = models.DateField(blank=True, null=True)

    # 🔹 عکس
    image = models.ImageField(upload_to='employees/', blank=True, null=True)

    # 🔹 وضعیت
    is_active = models.BooleanField(default=True)

    # 🔹 timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name()


class EmployeeLeaveAbsence(models.Model):
    RECORD_TYPE_CHOICES = [
        ('leave', 'leave'),
        ('absent', 'absent'),
    ]

    UNIT_CHOICES = [
        ('day', 'day'),
        ('hour', 'hour'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_absence_records'
    )

    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPE_CHOICES,
        verbose_name='نوع ثبت'
    )

    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default='day',
        verbose_name='نوع مقدار'
    )

    from_date = models.DateField(verbose_name='از تاریخ')
    to_date = models.DateField(verbose_name='تا تاریخ', blank=True, null=True)

    hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='ساعت'
    )

    reason = models.TextField(blank=True, null=True, verbose_name='دلیل')

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_employee_leaves'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-from_date', '-id']

    def __str__(self):
        return f"{self.employee} - {self.get_record_type_display()}"

    def clean(self):
        if self.unit == 'day':
            if not self.to_date:
                self.to_date = self.from_date

            if self.to_date < self.from_date:
                raise ValidationError("تا تاریخ نمی‌تواند از تاریخ شروع کوچکتر باشد")

            if self.hours:
                raise ValidationError("برای ثبت روزانه، فیلد ساعت باید خالی باشد")

        elif self.unit == 'hour':
            if not self.hours or self.hours <= 0:
                raise ValidationError("برای ثبت ساعتی باید مقدار ساعت وارد شود")

            if self.hours > Decimal('8'):
                raise ValidationError("مقدار ساعت نمی‌تواند بیشتر از 8 باشد")

            self.to_date = self.from_date

    @property
    def number_of_days(self):
        if self.unit == 'day':
            end_date = self.to_date or self.from_date
            return (end_date - self.from_date).days + 1
        return Decimal(self.hours or 0) / Decimal('8')

    @property
    def number_of_hours(self):
        if self.unit == 'hour':
            return self.hours or Decimal('0')
        return Decimal(self.number_of_days) * Decimal('8')
    

class EmployeeBalance(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='balance'
    )

    company_payable_to_employee = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    employee_payable_to_company = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee}"

    @property
    def net_balance(self):
        """
        اگر مثبت باشد یعنی شرکت به کارمند بدهکار است
        اگر منفی باشد یعنی کارمند به شرکت بدهکار است
        """
        return self.company_payable_to_employee - self.employee_payable_to_company

    @property
    def balance_status(self):
        if self.company_payable_to_employee > self.employee_payable_to_company:
            return "Company owes employee"
        elif self.employee_payable_to_company > self.company_payable_to_employee:
            return "Employee owes company"
        return "Settled"


class EmployeePayroll(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('year', 'month')
        ordering = ['-year', '-month', '-id']

    def __str__(self):
        return f"Payroll {self.year}-{self.month}"
    

class EmployeePayrollLine(models.Model):
    payroll = models.ForeignKey(
        EmployeePayroll,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payroll_lines'
    )

    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    total_leave_days = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_absent_days = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    allowed_paid_leave_days = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    extra_leave_days = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    daily_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    leave_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    absent_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_posted_to_balance = models.BooleanField(default=False)
    posted_balance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('payroll', 'employee')
        ordering = ['employee__first_name']

    def __str__(self):
        return f"{self.employee} - {self.payroll}"
        

class EmployeeSalaryPayment(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='salary_payments'
    )

    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.amount}"
    

class EmployeeBalanceLedger(models.Model):
    ENTRY_TYPE_CHOICES = [
        ('payroll', 'Payroll'),
        ('salary_payment', 'Salary Payment'),
        ('adjustment_add_company_debt', 'Adjustment Add Company Debt'),
        ('adjustment_add_employee_debt', 'Adjustment Add Employee Debt'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='balance_ledger')
    entry_type = models.CharField(max_length=50, choices=ENTRY_TYPE_CHOICES)

    payroll_line = models.ForeignKey(
        'EmployeePayrollLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ledger_entries'
    )
    salary_payment = models.ForeignKey(
        'EmployeeSalaryPayment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ledger_entries'
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    company_payable_before = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    company_payable_after = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    employee_payable_before = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    employee_payable_after = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)