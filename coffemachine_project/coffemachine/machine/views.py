from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.template.loader import render_to_string
from django.views import View

from .handler import CoffeeBrewMechanism
from .forms import CoffeeChoiceForm
from .models import Coffee

#use singelton power
mechanism = CoffeeBrewMechanism()


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
        method = request.POST.get("method", None)
        if request.is_ajax():
            if self._handle_form():
                return JsonResponse(self.json_kwargs)
        return render(request, self.template_name, self.kwargs)

    def _init_kwargs(self):
        self.kwargs = {
            "title": self.title
        }
        self.json_kwargs = {}

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
            coffee = Coffee.objects.get(coffee_type=self.form.cleaned_data["coffee_type"])
            status = mechanism.make_coffee(coffee)
            if isinstance(status, dict):
                html = render_to_string("core/problem.html", {"problems": status.keys()})
                self.json_kwargs["problems"] = html
                return True
            html = render_to_string("core/coffee_cup.html", {"coffee_size": status})
            self.json_kwargs["html"] = html
            return True
        return False


class CoffeeExtraOptionsAjaxView(View):
    view_name = "extra_options"

    def post(self, request, *args, **kwargs):
        methods = {
            "beans_options": self.beans_refill,
            "water_options": self.water_refill,
            "milk_options": self.milk_refill,
            "trash_options": self.trash_remove
        }
        method = request.POST.get("method")

        if method:
            return methods.get(method)()
        return JsonResponse({"error": "NotImplemented method"})

    def _generate_response(self, message):
        return JsonResponse({
            "action": message,
        })

    def beans_refill(self):
        mechanism.refill_beans_tank()
        return self._generate_response("Beans successfully refiled")

    def water_refill(self):
        mechanism.refill_water_tank()
        return self._generate_response("Water successfully refiled")

    def milk_refill(self):
        mechanism.milk_heater.fill_milk()
        return self._generate_response("Milk successfully refiled")

    def trash_remove(self):
        mechanism.trash_bin.cleanup()
        return self._generate_response("Trash throw away")
