from django.db import models


class Expense(models.Model):
    CATEGORY_CHOICES = (
        ('salary', 'Salary'),
        ('rent', 'Rent'),
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('electricity', 'Electricity'),
        ('internet', 'Internet'),
        ('other', 'Other'),
    )

    CURRENCY_CHOICES = (
        ('AFN', 'Afghani'),
        ('USD', 'US Dollar'),
    )

    title = models.CharField(max_length=200, verbose_name='Title')
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='Category'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Amount')

    currency = models.CharField(   # 👈 نوی فیلډ
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='AFN',
        verbose_name='Currency'
    )

    date = models.DateField(verbose_name='Date')
    note = models.TextField(blank=True, null=True, verbose_name='Note')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.title} - {self.amount} {self.currency}"


class Income(models.Model):
    SOURCE_CHOICES = (
        ('project', 'Project'),
        ('business', 'Business'),
        ('sale', 'Sale'),
        ('service', 'Service'),
        ('other', 'Other'),
    )

    CURRENCY_CHOICES = (
        ('AFN', 'Afghani'),
        ('USD', 'US Dollar'),
    )

    title = models.CharField(max_length=200, verbose_name='Title')
    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES,
        verbose_name='Source'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Amount')

    currency = models.CharField(   # 👈 نوی فیلډ
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='AFN',
        verbose_name='Currency'
    )

    date = models.DateField(verbose_name='Date')
    note = models.TextField(blank=True, null=True, verbose_name='Note')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Income'
        verbose_name_plural = 'Income'
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.title} - {self.amount} {self.currency}"