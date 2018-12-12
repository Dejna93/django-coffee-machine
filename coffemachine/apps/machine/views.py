from django.shortcuts import render

# Create your views here.
from django.views import View


class CoffeeMachineView(View):
    template_name = "core/make_coffee_template.html"
    view_name = "coffee_machine_main_view"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={

        })

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, context={

        })
