from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django import forms
from .models import Income, Expense
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget
from django import forms
from .models import Income, Expense, IncomeSource, ExpenseCategory



from django import forms
from .models import Income, Expense, IncomeSource, ExpenseCategory


class IncomeSourceForm(forms.ModelForm):
    class Meta:
        model = IncomeSource
        fields = ['name', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Source name"
        })
        self.fields["is_active"].widget.attrs.update({
            "class": "form-check-input"
        })


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Category name"
        })
        self.fields["is_active"].widget.attrs.update({
            "class": "form-check-input"
        })
        


class IncomeForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date"
        })
    )
    class Meta:
        model = Income
        fields = ["title", "source", "amount", "currency", "date", "note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["source"].queryset = IncomeSource.objects.filter(is_active=True)

        self.fields["title"].widget.attrs.update({
            "class": "form-control",
            "placeholder": ""
        })
        self.fields["source"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["amount"].widget.attrs.update({
            "class": "form-control",
            "step": "0.01"
        })
        self.fields["currency"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["date"].widget.attrs.update({
            "class": "form-control",
            "type": "date"
        })
        self.fields["note"].widget.attrs.update({
            "class": "form-control",
            "rows": "3"
        })


class ExpenceForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date"
        })
    )
    class Meta:
        model = Expense
        fields = ["title", "category", "amount", "currency", "date", "note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = ExpenseCategory.objects.filter(is_active=True)

        self.fields["title"].widget.attrs.update({
            "class": "form-control",
            "placeholder": ""
        })
        self.fields["category"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["amount"].widget.attrs.update({
            "class": "form-control",
            "step": "0.01"
        })
        self.fields["currency"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["date"].widget.attrs.update({
            "class": "form-control",
            "type": "date"
        })
        self.fields["note"].widget.attrs.update({
            "class": "form-control",
            "rows": "3"
        })