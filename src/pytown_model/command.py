from __future__ import annotations

import math
from abc import abstractmethod

from pytown_core.patterns.behavioral import Command
from pytown_core.serializers import IJSONSerializable

from .buildings import BuildingProcess, BuildingTransaction
from .buildings.factory import BuildingFactory
from .check import (
    AvailableCheck,
    AwakenCheck,
    BackgroundBuildCheck,
    BackgroundMovementCheck,
    CheckResult,
    EnergyCheck,
    InventoryAddCheck,
    InventoryRemoveCheck,
    TransactionCheck,
)
from .inventory import Item


class ServerCommand(IJSONSerializable, Command):
    def __init__(self):

        self.client_id = None
        self.town = None  # TODO: will be set by townmanager
        self.check_result = CheckResult()

    def execute(self):
        self._check()

        if self.check_result:
            self._do()

    @abstractmethod
    def _check(self):
        raise NotImplementedError

    @abstractmethod
    def _do(self):
        raise NotImplementedError

    @abstractmethod
    def __repr__(self):
        pass

    @classmethod
    @abstractmethod
    def from_json_dict(cls, json_dict) -> ServerCommand:
        raise NotImplementedError

    def to_json_dict(self) -> dict:
        json_dict = {}
        json_dict["client_id"] = self.client_id
        json_dict["check_result"] = self.check_result.to_json_dict()
        return json_dict

    def to_podsixnet(self):
        podsixnet_dict = self.to_json_dict()
        podsixnet_dict["action"] = "command"
        return podsixnet_dict


class MovePlayerCommand(ServerCommand):

    ENERGY_COST = 1

    def __init__(self, direction: str):
        ServerCommand.__init__(self)

        self._direction = direction

    def __repr__(self):
        msg = "Move ServerCommand : {}".format(self._direction)
        if not self.check_result:
            msg += "\n{}".format(self.check_result)
        return msg

    def _check(self):
        player = self.town.get_player(self.client_id)
        EnergyCheck(player, MovePlayerCommand.ENERGY_COST).check(self.check_result)

        AvailableCheck(player).check(self.check_result)

        for tile in self._get_tiles_coordinates_dict().values():
            if tile not in self.town.backgrounds.keys():
                self.check_result += "tile {} not in town".format(tile)
                return

            BackgroundMovementCheck(self.town.backgrounds[tile], player).check(
                self.check_result
            )

    def _do(self):

        (x_dest, y_dest) = self.tile_dest
        player = self.town.get_player(self.client_id)
        player.status = "move"
        player.direction = self._direction
        player.energy.value -= MovePlayerCommand.ENERGY_COST

        player.x = x_dest
        player.y = y_dest

    @property
    def tile_dest(self) -> tuple:
        movement_matrix = {}
        movement_matrix["left"] = (-1, 0)
        movement_matrix["right"] = (+1, 0)
        movement_matrix["up"] = (0, -1)
        movement_matrix["down"] = (0, +1)

        player = self.town.get_player(self.client_id)
        tile = self.town.get_player_tile(self.client_id)
        background = self.town.backgrounds[tile]

        bg_multiplicator = background.move_multiplicator
        x_dest = (
            player.x
            + movement_matrix[self._direction][0] * bg_multiplicator * player.velocity
        )
        y_dest = (
            player.y
            + movement_matrix[self._direction][1] * bg_multiplicator * player.velocity
        )

        return (x_dest, y_dest)

    def _get_tiles_coordinates_dict(self):

        (x_dest, y_dest) = self.tile_dest

        tiles_coordinates_dict = {
            "topleft": (math.floor(x_dest), math.floor(y_dest)),
            "topright": (math.floor(x_dest + 0.99), math.floor(y_dest)),
            "bottomleft": (math.floor(x_dest), math.floor(y_dest + 0.99)),
            "bottomright": (math.floor(x_dest + 0.99), math.floor(y_dest + 0.99)),
        }
        return tiles_coordinates_dict

    @classmethod
    def from_json_dict(cls, json_dict) -> MovePlayerCommand:
        return cls(json_dict["direction"])

    def to_json_dict(self):
        json_dict = super().to_json_dict()
        json_dict["command"] = "move"
        json_dict["direction"] = self._direction
        return json_dict


class BuildCommand(ServerCommand):
    def __init__(self, tile: tuple, building_name: str):
        ServerCommand.__init__(self)

        self._tile = tile
        self._building_name = building_name

    def _check(self):

        player = self.town.get_player(self.client_id)
        AvailableCheck(player).check(self.check_result)

        if self._tile not in self.town.backgrounds:
            self.check_result += "tile {} not in town".format(self._tile)
            return

        background = self.town.backgrounds[self._tile]
        BackgroundBuildCheck(background, self._building_name).check(self.check_result)

        if self._tile in self.town.buildings:
            self.check_result += "Can't build {} : {} already built on {}".format(
                self._building_name, self.town.buildings[self._tile].name, self._tile
            )

    def _do(self):
        self.town.set_building(
            BuildingFactory.create_building_by_name(self._building_name), self._tile
        )

    def __repr__(self):
        msg = "Build ServerCommand : {} in {}".format(self._building_name, self._tile)
        if not self.check_result:
            msg += "\n{}".format(self.check_result)
        return msg

    @classmethod
    def from_json_dict(cls, json_dict: dict) -> BuildCommand:
        return cls(json_dict["tile"], json_dict["building_name"])

    def to_json_dict(self):
        json_dict = super().to_json_dict()
        json_dict["command"] = "build"
        json_dict["building_name"] = self._building_name
        json_dict["tile"] = self._tile
        return json_dict


class CollectResourceCommand(ServerCommand):

    ENERGY_COST = 30

    def __init__(self, tile: tuple, item: Item):
        ServerCommand.__init__(self)

        self._tile = tile
        self._item = item

    def _check(self):
        player = self.town.get_player(self.client_id)

        AvailableCheck(player).check(self.check_result)

        if self._tile not in self.town.resources:
            self.check_result += "No resource in {}".format(self._tile)
            return

        resource = self.town.resources[self._tile]

        TransactionCheck(resource, player, self._item).check(self.check_result)

        EnergyCheck(player, CollectResourceCommand.ENERGY_COST).check(self.check_result)

    def _do(self):
        player = self.town.get_player(self.client_id)
        player.inventory.add_item(self._item)
        resource = self.town.resources[self._tile]
        resource.inventory.remove_item(self._item)
        player.energy.value -= CollectResourceCommand.ENERGY_COST

    def __repr__(self):
        msg = "Collect Resource ServerCommand : {}".format(self._item)
        if not self.check_result:
            msg += "\n{}".format(self.check_result)
        return msg

    @classmethod
    def from_json_dict(cls, json_dict: dict) -> CollectResourceCommand:
        return cls(json_dict["tile"], Item.from_json_dict(json_dict["item"]))

    def to_json_dict(self) -> dict:
        json_dict = super().to_json_dict()
        json_dict["command"] = "collect"
        json_dict["tile"] = self._tile
        json_dict["item"] = self._item.to_json_dict()
        return json_dict


class BuildingProcessCommand(ServerCommand):
    def __init__(self, tile: tuple, building_process: BuildingProcess):
        ServerCommand.__init__(self)

        self._tile = tile
        self._building_process = building_process

    def _check(self):

        player = self.town.get_player(self.client_id)
        AvailableCheck(player).check(self.check_result)

        if self._tile not in self.town.buildings:
            self.check_result += "No building on {}".format(self._tile)
            return

        building = self.town.buildings[self._tile]
        player = self.town.get_player(self.client_id)

        InventoryRemoveCheck(
            building.inventory, self._building_process.item_required
        ).check(self.check_result)
        InventoryAddCheck(building.inventory, self._building_process.item_result).check(
            self.check_result
        )
        EnergyCheck(player, self._building_process.energy_required).check(
            self.check_result
        )

    def _do(self):
        building = self.town.buildings[self._tile]
        building.inventory.remove_item(self._building_process.item_required)
        building.inventory.add_item(self._building_process.item_result)
        player = self.town.get_player(self.client_id)
        player.energy.value -= self._building_process.energy_required

    def __repr__(self):
        msg = "BuildingProcessCommand ServerCommand {}".format(self._building_process)
        if not self.check_result:
            msg += "\n{}".format(self.check_result)
        return msg

    @classmethod
    def from_json_dict(cls, json_dict):
        return cls(
            json_dict["tile"],
            BuildingProcess.from_json_dict(json_dict["building_process"]),
        )

    def to_json_dict(self):
        json_dict = super().to_json_dict()
        json_dict["command"] = "building_process"
        json_dict["tile"] = self._tile
        json_dict["building_process"] = self._building_process.to_json_dict()
        return json_dict


class BuyCommand(ServerCommand):
    def __init__(self, tile: tuple, transaction: BuildingTransaction):
        ServerCommand.__init__(self)

        self._tile = tile
        self._transaction = transaction

    def _check(self):
        building = self.town.buildings[self._tile]
        player = self.town.get_player(self.client_id)

        item = Item(self._transaction.item_name, 1)

        AvailableCheck(player).check(self.check_result)

        TransactionCheck(building, player, item).check(self.check_result)

    def _do(self):
        item = Item(self._transaction.item_name, 1)
        building = self.town.buildings[self._tile]
        player = self.town.get_player(self.client_id)
        building.inventory.remove_item(item)
        player.inventory.add_item(item)

    def __repr__(self):
        msg = "BuyCommand ServerCommand {}".format(self._transaction.item_name)
        if not self.check_result:
            msg += "\n{}".format(self.check_result)
        return msg

    @classmethod
    def from_json_dict(cls, json_dict):
        return cls(
            json_dict["tile"],
            BuildingTransaction.from_json_dict(json_dict["transaction"]),
        )

    def to_json_dict(self):
        json_dict = super().to_json_dict()
        json_dict["command"] = "buy"
        json_dict["tile"] = self._tile
        json_dict["transaction"] = self._transaction.to_json_dict()
        return json_dict


class SellCommand(ServerCommand):
    def __init__(self, tile: tuple, transaction: BuildingTransaction):
        ServerCommand.__init__(self)

        self._tile = tile
        self._transaction = transaction

    def _check(self):
        building = self.town.buildings[self._tile]
        player = self.town.get_player(self.client_id)

        item = Item(self._transaction.item_name, 1)

        AvailableCheck(player).check(self.check_result)
        TransactionCheck(player, building, item).check(self.check_result)

    def _do(self):
        item = Item(self._transaction.item_name, 1)
        building = self.town.buildings[self._tile]
        player = self.town.get_player(self.client_id)
        building.inventory.add_item(item)
        player.inventory.remove_item(item)

    def __repr__(self):
        msg = "SellCommand ServerCommand {}".format(self._transaction.item_name)
        if not self.check_result:
            msg += "\n{}".format(self.check_result)
        return msg

    @classmethod
    def from_json_dict(cls, json_dict):
        return cls(
            json_dict["tile"],
            BuildingTransaction.from_json_dict(json_dict["transaction"]),
        )

    def to_json_dict(self):
        json_dict = super().to_json_dict()
        json_dict["command"] = "sell"
        json_dict["tile"] = self._tile
        json_dict["transaction"] = self._transaction.to_json_dict()
        return json_dict


class BuildBuildingCommand(ServerCommand):

    ENERGY_COST = 20

    def __init__(self, tile: tuple, item: Item):
        ServerCommand.__init__(self)

        self._item = item
        self._tile = tile

    def _check(self):
        building = self.town.buildings[self._tile]
        player = self.town.get_player(self.client_id)

        AvailableCheck(player).check(self.check_result)

        EnergyCheck(player, BuildBuildingCommand.ENERGY_COST).check(self.check_result)
        TransactionCheck(building, building, self._item).check(self.check_result)

    def _do(self):
        building = self.town.buildings[self._tile]
        player = self.town.get_player(self.client_id)

        player.energy.value -= BuildBuildingCommand.ENERGY_COST
        building.inventory.remove_item(self._item)
        building.construction_inventory.add_item(self._item)

    def __repr__(self):
        msg = "Build Building ServerCommand {}".format(self._item)
        if not self.check_result:
            msg += "\n{}".format(self.check_result)
        return msg

    @classmethod
    def from_json_dict(cls, json_dict):
        return cls(json_dict["tile"], Item.from_json_dict(json_dict["item"]))

    def to_json_dict(self):
        json_dict = super().to_json_dict()
        json_dict["command"] = "build_building"
        json_dict["tile"] = self._tile
        json_dict["item"] = self._item.to_json_dict()
        return json_dict


class UpgradeBuildingCommand(ServerCommand):
    def __init__(self, tile: tuple):
        ServerCommand.__init__(self)

        self._tile = tile

    def _check(self):
        building = self.town.buildings[self._tile]
        player = self.town.get_player(self.client_id)
        AvailableCheck(player).check(self.check_result)

        if not building.construction_inventory.is_full():
            self.check_result += "construction not finished"

    def _do(self):
        building = self.town.buildings[self._tile]
        building.upgrade()

    def __repr__(self):
        msg = "Upgrade Building ServerCommand {}".format(self._tile)
        if not self.check_result:
            msg += "\n{}".format(self.check_result)
        return msg

    @classmethod
    def from_json_dict(cls, json_dict):
        return cls(json_dict["tile"])

    def to_json_dict(self):
        json_dict = super().to_json_dict()
        json_dict["command"] = "upgrade_building"
        json_dict["tile"] = self._tile
        return json_dict


class SleepCommand(ServerCommand):

    ENERGY_REGEN_IN_HOUSE = 4
    ENERGY_REGEN_IN_GROUND = 2

    def __init__(self):
        ServerCommand.__init__(self)

    def _check(self):

        tile = self.town.get_player_tile(self.client_id)

        # Player not in building
        if tile in self.town.buildings and self.town.buildings[tile].name != "cabane":
            self.check_result += "Can't sleep in building"

    def _do(self):

        player = self.town.get_player(self.client_id)
        tile = self.town.get_player_tile(self.client_id)

        # Change player sprite
        player.status = "sleep"
        player.energy.regen = SleepCommand.ENERGY_REGEN_IN_GROUND

        # Change energy regeneration depending on where he sleeps
        if tile in self.town.buildings and self.town.buildings[tile].name == "cabane":
            player.energy.regen = SleepCommand.ENERGY_REGEN_IN_HOUSE

    def __repr__(self):
        msg = "Sleep command. Player id: {}".format(self.client_id)
        if not self.check_result:
            msg += "\n{}".format(self.check_result)
        return msg

    @classmethod
    def from_json_dict(cls, json_dict: dict) -> SleepCommand:
        return cls()

    def to_json_dict(self):
        json_dict = super().to_json_dict()
        json_dict["command"] = "sleep"
        return json_dict


class WakeUpCommand(ServerCommand):
    def __init__(self):
        ServerCommand.__init__(self)

    def _check(self):

        player = self.town.get_player(self.client_id)

        is_sleeping_check = CheckResult()
        AwakenCheck(player).check(is_sleeping_check)

        if is_sleeping_check is False:
            self.check_result += "{} is already awake".format(player.name)

    def _do(self):

        player = self.town.get_player(self.client_id)
        player.status = "idle"

        player.energy.reset_regen()

    def __repr__(self):
        msg = "Wake up command. Player id: {}".format(self.client_id)
        if not self.check_result:
            msg += "\n{}".format(self.check_result)
        return msg

    @classmethod
    def from_json_dict(cls, json_dict: dict) -> WakeUpCommand:
        return cls()

    def to_json_dict(self):
        json_dict = super().to_json_dict()
        json_dict["command"] = "wakeup"
        return json_dict


class HelpPlayerCommand(ServerCommand):

    ENERGY_TO_HELP = 20
    HEALTH_TO_GIVE = 1

    def __init__(self, player_to_help_id):
        ServerCommand.__init__(self)

        self._player_to_help_id = player_to_help_id

    def _check(self):
        player = self.town.get_player(self.client_id)
        AvailableCheck(player).check(self.check_result)

        # The two players id exists in the town ?
        if self.client_id not in self.town.players.keys():
            self.check_result += "Player {} does not exist".format(self.client_id)
            return

        if self._player_to_help_id not in self.town.players.keys():
            self.check_result += "Player {} does not exist".format(
                self._player_to_help_id
            )
            return

        # Check if the two players are in the same tile
        if self.town.get_player_tile(self.client_id) != self.town.get_player_tile(
            self._player_to_help_id
        ):
            self.check_result += "Players {} and {} are not in the same tile".format(
                self.client_id, self._player_to_help_id
            )
            return

        # Check if I have enough energy to help
        EnergyCheck(
            self.town.get_player(self.client_id), HelpPlayerCommand.ENERGY_TO_HELP
        ).check(self.check_result)

        # Check if patient doesn't have health
        is_alive_check = CheckResult()
        AvailableCheck(self.town.get_player(self._player_to_help_id)).check(
            is_alive_check
        )

        if is_alive_check:
            self.check_result += "{} has enough health to keep moving".format(
                self._player_to_help_id
            )

    def _do(self):

        player_helper = self.town.get_player(self.client_id)
        player_helper.energy.value -= HelpPlayerCommand.ENERGY_TO_HELP

        player_to_help = self.town.get_player(self._player_to_help_id)
        player_to_help.health.value += HelpPlayerCommand.HEALTH_TO_GIVE

    def __repr__(self):
        msg = "HelpPlayerCommand: try to help {}".format(self._player_to_help_id)
        if not self.check_result:
            msg += "\n{}".format(self.check_result)
        return msg

    @classmethod
    def from_json_dict(cls, json_dict: dict) -> HelpPlayerCommand:
        return cls(json_dict["player_to_help_id"])

    def to_json_dict(self):
        json_dict = super().to_json_dict()
        json_dict["command"] = "help"
        json_dict["player_to_help_id"] = self._player_to_help_id
        return json_dict


class CommandsFactory:

    COMMANDS_DICT = {}
    COMMANDS_DICT["move"] = MovePlayerCommand
    COMMANDS_DICT["build"] = BuildCommand
    COMMANDS_DICT["collect"] = CollectResourceCommand
    COMMANDS_DICT["building_process"] = BuildingProcessCommand
    COMMANDS_DICT["buy"] = BuyCommand
    COMMANDS_DICT["sell"] = SellCommand
    COMMANDS_DICT["build_building"] = BuildBuildingCommand
    COMMANDS_DICT["upgrade_building"] = UpgradeBuildingCommand
    COMMANDS_DICT["help"] = HelpPlayerCommand
    COMMANDS_DICT["sleep"] = SleepCommand
    COMMANDS_DICT["wakeup"] = WakeUpCommand

    @staticmethod
    def from_podsixnet(podsixnet_dict):

        if podsixnet_dict["command"] in CommandsFactory.COMMANDS_DICT:
            command = CommandsFactory.COMMANDS_DICT[
                podsixnet_dict["command"]
            ].from_json_dict(podsixnet_dict)
        else:
            raise NotImplementedError

        command.client_id = podsixnet_dict["client_id"]
        command.check_result = CheckResult.from_json_dict(
            podsixnet_dict["check_result"]
        )
        return command
