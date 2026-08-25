from dataclasses import replace

from data.buffers.assetsLoader import AssetsLoader
from data.emitters.image import ImageData
from data.spatial.hitbox import Hitbox
from data.sprites.sprite import Animation, SpriteData

from packages.worldspawn.sprites.uis import base


class Text(base.UI):
    """A line of text.

    The engine renders text by putting the string straight into the
    ImageData, and ImageData is frozen, so changing the text means swapping
    in a new one and telling the Image to reload. Doing that here keeps the
    animation the single source of truth for what the sprite looks like.
    """

    def __init__(self, core, pos=(0, 0, "world"), text="", font=None, fontSize=1,
                 visiblePlayers=None, interactivePlayers=None,
                 color=(255, 255, 255, 255), renderOrder=base.CONTENT):
        self._text = str(text)
        self.font = font
        self.fontSize = fontSize
        self.color = color
        self.animation = Animation(self.buildImageData(renderOrder))
        objectData = SpriteData(Hitbox(*self.measure()), {"default": self.animation},
                                clientData=self.clientKeys("text"))
        super().__init__(core, pos, objectData, visiblePlayers, interactivePlayers)

    def buildImageData(self, renderOrder):
        return ImageData(path=self.font, text=self._text, color=self.color,
                         factoredSize=self.fontSize, renderOrder=renderOrder)

    def measure(self):
        w, h = AssetsLoader.get("fonts", self.font).size(self._text)
        return w * self.fontSize, h * self.fontSize

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        text = str(text)
        if text == self._text:
            return
        self._text = text
        self.animation.imageData = replace(self.animation.imageData, text=text)
        self.image.setImageData(self.animation.imageData)
        self.resize(*self.measure())

    def setText(self, text):
        self.text = text

    def setColor(self, color):
        self.color = color
        self.animation.imageData = replace(self.animation.imageData, color=color)
        self.image.setImageData(self.animation.imageData)


def getObject():
    return Text
