from dataclasses import replace

import pygame

from data.emitters.image import Image, ImageData
from data.spatial.hitbox import Hitbox
from data.sprites.sprite import Animation, SpriteData
from data.system import events

from packages.worldspawn.sprites.uis import base, label


class InventorySelector(base.UI):
    """Mouse cursor for an InventoryView.

    Highlights the cell under the pointer. The first click marks a cell, the
    second one runs Inventory.interact between the two, which merges the
    stacks when they hold the same item and swaps them otherwise. Every view
    passed in is refreshed afterwards, so a hotbar showing the same row
    updates together with the full grid.

    Only the side that owns the inventory does any of this: on a joined
    client `owner` is None and the selector is just a sprite the host moves.

    Cursor and mark are plain textures. A package whose marker was drawn
    wider than the cell pitch sets cursorSize to None and gets the art at its
    own size, overhanging the cell the way it was meant to.
    """

    cursorTexture = "ui/selector"
    markTexture = "ui/selected"
    # box both marks are scaled into: "slot" follows the view's pitch, None
    # keeps each texture's own size, a pair forces one
    cursorSize = "slot"

    @staticmethod
    def inventoryInteractEventTemplate(ownerID, fromSlot, toSlot, playerID):
        return pygame.event.Event(events.EventRegister.getID("inventoryInteract"), locals())

    inventoryInteractEvent = events.EventRegister.register("inventoryInteract",
                                                           inventoryInteractEventTemplate)

    def __init__(self, core, pos=None, view=None, owner=None, views=None,
                 visiblePlayers=None, interactivePlayers=None):
        self.view = view
        self.owner = owner
        self.views = list(views) if views != None else ([view] if view != None else [])
        self.marked = None
        self.mark = None
        imageData = self.cursorData()
        size = self.markSize()
        objectData = SpriteData(
            Hitbox(*(size if size != None else Image.measure(imageData))),
            {"default": Animation(imageData)},
            clientData=self.clientKeys("scale"))
        if visiblePlayers == None and view != None:
            visiblePlayers = view.visiblePlayers
        if interactivePlayers == None and view != None:
            interactivePlayers = view.interactivePlayers
        super().__init__(core, pos if pos != None else self.cellPos(0, 0), objectData,
                         visiblePlayers, interactivePlayers)

    def markSize(self):
        if self.cursorSize == None:
            return None
        if self.cursorSize != "slot":
            return tuple(self.cursorSize)
        slot = self.view.slotSize if self.view != None else 36
        return slot, slot

    def cursorData(self):
        imageData = ImageData(self.cursorTexture, renderOrder=base.OVERLAY)
        size = self.markSize()
        return imageData if size == None else replace(imageData, scaleSize=size)

    def cellPos(self, w, h):
        if self.view == None:
            return 0, 0, "world"
        return self.view.slotOrigin(w, h) + (self.view.dimension,)

    def moveToCell(self, cell):
        self.axis = self.cellPos(*cell)[:2]

    # marking

    def markCell(self, cell):
        # only one cell is ever marked, and the previous marker is a sprite of
        # its own: leaving it behind puts a highlight on the grid that nothing
        # owns any more and nothing can clear
        self.clearMark()
        self.marked = cell
        self.mark = label.Label(self.core, self.cellPos(*cell), self.markTexture,
                                self.markSize(), self.visiblePlayers,
                                self.interactivePlayers, base.OVERLAY)
        self.addUiPart(self.mark)

    def clearMark(self):
        self.marked = None
        if self.mark != None:
            self.removeUiPart(self.mark)
            self.mark = None

    def hide(self):
        # a mark left behind would resolve against the next click after the
        # window is opened again, moving a stack the player forgot about
        self.clearMark()
        super().hide()

    def validCell(self, cell):
        """Whether a cell still names a slot, in the grid and in the model.

        Both can change under an open window: a bag upgrade resizes the
        inventory and the view together. A mark taken before that names a cell
        that no longer exists, and Inventory.interact walks off the end of its
        rows when it is handed one.
        """
        if not (0 <= cell[0] < self.view.w and 0 <= cell[1] < self.view.h):
            return False
        inventory = self.owner.inventory
        return cell[0] < inventory.getW() and cell[1] < inventory.getH()

    def interact(self, cell, playerID):
        fromSlot, toSlot = self.marked, cell
        self.clearMark()
        if fromSlot == toSlot:
            return
        # Inventory.interact(a, b) pulls b into a, so the destination goes
        # first for the stack to end up where it was dropped
        self.owner.inventory.interact(*toSlot, *fromSlot)
        for view in self.views:
            view.refresh()
        self.addEvent(self.inventoryInteractEventTemplate(self.owner.id, fromSlot,
                                                          toSlot, playerID))

    def update(self):
        super().update()
        if not self.visible or self.view == None or self.owner == None:
            return False
        if not self.view.visible:
            # the cells are not on screen, so neither is anything the player
            # could be aiming at
            return False
        if self.marked != None and not self.validCell(self.marked):
            self.clearMark()
        for playerID, inp in self.inputs():
            cell = self.view.slotAt(inp.getMousePos())
            if cell == None:
                continue
            self.moveToCell(cell)
            if not inp.mouseClicked() or not self.validCell(cell):
                continue
            if self.marked == None:
                self.markCell(cell)
            else:
                self.interact(cell, playerID)
        return False


def getObject():
    return InventorySelector
