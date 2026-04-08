from django import forms
from .models import *
from django.core.exceptions import ValidationError


class IncomeForm(forms.ModelForm):
    

    class Meta:
        model = Income
        fields = ["title", "source", "amount", "currency","date","note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].widget.attrs.update({
            "class": "form-control",
            "placeholder": ""
        })
        self.fields["source"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["amount"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["currency"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["date"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["note"].widget.attrs.update({
            "class": "form-select"
        })
       
       

class ExpenceForm(forms.ModelForm):
    
    class Meta:
        model = Expense
        fields = ["title", "category", "amount", "currency","date","note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].widget.attrs.update({
            "class": "form-control",
            "placeholder": ""
        })
        self.fields["category"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["amount"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["currency"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["date"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["note"].widget.attrs.update({
            "class": "form-select"
        })
       
