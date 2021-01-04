from __future__ import annotations

import logging

from pytown_core.serializers import IJSONSerializable


class InventoryFactoryMethod:
    @staticmethod
    def make_purse():
        inventory = Inventory("purse")
        inventory.allow_item("plank", 5)
        inventory.allow_item("wood", 6)
        inventory.allow_item("coal", 4)
        inventory.allow_item("gold", 3)
        return inventory

    @staticmethod
    def make_backpack():
        inventory = Inventory("backpack")
        inventory.allow_item("plank", 5)
        inventory.allow_item("wood", 6)
        inventory.allow_item("coal", 4)
        inventory.allow_item("gold", 3)
        return inventory

    @staticmethod
    def make_warehouse():
        inventory = Inventory("backpack")
        inventory.allow_item("wood", 100)
        inventory.allow_item("plank", 150)
        inventory.allow_item("coal", 200)
        inventory.allow_item("gold", 100)
        return inventory


class Item(IJSONSerializable):
    def __init__(self, name, quantity, max_quantity=0):

        self.name = name
        self.quantity = quantity
        self.max_quantity = max_quantity

    def __repr__(self):
        return "{} {}".format(self.name, self.quantity)

    @classmethod
    def from_json_dict(cls, json_dict):
        return cls(json_dict["name"], json_dict["quantity"], json_dict["max_quantity"])

    def to_json_dict(self):
        json_dict = {}
        json_dict["name"] = self.name
        json_dict["quantity"] = self.quantity
        json_dict["max_quantity"] = self.max_quantity
        return json_dict


class Inventory(IJSONSerializable):
    def __init__(self, name):

        self.name = name
        self.items_list = []

    def get_quantity(self, name):
        quantity = 0
        if not self.is_item_allowed(name):
            logging.warning("Try to get quantity of a non allowed item")

        for item in self.items_list:
            if item.name == name:
                quantity = item.quantity
        return quantity

    def __len__(self):
        return len(self.items_list)

    def __contains__(self, item):
        return item in self.items_list

    def allow_item(self, item_name, quantity_max):
        self.items_list.append(Item(item_name, 0, quantity_max))

    def is_full(self):
        is_full = True
        for item in self.items_list:
            if item.quantity != item.max_quantity:
                is_full = False
        return is_full

    def is_item_allowed(self, item_name):
        for l_item in self.items_list:
            if l_item.name == item_name:
                return True
        return False

    def add_item(self, item: Item) -> None:
        for l_item in self.items_list:
            if l_item.name == item.name:
                l_item.quantity += item.quantity

    def remove_item(self, item: Item) -> None:
        for l_item in self.items_list:
            if l_item.name == item.name:
                l_item.quantity -= item.quantity

    @classmethod
    def from_json_dict(cls, json_dict):
        inventory = cls(json_dict["name"])

        for item in json_dict["items"]:
            inventory.items_list.append(Item.from_json_dict(item))
        return inventory

    def to_json_dict(self):
        json_dict = {}
        json_dict["name"] = self.name

        items_list = []
        for item in self.items_list:
            items_list.append(item.to_json_dict())
        json_dict["items"] = items_list
        return json_dict


class InventoryError(Exception):
    def __init__(self, inventory, item):
        Exception.__init__(self)
        self.inventory = inventory
        self.item = item
        self.msg = str("default Inventory error msg")


class ItemNotAllowedError(InventoryError):
    def __init__(self, inventory, item):
        InventoryError.__init__(self, inventory, item)
        self.msg = str("Item not allowed for this inventory")


class ItemMaxQuantityError(InventoryError):
    def __init__(self, inventory, item):
        InventoryError.__init__(self, inventory, item)
        self.msg = str(
            "can't add {} to {} : outbounds max quantity".format(
                item.quantity, item.name
            )
        )


class NegativeValueError(InventoryError):
    def __init__(self, inventory, item):
        InventoryError.__init__(self, inventory, item)
        self.msg = str("Can't use negative value")


class ItemMinQuantityError(InventoryError):
    def __init__(self, inventory, item):
        InventoryError.__init__(self, inventory, item)
        self.msg = str(
            "The quantity to remove is bigger than the existing quantity in the inventory"
        ).format(item.quantity, item.name)
