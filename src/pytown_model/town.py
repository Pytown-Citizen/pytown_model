from __future__ import annotations

import logging
import math
import pickle

from pytown_core.serializers import IJSONSerializable

from .buildings import Building
from .buildings.factory import GoldMineFactory, LumberingFactory, SawmillFactory
from .characters import Character, Player
from .entity import Background, BackgroundCreator, Resource, ResourceCreator


class Town(IJSONSerializable):
    """
    Representation of the town board with different tiles
    Town act like a facade for accessing town objects
    """

    def __init__(self, name):

        self.name = name

        self.backgrounds = {}  # Dict with (x,y) as key
        self.resources = {}
        self.buildings = {}
        self.characters = {}
        self.players = {}  # Dict with player_id as key

    def __repr__(self):
        log = "\n"

        line = 0
        for background in self.backgrounds:
            if self.backgrounds[background][1] == line:
                log += repr(background)
            else:
                log += "\n"
                log += repr(background)
                line += 1

        return log

    def get_tiles_w(self):
        w = 0
        for background in self.backgrounds:
            if background[0] >= w:
                w = background[0]
        return w + 1

    def get_tiles_h(self):
        h = 0
        for background in self.backgrounds:
            if background[1] >= h:
                h = background[1]
        return h + 1

    def get_size(self):
        return (self.get_tiles_w(), self.get_tiles_h())

    def get_background(self, tile):
        if tile in self.backgrounds:
            return self.backgrounds[tile]
        raise TownEntityNotFound("background", tile)

    def set_background(self, background: Background, tile):
        self.backgrounds[tile] = background

    def get_resource(self, tile):
        if tile in self.resources:
            return self.resources[tile]
        raise TownEntityNotFound("resource", tile)

    def set_resource(self, resource: Resource, tile):
        self.resources[tile] = resource

    def get_building(self, tile):
        if tile in self.buildings.keys():
            return self.buildings[tile]
        raise TownEntityNotFound("building", tile)

    def set_building(self, building: Building, tile):
        self.buildings[tile] = building

    def get_buildings_allowed_list_by_tile(self, tile: tuple):

        if tile in self.buildings.keys():
            return []

        if tile in self.resources.keys():
            resource = self.get_resource(tile)
            return resource.buildings_allowed_list

        background = self.get_background(tile)
        return background.buildings_allowed_list

    def get_character(self, tile):
        if tile in self.characters:
            return self.characters[tile]
        raise TownEntityNotFound("character", tile)

    def set_character(self, character: Character, tile):
        self.characters[tile] = character

    def get_player(self, player_id) -> Player:
        if player_id in self.players:
            return self.players[player_id]
        return None

    def set_player(self, player: Player):
        self.players[player.player_id] = player

    def add_player(self, player: Player, tile: tuple):
        player.x = tile[0]
        player.y = tile[1]
        self.players[player.player_id] = player

    def get_player_tile(self, player_id):
        player = self.get_player(player_id)
        tile_selected = (math.floor(player.x + 0.5), math.floor(player.y + 0.5))
        return tile_selected

    def get_players_by_tile(self, tile):
        players_list = []
        for player in self.players.values():
            player_tile = self.get_player_tile(player.player_id)
            if player_tile == tile:
                players_list.append(player)
        return players_list

    def __len__(self):
        return len(self.backgrounds)

    def save(self):
        file_name = self.name + ".pytown"
        with open(file_name, "wb") as town_file:
            my_pickler = pickle.Pickler(town_file)
            my_pickler.dump(self)
            logging.info("town saved")

    def load(self):
        file_name = self.name + ".pytown"
        try:
            with open(file_name, "rb") as town_file:
                my_unpickler = pickle.Unpickler(town_file)
                town = my_unpickler.load()

                self.backgrounds = town.backgrounds  # Dict with (x,y) as key
                self.resources = town.resources
                self.buildings = town.buildings
                self.characters = town.characters
                self.players = town.players

        except FileNotFoundError:
            logging.warning("No filetown found")
            return

    @classmethod
    def from_json_dict(cls, json_dict):
        town = cls(json_dict["name"])
        for background in json_dict["backgrounds"]:
            town.backgrounds[background] = Background.from_json_dict(
                json_dict["backgrounds"][background]
            )
        for resource in json_dict["resources"]:
            town.resources[resource] = Resource.from_json_dict(
                json_dict["resources"][resource]
            )
        for building in json_dict["buildings"]:
            town.buildings[building] = Building.from_json_dict(
                json_dict["buildings"][building]
            )
        for character in json_dict["characters"]:
            town.characters[character] = Character.from_json_dict(
                json_dict["characters"][character]
            )
        for player in json_dict["players"]:
            town.players[player] = Player.from_json_dict(json_dict["players"][player])
        return town

    def to_json_dict(self):
        json_dict = {}
        json_dict["name"] = self.name

        backgrounds_dict = {}
        for background in self.backgrounds:
            backgrounds_dict[background] = self.backgrounds[background].to_json_dict()
        json_dict["backgrounds"] = backgrounds_dict

        resources_dict = {}
        for resource in self.resources:
            resources_dict[resource] = self.resources[resource].to_json_dict()
        json_dict["resources"] = resources_dict

        buildings_dict = {}
        for building in self.buildings:
            buildings_dict[building] = self.buildings[building].to_json_dict()
        json_dict["buildings"] = buildings_dict

        characters_dict = {}
        for character in self.characters:
            characters_dict[character] = self.characters[character].to_json_dict()
        json_dict["characters"] = characters_dict

        players_dict = {}
        for player in self.players:
            players_dict[player] = self.players[player].to_json_dict()
        json_dict["players"] = players_dict

        return json_dict


class TownCreator:
    @staticmethod
    def createDefaultTown(tiles_nb_w, tiles_nb_h) -> Town:
        town = Town("testown")

        town = TownCreator._initializetiles(town, tiles_nb_w, tiles_nb_h)

        # Add road on n-1 line
        j = town.get_tiles_h() - 2
        for i in range(town.get_tiles_w()):
            town.backgrounds[(i, j)] = BackgroundCreator().create_road_background()

        # Add water on last line
        j = town.get_tiles_h() - 1
        for i in range(town.get_tiles_w()):
            town.backgrounds[(i, j)] = BackgroundCreator().create_water_background()

        return town

    @staticmethod
    def create_basic_town():
        town = Town("basictown")
        tiles_nb_w = 11
        tiles_nb_h = 6
        town = TownCreator._initializetiles(town, tiles_nb_w, tiles_nb_h)

        town.set_resource(ResourceCreator().create_forest(), (0, 3))
        town.set_resource(ResourceCreator().create_forest(), (5, 2))
        town.set_resource(ResourceCreator().create_golden_vein(), (9, 1))
        town.set_resource(ResourceCreator().create_golden_vein(), (6, 0))

        town.set_building(LumberingFactory().create_building(), (5, 2))
        town.set_building(SawmillFactory().create_building(), (7, 3))
        town.set_building(GoldMineFactory().create_building(), (6, 0))

        town.buildings[(5, 2)].upgrade()
        town.buildings[(6, 0)].upgrade()
        town.buildings[(7, 3)].upgrade()

        return town

    @staticmethod
    def _initializetiles(town, tiles_nb_w, tiles_nb_h):
        for j in range(tiles_nb_h):
            for i in range(tiles_nb_w):
                town.backgrounds[(i, j)] = BackgroundCreator().create_grass_backgound()
        return town


class TownEntityNotFound(IndexError):
    def __init__(self, entity, tile):
        IndexError.__init__(self)
        self.entity = entity
        self.tile = tile
        self.msg = "{} not found at {} in town".format(self.entity.name, self.tile)
