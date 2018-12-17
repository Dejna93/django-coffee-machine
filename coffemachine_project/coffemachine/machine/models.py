from django.db import models


class CoffeeSize(models.Model):
    name = models.CharField(max_length=10)
    capacity = models.IntegerField()

    def __str__(self):
        return "%s :%s" % (self.name, self.capacity)


class Coffee(models.Model):
    coffee_types = (("espresso", "Espresso"), ("americano", "Americano"), ("latte", "latte"))

    coffee_type = models.CharField(max_length=15, choices=coffee_types)
    beans = models.CharField(max_length=15)
    size = models.ForeignKey(CoffeeSize)
    contains_milk = models.BooleanField(default=False)
    time_preparing = models.IntegerField()

