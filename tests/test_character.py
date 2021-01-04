import unittest

from pytown_model.characters import Character


class Character_test(unittest.TestCase):
    def setUp(self):
        self.character = Character("test")

    def test_json_serialize_deserialize(self):
        json_dict = self.character.to_json_dict()

        self.assertDictEqual(
            json_dict, {"name": "test", "direction": "down", "status": "idle"}
        )

        clone = Character.from_json_dict(json_dict)
        self.assertEqual(clone.name, self.character.name)
        self.assertEqual(clone.direction, self.character.direction)
        self.assertEqual(clone.status, self.character.status)
