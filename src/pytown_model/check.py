from __future__ import annotations

from abc import ABC, abstractmethod

from pytown_core.serializers import IJSONSerializable

from .inventory import Inventory, Item, NegativeValueError


class CheckResult(IJSONSerializable):
    def __init__(self):
        self._msg = ""

    @property
    def msg(self):
        return self._msg

    def __iadd__(self, msg):
        if self._msg != "":
            self._msg += "\n"
        self._msg += msg
        return self

    def __eq__(self, msg):
        return self._msg == msg

    def __bool__(self):
        if self._msg == "":
            return True
        else:
            return False

    def __repr__(self):
        return "({} , {})".format(self.__bool__(), self.msg)

    @classmethod
    def from_json_dict(cls, json_dict):
        check_result = cls()
        check_result += json_dict["msg"]
        return check_result

    def to_json_dict(self):
        json_dict = {}
        json_dict["msg"] = self._msg
        return json_dict


class Check(ABC):
    @abstractmethod
    def check(self, check_result: CheckResult):
        raise NotImplementedError


class TransactionCheck(Check):
    def __init__(self, sender, receiver, item: Item):

        self._sender = sender
        self._receiver = receiver
        self._item = item

    def check(self, check_result: CheckResult):

        try:
            self._sender.inventory
        except AttributeError:
            check_result += "{} has no inventory".format(self._sender)

        try:
            self._receiver.inventory
        except AttributeError:
            check_result += "{} has no inventory".format(self._receiver)

        InventoryRemoveCheck(self._sender.inventory, self._item).check(check_result)
        InventoryAddCheck(self._receiver.inventory, self._item).check(check_result)

        return check_result


class InventoryAddCheck(Check):
    def __init__(self, inventory: Inventory, item: Item):
        self._inventory = inventory
        self._item = item

    def check(self, check_result: CheckResult):

        if self._item.quantity < 0:
            raise NegativeValueError(self, self._item)

        if self._inventory.is_item_allowed(self._item.name):
            for l_item in self._inventory.items_list:
                if l_item.name == self._item.name:
                    if l_item.max_quantity < l_item.quantity + self._item.quantity:
                        check_result += "{} > {} max quantity".format(
                            self._item.quantity, self._item.name
                        )
        else:
            check_result += "{} not found in inventory".format(self._item.name)


class InventoryRemoveCheck(Check):
    def __init__(self, inventory: Inventory, item: Item):
        self._inventory = inventory
        self._item = item

    def check(self, check_result: CheckResult):

        if self._item.quantity < 0:
            raise NegativeValueError(self, self._item)

        if self._inventory.is_item_allowed(self._item.name):
            for l_item in self._inventory.items_list:
                if l_item.name == self._item.name:
                    if l_item.quantity < self._item.quantity:
                        check_result += "not enough {} ({}) to remove {}".format(
                            self._item.name,
                            self._inventory.get_quantity(self._item.name),
                            self._item.quantity,
                        )
        else:
            check_result += "{} not found in inventory".format(self._item.name)


class BackgroundMovementCheck(Check):
    def __init__(self, background, player):
        self._background = background
        self._player = (
            player  # We keep it if we allow some swimmer player to go in water
        )

    def check(self, check_result: CheckResult):
        if self._background.name == "water":
            check_result += "Can't go in water"


class EnergyCheck(Check):
    def __init__(self, player, energy_required):
        self._player = player
        self._energy_required = energy_required

    def check(self, check_result: CheckResult):
        if self._player.energy.value < self._energy_required:
            check_result += "No enough energy({}) : {} required".format(
                self._player.energy.value, self._energy_required
            )


class AliveCheck(Check):
    def __init__(self, player):
        self._player = player

    def check(self, check_result: CheckResult):
        if self._player.health.value <= 0:
            check_result += "Health is 0. Player is not alive"


class AwakenCheck(Check):
    def __init__(self, player):
        self._player = player

    def check(self, check_result: CheckResult):
        if self._player.status == "sleep":
            check_result += "Player is sleeping"


class AvailableCheck(Check):
    def __init__(self, player):
        self._player = player

    def check(self, check_result: CheckResult):
        AliveCheck(self._player).check(check_result)
        AwakenCheck(self._player).check(check_result)


class BackgroundBuildCheck(Check):
    def __init__(self, background, building_name):
        self._background = background
        self._building_name = building_name

    def check(self, check_result: CheckResult):
        if self._background.name == "road":
            check_result += "Can't build on road"
