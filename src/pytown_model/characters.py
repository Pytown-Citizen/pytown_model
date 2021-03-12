import time

from pytown_core.serializers import IJSONSerializable

from .inventory import Inventory, InventoryFactoryMethod


class Character(IJSONSerializable):
    def __init__(self, name, direction="down", status="idle"):

        self.tile_ref = None

        self.cat = "characters"
        self.name = name
        self.direction = direction
        self._status = status
        self._move_internal_time = time.time()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value == "move":
            self._move_internal_time = time.time()

        self._status = value

    def _reset_status(self):
        self._status = "idle"

    def __repr__(self):
        return self.name

    @classmethod
    def from_json_dict(cls, json_dict):
        character = None
        if "player_id" in json_dict:
            character = Player.from_json_dict(json_dict)
        else:
            character = cls(json_dict["name"])
        character.direction = json_dict["direction"]
        character.status = json_dict["status"]
        return character

    def to_json_dict(self):
        json_dict = {}
        json_dict["name"] = self.name
        json_dict["direction"] = self.direction
        json_dict["status"] = self.status
        return json_dict


class Player(Character):
    def __init__(self, player_id, name, x, y, direction="down", status="idle"):
        Character.__init__(self, name, direction, status)

        self.player_id = player_id
        self.velocity = 0.05
        self.x = x
        self.y = y

        self.inventory = InventoryFactoryMethod.make_purse()

        self.health = PlayerStatus(470, 1000, 0)
        self.hunger = PlayerStatus(1000, 1000, -1)
        self.energy = PlayerStatus(900, 1000, 0)

    def do(self):
        # regen energy
        self.health.regenerate()
        self.hunger.regenerate()

        self.energy.value_limit = self.hunger.value
        self.energy.regenerate()

    def do_move_check(self):
        if self.status == "move" and time.time() - self._move_internal_time > 0.1:
            self.status = "idle"

    @classmethod
    def from_json_dict(cls, json_dict):
        player = cls(
            json_dict["player_id"],
            json_dict["name"],
            json_dict["x"],
            json_dict["y"],
            json_dict["direction"],
            json_dict["status"],
        )
        player.velocity = json_dict["velocity"]
        player.inventory = Inventory.from_json_dict(json_dict["inventory"])
        player.health = PlayerStatus.from_json_dict(json_dict["health"])
        player.hunger = PlayerStatus.from_json_dict(json_dict["hunger"])
        player.energy = PlayerStatus.from_json_dict(json_dict["energy"])
        return player

    def to_json_dict(self):
        json_dict = {}
        json_dict = super().to_json_dict()
        json_dict["player_id"] = self.player_id
        json_dict["velocity"] = self.velocity
        json_dict["x"] = self.x
        json_dict["y"] = self.y
        json_dict["inventory"] = self.inventory.to_json_dict()
        json_dict["health"] = self.health.to_json_dict()
        json_dict["hunger"] = self.hunger.to_json_dict()
        json_dict["energy"] = self.energy.to_json_dict()
        return json_dict


class PlayerStatus(IJSONSerializable):
    def __init__(self, value, value_max, regen_base):

        self.value = value
        self.value_max = value_max

        self._regen_base = regen_base
        self.regen = regen_base  # dynamic regen

        self._value_limit = value_max

    @property
    def value_limit(self):
        return self._value_limit

    @value_limit.setter
    def value_limit(self, value):
        if value <= self.value_max:
            self._value_limit = value
        else:
            self._value_limit = self.value_max

    def regenerate(self):
        if self.value + self.regen < 0:
            self.value = 0
        elif self.value + self.regen <= self._value_limit:
            self.value += self.regen
        else:
            self.value = self._value_limit

    def reset_regen(self):
        self.regen = self._regen_base

    @classmethod
    def from_json_dict(cls, json_dict):
        player_status = cls(
            json_dict["value"], json_dict["value_max"], json_dict["regen"]
        )
        player_status.value_limit = json_dict["value_limit"]
        player_status.regen_base = json_dict["regen_base"]
        return player_status

    def to_json_dict(self):
        json_dict = {}
        json_dict["value"] = self.value
        json_dict["value_max"] = self.value_max
        json_dict["regen"] = self.regen
        json_dict["regen_base"] = self._regen_base
        json_dict["value_limit"] = self._value_limit
        return json_dict
