from django.urls import path
from . import views

app_name = 'employee'

urlpatterns = [
    path('employee_create/', views.employee_create, name='employee_create'),
    path('update/<int:employee_id>/', views.employee_update, name='employee_update'),
    path('delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('employee_detail/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employee/<int:employee_id>/leave-absence/', views.leave_absence_create, name='leave_absence_create'),
    path('leave-absence/<int:record_id>/update/', views.leave_absence_update, name='leave_absence_update'),
    path('leave-absence/<int:record_id>/delete/', views.leave_absence_delete, name='leave_absence_delete'),

    path('payroll/create/', views.create_monthly_payroll, name='create_monthly_payroll'),
    path('payroll/<int:payroll_id>/', views.payroll_detail, name='payroll_detail'),
    path('delete_payroll/<int:payroll_id>/', views.delete_monthly_payroll, name='delete_monthly_payroll'),

    path('employee/<int:employee_id>/salary-payment/create/', views.employee_salary_payment_create, name='employee_salary_payment_create'),
    path('salary-payment/<int:payment_id>/delete/',views.employee_salary_payment_delete,name='employee_salary_payment_delete'
),
]