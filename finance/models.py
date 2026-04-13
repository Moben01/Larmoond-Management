from django.db import models


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Category Name')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Expense Category'
        verbose_name_plural = 'Expense Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class IncomeSource(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Source Name')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Income Source'
        verbose_name_plural = 'Income Sources'
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    CURRENCY_CHOICES = (
        ('AFN', 'Afghani'),
        ('USD', 'US Dollar'),
    )

    title = models.CharField(max_length=200, verbose_name='Title')
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        verbose_name='Category'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Amount')
    currency = models.CharField(
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
    CURRENCY_CHOICES = (
        ('AFN', 'Afghani'),
        ('USD', 'US Dollar'),
    )

    title = models.CharField(max_length=200, verbose_name='Title')
    source = models.ForeignKey(
        IncomeSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incomes',
        verbose_name='Source'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Amount')
    currency = models.CharField(
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