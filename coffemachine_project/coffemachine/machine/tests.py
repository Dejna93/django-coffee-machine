# Create your tests here.
from django.test import TestCase, Client

from coffemachine_project.coffemachine.machine.handler import PressurePump


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
    pass
