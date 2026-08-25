from dataclasses import dataclass, replace

from data.emitters.image import ImageData
from data.spatial.hitbox import Hitbox
from data.sprites.sprite import Animation, Sprite, SpriteData

# Tiles are ground: below the render band the display manager sorts by y, so
# they never get drawn over a character standing on them.
GROUND = 2


@dataclass
class TileData(SpriteData):
    solid: bool = False


class Tile(Sprite):
    """A single square of world.

    Subclass it and set the class attributes; getDefaultData turns them into
    the TileData the engine wants, so a new tile is four lines of code.
    Nothing in the engine reads `solid` - the Player does, when it decides
    whether it is allowed to finish a step.
    """

    texture = "tiles/grass"
    tileSize = (16, 16)
    isSolid = False

    def __init__(self, core, pos=(0, 0, "world"), objectData=None, dictData=None):
        super().__init__(core, pos, objectData, dictData or {})
        self._color = (255, 255, 255, 255)

    def getDefaultData(self):
        self.objectData = TileData(
            Hitbox(*self.tileSize),
            {"default": Animation(ImageData(self.texture, scaleSize=self.tileSize,
                                            renderOrder=GROUND))},
            clientData=["color"],
            solid=self.isSolid)

    @property
    def solid(self):
        return self.objectData.solid

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = tuple(color)
        animation = self.getCurrentAnimation()
        animation.imageData = replace(animation.imageData, color=self._color)
        self.image.setImageData(animation.imageData)


def getObject():
    return Tile
