# Create your tests here.
from django.test import TestCase, Client

from coffemachine_project.coffemachine.machine.handler import PressurePump, WaterHeater, MilkHeater, WaterTank, MilkTank, TrashBin, CoffeeGrinder


class MachineTestCases(TestCase):
    def setUp(self):
        self.create_client()

    def create_client(self):
        self.client = Client()


class PressurePump_Test(MachineTestCases):
    def initials(self):
        return PressurePump()

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
    def test_boil_0_water(self):
        heater = WaterHeater()
        self.assertFalse(heater.run_process(water_to_boil=0))

    def test_boil_min_capacity(self):
        heater = WaterHeater()
        self.assertTrue(heater.run_process(water_to_boil=WaterHeater.MIN_CAPACITY))

    def test_boil_normal_capacity(self):
        heater = WaterHeater()
        self.assertTrue(heater.run_process(water_to_boil=WaterHeater.CAPACITY / 2))

    def test_boil_overflow_capacity(self):
        heater = WaterHeater()
        self.assertFalse(heater.run_process(water_to_boil=WaterHeater.CAPACITY + 1))

    def test_boil_couple_times_without_refill(self):
        heater = WaterHeater()
        status = []
        for time in range(WaterTank.CAPACITY // WaterHeater.CAPACITY):
            status.append(heater.run_process(water_to_boil=WaterHeater.CAPACITY))
        self.assertTrue(status[0])
        self.assertTrue(status[-1][WaterHeater.ERROR_EMPTY_WATER_TANK])

    def test_boil_couple_times_with_refill(self):
        heater = WaterHeater()
        status = None
        for _ in range(WaterTank.CAPACITY // WaterHeater.CAPACITY):
            status = heater.run_process(water_to_boil=WaterHeater.CAPACITY)
        self.assertTrue(status[WaterHeater.ERROR_EMPTY_WATER_TANK])
        heater.water_tank.fill_fluid_tank(WaterTank.CAPACITY)
        status = heater.run_process(water_to_boil=WaterHeater.CAPACITY)
        self.assertTrue(status)


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
        self.assertEqual(trash.current_weight, 1)

    def test_throw_away_trash(self):
        trash = TrashBin()
        trash.run_process()
        trash.cleanup()
        self.assertEqual(trash.current_weight, 0)


class CoffeeGrinder_Test(MachineTestCases):
    def test_grind_normal_amount_coffee(self):
        grinder = CoffeeGrinder()
        self.assertTrue(grinder.grind_beans(amount=CoffeeGrinder.CAPACITY / 2))

    def test_grind_0_amount_coffee(self):
        grinder = CoffeeGrinder()
        self.assertFalse(grinder.grind_beans(amount=0))

    def test_grind_over_amount_coffee(self):
        grinder = CoffeeGrinder()
        self.assertFalse(grinder.grind_beans(amount=CoffeeGrinder.CAPACITY + 1))

    def test_grind_couple_times_coffee(self):
        grinder = CoffeeGrinder()
        for amount in range(100, CoffeeGrinder.CAPACITY * 10, 100):
            status = grinder.grind_beans(amount=amount)

        self.assertFalse(status)
