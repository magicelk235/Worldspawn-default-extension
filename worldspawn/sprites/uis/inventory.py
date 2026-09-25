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

    Left to itself the grid is positioned relative to the middle of the
    screen, so an offset of (0, 0) centres it and a positive y offset pins it
    lower down. Passing pos puts it exactly there instead, and it stays there
    across a resize.

    Four things are meant to be overridden by a package with its own art:
    backgroundData() for the panel texture, panelSize() when the panel covers
    more than the cells it holds - a cell marker wider than the pitch leaves a
    border - iconSize / iconPadding for how the icon sits in its cell, and
    slotClass for a cell that draws more than an icon and a count.
    """

    slotClass = itemSlot.ItemSlot

    slotSize = 36
    # box every icon is drawn in; None draws each item at its own size
    iconSize = 16
    # where the icon sits inside its cell; None centres a fixed size icon
    iconPadding = None

    def __init__(self, core, pos=None, w=5, h=5, inventoryList=None,
                 visiblePlayers=None, interactivePlayers=None, offset=(0, 0)):
        self.w = w
        self.h = h
        self.offset = tuple(offset)
        # the model hands out one list object and refills it in place, so the
        # reference is what keeps a view in step with an inventory that grows
        self.inventoryList = inventoryList if inventoryList != None else []
        self.centered = pos == None
        self.slots = []
        objectData = SpriteData(Hitbox(*self.panelSize()),
                                {"default": Animation(self.backgroundData())},
                                clientData=self.clientKeys("grid"))
        super().__init__(core, pos if pos != None else self.centeredPos(core),
                         objectData, visiblePlayers, interactivePlayers)
        if self.authoritative:
            self.buildSlots()

    # geometry

    def gridSize(self):
        """Span of the cells themselves, which is what cell maths uses."""
        return self.w * self.slotSize, self.h * self.slotSize

    def panelSize(self):
        """Size of the drawn panel, and of the box that answers clicks."""
        return self.gridSize()

    @property
    def grid(self):
        return [self.w, self.h]

    @grid.setter
    def grid(self, grid):
        """Adopt a grid handed over by the host.

        The panel's shape is baked into its image, so the image has to be
        rebuilt whenever the dimensions change. A client never owns the slots
        themselves; the host streams those as sprites of their own.
        """
        self.w, self.h = grid
        self.resize(*self.panelSize())
        self.applyBackground()

    def applyBackground(self):
        animation = self.getCurrentAnimation()
        animation.imageData = self.backgroundData()
        self.image.setImageData(animation.imageData)

    def centeredPos(self, core):
        screen = core.emittersManager.getScreenSize()
        panel = self.panelSize()
        centered = Rect.subPos((screen[0] // 2, screen[1] // 2),
                               (panel[0] // 2, panel[1] // 2))
        return Rect.addPos(centered, self.offset) + ("world",)

    def slotPadding(self):
        if self.iconPadding != None:
            return tuple(self.iconPadding)
        if self.iconSize == None:
            return 0, 0
        padding = (self.slotSize - self.iconSize) // 2
        return padding, padding

    def slotOrigin(self, w, h):
        return Rect.addPos(self.axis, (w * self.slotSize, h * self.slotSize))

    def slotPos(self, w, h):
        return Rect.addPos(self.slotOrigin(w, h), self.slotPadding()) + (self.dimension,)

    def slotIndex(self, w, h):
        return w + h * self.w

    def slotAt(self, point):
        """Grid cell under a screen point, or None when the point is outside.

        The panel can be larger than the cells it holds, so landing inside it
        is not enough; a click on the border belongs to no cell.
        """
        if not self.containsPoint(point):
            return None
        relative = Rect.subPos(point, self.axis)
        cell = relative[0] // self.slotSize, relative[1] // self.slotSize
        if not (0 <= cell[0] < self.w and 0 <= cell[1] < self.h):
            return None
        return cell

    # contents

    def backgroundData(self):
        # cutSize tiles the single slot texture across the whole panel.
        return ImageData("ui/slot", cutSize=self.panelSize(),
                         renderOrder=base.BACKGROUND)

    def slotIconSize(self):
        return None if self.iconSize == None else (self.iconSize, self.iconSize)

    def buildSlots(self):
        for h in range(self.h):
            for w in range(self.w):
                slot = self.slotClass(self.core, self.slotPos(w, h),
                                      size=self.slotIconSize(),
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
        self.inventoryList = inventoryList
        self.refresh()

    def setGrid(self, w, h):
        self.w = w
        self.h = h
        self.resize(*self.panelSize())
        self.applyBackground()
        self.reposition()
        if self.authoritative:
            self.clearSlots()
            self.buildSlots()

    def reposition(self):
        """Put the panel back where it belongs and drag the cells along.

        A view that was given a position owns it: only a centred one is
        re-derived, or growing the grid would tear a panel a package placed by
        hand out to the middle of the screen.
        """
        if self.centered:
            self.axis = self.centeredPos(self.core)[:2]
        for h in range(self.h):
            for w in range(self.w):
                index = self.slotIndex(w, h)
                if index < len(self.slots):
                    self.slots[index].moveTo(self.slotPos(w, h))


def getObject():
    return InventoryView
