from dataclasses import replace

from data.emitters.image import ImageData
from data.spatial.hitbox import Hitbox
from data.spatial.rect import Rect
from data.sprites.sprite import Animation, SpriteData

from packages.worldspawn.sprites.uis import base, itemSlot


class InventoryView(base.UI):
    """A grid of item slots drawn over an inventory.

    It holds the flat, row-major list handed out by Inventory.toList(). That
    list contains the live InventoryItem objects, so moving items around in
    the model shows up here after a refresh() without copying anything.

    The grid is positioned relative to the middle of the screen, so an offset
    of (0, 0) centres it and a positive y offset pins it lower down.
    """

    slotSize = 36
    iconSize = 16

    def __init__(self, core, pos=None, w=5, h=5, inventoryList=None,
                 visiblePlayers=None, interactivePlayers=None, offset=(0, 0)):
        self.w = w
        self.h = h
        self.offset = tuple(offset)
        self.inventoryList = list(inventoryList or ())
        self.slots = []
        objectData = SpriteData(Hitbox(*self.gridSize()),
                                {"default": Animation(self.backgroundData())},
                                clientData=self.clientKeys("grid"))
        super().__init__(core, pos if pos != None else self.centeredPos(core),
                         objectData, visiblePlayers, interactivePlayers)
        if self.authoritative:
            self.buildSlots()

    # geometry

    def gridSize(self):
        return self.w * self.slotSize, self.h * self.slotSize

    @property
    def grid(self):
        return [self.w, self.h]

    @grid.setter
    def grid(self, grid):
        """Adopt a grid handed over by the host.

        The background is one slot texture tiled to the whole grid, so the
        shape is baked into the image and has to be rebuilt whenever the
        dimensions change. A client never owns the slots themselves; the host
        streams those as sprites of their own.
        """
        self.w, self.h = grid
        animation = self.getCurrentAnimation()
        animation.imageData = replace(animation.imageData, cutSize=self.gridSize())
        self.image.setImageData(animation.imageData)

    def centeredPos(self, core):
        screen = core.emittersManager.getScreenSize()
        grid = self.gridSize()
        centered = Rect.subPos((screen[0] // 2, screen[1] // 2),
                               (grid[0] // 2, grid[1] // 2))
        return Rect.addPos(centered, self.offset) + ("world",)

    def slotOrigin(self, w, h):
        return Rect.addPos(self.axis, (w * self.slotSize, h * self.slotSize))

    def slotPos(self, w, h):
        padding = (self.slotSize - self.iconSize) // 2
        return Rect.addPos(self.slotOrigin(w, h), (padding, padding)) + (self.dimension,)

    def slotIndex(self, w, h):
        return w + h * self.w

    def slotAt(self, point):
        """Grid cell under a screen point, or None when the point is outside."""
        if not self.containsPoint(point):
            return None
        relative = Rect.subPos(point, self.axis)
        return relative[0] // self.slotSize, relative[1] // self.slotSize

    # contents

    def backgroundData(self):
        # cutSize tiles the single slot texture across the whole grid.
        return ImageData("ui/slot", cutSize=self.gridSize(), renderOrder=base.BACKGROUND)

    def buildSlots(self):
        for h in range(self.h):
            for w in range(self.w):
                slot = itemSlot.ItemSlot(self.core, self.slotPos(w, h),
                                         size=(self.iconSize, self.iconSize),
                                         visiblePlayers=self.visiblePlayers,
                                         interactivePlayers=self.interactivePlayers)
                self.slots.append(slot)
                self.addUiPart(slot)
        self.refresh()

    def clearSlots(self):
        for slot in self.slots:
            slot.remove()
            self.removeUiPart(slot)
        self.slots = []

    def refresh(self):
        for index, slot in enumerate(self.slots):
            if index < len(self.inventoryList):
                item = self.inventoryList[index]
                slot.setItem(item.getItemName(), item.getCount())
            else:
                slot.setItem("none", 0)

    def setInventory(self, inventoryList):
        self.inventoryList = list(inventoryList)
        self.refresh()

    def setGrid(self, w, h):
        self.w = w
        self.h = h
        self.resize(*self.gridSize())
        self.animation = self.getAnimation()
        self.animation.imageData = replace(self.animation.imageData, cutSize=self.gridSize())
        self.image.setImageData(self.animation.imageData)
        self.reposition()
        if self.authoritative:
            self.clearSlots()
            self.buildSlots()

    def reposition(self):
        pos = self.centeredPos(self.core)
        self.axis = pos[:2]
        for h in range(self.h):
            for w in range(self.w):
                index = self.slotIndex(w, h)
                if index < len(self.slots):
                    self.slots[index].moveTo(self.slotPos(w, h))


def getObject():
    return InventoryView
