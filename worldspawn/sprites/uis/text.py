from dataclasses import replace

from data.emitters.image import Image, ImageData
from data.spatial.hitbox import Hitbox
from data.sprites.sprite import Animation, SpriteData

from packages.worldspawn.sprites.uis import base


class Text(base.UI):
    """A line of text.

    The engine renders text by putting the string straight into the
    ImageData, and ImageData is frozen, so changing the text means swapping
    in a new one and telling the Image to reload. Doing that here keeps the
    animation the single source of truth for what the sprite looks like.

    font is an asset key under assets/fonts; None is pygame's built-in font.
    fontSize is the point size the file is opened at, the way any other text
    is sized - None leaves the font at its own default. Whether the glyphs are
    antialiased is the font's business: a pixel font is not.

    The hitbox is measured off the rendered line rather than the font's
    metrics, which disagree by a pixel or two and would leave a clickable box
    that is not the box on screen.
    """

    def __init__(self, core, pos=(0, 0, "world"), text="", font=None, fontSize=None,
                 visiblePlayers=None, interactivePlayers=None,
                 color=(255, 255, 255, 255), renderOrder=base.CONTENT):
        self._text = str(text)
        self._font = font
        self._fontSize = fontSize
        self._color = color
        self.animation = Animation(self.buildImageData(renderOrder))
        objectData = SpriteData(Hitbox(*Image.measure(self.animation.imageData)),
                                {"default": self.animation},
                                clientData=self.clientKeys("text", "color", "font",
                                                           "fontSize", "renderOrder"))
        super().__init__(core, pos, objectData, visiblePlayers, interactivePlayers)

    def buildImageData(self, renderOrder):
        return ImageData(path=self._font, text=self._text, color=self._color,
                         fontSize=-1 if self._fontSize == None else self._fontSize,
                         renderOrder=renderOrder)

    def rebuild(self, **fields):
        """Swap in new image data and follow it with the hitbox.

        Every part of a line's appearance goes through here, including the
        copies a client is told about: what a line says, what colour it is and
        what face it is set in all arrive as plain attributes over the wire, so
        assigning one has to redraw it or a client would keep the look its own
        class defaults gave it and ignore the host.
        """
        self.animation.imageData = replace(self.animation.imageData, **fields)
        if getattr(self, "image", None) == None:
            return
        self.image.setImageData(self.animation.imageData)
        self.resize(*self.image.size)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        text = str(text)
        if text == self._text:
            return
        self._text = text
        self.rebuild(text=text)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        # a colour that came from a host arrives as a list, and the rest of the
        # game compares colours against tuples
        color = tuple(color)
        if color == self._color:
            return
        self._color = color
        self.rebuild(color=color)

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        if font == self._font:
            return
        self._font = font
        self.rebuild(path=font)

    @property
    def fontSize(self):
        return self._fontSize

    @fontSize.setter
    def fontSize(self, fontSize):
        if fontSize == self._fontSize:
            return
        self._fontSize = fontSize
        self.rebuild(fontSize=-1 if fontSize == None else fontSize)

    def setText(self, text):
        self.text = text

    def setColor(self, color):
        self.color = color


def getObject():
    return Text
