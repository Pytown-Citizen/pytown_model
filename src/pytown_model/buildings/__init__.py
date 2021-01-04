from __future__ import annotations

import logging

from pytown_core.patterns.behavioral import FSM, IState
from pytown_core.serializers import IJSONSerializable

from ..inventory import Inventory, InventoryFactoryMethod, Item


# Building delegate his behavior to its state
class Building(FSM, IJSONSerializable):
    def __init__(self):
        FSM.__init__(self, InitialState)

    @property
    def name(self):
        return self._state.name

    @property
    def inventory(self):
        return self._state.inventory

    @property
    def construction_inventory(self):
        return self._state.construction_inventory

    @property
    def actions(self):
        return self._state.actions

    @property
    def building_processes(self):
        return self._state.building_processes

    @property
    def building_transactions(self):
        return self._state.building_transactions

    def upgrade(self):
        self._state.upgrade()

    def downgrade(self):
        raise NotImplementedError

    @classmethod
    def from_json_dict(cls, json_dict):
        building = cls()
        state_dict = json_dict["state"]

        building._state = BuildingState.from_json_dict(building, state_dict)
        return building

    def to_json_dict(self):
        json_dict = {}
        json_dict["state"] = self._state.to_json_dict()
        return json_dict


# Fake state to be able to instanciate a building without already define BulidingState #TODO : this should be cleaned at pytown_core.patterns level
class InitialState(IState):
    def do(self):
        pass


# Represent a building state, commonly a level of the building and it's behavior
# (construction required for the next level, transformations possible for a sawmill, actions, ...)
class BuildingState(IState, IJSONSerializable):
    def __init__(
        self,
        building,
        name,
        inventory,
        construction_inventory,
        actions,
        building_processes,
        building_transactions,
    ):
        IState.__init__(self, building)

        self.name = name
        self.inventory = inventory
        self.construction_inventory = construction_inventory
        self.actions = actions
        self.building_processes = building_processes
        self.building_transactions = building_transactions

        self.next_state = None

    def upgrade(self):
        if self.next_state is not None:
            logging.info("Upgrade {} => {}".format(self.name, self.next_state.name))

            # TODO : keep what it is in inventory

            self._fsm._state = self.next_state
        else:
            logging.warning("Building already maximum state")

            self.do()

    def do(self):
        # update inventory
        pass

    @classmethod
    def from_json_dict(cls, building, json_dict):

        name = json_dict["name"]
        inventory = Inventory.from_json_dict(json_dict["inventory"])
        construction_inventory = Inventory.from_json_dict(
            json_dict["construction_inventory"]
        )
        actions = []

        for action in json_dict["actions"]:
            actions.append(Action.from_json_dict(action))

        building_processes = []
        for process in json_dict["building_processes"]:
            building_processes.append(BuildingProcess.from_json_dict(process))

        building_transactions = []
        for transaction in json_dict["building_transactions"]:
            building_transactions.append(
                BuildingTransaction.from_json_dict(transaction)
            )

        building_state = cls(
            building,
            name,
            inventory,
            construction_inventory,
            actions,
            building_processes,
            building_transactions,
        )
        return building_state

    def to_json_dict(self):
        json_dict = {}
        json_dict["name"] = self.name
        json_dict["inventory"] = self.inventory.to_json_dict()
        json_dict["construction_inventory"] = self.construction_inventory.to_json_dict()

        actions = []
        for action in self.actions:
            actions.append(action.to_json_dict())
        json_dict["actions"] = actions

        building_processes = []
        for process in self.building_processes:
            building_processes.append(process.to_json_dict())
        json_dict["building_processes"] = building_processes

        building_transactions = []
        for transaction in self.building_transactions:
            building_transactions.append(transaction.to_json_dict())
        json_dict["building_transactions"] = building_transactions

        return json_dict


# This represent an action you can do inside the building (ex : "sleep")
class Action(IJSONSerializable):
    def __init__(self, name):

        self.name = name

    @classmethod
    def from_json_dict(cls, json_dict):
        return cls(json_dict["name"])

    def to_json_dict(self):
        json_dict = {}
        json_dict["name"] = self.name
        return json_dict


class BuildingProcess(IJSONSerializable):
    def __init__(
        self, item_required: Item, name: str, item_result: Item, energy_required: int
    ):

        self.name = name
        self.item_required = item_required
        self.item_result = item_result
        self.energy_required = energy_required

    def __repr__(self):
        return "{} = {} => {}".format(self.item_required, self.name, self.item_result)

    @classmethod
    def from_json_dict(cls, json_dict):
        return cls(
            Item.from_json_dict(json_dict["item_required"]),
            json_dict["name"],
            Item.from_json_dict(json_dict["item_result"]),
            json_dict["energy_required"],
        )

    def to_json_dict(self):
        json_dict = {}
        json_dict["item_required"] = self.item_required.to_json_dict()
        json_dict["name"] = self.name
        json_dict["item_result"] = self.item_result.to_json_dict()
        json_dict["energy_required"] = self.energy_required
        return json_dict


class BuildingTransaction(IJSONSerializable):
    def __init__(self, item_name: str, buy_price: int, sell_price: int):

        self.item_name = item_name
        self.buy_price = buy_price
        self.sell_price = sell_price

    @classmethod
    def from_json_dict(cls, json_dict):
        return cls(
            json_dict["item_name"], json_dict["buy_price"], json_dict["sell_price"]
        )

    def to_json_dict(self):
        json_dict = {}
        json_dict["item_name"] = self.item_name
        json_dict["buy_price"] = self.buy_price
        json_dict["sell_price"] = self.sell_price
        return json_dict
