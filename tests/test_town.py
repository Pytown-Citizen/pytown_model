import unittest
from pytown_model.town import TownCreator, Town


class Town_test(unittest.TestCase):
    def setUp(self):
        self.town = TownCreator.create_default_town(6, 4)

    def test_size(self):
        self.assertEqual(self.town.get_tiles_w(), 6)
        self.assertEqual(self.town.get_tiles_h(), 4)

    # def test_iter_town(self):
    #     check_str = ""
    #     for background in self.town.backgrounds.values():
    #         check_str += repr(background)
    #     self.assertEqual(len(self.town), 24)
    #     self.assertEqual(check_str, "GGGGGGGGGGGGRRRRRRWWWWWW")

    # def test_json_dict_serialize_deserialize(self):
    #     town_dict = self.town.to_json_dict()
    #     print(town_dict)

    #     self.assertDictEqual(town_dict, {'name': 'testown', 'backgrounds': {(0, 0): {'name': 'grass', 'cat': 'backgrounds'}, (1, 0): {'name': 'grass', 'cat': 'backgrounds'}, (2, 0): {'name': 'grass', 'cat': 'backgrounds'}, (3, 0): {'name': 'grass', 'cat': 'backgrounds'}, (4, 0): {'name': 'grass', 'cat': 'backgrounds'}, (5, 0): {'name': 'grass', 'cat': 'backgrounds'}, (0, 1): {'name': 'grass', 'cat': 'backgrounds'}, (1, 1): {'name': 'grass', 'cat': 'backgrounds'}, (2, 1): {'name': 'grass', 'cat': 'backgrounds'}, (3, 1): {'name': 'grass', 'cat': 'backgrounds'}, (4, 1): {'name': 'grass', 'cat': 'backgrounds'}, (5, 1): {'name': 'grass', 'cat': 'backgrounds'}, (0, 2): {'name': 'road', 'cat': 'backgrounds'}, (1, 2): {'name': 'road', 'cat': 'backgrounds'}, (2, 2): {'name': 'road', 'cat': 'backgrounds'}, (3, 2): {'name': 'road', 'cat': 'backgrounds'}, (4, 2): {'name': 'road', 'cat': 'backgrounds'}, (5, 2): {'name': 'road', 'cat': 'backgrounds'}, (0, 3): {'name': 'water', 'cat': 'backgrounds'}, (1, 3): {'name': 'water', 'cat': 'backgrounds'}, (2, 3): {'name': 'water', 'cat': 'backgrounds'}, (3, 3): {'name': 'water', 'cat': 'backgrounds'}, (4, 3): {'name': 'water', 'cat': 'backgrounds'}, (5, 3): {'name': 'water', 'cat': 'backgrounds'}}, 'resources': {(0, 0): {'name': 'grass', 'cat': 'backgrounds'}, (1, 0): {'name': 'grass', 'cat': 'backgrounds'}, (2, 0): {'name': 'grass', 'cat': 'backgrounds'}, (3, 0): {'name': 'grass', 'cat': 'backgrounds'}, (4, 0): {'name': 'grass', 'cat': 'backgrounds'}, (5, 0): {'name': 'grass', 'cat': 'backgrounds'}, (0, 1): {'name': 'grass', 'cat': 'backgrounds'}, (1, 1): {'name': 'grass', 'cat': 'backgrounds'}, (2, 1): {'name': 'grass', 'cat': 'backgrounds'}, (3, 1): {'name': 'grass', 'cat': 'backgrounds'}, (4, 1): {'name': 'grass', 'cat': 'backgrounds'}, (5, 1): {'name': 'grass', 'cat': 'backgrounds'}, (0, 2): {'name': 'road', 'cat': 'backgrounds'}, (1, 2): {'name': 'road', 'cat': 'backgrounds'}, (2, 2): {'name': 'road', 'cat': 'backgrounds'}, (3, 2): {'name': 'road', 'cat': 'backgrounds'}, (4, 2): {'name': 'road', 'cat': 'backgrounds'}, (5, 2): {'name': 'road', 'cat': 'backgrounds'}, (0, 3): {'name': 'water', 'cat': 'backgrounds'}, (1, 3): {'name': 'water', 'cat': 'backgrounds'}, (2, 3): {'name': 'water', 'cat': 'backgrounds'}, (3, 3): {'name': 'water', 'cat': 'backgrounds'}, (4, 3): {'name': 'water', 'cat': 'backgrounds'}, (5, 3): {'name': 'water', 'cat': 'backgrounds'}}, 'buildings': {}, 'characters': {}, 'players': {}})
    #     clone = Town.from_json_dict(town_dict)
    #     self.assertDictEqual(clone.to_json_dict(), self.town.to_json_dict())
