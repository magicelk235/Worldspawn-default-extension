import pygame

from data.emitters.image import ImageData
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
    """

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
        size = view.slotSize if view != None else 36
        objectData = SpriteData(
            Hitbox(size, size),
            {"default": Animation(ImageData("ui/selector", scaleSize=(size, size),
                                            renderOrder=base.OVERLAY))},
            clientData=self.clientKeys())
        if visiblePlayers == None and view != None:
            visiblePlayers = view.visiblePlayers
        if interactivePlayers == None and view != None:
            interactivePlayers = view.interactivePlayers
        super().__init__(core, pos if pos != None else self.cellPos(0, 0), objectData,
                         visiblePlayers, interactivePlayers)

    def cellPos(self, w, h):
        if self.view == None:
            return 0, 0, "world"
        return self.view.slotOrigin(w, h) + (self.view.dimension,)

    def moveToCell(self, cell):
        self.axis = self.cellPos(*cell)[:2]

    # marking

    def markCell(self, cell):
        self.marked = cell
        self.mark = label.Label(self.core, self.cellPos(*cell), "ui/selected",
                                (self.rect.w, self.rect.h), self.visiblePlayers,
                                self.interactivePlayers, base.OVERLAY)
        self.addUiPart(self.mark)

    def clearMark(self):
        self.marked = None
        if self.mark != None:
            self.removeUiPart(self.mark)
            self.mark = None

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
        for playerID, inp in self.inputs():
            cell = self.view.slotAt(inp.getMousePos())
            if cell == None:
                continue
            self.moveToCell(cell)
            if inp.mouseClicked():
                if self.marked == None:
                    self.markCell(cell)
                else:
                    self.interact(cell, playerID)
        return False


def getObject():
    return InventorySelector
