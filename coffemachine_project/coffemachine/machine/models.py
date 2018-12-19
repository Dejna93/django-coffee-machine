from six import python_2_unicode_compatible
from django.db import models


@python_2_unicode_compatible
class Coffee(models.Model):
    coffee_types = (("espresso", "Espresso"), ("americano", "Americano"), ("latte", "Latte"))
    sizes = ((120, "Normal"), (240, "Large"))
    coffee_type = models.CharField(max_length=15, choices=coffee_types)
    beans = models.CharField(max_length=15)
    coffee_quantity = models.IntegerField()
    size = models.IntegerField(choices=sizes)
    extra_quantity = models.IntegerField(null=True, blank=True)
    contains_milk = models.BooleanField(default=False)
    time_preparing = models.IntegerField()

    def __str__(self):
        return "%s, %s" % (self.coffee_type, self.size)
