from abc import ABCMeta


class Container(object):
    __metaclass__ = ABCMeta
    CAPACITY = 0

    def __init__(self, fill_fluid=True):
        self.content_level = 0
        if fill_fluid:
            self.fill_tank(self.CAPACITY)

    def fill_tank(self, capacity):
        """
        Filling the container with given amount of something
        :param capacity:
        :return:
        """
        if self.CAPACITY < capacity:
            return False
        elif capacity < 0:
            raise ValueError("It is possible to have minus something in bottle?")
        elif capacity + self.content_level <= self.CAPACITY:
            self.content_level += capacity
            return True
        else:
            self.content_level = self.CAPACITY
            return False

    def get_amount_from_container(self, amount):
        if self.content_level - amount > 0:
            self.content_level -= amount
            return True
        else:
            return False


class WaterTank(Container):
    CAPACITY = 1000  # ml


class MilkTank(Container):
    CAPACITY = 300  # ml
    WATER_FOR_LATHER = 150  # ml


class CoffeeBeansTank(Container):
    CAPACITY = 500  # dg
