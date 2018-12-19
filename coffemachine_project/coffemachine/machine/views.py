from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.template.loader import render_to_string
from django.views import View

from coffemachine.machine.handler import CoffeeBrewMechanism
from coffemachine.machine.forms import CoffeeChoiceForm
from coffemachine.machine.models import Coffee

mechanism = CoffeeBrewMechanism()


class CoffeeMachineView(View):
    """
    Main coffee machine view. It handle process of making coffee by the user.
    Attributes:
        template_name - string path to html template
        view_name - string with view name used in urls
        title - string title of view
        default_form - CoffeeChoiceForm - a default form to initialize in view
    """
    template_name = "core/make_coffee_template.html"
    view_name = "coffee_machine_main_view"
    title = "Coffee Machine Simulator"
    default_form = CoffeeChoiceForm

    def common_steps(self, request):
        """
        Methods provides common steps for get and post method
        :param request: Django request
        """
        self.request = request
        self._init_kwargs()
        self._set_forms()

    def get(self, request, *args, **kwargs):
        self.common_steps(request)
        return render(request, self.template_name, self.kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handling ajax request
        :return: JsonResponse which contains image path if making coffee was successfully,
        otherwise contains html with each errors
        """
        self.common_steps(request)
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
        """
        Method checks if form is valid. If it successfully get coffee object from db.
        Execute  making coffee, if successfully add to response kwargs path to image.
        Otherwise render template with problems
        :return: True if form is valid, otherwise False
        """
        if self.form.is_valid():
            coffee = Coffee.objects.get(coffee_type=self.form.cleaned_data["coffee_type"])
            status = mechanism.make_coffee(coffee)
            if isinstance(status, dict):
                html = render_to_string("core/problem.html", {"problems": status.keys()})
                self.json_kwargs["problems"] = html
                return True
            self.json_kwargs["image"] = status
            return True
        return False


class CoffeeExtraOptionsAjaxView(View):
    """
    Ajax view for handling operations like refill water, milk, beans or remove trash.
    If given method is in available methods, it return JsonResponse with proper message.
    Otherwise return JsonResponse with error message
    """
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
        mechanism.remove_trash_bin()
        return self._generate_response("Trash throw away")
