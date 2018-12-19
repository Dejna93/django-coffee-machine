from abc import ABCMeta, abstractmethod

from coffemachine.machine.container import MilkTank, CoffeeBeansTank, WaterTank


class DevicePart(object):
    """
    This abstract class provides basic operations for all device parts in coffee machine

    Attributes:
            _errors (dict): collect errors in mechanism
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self._errors = {}

    @abstractmethod
    def cleanup(self):
        """
        Method must be overridden.
        """
        pass

    @abstractmethod
    def run_process(self):
        """
        Method must be overridden.
        """
        pass

    def get_device_errors(self):
        """
        Return a dict with errors if any key was found, otherwise return False
        :return:
        """
        if self._errors.keys():
            return self._errors
        return False

    def add_error(self, error):
        """
        Add error to device
        :string error:
        """
        self._errors[error] = True


class PressurePump(DevicePart):
    """
    Simulation class for pressure pump. Main task to pressurize water for other devices.

    Attributes:
         MAX_PRESSURE (int): Maximum compression during production
         current_pressure (int): Current level of compression
    """
    MAX_PRESSURE = 10  # bar

    def __init__(self):
        super(PressurePump, self).__init__()
        self.current_pressure = 1  # bar

    def check_current_pressure(self):
        """
        :return True if compression reach max level, otherwise False
        """
        return self.current_pressure == self.MAX_PRESSURE

    def cleanup(self):
        """
        Simulation of valve opening for release pressurized water
        """
        self.current_pressure = 1

    def run_process(self):
        """
        Simulation of compressing water
        :return: result of check_current_pressure method
        """
        for bar in range(PressurePump.MAX_PRESSURE + 1):
            self.current_pressure = bar
        return self.check_current_pressure()


class WaterHeater(DevicePart):
    """
    Device to boiling water. Provides hot water for brew coffee, pressure pump and milk heater

    Attributes:
        CAPACITY (int) - static variable, maximum amount of water to boil at once
        MIN_CAPACITY (int) - minimum of water to start process of boiling
        BOILING_POINT (int) - temperature of boiling water
        ERROR_EMPTY_WATER_TANK (string) - error message
        ERROR_NOT_ENOUGH_WATER_TO_BOIL (string) - error message
        ERROR_BAD_TEMP (string) - error message
    """
    CAPACITY = 350  # ml
    MIN_CAPACITY = 50  # ml
    BOILING_POINT = 100  # C

    ERROR_EMPTY_WATER_TANK = "Empty water tank"
    ERROR_NOT_ENOUGH_WATER_TO_BOIL = "Not enough water in heater to boil"
    ERROR_BAD_TEMP = "Too low water temperature"

    def __init__(self):
        """
        Constructor, initialize object of water tank and minimum amount of water
        """
        super(WaterHeater, self).__init__()
        self.water_tank = WaterTank()
        self.water_temp = 20  # C
        self.current_capacity = self.MIN_CAPACITY

    def check_is_water_boiling(self):
        """
        CHeck if water reached boiling point, otherwise add proper error message
        :return: True or False
        """
        if not self.water_temp == self.BOILING_POINT:
            self.add_error(self.ERROR_BAD_TEMP)
            return False
        return True

    def check_is_enough_water_capacity(self):
        """
        Check if device tank has enough water to start process of boiling water. Otherwise add proper error message
        :return: True of False
        """
        if not self.MIN_CAPACITY <= self.current_capacity <= WaterHeater.CAPACITY:
            self.add_error(self.ERROR_NOT_ENOUGH_WATER_TO_BOIL)
            return False
        return True

    def cleanup(self):
        """
        Reset state of device
        """
        self.current_capacity = self.MIN_CAPACITY
        self.water_temp = 20  # C

    def refill_water_tank(self):
        """
        Provides refilling water of main coffee machine water tank, and reset errors message
        """
        self.water_tank.fill_tank(WaterTank.CAPACITY)
        self._errors = {}

    def run_process(self, water_to_boil=CAPACITY):
        """
        Run process of simulation boiling water in device tank, and send it to coffee brew device
        :param water_to_boil: amount of water to boil
        """
        self.current_capacity = water_to_boil
        if not self.check_is_enough_water_capacity():
            return False
        self.send_water_to_brew()

    def prepare_to_boiling(self, amount=CAPACITY):
        """
        If is enough water in tank, get amount of water from tank, then boil water
        :amount: int - amount of water
        :return: True or False
        """
        if self.check_is_enough_water_capacity():
            water_for_tank = self.water_tank.get_amount_from_container(amount)
            if water_for_tank:  # check if empty tank is empty
                for temp in range(self.water_temp, 101):
                    self.water_temp = temp
                return True
            else:
                self.add_error(self.ERROR_EMPTY_WATER_TANK)
                return False
        return False

    def prepare_water_for_pressure_pump(self):
        """
        Process to prepare water for pressure pump
        :return: result of check_is_water_boiling method
        """
        self.prepare_to_boiling()
        return self.check_is_water_boiling()

    def send_water_to_brew(self):
        """
        Send of boiled water to coffee brew
        :return: True if water are boiled otherwise False
        """
        if not self.prepare_to_boiling(amount=self.current_capacity):
            return False
        self.prepare_water_for_pressure_pump()
        result = self.check_is_water_boiling()
        self.cleanup()
        return result


class MilkHeater(DevicePart):
    """
    Device for foaming milk.

    Attributes:
        CAPACITY (int) - static variable, maximum amount of milk to foam at once
        ERROR_EMPTY_MILK_TANK (string) - error message
        water_heater  (WaterHeater) - device to help milk heater to foam milk.
        milk_tank (MilkTank) - milk tank contains milk
    """
    CAPACITY = 150  # ml
    ERROR_EMPTY_MILK_TANK = "Empty milk tank"

    def __init__(self, water_heater):
        """
        Constructor, initialize object of milk tank.
        :param water_heater: (WaterHeater) - object of water heater.
        """
        super(MilkHeater, self).__init__()
        self.water_heater = water_heater
        self.milk_tank = MilkTank()

    def fill_water(self):
        """
        Fill water tank and remove proper error.
        """
        self.water_heater.water_tank.fill_tank(WaterTank.CAPACITY)
        if self.water_heater.ERROR_EMPTY_WATER_TANK in self._errors.keys():
            del self._errors[self.water_heater.ERROR_EMPTY_WATER_TANK]

    def fill_milk(self):
        """
        Fill milk tank and remove proper error.
        :return:
        """
        self.milk_tank.fill_tank(self.milk_tank.CAPACITY)
        if self.ERROR_EMPTY_MILK_TANK in self._errors.keys():
            del self._errors[self.ERROR_EMPTY_MILK_TANK]

    def run_process(self):
        """
        Run process of loaming milk. Get boiled water, prepare pressure pump,
        get amount of milk. If successfully, then lather milk for 10 second.
        :return: True if successfully, otherwise False
        """
        prepare_boiling = self.water_heater.prepare_to_boiling(MilkTank.WATER_FOR_LATHER)
        prepare_pressure_pump = self.water_heater.prepare_water_for_pressure_pump()
        if prepare_boiling and prepare_pressure_pump:
            milk_for_lather = self.milk_tank.get_amount_from_container(self.CAPACITY)
            if milk_for_lather:
                for second in range(10):
                    pass
                return True
            else:
                self.add_error(self.ERROR_EMPTY_MILK_TANK)
                return False
        if not prepare_boiling:
            self.add_error(self.water_heater.ERROR_NOT_ENOUGH_WATER_TO_BOIL)
        if not prepare_pressure_pump:
            self.add_error("Pump")
        return False

    def cleanup(self):
        pass


class TrashBin(DevicePart):
    """
    Trash bin for wastes from processed beans.

    Attributes:
        CAPACITY (int) - static variable, maximum amount trash
        ERROR_FULL_TRASH (string) - error message
        current_level (int) - current level of filling the bin
    """
    CAPACITY = 4  # TRAILS
    ERROR_FULL_TRASH = "Full trash bin"

    def __init__(self):
        super(TrashBin, self).__init__()
        self.current_level = 0

    def is_trash_full(self):
        """
        Check if trash bin is full
        :return: True if full otherwise False
        """
        if self.current_level >= self.CAPACITY:
            self.add_error(self.ERROR_FULL_TRASH)
            return False
        return True

    def cleanup(self):
        """
        Throw away trash, and reset errors
        """
        self._errors = {}
        self.current_level = 0

    def run_process(self):
        """
        Add new waste to bin
        """
        self.current_level += 1


class CoffeeGrinder(DevicePart):
    """
    Device coffee grinder, get proper of coffee beans and grind them.

    Attributes:
        CAPACITY (int) - static variable, maximum amount trash
        ERROR_NOT_ENOUGH_BEANS_TO_GRIND (string) - error message
        coffee_tank (CoffeeBeansTank) - container with available coffee beans
        current_capacity - current level of grinded coffee beans
    """
    CAPACITY = 200  # ml
    ERROR_NOT_ENOUGH_BEANS_TO_GRIND = "Not enough beans to grind"

    def __init__(self, fill_coffee_beans=True):
        """
        Constructor for initialize coffee tank, current_capacity. Fill coffee tank.
        :fill_coffee_beans: True to fill coffee beans otherwise False
        """
        super(CoffeeGrinder, self).__init__()
        self.coffee_tank = CoffeeBeansTank()
        self.current_capacity = 0
        if fill_coffee_beans:
            self.coffee_tank.fill_tank(self.CAPACITY)

    def cleanup(self):
        """
        Reset device state, and refill coffee tank beans and reset errors
        """
        self.current_capacity = 0
        self.coffee_tank.fill_tank(CoffeeBeansTank.CAPACITY)
        self._errors = {}

    def check_is_enough_coffee_beans(self):
        return 0 < self.current_capacity <= self.CAPACITY

    def grind_beans(self, amount):
        """
        Run process of grinding beans. Get amount coffee beans from container and grind them.
        amount: (int) - amount of coffee beans
        :return: True if grind was completed successfully else False
        """
        if 0 < amount <= self.CAPACITY:
            coffee = self.coffee_tank.get_amount_from_container(amount)
            if coffee:
                for sec in range(5):
                    pass
                return True
            else:
                self.add_error(self.ERROR_NOT_ENOUGH_BEANS_TO_GRIND)
                return False
        return False

    def run_process(self):
        pass
