# Create your tests here.
from collections import defaultdict

from django.test import TestCase, Client

from coffemachine.machine.container import WaterTank, MilkTank
from coffemachine.machine.devices import PressurePump, WaterHeater, MilkHeater, TrashBin, CoffeeGrinder
from coffemachine.machine.handler import CoffeeBrewMechanism, AmericanoRecipe, LatteRecipe, EspressoRecipe
from coffemachine.machine.models import Coffee


class MachineTestCases(TestCase):
    def setUp(self):
        self.create_client()

    def create_client(self):
        self.client = Client()


class PressurePump_Test(MachineTestCases):
    def test_initial_device(self):
        pressurepomp = PressurePump()
        self.assertTrue(pressurepomp.run_process())

    def test_check_cleanup_after_process(self):
        pressurepomp = PressurePump()
        status = pressurepomp.run_process()
        pressurepomp.cleanup()
        self.assertTrue(status)
        self.assertEqual(pressurepomp.current_pressure, 1)


class WaterHeater_Test(MachineTestCases):

    def boil_some_water(self, water_to_boil):
        heater = WaterHeater()
        heater.run_process(water_to_boil=water_to_boil)
        self.assertFalse(heater.get_device_errors())

    def test_boil_0_water(self):
        heater = WaterHeater()
        heater.run_process(water_to_boil=0)
        self.assertTrue(heater.get_device_errors()[WaterHeater.ERROR_NOT_ENOUGH_WATER_TO_BOIL])

    def test_boil_normal_capacity(self):
        self.boil_some_water(WaterHeater.CAPACITY / 2)

    def test_boil_overflow_capacity(self):
        heater = WaterHeater()
        self.assertFalse(heater.run_process(water_to_boil=WaterHeater.CAPACITY + 1))

    def test_boil_couple_times_without_refill(self):
        heater = WaterHeater()
        status = []
        for time in range(WaterTank.CAPACITY // WaterHeater.CAPACITY):
            heater.run_process(water_to_boil=WaterHeater.CAPACITY)
            status.append(heater.get_device_errors())
        self.assertFalse(status[0])
        self.assertTrue(status[-1][WaterHeater.ERROR_EMPTY_WATER_TANK])

    def test_boil_couple_times_with_refill(self):
        heater = WaterHeater()
        for _ in range(WaterTank.CAPACITY // WaterHeater.CAPACITY):
            heater.run_process(water_to_boil=WaterHeater.CAPACITY)
        self.assertTrue(heater.get_device_errors()[WaterHeater.ERROR_EMPTY_WATER_TANK])
        heater.water_tank.fill_tank(WaterTank.CAPACITY)
        status = heater.run_process(water_to_boil=WaterHeater.CAPACITY)
        self.assertFalse(status)


class MilkHeater_Test(MachineTestCases):
    def test_lather_milk_enough_water(self):
        heater = WaterHeater()
        milk_heater = MilkHeater(heater)
        self.assertTrue(milk_heater.run_process())

    def test_lather_milk_couple_times(self):
        heater = WaterHeater()
        milk_heater = MilkHeater(heater)
        for _ in range(MilkTank.CAPACITY // MilkHeater.CAPACITY):
            milk_heater.run_process()
        self.assertTrue(milk_heater._errors)

    def test_lather_milk_couple_times_with_refill_milk(self):
        heater = WaterHeater()
        milk_heater = MilkHeater(heater)
        for _ in range((MilkTank.CAPACITY // MilkHeater.CAPACITY) + 1):
            milk_heater.run_process()
        self.assertTrue(milk_heater._errors[milk_heater.ERROR_EMPTY_MILK_TANK])
        milk_heater.fill_milk()
        self.assertTrue(milk_heater.run_process())


class TrashBin_Test(MachineTestCases):
    def test_init_trash(self):
        trash = TrashBin()
        trash.run_process()
        self.assertEqual(trash.current_level, 1)

    def test_throw_away_trash(self):
        trash = TrashBin()
        trash.run_process()
        trash.cleanup()
        self.assertEqual(trash.current_level, 0)


class CoffeeGrinder_Test(MachineTestCases):
    def grind_amount_of_coffee(self, coffee):
        grinder = CoffeeGrinder()
        self.assertTrue(grinder.grind_beans(amount=coffee))

    def test_grind_normal_amount_coffee(self):
        self.grind_amount_of_coffee(CoffeeGrinder.CAPACITY / 2)

    def test_grind_0_amount_coffee(self):
        grinder = CoffeeGrinder()
        self.assertFalse(grinder.grind_beans(amount=0))

    def test_grind_over_amount_coffee(self):
        grinder = CoffeeGrinder()
        self.assertFalse(grinder.grind_beans(amount=CoffeeGrinder.CAPACITY + 1))

    def test_grind_couple_times_coffee(self):
        grinder = CoffeeGrinder()
        status = None
        for amount in range(100, CoffeeGrinder.CAPACITY * 10, 100):
            status = grinder.grind_beans(amount=amount)

        self.assertFalse(status)


class WaterTank_Test(MachineTestCases):
    def test_init_water_tank(self):
        tank = WaterTank()
        self.assertEqual(tank.content_level, WaterTank.CAPACITY)

    def test_fill_liquid_tank__minus_capacity(self):
        tank = WaterTank()
        with self.assertRaisesMessage(ValueError, "It is possible to have minus something in bottle?"):
            tank.fill_tank(-100)

    def test_fill_liquid_tank__0_capacity(self):
        tank = WaterTank()
        capacity = tank.content_level
        self.assertEqual(capacity, WaterTank.CAPACITY)
        tank.fill_tank(0)
        self.assertEqual(capacity, WaterTank.CAPACITY)

    def test_fill_liquid_tank__normal_capacity(self):
        tank = WaterTank()
        initial_value = WaterTank.CAPACITY * 0.1
        additional_value = WaterTank.CAPACITY // 4
        tank.content_level = initial_value  # simiul proces of gettting fluid
        self.assertEqual(tank.content_level, initial_value)
        tank.fill_tank(additional_value)
        self.assertEqual(tank.content_level, initial_value + additional_value)

    def test_fill_liquid_tank__above_capacity(self):
        tank = WaterTank()
        self.assertFalse(tank.fill_tank(100)[0])
        self.assertEqual(tank.content_level, WaterTank.CAPACITY)


class CoffeeBrewMechanism_Test(MachineTestCases):
    fixtures = ['coffee.json']

    def test_espresso_init(self):
        coffee = Coffee.objects.get(coffee_type="espresso")
        brew_mechanism = CoffeeBrewMechanism()
        self.assertEqual(brew_mechanism.make_coffee(coffee), EspressoRecipe.IMAGE)

    def test_make_couple_cups_of_espresso_coffee(self):
        coffee = Coffee.objects.get(coffee_type="espresso")
        brew_mechanism = CoffeeBrewMechanism()
        status = defaultdict(lambda: False)
        for _ in range(5):
            status = brew_mechanism.make_coffee(coffee)
        self.assertTrue(status[WaterHeater.ERROR_EMPTY_WATER_TANK])

    def test_americano_init(self):
        coffee = Coffee.objects.get(coffee_type="americano")
        brew_mechanism = CoffeeBrewMechanism()
        self.assertEqual(brew_mechanism.make_coffee(coffee), AmericanoRecipe.IMAGE)

    def test_make_couple_cups_of_americano_coffee(self):
        coffee = Coffee.objects.get(coffee_type="americano")
        brew_mechanism = CoffeeBrewMechanism()
        status = defaultdict(lambda: False)
        for _ in range(5):
            status = brew_mechanism.make_coffee(coffee)
        self.assertTrue(status[WaterHeater.ERROR_EMPTY_WATER_TANK])

    def test_late_init(self):
        coffee = Coffee.objects.get(coffee_type="latte")
        brew_mechanism = CoffeeBrewMechanism()
        self.assertEqual(brew_mechanism.make_coffee(coffee), LatteRecipe.IMAGE)

    def test_make_couple_cups_of_late_coffee(self):
        coffee = Coffee.objects.get(coffee_type="latte")
        brew_mechanism = CoffeeBrewMechanism()
        status = defaultdict(lambda: False)
        for _ in range(5):
            status = brew_mechanism.make_coffee(coffee)
        self.assertTrue(status[WaterHeater.ERROR_EMPTY_WATER_TANK])
