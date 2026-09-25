from dataclasses import replace

from data.emitters.image import Image, ImageData
from data.spatial.hitbox import Hitbox
from data.spatial.rect import Rect
from data.sprites.sprite import Animation, SpriteData

from packages.worldspawn.sprites.uis import base, text


class ItemSlot(base.UI):
    """One inventory cell: the item's icon plus its stack count.

    Item textures are looked up as items/<name>, which is why the empty item
    is called "none" and ships a fully transparent texture - an empty slot is
    a real ItemSlot drawing nothing.

    size forces every icon to the same box. Leaving it out draws each texture
    at its own size, which is what a set of hand drawn items wants: a 13 by 21
    sword squeezed into a square comes out visibly wrong. The hitbox follows
    whichever of the two is in play.
    """

    # what the stack count is drawn with; a package with its own font and a
    # background to read against overrides these rather than the whole widget
    countFont = None
    countFontSize = None
    countColor = (255, 255, 255, 255)
    # offset of the count from the icon's top left; None centres it
    countOffset = None

    def __init__(self, core, pos=(0, 0, "world"), itemName="none", count=0,
                 size=None, visiblePlayers=None, interactivePlayers=None):
        self._itemName = itemName
        self._count = count
        self.fixedSize = tuple(size) if size != None else None
        imageData = self.iconData()
        self.iconSize = self.fixedSize if self.fixedSize != None else Image.measure(imageData)
        self.animation = Animation(imageData)
        objectData = SpriteData(Hitbox(*self.iconSize), {"default": self.animation},
                                clientData=self.clientKeys("itemName", "count",
                                                           "scale"))
        super().__init__(core, pos, objectData, visiblePlayers, interactivePlayers)
        self.countText = None
        if self.authoritative:
            self.countText = self.buildCountText()
            self.addUiPart(self.countText)

    def texturePath(self):
        return f"items/{self._itemName}"

    def iconData(self):
        imageData = ImageData(path=self.texturePath(), renderOrder=base.CONTENT)
        if self.fixedSize != None:
            imageData = replace(imageData, scaleSize=self.fixedSize)
        return imageData

    def buildCountText(self):
        return text.Text(self.core, self.countPos(), self.countLabel(),
                         font=self.countFont, fontSize=self.countFontSize,
                         visiblePlayers=self.visiblePlayers,
                         interactivePlayers=self.interactivePlayers,
                         color=self.countColor, renderOrder=base.OVERLAY)

    def countPos(self):
        offset = self.countOffset
        if offset == None:
            offset = (self.iconSize[0] // 2, self.iconSize[1] // 2)
        return Rect.addPos(self.axis, offset) + (self.dimension,)

    def countLabel(self):
        return str(self._count) if self._count > 1 else ""

    @property
    def itemName(self):
        return self._itemName

    @itemName.setter
    def itemName(self, itemName):
        if itemName == self._itemName:
            return
        self._itemName = itemName
        self.animation.imageData = self.iconData()
        self.image.setImageData(self.animation.imageData)
        if self.fixedSize == None:
            # a different item is a different shape, and the count hangs off
            # the icon's size when no offset was pinned down
            self.iconSize = self.image.size
            self.resize(*self.iconSize)
            self.moveTo(self.pos)

    @property
    def scale(self):
        return None if self.fixedSize == None else list(self.fixedSize)

    @scale.setter
    def scale(self, scale):
        """Adopt the icon box the cell was built with.

        Whether every item is forced into one square or drawn at its own size
        is decided by the view that owns the cell, so a client rebuilding the
        cell on its own has no way to know. It has to land on fixedSize rather
        than straight on the animation, or the next item swap would go back to
        drawing the raw texture.
        """
        self.fixedSize = tuple(scale) if scale != None else None
        self.animation.imageData = self.iconData()
        self.image.setImageData(self.animation.imageData)
        self.iconSize = self.image.size
        self.resize(*self.iconSize)
        self.moveTo(self.pos)

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, count):
        self._count = count
        if self.countText != None:
            self.countText.text = self.countLabel()

    def setItem(self, itemName, count):
        self.itemName = itemName
        self.count = count

    def moveTo(self, pos):
        self.axis = pos[:2]
        self.dimension = pos[2]
        if self.countText != None:
            self.countText.axis = self.countPos()[:2]


def getObject():
    return ItemSlot
