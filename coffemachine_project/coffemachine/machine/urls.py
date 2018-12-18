# Django imports
from .handler import CoffeeBrewMechanism
from .views import CoffeeMachineView, CoffeeExtraOptionsAjaxView
from django.conf.urls import url


MECHANISM = CoffeeBrewMechanism()

urlpatterns = [
    url(r'^$', CoffeeMachineView.as_view(), {'template_name': CoffeeMachineView.template_name},
        name=CoffeeMachineView.view_name),
    url(r'^ajax/$', CoffeeExtraOptionsAjaxView.as_view(), name=CoffeeExtraOptionsAjaxView.view_name),
]
