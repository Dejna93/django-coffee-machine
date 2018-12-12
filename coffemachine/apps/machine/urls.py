# Django imports
from apps.machine.views import CoffeeMachineView
from django.conf.urls import url

urlpatterns = [
    url(r'coffee/$', CoffeeMachineView.as_view(), {'template_name': CoffeeMachineView.template_name},
        name=CoffeeMachineView.view_name),
]
