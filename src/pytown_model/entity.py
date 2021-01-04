from pytown_core.serializers import IJSONSerializable

from .inventory import Inventory, Item


class BackgroundCreator:
    def create_grass_backgound(self):
        return Background("grass", ["house", "sawmill"], 1)

    def create_water_background(self):
        return Background("water", [], 0.5)

    def create_road_background(self):
        return Background("road", [], 2)

    def create_sand_background(self):
        return Background("sand", ["house"], 0.5)


class Background(IJSONSerializable):
    def __init__(
        self, name: str, buildings_allowed_list: list, move_multiplicator: int
    ):
        self.name = name
        self.buildings_allowed_list = buildings_allowed_list
        self.move_multiplicator = move_multiplicator

    def __repr__(self):
        return "{}".format(self.name)

    @classmethod
    def from_json_dict(cls, json_dict):
        background = cls(
            json_dict["name"],
            json_dict["buildings_allowed_list"],
            json_dict["move_multiplicator"],
        )
        return background

    def to_json_dict(self):
        json_dict = {}
        json_dict["name"] = self.name
        json_dict["buildings_allowed_list"] = self.buildings_allowed_list
        json_dict["move_multiplicator"] = self.move_multiplicator
        return json_dict


class ResourceCreator:
    def create_forest(self):
        resource = Resource("forest", ["lumbering"])
        resource.inventory.name = "wood"
        resource.inventory.allow_item("wood", 100)
        resource.inventory.add_item(Item("wood", 50))
        return resource

    def create_golden_vein(self):
        resource = Resource("goldvein", ["goldmine"])
        resource.inventory.name = "gold"
        resource.inventory.allow_item("gold", 100)
        resource.inventory.add_item(Item("gold", 50))
        return resource

    def crete_stone_vein(self):
        resource = Resource("stonevein", ["stonemine"])
        resource.inventory.name = "stone"
        resource.inventory.allow_item("stone", 100)
        resource.inventory.add_item(Item("stone", 50))
        return resource

    def create_iron_vein(self):
        resource = Resource("ironvein", ["ironmine"])
        resource.inventory.name = "iron"
        resource.inventory.allow_item("iron", 100)
        resource.inventory.add_item(Item("iron", 50))
        return resource


class Resource(IJSONSerializable):
    def __init__(self, name: str, buildings_allowed_list: list):

        self.name = name
        self.inventory = Inventory(name)
        self.buildings_allowed_list = buildings_allowed_list

    def __repr__(self):
        return self.name

    @classmethod
    def from_json_dict(cls, json_dict):
        resource = cls(json_dict["name"], json_dict["buildings_allowed_list"])
        resource.inventory = Inventory.from_json_dict(json_dict["inventory"])
        return resource

    def to_json_dict(self):
        json_dict = {}
        json_dict["name"] = self.name
        json_dict["inventory"] = self.inventory.to_json_dict()
        json_dict["buildings_allowed_list"] = self.buildings_allowed_list
        return json_dict
