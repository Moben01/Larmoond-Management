from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(EmployeePayrollLine)
admin.site.register(EmployeeBalance)
admin.site.register(EmployeeBalanceLedger)
admin.site.register(EmployeeSalaryPayment)
