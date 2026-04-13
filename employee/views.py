from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from home.models import *
from django.db import transaction
from itertools import chain
from django.db.models import Sum


def employee_create(request):
    employee_records = Employee.objects.all().order_by('-id')

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee added successfully 👤")
            return redirect('employee:employee_create')
        else:
            messages.error(request, "Failed to add employee ❌")
    else:
        form = EmployeeForm()

    context = {
        'employee_form': form,
        'employee_records': employee_records
    }

    return render(request, 'employee/employee_form.html', context)


def employee_update(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee updated successfully ✏️")
        else:
            messages.error(request, "Failed to update employee ❌")

    return redirect('employee:employee_create')


def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        employee_name = f"{employee.first_name} {employee.last_name}".strip()
        employee.delete()
        messages.success(request, f"Employee '{employee_name}' deleted successfully 🗑️")
    else:
        messages.warning(request, "Invalid delete request ⚠️")

    return redirect('employee:employee_create')


def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    employee_balance, _ = EmployeeBalance.objects.get_or_create(employee=employee)

    assigned_projects = employee.assigned_projects.all()
    all_projects = assigned_projects.distinct().order_by('-created_at')

    total_projects = all_projects.count()
    active_projects = all_projects.filter(status='in_progress').count()
    completed_projects = all_projects.filter(status='completed').count()

    payroll_records = EmployeePayrollLine.objects.filter(
        employee=employee
    ).select_related('payroll').order_by('-payroll__date', '-id')

    payment_records = EmployeeSalaryPayment.objects.filter(
        employee=employee
    ).order_by('-date', '-id')

    # ✅ full ledger for modal
    full_ledger_records = EmployeeBalanceLedger.objects.filter(
        employee=employee
    ).order_by('-created_at', '-id')

    payment_form = EmployeeSalaryPaymentForm()

    combined_earnings = sorted(
        chain(payroll_records, payment_records),
        key=lambda x: x.created_at,
        reverse=True
    )

    chart_months = []
    chart_net_salaries = []
    chart_base_salaries = []
    chart_deductions = []

    for record in payroll_records.order_by('payroll__date', 'id'):
        chart_months.append(f"{record.payroll.month}/{record.payroll.year}")
        chart_net_salaries.append(float(record.net_salary))
        chart_base_salaries.append(float(record.base_salary))
        chart_deductions.append(float(record.total_deduction))

    context = {
        'employee': employee,
        'projects': all_projects,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'employee_balance': employee_balance,
        'payroll_records': payroll_records,
        'payment_records': payment_records,
        'payment_form': payment_form,
        'combined_earnings': combined_earnings,
        'full_ledger_records': full_ledger_records,   # ✅ مهم
        'chart_months': chart_months,
        'chart_net_salaries': chart_net_salaries,
        'chart_base_salaries': chart_base_salaries,
        'chart_deductions': chart_deductions,
    }
    return render(request, 'employee/employee_detail.html', context)


def leave_absence_create(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    records = EmployeeLeaveAbsence.objects.filter(employee=employee).order_by('-from_date', '-id')

    if request.method == 'POST':
        form = EmployeeLeaveAbsenceForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.employee = employee
            record.save()
            messages.success(request, "ریکارد رخصتی/غیرحاضری موفقانه ثبت شد ✅")
            return redirect('employee:leave_absence_create', employee_id=employee.id)
        else:
            messages.error(request, "در ثبت ریکارد مشکل پیش آمد ❌")
    else:
        form = EmployeeLeaveAbsenceForm()

    context = {
        'form': form,
        'records': records,
        'employee': employee,
    }
    return render(request, 'employee/leave_absence_form.html', context)


def leave_absence_update(request, record_id):
    record = get_object_or_404(EmployeeLeaveAbsence, id=record_id)

    if request.method == 'POST':
        form = EmployeeLeaveAbsenceForm(request.POST, instance=record)
        if form.is_valid():
            updated = form.save(commit=False)
            if request.user.is_authenticated and updated.status == 'approved':
                updated.approved_by = request.user
            updated.save()
            messages.success(request, "ریکارد موفقانه ایدیت شد ✏️")
        else:
            messages.error(request, "در ایدیت ریکارد مشکل پیش آمد ❌")

    return redirect('employee:leave_absence_create', employee_id=record.employee.id)


def leave_absence_delete(request, record_id):
    record = get_object_or_404(EmployeeLeaveAbsence, id=record_id)
    employee_id = record.employee.id

    if request.method == 'POST':
        record.delete()
        messages.success(request, "ریکارد موفقانه حذف شد 🗑️")
    else:
        messages.warning(request, "درخواست حذف نادرست است ⚠️")

    return redirect('employee:leave_absence_create', employee_id=employee_id)



def get_employee_leave_summary_for_payroll(employee, year, month):
    qs = EmployeeLeaveAbsence.objects.filter(
        employee=employee,
        from_date__year=year,
        from_date__month=month,
    )

    total_leave_days = Decimal('0')
    total_absent_days = Decimal('0')

    for rec in qs:
        days = Decimal(str(rec.number_of_days))
        if rec.record_type == 'leave':
            total_leave_days += days
        elif rec.record_type == 'absent':
            total_absent_days += days

    return {
        'total_leave_days': total_leave_days,
        'total_absent_days': total_absent_days,
    }


def build_employee_payroll_line(employee, payroll):
    setting = AttendanceSetting.objects.first()
    allowed_paid_leave_days = Decimal(
        str(setting.allowed_paid_leave_days_per_month if setting else 2)
    )

    summary = get_employee_leave_summary_for_payroll(employee, payroll.year, payroll.month)

    total_leave_days = Decimal(str(summary['total_leave_days']))
    total_absent_days = Decimal(str(summary['total_absent_days']))

    extra_leave_days = total_leave_days - allowed_paid_leave_days
    if extra_leave_days < 0:
        extra_leave_days = Decimal('0')

    base_salary = Decimal(str(employee.salary or 0))
    daily_salary = base_salary / Decimal('30')

    leave_deduction = extra_leave_days * daily_salary
    absent_deduction = total_absent_days * daily_salary
    total_deduction = leave_deduction + absent_deduction

    net_salary = base_salary - total_deduction
    if net_salary < 0:
        net_salary = Decimal('0')

    line, created = EmployeePayrollLine.objects.get_or_create(
        payroll=payroll,
        employee=employee,
        defaults={
            'base_salary': base_salary,
            'total_leave_days': total_leave_days,
            'total_absent_days': total_absent_days,
            'allowed_paid_leave_days': allowed_paid_leave_days,
            'extra_leave_days': extra_leave_days,
            'daily_salary': daily_salary,
            'leave_deduction': leave_deduction,
            'absent_deduction': absent_deduction,
            'total_deduction': total_deduction,
            'net_salary': net_salary,
        }
    )

    if not created:
        line.base_salary = base_salary
        line.total_leave_days = total_leave_days
        line.total_absent_days = total_absent_days
        line.allowed_paid_leave_days = allowed_paid_leave_days
        line.extra_leave_days = extra_leave_days
        line.daily_salary = daily_salary
        line.leave_deduction = leave_deduction
        line.absent_deduction = absent_deduction
        line.total_deduction = total_deduction
        line.net_salary = net_salary
        line.save()

    return line


def post_payroll_line_to_balance(line):
    if not line:
        return

    balance, _ = EmployeeBalance.objects.get_or_create(employee=line.employee)

    company_before = Decimal(str(balance.company_payable_to_employee or 0))
    employee_before = Decimal(str(balance.employee_payable_to_company or 0))

    old_posted_amount = Decimal(str(line.posted_balance_amount or 0))
    new_amount = Decimal(str(line.net_salary or 0))

    # فقط تفاوت را به balance اعمال کن
    difference = new_amount - old_posted_amount

    if difference == 0:
        return

    balance.company_payable_to_employee = company_before + difference
    balance.save()

    EmployeeBalanceLedger.objects.create(
        employee=line.employee,
        entry_type='payroll',
        amount=difference,
        company_payable_before=company_before,
        company_payable_after=balance.company_payable_to_employee,
        employee_payable_before=employee_before,
        employee_payable_after=balance.employee_payable_to_company,
        note=f'Payroll synced for {line.payroll.year}-{line.payroll.month}'
    )

    line.is_posted_to_balance = True
    line.posted_balance_amount = new_amount
    line.save()


@transaction.atomic
def create_monthly_payroll(request):
    payrolls = EmployeePayroll.objects.all()

    if request.method == 'POST':
        form = EmployeePayrollCreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            payroll_date = form.cleaned_data['date']
            description = form.cleaned_data['description']

            year = payroll_date.year
            month = payroll_date.month

            payroll, created = EmployeePayroll.objects.get_or_create(
                year=year,
                month=month,
                defaults={
                    'title': title,
                    'date': payroll_date,
                    'description': description,
                }
            )

            if not created:
                payroll.title = title
                payroll.date = payroll_date
                payroll.description = description
                payroll.save()

            employees = Employee.objects.filter(is_active=True).order_by('first_name', 'last_name')

            created_count = 0
            for employee in employees:
                line = build_employee_payroll_line(employee, payroll)
                post_payroll_line_to_balance(line)
                created_count += 1

            messages.success(
                request,
                f"Payroll for {year}-{month} created successfully for {created_count} employees ✅"
            )
            return redirect('employee:create_monthly_payroll')
        else:
            messages.error(request, "Failed to create payroll ❌")
    else:
        form = EmployeePayrollCreateForm()

    return render(request, 'employee/create_payroll.html', {
        'form': form,
        'payrolls': payrolls,
    })


def payroll_detail(request, payroll_id):
    payroll = get_object_or_404(
        EmployeePayroll.objects.prefetch_related('lines__employee'),
        id=payroll_id
    )

    lines = payroll.lines.all().order_by('employee__first_name')

    # totals
    totals = lines.aggregate(
        total_base=Sum('base_salary'),
        total_leave=Sum('total_leave_days'),
        total_absent=Sum('total_absent_days'),
        total_deduction=Sum('total_deduction'),
        total_net=Sum('net_salary'),
    )

    context = {
        'payroll': payroll,
        'lines': lines,
        'totals': totals,
    }
    return render(request, 'employee/payroll_detail.html', context)


def delete_monthly_payroll(request, payroll_id):
    payroll = get_object_or_404(EmployeePayroll, id=payroll_id)

    if request.method == 'POST':
        payroll.delete()
        messages.success(request, "Payroll deleted successfully 🗑️")
    else:
        messages.warning(request, "Invalid delete request ⚠️")

    return redirect('employee:create_monthly_payroll')


def apply_salary_payment(employee, amount, payment=None):
    amount = Decimal(str(amount))
    balance, _ = EmployeeBalance.objects.get_or_create(employee=employee)

    company_before = Decimal(str(balance.company_payable_to_employee or 0))
    employee_before = Decimal(str(balance.employee_payable_to_company or 0))

    if balance.company_payable_to_employee >= amount:
        balance.company_payable_to_employee -= amount
    else:
        remaining = amount - balance.company_payable_to_employee
        balance.company_payable_to_employee = Decimal('0')
        balance.employee_payable_to_company += remaining

    balance.save()

    EmployeeBalanceLedger.objects.create(
        employee=employee,
        entry_type='salary_payment',
        salary_payment=payment,
        amount=amount,
        company_payable_before=company_before,
        company_payable_after=balance.company_payable_to_employee,
        employee_payable_before=employee_before,
        employee_payable_after=balance.employee_payable_to_company,
        note=f'Salary payment recorded'
    )


@transaction.atomic
def employee_salary_payment_create(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        form = EmployeeSalaryPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.employee = employee
            payment.save()

            apply_salary_payment(employee, payment.amount, payment=payment)

            messages.success(request, "Salary payment recorded successfully ✅")
        else:
            messages.error(request, "Failed to save payment ❌")

    return redirect('employee:employee_detail', employee_id=employee.id)


@transaction.atomic
def employee_salary_payment_delete(request, payment_id):
    payment = get_object_or_404(EmployeeSalaryPayment, id=payment_id)
    employee = payment.employee

    if request.method == 'POST':
        balance, _ = EmployeeBalance.objects.get_or_create(employee=employee)

        company_before = Decimal(str(balance.company_payable_to_employee or 0))
        employee_before = Decimal(str(balance.employee_payable_to_company or 0))

        # برعکسِ payment عمل می‌کنیم
        balance.company_payable_to_employee = company_before + Decimal(str(payment.amount))
        balance.save()

        EmployeeBalanceLedger.objects.create(
            employee=employee,
            entry_type='adjustment_add_company_debt',
            amount=payment.amount,
            company_payable_before=company_before,
            company_payable_after=balance.company_payable_to_employee,
            employee_payable_before=employee_before,
            employee_payable_after=balance.employee_payable_to_company,
            note=f'Reversed deleted payment #{payment.id}'
        )

        payment.delete()
        messages.success(request, "Payment deleted successfully 🗑️")
    else:
        messages.warning(request, "Invalid delete request ⚠️")

    return redirect('employee:employee_detail', employee_id=employee.id)