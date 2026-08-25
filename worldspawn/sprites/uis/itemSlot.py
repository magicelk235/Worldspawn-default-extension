from dataclasses import replace

from data.emitters.image import ImageData
from data.spatial.hitbox import Hitbox
from data.spatial.rect import Rect
from data.sprites.sprite import Animation, SpriteData

from packages.worldspawn.sprites.uis import base, text


class ItemSlot(base.UI):
    """One inventory cell: the item's icon plus its stack count.

    Item textures are looked up as items/<name>, which is why the empty item
    is called "none" and ships a fully transparent texture - an empty slot is
    a real ItemSlot drawing nothing.
    """

    def __init__(self, core, pos=(0, 0, "world"), itemName="none", count=0,
                 size=(16, 16), visiblePlayers=None, interactivePlayers=None):
        self._itemName = itemName
        self._count = count
        self.iconSize = tuple(size)
        self.animation = Animation(ImageData(path=self.texturePath(), scaleSize=self.iconSize,
                                             renderOrder=base.CONTENT))
        objectData = SpriteData(Hitbox(*self.iconSize), {"default": self.animation},
                                clientData=self.clientKeys("itemName", "count"))
        super().__init__(core, pos, objectData, visiblePlayers, interactivePlayers)
        self.countText = None
        if self.authoritative:
            self.countText = text.Text(core, self.countPos(), self.countLabel(),
                                       visiblePlayers=self.visiblePlayers,
                                       interactivePlayers=self.interactivePlayers,
                                       renderOrder=base.OVERLAY)
            self.addUiPart(self.countText)

    def texturePath(self):
        return f"items/{self._itemName}"

    def countPos(self):
        return Rect.addPos(self.axis, (self.iconSize[0] // 2, self.iconSize[1] // 2)) + (self.dimension,)

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
        self.animation.imageData = replace(self.animation.imageData, path=self.texturePath())
        self.image.setImageData(self.animation.imageData)

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
