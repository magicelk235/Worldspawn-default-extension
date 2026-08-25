from packages.worldspawn.sprites.tiles.base import Tile


class Stone(Tile):
    texture = "tiles/stone"
    isSolid = True


def getObject():
    return Stone
