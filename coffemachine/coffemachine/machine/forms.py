from django import forms

from .models import Coffee


class CoffeeChoiceForm(forms.Form):
    coffee_type = forms.ChoiceField(choices=Coffee.coffee_types)
