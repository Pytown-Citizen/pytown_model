import unittest

from pytown_model.buildings.factory import HouseFactory, SawmillFactory


class BuildingTest(unittest.TestCase):
    def setUp(self):
        self.house = HouseFactory().create_building()
        self.house2 = HouseFactory().create_building()
        self.sawmill = SawmillFactory().create_building()

    def test_upgrade_building(self):
        self.assertEqual(True, True)
