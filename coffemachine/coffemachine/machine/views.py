from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views import View

from .forms import CoffeeChoiceForm
from .models import Coffee
from .handler import CoffeeBrewMechanism


class CoffeeMachineView(View):
    template_name = "core/make_coffee_template.html"
    view_name = "coffee_machine_main_view"
    title = ""
    default_form = CoffeeChoiceForm

    def common_steps(self, request):
        self.request = request
        self.coffee = None
        self._init_kwargs()
        self._set_forms()

    def get(self, request, *args, **kwargs):
        self.common_steps(request)
        return render(request, self.template_name, self.kwargs)

    def post(self, request, *args, **kwargs):
        self.common_steps(request)
        if self._handle_form():
            coffee_machine = CoffeeBrewMechanism(coffee=self.coffee)
            hot_coffee = coffee_machine.make_coffee()
            #todo some one to handle it
        return render(request, self.template_name, self.kwargs)

    def _init_kwargs(self):
        self.kwargs = {
            "title": self.title
        }

    def _update_kwargs(self, dictionary):
        if dictionary:
            self.kwargs.update(dictionary)

    def _set_forms(self):
        data = self.request.POST or None
        self.form = self.default_form(
            data=data,
        )
        self._update_kwargs({
            "form": self.form,
        })

    def _handle_form(self):
        if self.form.is_valid():
            self.coffee = get_object_or_404(Coffee, coffee_type=self.form.cleaned_data["coffee_type"])
