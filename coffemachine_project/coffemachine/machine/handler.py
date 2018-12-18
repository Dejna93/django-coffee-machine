from abc import ABCMeta, abstractmethod


class DevicePart(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._errors = {}

    @abstractmethod
    def check_current_status(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def run_process(self):
        pass

    def is_any_errors(self):
        if not self._errors.keys():
            return True
        return self._errors

    def add_error(self, error):
        self._errors[error] = True


class PressurePump(DevicePart):
    MAX_PRESSURE = 10  # bar

    def __init__(self):
        super(PressurePump, self).__init__()
        self.current_pressure = 1  # bar

    def check_current_status(self):
        return self.current_pressure == self.MAX_PRESSURE

    def cleanup(self):
        self.current_pressure = 1

    def run_process(self):
        for bar in range(PressurePump.MAX_PRESSURE + 1):
            self.current_pressure = bar
            print "Increase pressure to %s bar" % self.current_pressure
        return self.check_current_status()

    def reset(self):
        self.current_pressure = 1


class WaterHeater(DevicePart):
    CAPACITY = 350  # ml
    MIN_CAPACITY = 50  # ml
    EFFERVESCENCE = 100  # C

    ERROR_EMPTY_WATER_TANK = "Empty water tank"
    ERROR_NOT_ENOUGH_WATER_TO_BOIL = "Not enough water in heater to boil"
    ERROR_BAD_TEMP = "Too low water temperature"

    def __init__(self):
        super(WaterHeater, self).__init__()
        self.water_tank = WaterTank()
        self.water_temp = 20  # C
        self.current_capacity = self.MIN_CAPACITY

    def check_current_status(self):
        pass

    def check_is_water_boiling(self):
        if not self.water_temp == self.EFFERVESCENCE:
            self.add_error(self.ERROR_BAD_TEMP)
            return False
        return True

    def check_is_enough_water_capacity(self):
        if not self.MIN_CAPACITY <= self.current_capacity <= WaterHeater.CAPACITY:
            self.add_error(self.ERROR_NOT_ENOUGH_WATER_TO_BOIL)
            return False
        return True

    def cleanup(self):
        self.current_capacity = self.MIN_CAPACITY
        self.water_temp = 20  # C

    def run_process(self, water_to_boil=CAPACITY):
        self.current_capacity = water_to_boil
        if not self.check_is_enough_water_capacity():
            return False
        self.send_water_to_brew()
        return self.is_any_errors()

    def prepare_to_boiling(self, amount=CAPACITY):
        if self.check_is_enough_water_capacity():
            water_for_tank = self.water_tank.get_amount_from_conteiner(amount)
            if water_for_tank:  # check if empty tank is empty
                for temp in range(self.water_temp, 101):
                    print "Start boiling water %s" % temp
                    self.water_temp = temp
                return True
            else:
                self.add_error(self.ERROR_EMPTY_WATER_TANK)
                print "Is not enough water please refill"
                return False
        return False

    def prepare_water_for_pressure_pomp(self):
        self.prepare_to_boiling()
        return self.check_is_water_boiling()

    def send_water_to_brew(self):
        if not self.prepare_to_boiling(amount=self.current_capacity):
            return False
        self.prepare_water_for_pressure_pomp()
        result = self.check_is_water_boiling()
        self.cleanup()
        return result


class MilkHeater(DevicePart):
    CAPACITY = 150  # ml
    ERROR_EMPTY_MILK_TANK = "Empty milk tank"

    def __init__(self, water_heater):
        super(MilkHeater, self).__init__()
        self.water_heater = water_heater
        self.milk_tank = MilkTank()

    def check_current_status(self):
        pass

    def cleanup(self):
        pass

    def fill_water(self):
        self.water_heater.water_tank.fill_fluid_tank(WaterTank.CAPACITY)
        del self._errors[self.water_heater.ERROR_EMPTY_WATER_TANK]

    def fill_milk(self):
        self.milk_tank.fill_fluid_tank(self.milk_tank.CAPACITY)
        del self._errors[self.ERROR_EMPTY_MILK_TANK]

    def run_process(self):
        prepare_boiling = self.water_heater.prepare_to_boiling(MilkTank.WATER_FOR_LATHER)
        prepare_pressure_pump = self.water_heater.prepare_water_for_pressure_pomp()
        if prepare_boiling and prepare_pressure_pump:
            milk_for_lather = self.milk_tank.get_amount_from_conteiner(self.CAPACITY)
            if milk_for_lather:
                for second in range(10):
                    print "Start lather milk"
                return True
            else:
                self.add_error(self.ERROR_EMPTY_MILK_TANK)
                return False
        if not prepare_boiling:
            self.add_error(self.water_heater.ERROR_NOT_ENOUGH_WATER_TO_BOIL)
        if not prepare_pressure_pump:
            self.add_error("Pump")
        return False


class CoffeeBrewRecipe(object):
    __metaclass__ = ABCMeta

    def brew(self, mechanism):
        raise NotImplementedError


class EspressoRecipe(CoffeeBrewRecipe):
    def brew(self, mechanism):
        return mechanism.make_basic_coffee()


class AmericanoRecipe(CoffeeBrewRecipe):
    def brew(self, mechanism):
        status_coffee = mechanism.make_basic_coffee()
        if isinstance(status_coffee, dict):
            return status_coffee
        status_extra_water = mechanism.boiling_water(mechanism.coffee.extra_quantity)
        if isinstance(status_extra_water, dict):
            return status_extra_water

        status_coffee += mechanism.coffee.extra_quantity
        return status_coffee


class LateRecipe(CoffeeBrewRecipe):
    def brew(self, mechanism):
        status_coffee = mechanism.make_basic_coffee()
        if isinstance(status_coffee, dict):
            return status_coffee
        status_milk = mechanism.lather_milk()
        if isinstance(status_milk, dict):
            return status_milk
        size_coffee = status_coffee + mechanism.coffee.extra_quantity
        return size_coffee


class CoffeeBrewMechanism(object):
    def __init__(self, coffee):
        self.coffee = coffee
        self.water_heater = WaterHeater()
        self.milk_heater = MilkHeater(self.water_heater)
        self.coffee_grinder = CoffeeGrinder()
        self.pressure_pump = PressurePump()
        self.trash_bin = TrashBin()

        self.errors = {}

        self.coffee_method = None
        self.methods_brew = {
            "espresso": EspressoRecipe,
            "americano": AmericanoRecipe,
            "latte": LateRecipe,
        }

    def set_method_for_coffee(self, coffee):
        self.coffee_method = self.methods_brew.get(coffee.coffee_type)()

    def prepare_ground_coffee(self, coffee):
        self.coffee_grinder.grind_beans(coffee.coffee_quantity)
        return self.coffee_grinder.is_any_errors()

    def boiling_water(self, quantity):
        self.water_heater.run_process(water_to_boil=quantity)
        return self.water_heater.is_any_errors()

    def prepare_pressure_pump(self):
        self.pressure_pump.run_process()
        return self.pressure_pump.is_any_errors()

    def lather_milk(self):
        self.milk_heater.run_process()
        return self.milk_heater.is_any_errors()

    def _update_status(self, status):
        if isinstance(status, dict):
            self.errors.update(status)

    def make_basic_coffee(self):
        status = self.prepare_ground_coffee(self.coffee)
        self._update_status(status)
        status = self.boiling_water(self.coffee.size)
        self._update_status(status)
        status = self.prepare_pressure_pump()
        self._update_status(status)

        if self.errors.keys():
            return self.errors
        return self.run_brew_process()

    def run_brew_process(self):
        self.pressure_pump.cleanup()
        self.water_heater.cleanup()
        self.trash_bin.add_trash()
        return self.coffee.size

    def make_coffee(self):
        self.set_method_for_coffee(self.coffee)
        return self.coffee_method.brew(self)


class TrashBin(DevicePart):
    CAPACITY = 10  # TRAILS

    def __init__(self):
        super(TrashBin, self).__init__()
        self.current_weight = 0

    def check_current_status(self):
        return self.current_weight + 1 < self.CAPACITY

    def cleanup(self):
        print "Throw away trash"
        self.current_weight = 0

    def run_process(self):
        self.add_trash()

    def add_trash(self):
        self.current_weight += 1


class CoffeeGrinder(DevicePart):
    CAPACITY = 200  # ml
    ERROR_NOT_ENOUGH_BEANS_TO_GRIND = "Not enough beans to grind"

    def __init__(self, fill_coffee_beans=True):
        super(CoffeeGrinder, self).__init__()
        self.coffee_tank = CoffeeBeansTank()
        self.current_capacity = 0
        if fill_coffee_beans:
            self.coffee_tank.fill_fluid_tank(self.CAPACITY)

    def check_current_status(self):
        pass

    def cleanup(self):
        self.current_capacity = 0

    def run_process(self):
        pass

    def check_is_enough_coffee_beans(self):
        return 0 < self.current_capacity <= self.CAPACITY

    def grind_beans(self, amount):
        if 0 < amount <= self.CAPACITY:
            coffee = self.coffee_tank.get_amount_from_conteiner(amount)
            if coffee:
                for sec in range(5):
                    print "Start griding beans"
                return True
            else:
                self.add_error(self.ERROR_NOT_ENOUGH_BEANS_TO_GRIND)
                return False
        return False


class Conteiner(object):
    __metaclass__ = ABCMeta
    CAPACITY = 0
    NAME = ""
    TEXT_SEND_FROM_CONTEINER = ""
    TEXT_PLEASE_FILL = ""
    TEXT_WAS_FULLY_FILLED = ""
    TEXT_FILLED = ""
    TEXT_FILLED_TO_MAX = ""

    def __init__(self, fill_fluid=True):
        self.content_level = 0
        if fill_fluid:
            self.fill_fluid_tank(self.CAPACITY)

    def fill_fluid_tank(self, capacity):
        if self.CAPACITY < capacity:
            print self.TEXT_WAS_FULLY_FILLED
            return False
        elif capacity < 0:
            raise ValueError("Cannot put minus content") # todo better eng
        elif capacity + self.content_level <= self.CAPACITY:
            self.content_level += capacity
            print self.TEXT_FILLED % capacity
            return True, self.content_level
        else:
            self.content_level = self.CAPACITY
            print self.TEXT_FILLED_TO_MAX % capacity
            return False, self.content_level

    def get_amount_from_conteiner(self, amount):
        if self.content_level - amount > 0:
            self.content_level -= amount
            print self.TEXT_SEND_FROM_CONTEINER
            return True
        else:
            print self.TEXT_PLEASE_FILL
            return False


class WaterTank(Conteiner):
    CAPACITY = 1000  # ml
    TEXT_SEND_FROM_CONTEINER = "Water is get from tank"
    TEXT_PLEASE_FILL = "Please fill water tank"
    TEXT_WAS_FULLY_FILLED = "Water tank is full"
    TEXT_FILLED = "Water tank is filled [%s]"
    TEXT_FILLED_TO_MAX = "Water tank is already filled to his max capacity  [%s]"


class MilkTank(Conteiner):
    CAPACITY = 300  # ml
    WATER_FOR_LATHER = 150  # ml
    TEXT_SEND_FROM_CONTEINER = "Milk is get from tank"
    TEXT_PLEASE_FILL = "Please fill milk tank"
    TEXT_WAS_FULLY_FILLED = "Milk tank is full"
    TEXT_FILLED = "Milk tank is filled [%s]"
    TEXT_FILLED_TO_MAX = "Milk tank is already filled to his max capacity  [%s]"


class CoffeeBeansTank(Conteiner):
    CAPACITY = 500 # dg
    TEXT_SEND_FROM_CONTEINER = "Coffee beans is get from tank"
    TEXT_PLEASE_FILL = "Please fill coffee beans tank"
    TEXT_WAS_FULLY_FILLED = "Coffee beans tank is full"
    TEXT_FILLED = "Coffee beans tank is filled [%s]"
    TEXT_FILLED_TO_MAX = "Coffee beans tank is already filled to his max capacity  [%s]"

