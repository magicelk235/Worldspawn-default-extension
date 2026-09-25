from dataclasses import replace

from data.emitters.image import Image, ImageData
from data.spatial.hitbox import Hitbox
from data.sprites.sprite import Animation, SpriteData

from packages.worldspawn.sprites.uis import base


class Label(base.UI):
    """A plain image with no behaviour.

    Useful as a child of another widget when you just need to stamp a texture
    somewhere: icons, highlights, backdrops.

    size scales the art and sets the hitbox to match; leaving it out draws the
    art at its own size and takes the hitbox from that. Either way the box that
    gets clicked is the box that was drawn, which is the whole point of having
    the two come from one place.

    A label can be handed a bare path or a whole ImageData, so what it looks
    like is entirely the caller's choice: a tiled backdrop, a tinted highlight,
    a mirrored icon. All of it is streamed as one field, because a client
    rebuilds the label with cls(core, pos) and has nothing else to go on -
    stream only the path and a tiled panel comes back as a single tile.
    """

    def __init__(self, core, pos=(0, 0, "world"), texture=None, size=None,
                 visiblePlayers=None, interactivePlayers=None,
                 renderOrder=base.OVERLAY):
        imageData = texture if isinstance(texture, ImageData) else ImageData(
            path=texture, renderOrder=renderOrder)
        if size != None:
            imageData = replace(imageData, scaleSize=tuple(size))
        else:
            size = Image.measure(imageData)
        objectData = SpriteData(Hitbox(*size), {"default": Animation(imageData)},
                                clientData=self.clientKeys("art"))
        super().__init__(core, pos, objectData, visiblePlayers, interactivePlayers)

    @property
    def texture(self):
        return self.getCurrentAnimation().imageData.path

    @texture.setter
    def texture(self, texture):
        animation = self.getCurrentAnimation()
        animation.imageData = replace(animation.imageData, path=texture)
        self.image.setImageData(animation.imageData)
        # a swapped texture is a different picture; the box follows it unless a
        # fixed size was asked for, in which case the scale already pins both
        if animation.imageData.scaleSize == -1:
            self.resize(*self.image.size)

    @property
    def art(self):
        return self.getCurrentAnimation().getImageData().toDict()

    @art.setter
    def art(self, art):
        animation = self.getCurrentAnimation()
        # keys this engine does not know are left at their local default
        # rather than taking the whole label down with a TypeError
        known = animation.imageData.__dict__
        animation.imageData = replace(animation.imageData,
                                      **{key: value for key, value in art.items()
                                         if key in known})
        self.image.setImageData(animation.imageData)
        self.resize(*self.image.size)


def getObject():
    return Label
