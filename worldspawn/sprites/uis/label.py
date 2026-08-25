from dataclasses import replace

from data.emitters.image import ImageData
from data.spatial.hitbox import Hitbox
from data.sprites.sprite import Animation, SpriteData

from packages.worldspawn.sprites.uis import base


class Label(base.UI):
    """A plain image with no behaviour.

    Useful as a child of another widget when you just need to stamp a texture
    somewhere: icons, highlights, backdrops.

    The texture path is streamed, because a client rebuilds the label with
    cls(core, pos) and would otherwise fall back to the engine's placeholder
    square.
    """

    def __init__(self, core, pos=(0, 0, "world"), texture=None, size=(16, 16),
                 visiblePlayers=None, interactivePlayers=None,
                 renderOrder=base.OVERLAY):
        imageData = texture if isinstance(texture, ImageData) else ImageData(
            path=texture, renderOrder=renderOrder)
        objectData = SpriteData(Hitbox(*size), {"default": Animation(imageData)},
                                clientData=self.clientKeys("texture"))
        super().__init__(core, pos, objectData, visiblePlayers, interactivePlayers)

    @property
    def texture(self):
        return self.getCurrentAnimation().imageData.path

    @texture.setter
    def texture(self, texture):
        animation = self.getCurrentAnimation()
        animation.imageData = replace(animation.imageData, path=texture)
        self.image.setImageData(animation.imageData)


def getObject():
    return Label
