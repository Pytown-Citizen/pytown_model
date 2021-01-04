from __future__ import annotations

from abc import ABC

from ..inventory import Inventory, Item
from . import Action, Building, BuildingProcess, BuildingState, BuildingTransaction


# class decorator : make the Concrete BuildingFactory able to register level through the decorator "level"
def level_register(cls):
    cls._states = []
    for methodname in dir(cls):
        method = getattr(cls, methodname)
        if hasattr(method, "_level"):
            cls._states.insert(method._level, method)
    return cls


# BuilingFactory method decorator : Register the method with the proper level


def level(level):
    def wrapper(method):
        method._level = level
        return method

    return wrapper


# BuildingFactory base class


class BuildingFactory(ABC):
    def create_building(self):
        states_func = self.__class__._states
        building = Building()
        states = []
        for i, state_func in enumerate(states_func):
            state = BuildingState(building, *state_func())
            states.append(state)
            if i > 0:
                states[i - 1].next_state = state

        building._state = states[0]

        return building

    @staticmethod
    def create_building_by_name(building_name):
        if building_name == "house":
            return HouseFactory().create_building()
        elif building_name == "sawmill":
            return SawmillFactory().create_building()
        elif building_name == "lumbering":
            return LumberingFactory().create_building()
        elif building_name == "goldmine":
            return GoldMineFactory().create_building()
        else:
            raise AttributeError("Building factory not implemented yet")


# Concretes Factory


@level_register
class SawmillFactory(BuildingFactory):
    @staticmethod
    @level(0)
    def chantier():
        name = "sawmillconstruction"

        inventory = Inventory("warehouse")
        inventory.allow_item("wood", 10)

        construction_inventory = Inventory("construction")
        construction_inventory.allow_item("wood", 1)

        actions = []
        building_processes = []
        building_transactions = []
        building_transactions.append(BuildingTransaction("wood", 10, -1))
        return (
            name,
            inventory,
            construction_inventory,
            actions,
            building_processes,
            building_transactions,
        )

    @staticmethod
    @level(1)
    def sawmill():
        name = "sawmill"

        inventory = Inventory("warehouse")
        inventory.allow_item("wood", 50)
        inventory.allow_item("plank", 50)

        construction_inventory = Inventory(name)
        construction_inventory.allow_item("wood", 1)
        construction_inventory.allow_item("plank", 3)
        construction_inventory.allow_item("rope", 2)

        # construction_inventory.add_item("wood", 1)
        # construction_inventory.add_item("plank", 3)
        # construction_inventory.add_item("rope", 2)

        actions = []
        building_processes = []
        building_processes.append(
            BuildingProcess(Item("wood", 2), "build", Item("plank", 1), 10)
        )
        building_transactions = []
        building_transactions.append(BuildingTransaction("wood", 10, -1))
        building_transactions.append(BuildingTransaction("plank", -1, 50))

        return (
            name,
            inventory,
            construction_inventory,
            actions,
            building_processes,
            building_transactions,
        )


@level_register
class HouseFactory(BuildingFactory):
    @staticmethod
    @level(0)
    def _build_level_0():
        name = "houseconstruction"

        inventory = Inventory("warehouse")
        inventory.allow_item("wood", 10)

        construction_inventory = Inventory("construction")
        construction_inventory.allow_item("wood", 1)

        actions = []
        building_processes = []
        building_transactions = []
        building_transactions.append(BuildingTransaction("wood", 10, -1))

        return (
            name,
            inventory,
            construction_inventory,
            actions,
            building_processes,
            building_transactions,
        )

    @staticmethod
    @level(1)
    def cabane():
        name = "cabane"

        inventory = Inventory("warehouse")
        inventory.allow_item("wood", 10)
        inventory.allow_item("plank", 20)

        construction_inventory = Inventory("construction")
        construction_inventory.allow_item("wood", 5)
        construction_inventory.allow_item("plank", 10)

        actions = []
        actions.append(Action("sleep"))
        building_processes = []
        building_transactions = []
        building_transactions.append(BuildingTransaction("wood", 10, -1))
        building_transactions.append(BuildingTransaction("plank", 20, -1))

        return (
            name,
            inventory,
            construction_inventory,
            actions,
            building_processes,
            building_transactions,
        )

    @staticmethod
    @level(2)
    def _build_level_1():
        name = "house"

        inventory = Inventory("warehouse")
        inventory.allow_item("wood", 10)

        construction_inventory = Inventory("construction")
        construction_inventory.allow_item("wood", 1)

        actions = []
        actions.append(Action("sleep"))
        building_processes = []
        building_transactions = []
        building_transactions.append(BuildingTransaction("wood", 10, -1))
        return (
            name,
            inventory,
            construction_inventory,
            actions,
            building_processes,
            building_transactions,
        )

    @staticmethod
    @level(3)
    def _build_level_2():
        name = "villa"

        inventory = Inventory("warehouse")
        inventory.allow_item("wood", 10)

        construction_inventory = Inventory("construction")
        construction_inventory.allow_item("wood", 1)

        actions = []
        actions.append(Action("sleep"))
        actions.append(Action("chill"))
        building_processes = []
        building_transactions = []
        building_transactions.append(BuildingTransaction("wood", 10, -1))
        return (
            name,
            inventory,
            construction_inventory,
            actions,
            building_processes,
            building_transactions,
        )


@level_register
class LumberingFactory(BuildingFactory):
    @staticmethod
    @level(0)
    def _build_level_0():
        name = "lumberingconstruction"

        inventory = Inventory("warehouse")
        inventory.allow_item("wood", 20)

        construction_inventory = Inventory("construction")
        construction_inventory.allow_item("wood", 1)

        actions = []
        building_processes = []
        building_transactions = []
        building_transactions.append(BuildingTransaction("wood", 10, -1))

        return (
            name,
            inventory,
            construction_inventory,
            actions,
            building_processes,
            building_transactions,
        )

    @staticmethod
    @level(1)
    def lumbering():
        name = "lumbering"

        inventory = Inventory("warehouse")
        inventory.allow_item("wood", 10)

        construction_inventory = Inventory("construction")
        construction_inventory.allow_item("wood", 5)

        actions = []
        building_processes = []
        building_transactions = []
        building_transactions.append(BuildingTransaction("wood", 10, -1))

        return (
            name,
            inventory,
            construction_inventory,
            actions,
            building_processes,
            building_transactions,
        )


@level_register
class GoldMineFactory(BuildingFactory):
    @staticmethod
    @level(0)
    def _build_level_0():
        name = "goldmineconstruction"

        inventory = Inventory("warehouse")
        inventory.allow_item("gold", 30)
        inventory.allow_item("wood", 10)

        construction_inventory = Inventory("construction")
        construction_inventory.allow_item("wood", 1)

        actions = []
        building_processes = []
        building_transactions = []
        building_transactions.append(BuildingTransaction("wood", 10, -1))

        return (
            name,
            inventory,
            construction_inventory,
            actions,
            building_processes,
            building_transactions,
        )

    @staticmethod
    @level(1)
    def goldmine():
        name = "goldmine"

        inventory = Inventory("warehouse")
        inventory.allow_item("gold", 50)

        construction_inventory = Inventory("construction")
        construction_inventory.allow_item("wood", 5)

        actions = []
        building_processes = []
        building_transactions = []
        building_transactions.append(BuildingTransaction("gold", 10, -1))

        return (
            name,
            inventory,
            construction_inventory,
            actions,
            building_processes,
            building_transactions,
        )
