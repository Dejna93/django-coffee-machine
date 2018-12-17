from abc import ABCMeta, abstractmethod


class DevicePart(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def check_current_status(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def run_process(self):
        pass


class PressurePump(DevicePart):
    MAX_PRESSURE = 10  # bar

    def __init__(self):
        self.current_pressure = 1  # bar

    def check_current_status(self):
        return self.current_pressure == self.MAX_PRESSURE

    def cleanup(self):
        self.current_pressure = 1

    def run_process(self):
        for bar in range(PressurePump.MAX_PRESSURE):
            self.current_pressure += bar
            print "Increase pressure to %s bar" % self.current_pressure
        return self.check_current_status()

    def reset(self):
        self.current_pressure = 1


class WaterHeater(DevicePart):
    CAPACITY = 300  # ml
    MIN_CAPACITY = 50  # ml
    EFFERVESCENCE = 100  # C

    def check_current_status(self):
        pass

    def check_is_water_boiling(self):
        return self.water_temp == self.EFFERVESCENCE

    def check_is_enough_water_capacity(self):
        return self.current_capacity >= self.MIN_CAPACITY or self.current_capacity <= WaterHeater.CAPACITY

    def cleanup(self):
        self.current_capacity = 0
        self.water_temp = 20  # C

    def run_process(self, water_to_boil=CAPACITY):
        if not self.check_is_enough_water_capacity():
            return False
        return self.send_water_to_brew(water_to_boil)

    def __init__(self):
        self.water_tank = WaterTank()
        self.water_temp = 20  # C
        self.current_capacity = 0

    def prepare_to_boiling(self, amount=CAPACITY):
        if self.check_is_enough_water_capacity():
            water_for_tank = self.water_tank.get_amount_of_water_for_boiling(amount)
            if water_for_tank:  # check if empty tank is empty
                for temp in range(self.water_temp, 100):
                    print "Start boiling water %s" % temp
                    self.water_temp = temp
            return True
        return False

    def prepare_water_for_pressure_pomp(self):
        self.prepare_to_boiling()
        return self.check_is_water_boiling()

    def send_water_to_brew(self, water_to_boil):
        self.prepare_to_boiling(amount=water_to_boil)
        self.prepare_water_for_pressure_pomp()
        result = self.check_is_water_boiling
        self.cleanup()
        return result


class MilkHeater(DevicePart):
    CAPACITY = 150  # ml

    def __init__(self, water_heater):
        self.water_heater = water_heater
        self.milk_tank = MilkTank()

    def check_current_status(self):
        pass

    def cleanup(self):
        pass

    def run_process(self):
        if self.water_heater.prepare_to_boiling(MilkTank.WATER_FOR_LATHER) and self.water_heater.prepare_water_for_pressure_pomp():
            milk_for_lather = self.milk_tank.get_amount_of_milk_for_lather(self.CAPACITY)
            if milk_for_lather:
                for second in range(10):
                    print "Start lather milk"
                return True
        return False


class CoffeeBrewStrategy(object):
    __metaclass__ = ABCMeta

    def brew(self, mechanism):
        raise NotImplementedError


class EspressoStrategy(CoffeeBrewStrategy):
    def brew(self, mechanism):
        return mechanism.make_basic_coffee()


class AmericanoStrategy(CoffeeBrewStrategy):
    def brew(self, mechanism):
        size_coffee = mechanism.make_basic_coffee()
        mechanism.boiling_water(WaterTank.CAPACITY / 3)
        size_coffee += WaterTank.CAPACITY / 3
        return size_coffee


class LateStrategy(CoffeeBrewStrategy):
    def brew(self, mechanism):
        size_coffee = mechanism.make_basic_coffee()
        mechanism.lather_milk()
        size_coffee += MilkHeater.CAPACITY
        return size_coffee


class CoffeeBrewMechanism(object):
    def __init__(self, coffee):
        self.coffee = coffee
        self.water_heater = WaterHeater()
        self.milk_heater = MilkHeater(self.water_heater)
        self.coffee_grinder = CoffeeGrinder()
        self.pressure_pump = PressurePump()
        self.trash_bin = TrashBin()

        self.coffee_method = None
        self.methods_brew = {
            "espresso": EspressoStrategy,
            "americano": AmericanoStrategy,
            "latte": LateStrategy,
        }

    def set_method_for_coffee(self, coffee):
        self.coffee_method = self.methods_brew.get(coffee.name)(self)

    def prepare_ground_coffee(self, coffee):
        return self.coffee_grinder.grind_beans(coffee.amount)

    def boiling_water(self):
        return self.water_heater.run_process()

    def prepare_pressure_pump(self):
        return self.pressure_pump.run_process()

    def lather_milk(self):
        return self.milk_heater.run_process()

    def make_basic_coffee(self):
        self.prepare_ground_coffee(self.coffee)
        self.boiling_water()
        self.prepare_pressure_pump()
        return self.run_brew_process()

    def run_brew_process(self):
        self.pressure_pump.cleanup()
        self.water_heater.cleanup()
        self.trash_bin.add_trash()
        return self.coffee.size

    def make_coffee(self):
        self.set_method_for_coffee(self.coffee)
        return self.coffee_method.brew()


class TrashBin(DevicePart):
    CAPACITY = 10  # TRAILS

    def __init__(self):
        self.current_weight = 0

    def check_current_status(self):
        return self.current_weight + 1 < self.CAPACITY

    def cleanup(self):
        self.current_weight = 0

    def run_process(self):
        self.add_trash()

    def is_enough_space_for_trash(self):
        return self.current_weight + 1 < self.CAPACITY

    def add_trash(self):
        self.current_weight += 1


class CoffeeGrinder(DevicePart):
    CAPACITY = 1000  # ml

    def __init__(self, fill_coffee_beans=True):
        self.current_capacity = 0
        if fill_coffee_beans:
            self.fill_coffee_beans_container(CoffeeGrinder.CAPACITY)

    def check_current_status(self):
        return self.current_capacity > 0

    def cleanup(self):
        self.current_capacity = 0

    def run_process(self):
        pass

    def fill_coffee_beans_container(self, capacity=None):
        if CoffeeGrinder.CAPACITY >= capacity:
            print "Coffee Grinder was fully filled"
        elif CoffeeGrinder.CAPACITY - self.current_capacity >= capacity:
            self.current_capacity += capacity
            print "Coffee Grinder is filled for %s" % capacity
        print "Cannot fill Coffee Grinder, too many beans"

    def prepare_beans_for_grind(self, amount):
        if self.current_capacity - amount > 0:
            self.current_capacity -= amount
            print "Successfully get enough beans to grind"
            return True
        print "Please fill coffee beans"
        return False

    def grind_beans(self, amount):
        if self.check_current_status() and self.prepare_beans_for_grind(amount):
            print "Grinding beans"
            return True
        return False


class FluidConteiner(object):
    __metaclass__ = ABCMeta
    CAPACITY = 0

    def __init__(self, fill_fluid=True):
        self.liquid_level = 0
        if fill_fluid:
            self.fill_fluid_tank(self.CAPACITY)

    def fill_fluid_tank(self, capacity):
        if self.CAPACITY > capacity:
            print "%s was fully filled" % self.__name__
        elif self.CAPACITY - self.liquid_level >= capacity:
            self.liquid_level += capacity
            print "%s is filled for %s" % (self.__name__, capacity)
        else:
            print "Cannot fill %s, too many %s" % (self.__name__, capacity)


class WaterTank(FluidConteiner):
    CAPACITY = 1000  # ml

    def get_amount_of_water_for_boiling(self, amount):
        if self.liquid_level - amount > 0:
            self.liquid_level -= amount
            print "%s send water to boiling" % self.__name__
            return True
        else:
            print "Please fill %s" % self.__name__
            # self.fill_water_tank()
            return False


class MilkTank(FluidConteiner):
    CAPACITY = 300  # ml
    WATER_FOR_LATHER = 300  # ml

    def get_amount_of_milk_for_lather(self, amount):
        if self.liquid_level - amount > 0:
            self.liquid_level -= amount
            print "Filling tank for lather"
            return True
        else:
            print "Please fill milk tank"
            return False
