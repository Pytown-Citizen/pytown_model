import unittest

from pytown_model.characters import PlayerStatus


class PlayerStatus_test(unittest.TestCase):
    def setUp(self):
        self.player_status = PlayerStatus(10, 100, 5)

    def test_init(self):
        self.assertEqual(self.player_status.value, 10)
        self.assertEqual(self.player_status.value_max, 100)
        self.assertEqual(self.player_status.regen, 5)

    def test_value_limit(self):
        self.player_status.value_limit = 80
        self.assertEqual(self.player_status.value_limit, 80)
        self.player_status.value_limit = 120
        self.assertEqual(self.player_status.value_limit, 100)

    def test_regenerate(self):
        self.player_status.regenerate()
        self.assertEqual(self.player_status.value, 15)
        self.player_status.value_limit = 17
        self.player_status.regenerate()
        self.assertEqual(self.player_status.value, 17)

    def test_to_json(self):
        self.player_status.value_limit = 90
        json_dict = self.player_status.to_json_dict()
        self.assertEqual(
            json_dict,
            {
                "value": 10,
                "value_max": 100,
                "regen": 5,
                "regen_base": 5,
                "value_limit": 90,
            },
        )
        self.player_status.regenerate()
        json_dict = self.player_status.to_json_dict()
        self.assertEqual(
            json_dict,
            {
                "value": 15,
                "value_max": 100,
                "regen": 5,
                "regen_base": 5,
                "value_limit": 90,
            },
        )

    def test_from_json(self):
        player_status = PlayerStatus.from_json_dict(
            {
                "value": 15,
                "value_max": 100,
                "regen": 5,
                "regen_base": 5,
                "value_limit": 90,
            }
        )
        self.assertIsInstance(player_status, PlayerStatus)
        self.assertEqual(player_status.value, 15)
        self.assertEqual(player_status.value_max, 100)
        self.assertEqual(player_status.value_limit, 90)
        self.assertEqual(player_status.regen, 5)
        self.assertEqual(player_status.regen_base, 5)
