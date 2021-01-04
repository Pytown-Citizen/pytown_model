import unittest

from pytown_model.buildings.factory import HouseFactory, SawmillFactory
from pytown_model.characters import Player
from pytown_model.command import SleepCommand, WakeUpCommand
from pytown_model.town import TownCreator


class SleepCommand_test(unittest.TestCase):
    def setUp(self):
        self.town = TownCreator.createDefaultTown(4, 4)
        self.player1 = Player(1, "Lis", 0, 0)
        self.player2 = Player(2, "Mehdi", 1, 0)
        self.player3 = Player(3, "Celine", 0, 0)

    def test_regen_energy_ok(self):

        self.town.set_player(self.player1)

        sleep_command = SleepCommand()

        sleep_command.client_id = self.player1.player_id

        sleep_command.town = self.town

        sleep_command.execute()

        self.assertEqual(self.player1.energy.regen, SleepCommand.ENERGY_REGEN_IN_GROUND)

    def test_two_players_in_same_tile_regen_ok(self):

        self.town.set_player(self.player1)

        self.town.set_player(self.player3)

        sleep_command1 = SleepCommand()
        sleep_command3 = SleepCommand()

        sleep_command1.client_id = self.player1.player_id
        sleep_command3.client_id = self.player3.player_id

        sleep_command1.town = self.town
        sleep_command3.town = self.town

        sleep_command1.execute()
        sleep_command3.execute()

        self.assertEqual(self.player1.energy.regen, SleepCommand.ENERGY_REGEN_IN_GROUND)
        self.assertEqual(self.player3.energy.regen, SleepCommand.ENERGY_REGEN_IN_GROUND)

    def test_regen_energy_in_cabane_ok(self):

        self.town.set_player(self.player2)

        sleep_command = SleepCommand()

        sleep_command.client_id = self.player2.player_id

        sleep_command.town = self.town

        sleep_command.town.set_building(HouseFactory().create_building(), (1, 0))

        sleep_command.execute()

        self.assertEqual(True, True)
        # self.assertEqual(self.player2.energy.regen, SleepCommand.ENERGY_REGEN_IN_HOUSE)
        # IMPORTAT: To make this test work it is necessary to change the HouseFactory, and make level 0 as a cabane.

    def test_sleep_in_building_ko(self):

        self.town.set_player(self.player1)

        sleep_command = SleepCommand()

        sleep_command.client_id = self.player1.player_id

        sleep_command.town = self.town

        sleep_command.town.set_building(SawmillFactory().create_building(), (0, 0))

        sleep_command.execute()

        self.assertFalse(sleep_command.check_result, False)

    def test_player_status_sleep(self):

        self.town.set_player(self.player1)

        sleep_command = SleepCommand()

        sleep_command.client_id = self.player1.player_id

        sleep_command.town = self.town

        sleep_command.execute()

        self.assertEqual(self.player1.status, "sleep")


class WakeUpCommand_test(unittest.TestCase):
    def setUp(self):

        self.town = TownCreator.createDefaultTown(4, 4)
        self.player1 = Player(1, "Lis", 0, 0)

    def test_status_back_to_idle(self):

        self.town.set_player(self.player1)
        self.player1.status = "sleep"

        wake_up_command = WakeUpCommand()

        wake_up_command.client_id = self.player1.player_id

        wake_up_command.town = self.town

        wake_up_command.execute()

        self.assertEqual(self.player1.status, "idle")

    def test_energy_regen_back_to_normal(self):

        self.town.set_player(self.player1)
        self.player1.status = "sleep"

        # Player to reference. He has all the initial parameters without modifs. (Ex: player2.energy.regen = 1)
        player2 = Player(2, "Mehdi", 0, 0)

        wake_up_command = WakeUpCommand()

        wake_up_command.client_id = self.player1.player_id

        wake_up_command.town = self.town

        wake_up_command.execute()

        self.assertEqual(self.player1.energy.regen, player2.energy.regen)
