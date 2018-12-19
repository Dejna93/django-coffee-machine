from .devices import WaterHeater, MilkHeater, CoffeeGrinder, PressurePump, TrashBin

try:
    import thread
except ModuleNotFoundError:
    import _thread as thread
from abc import ABCMeta


class CoffeeBrewRecipe(object):
    """
    Abstract recipe for brew coffee
    """
    __metaclass__ = ABCMeta

    IMAGE = ""

    def brew(self, mechanism):
        raise NotImplementedError


class EspressoRecipe(CoffeeBrewRecipe):
    IMAGE = "/static/images/espresso.png"

    def brew(self, mechanism):
        """
        Brew espresso coffee if something fails return dict with error messages
        :param mechanism: CoffeeBrewMachine object provides all required mechanism to complete task
        :return: String with path to espresso image, otherwise dict with error messages
        """
        status_coffee = mechanism.make_basic_coffee()
        if isinstance(status_coffee, dict):
            return status_coffee
        return self.IMAGE


class AmericanoRecipe(CoffeeBrewRecipe):
    IMAGE = "/static/images/espresso.png"

    def brew(self, mechanism):
        """
        Brew americano coffee. On start makes normal espresso then add extra amount of boiled water
        :param mechanism: CoffeeBrewMachine object provides all required mechanism to complete task
        :return: : String with path to americano image, otherwise dict with error messages
        """
        status_coffee = mechanism.make_basic_coffee()
        if isinstance(status_coffee, dict):
            return status_coffee
        status_extra_water = mechanism.boiling_water(mechanism.coffee.extra_quantity)
        if isinstance(status_extra_water, dict):
            return status_extra_water
        return self.IMAGE


class LatteRecipe(CoffeeBrewRecipe):
    IMAGE = "/static/images/latte.png"

    def brew(self, mechanism):
        """
        Brew latte coffee. On start makes normal espresso then add foamed milk.
        :param mechanism: CoffeeBrewMachine object provides all required mechanism to complete task
        :return: : String with path to latte image, otherwise dict with error messages
        """
        status_coffee = mechanism.make_basic_coffee()
        if isinstance(status_coffee, dict):
            return status_coffee
        status_milk = mechanism.lather_milk()
        if isinstance(status_milk, dict):
            return status_milk
        return self.IMAGE


class CoffeeBrewMechanism(object):
    """
    Class which combines all mechanism to simulate working coffee mechanism. Provides all required methods.
    This class implements singleton pattern, because only one device stay in virtual kitchen.
    Additionally django view life cycle forces to create object which keeps own state regardless of django view.
    Attributes:
        __lockObj - secure new creation of a new instance, caused thread racing
        __instance - instance of CoffeeBrewMechanism
    """

    __lockObj = thread.allocate_lock()
    __instance = None

    def __new__(cls, *args, **kwargs):
        """
        Create new instance if there is no any instance of this class. Otherwise return saved instance.
        :return: instance of CoffeeBrewMechanism
        """
        # Critical section start
        cls.__lockObj.acquire()
        try:
            if cls.__instance is None:
                cls.__instance = super(CoffeeBrewMechanism, cls).__new__(cls, *args, **kwargs)
        finally:
            cls.__lockObj.release()
        # critical section stop
        return cls.__instance

    def __init__(self):
        """
        Initialize all required devices, which will be used to simulate coffee machine.
        :param methods_brew (dict) - is used for call proper method of brewing coffee.
        :param coffee_method (CoffeeRecipe) - stores class containing recipe of brewing coffee
        """
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
            "latte": LatteRecipe,
        }

    def set_method_for_coffee(self, coffee):
        """
        Set new method of brew coffee
        :param coffee: (Coffee) - model object containing coffee, which client wants to drink
        """
        self.coffee_method = self.methods_brew.get(coffee.coffee_type)()

    def prepare_ground_coffee(self, coffee):
        """
        Run process of grinding beans for coffee. One of the API methods.
        :param coffee: (Coffee) - model object containing coffee, which client wants to drink
        :return: True if successfully completed process, otherwise dict with errors
        """
        self.coffee_grinder.grind_beans(coffee.coffee_quantity)
        return self.coffee_grinder.get_device_errors()

    def boiling_water(self, quantity):
        """
        Run process of boiling water for coffee. One of the API methods.
        :param quantity: (int) - how many water require to brew coffee
        :return: True if successfully completed process, otherwise dict with errors
        """
        self.water_heater.run_process(water_to_boil=quantity)
        return self.water_heater.get_device_errors()

    def prepare_pressure_pump(self):
        """
        Run process of preparing pressure pump.
        :return: True if successfully completed process, otherwise dict with errors
        """
        self.pressure_pump.run_process()
        return self.pressure_pump.get_device_errors()

    def lather_milk(self):
        """
        Run process of lather milk.
        :return: True if successfully completed process, otherwise dict with errors
        """
        self.milk_heater.run_process()
        return self.milk_heater.get_device_errors()

    def is_full_trash_bin(self):
        """
        Run process which checking current capacity of trash bin.
        :return: True if successfully completed process, otherwise dict with errors
        """
        self.trash_bin.is_trash_full()
        return self.trash_bin.get_device_errors()

    def _update_status(self, status):
        """
        Update errors if given arguments is dict.
        :param status: String or dict
        """
        if isinstance(status, dict):
            self.errors.update(status)

    def is_errors(self):
        return self.errors.keys()

    def step_preparing_trash(self):
        """
        First step of making basic coffee, checking current status of trash bin
        :raise OperationException if any errors
        """
        status = self.is_full_trash_bin()
        self._update_status(status)
        if self.is_errors():
            raise OperationException("step_preparing_trash")

    def step_preparing_ground_coffee(self):
        """
        Second step of making basic coffee, prepare ground coffee
        :raise OperationException if any errors
        """
        status = self.prepare_ground_coffee(self.coffee)
        self._update_status(status)
        if self.is_errors():
            raise OperationException("step_preparing_ground_coffee")

    def step_preparing_boiling_water(self):
        """
        Third step of making basic coffee, prepare to boil water
        :raise OperationException if any errors
        """
        status = self.boiling_water(self.coffee.size)
        self._update_status(status)
        if self.is_errors():
            raise OperationException("step_prepairing_boiling_water")

    def step_preparing_pressure_pump(self):
        """
        Fourth step of making basic coffee, prepare to use pressure pump
        :raise OperationException if any errors
        """
        status = self.prepare_pressure_pump()
        self._update_status(status)
        if self.errors.keys():
            raise OperationException("step_preparing_pressure_pump")

    def make_basic_coffee(self):
        """
        Method to make basic coffee, it means one cup of espresso.
        Execute all steps define above. If there is no errors,
        Run last process of brewing coffee
        :return: True if successfully completed brew process, otherwise dict with errors
        """
        try:
            self.step_preparing_trash()
            self.step_preparing_ground_coffee()
            self.step_preparing_boiling_water()
            self.step_preparing_pressure_pump()
        except OperationException as e:
            return self.errors
        return self.run_brew_process()

    def run_brew_process(self):
        """
        Simulation of brew coffee. For prepared ground coffee, hot water is passed though.
        Then coffee flows to cup, wastes going to trash. Process complete
        :return: True
        """
        self.pressure_pump.cleanup()
        self.water_heater.cleanup()
        self.trash_bin.run_process()
        return True

    def make_coffee(self, coffee):
        """
        Method set coffee recipe for given coffee object.
        Run proper brew process and return his status.
        :param coffee: (Coffee) - model object containing coffee, which client wants to drink
        :return: String with path to proper coffee image, otherwise dict with errors
        """
        self.coffee = coffee
        self.set_method_for_coffee(self.coffee)
        status = self.coffee_method.brew(self)
        if isinstance(status, dict):
            return status
        return status

    def refill_water_tank(self):
        """
        Run process of refilling water tank and erase error
        """
        self.water_heater.refill_water_tank()
        if self.errors.get(WaterHeater.ERROR_EMPTY_WATER_TANK):
            del self.errors[WaterHeater.ERROR_EMPTY_WATER_TANK]

    def refill_beans_tank(self):
        """
        Run process of refilling coffee beans tank and erase error
        :return:
        """
        self.coffee_grinder.cleanup()
        if self.errors.get(CoffeeGrinder.ERROR_NOT_ENOUGH_BEANS_TO_GRIND):
            del self.errors[CoffeeGrinder.ERROR_NOT_ENOUGH_BEANS_TO_GRIND]

    def remove_trash_bin(self):
        """
        Run process of removing trash and erase error
        :return:
        """
        self.trash_bin.cleanup()
        if self.errors.get(TrashBin.ERROR_FULL_TRASH):
            del self.errors[TrashBin.ERROR_FULL_TRASH]


class OperationException(Exception):
    """
    Own exception used in preparing stage to stop execute rest of mechanism
    """
    pass
