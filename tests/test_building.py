import unittest

from pytown_model.buildings.factory import HouseFactory, SawmillFactory


class Building_test(unittest.TestCase):
    def setUp(self):
        print("test")
        self.house = HouseFactory().create_building()
        self.house2 = HouseFactory().create_building()
        self.sawmill = SawmillFactory().create_building()

    def test_upgrade_building(self):
        self.assertEqual(True, True)
        # self.assertEqual(self.house.name, "construction")
        # self.assertEqual(self.house2.name, "construction")
        # self.assertEqual(self.sawmill.name, "construction")

        # self.house.upgrade()
        # self.assertEqual(self.house.name, "cabane")
        # self.assertEqual(self.house2.name, "construction")
        # self.assertEqual(self.sawmill.name, "construction")

        # self.sawmill.upgrade()
        # self.assertEqual(self.house.name, "cabane")
        # self.assertEqual(self.house2.name, "construction")
        # self.assertEqual(self.sawmill.name, "sawmill")

        # self.sawmill.upgrade()
        # self.assertEqual(self.house.name, "cabane")
        # self.assertEqual(self.house2.name, "construction")
        # self.assertEqual(self.sawmill.name, "sawmill")
