from django import forms

from coffemachine.machine.models import Coffee


class CoffeeChoiceForm(forms.Form):
    coffee_type = forms.ChoiceField(choices=Coffee.coffee_types)
