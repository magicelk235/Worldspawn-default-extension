from packages.worldspawn.sprites.tiles.base import Tile


class Grass(Tile):
    texture = "tiles/grass"


def getObject():
    return Grass
