"""Headless checks on what the widgets draw and where they answer clicks.

    python tests/test_widgets.py

test_package.py covers behaviour: opening windows, moving stacks, pressing
buttons. This one covers appearance, which is the half that used to drift:
every widget has to draw its own art, the box that gets clicked has to be the
box that was drawn, the geometry a package needs to change has to be reachable
from a subclass, and a widget's children have to follow it around.
"""

import shutil
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness

ROOT = harness.buildRoot()

import pygame

import data.core
from data.buffers.assetsLoader import AssetsLoader
from data.emitters.image import Image, ImageData
from data.managers.timeManager import TimeManager

from packages.worldspawn.sprites.uis import (base, button, inventory,
                                            inventorySelector, itemSlot, label,
                                            text)

core = data.core.Core()
player = core.getObject(core.userID)
localInput = core.getInputManager(core.userID)
ME = core.userID


def step(times=1, events=(), mouse=(0, 0)):
    for _ in range(times):
        localInput.setInput(list(events), [], mouse)
        core.addEvent(pygame.event.Event(TimeManager.timerEvent))
        core.clearEvents()
        core.update()
        core.endCycle()


def artSize(path):
    return AssetsLoader.get("textures", path)[0][0].get_size()


def click(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})


def asPackage(cls, model):
    """Let a check-local subclass keep its base's place in the package tree.

    The core reads a sprite's domain and prefab off its module path, and a
    class defined in a check script has none it recognises.
    """
    cls.__module__ = model.__module__
    return cls


step()

# --- Label: one size for the pixels and the hitbox --------------------------

# player_idle is 16x24, so a square default would hide a stretch
tall = artSize("player/player_idle")
assert tall[0] != tall[1], "this check needs a texture that is not square"

native = label.Label(core, (10, 10, "world"), "player/player_idle", None, {ME}, {ME})
core.addObject(native)
assert native.image.size == tall, f"no size given means the art's own: {native.image.size}"
assert native.size == tall, f"and the hitbox follows it: {native.size}"
assert native.containsPoint((10 + tall[0] - 1, 10 + tall[1] - 1))
assert not native.containsPoint((10 + tall[0], 10 + tall[1]))

scaled = label.Label(core, (10, 10, "world"), "player/player_idle", (40, 12), {ME}, {ME})
core.addObject(scaled)
assert scaled.image.size == (40, 12), scaled.image.size
assert scaled.size == (40, 12), "a size given is applied to both"

# a swapped texture takes the box with it when no size was pinned
square = artSize("ui/slot")
native.texture = "ui/slot"
assert native.image.size == square and native.size == square, (native.image.size, native.size)
scaled.texture = "ui/slot"
assert scaled.image.size == (40, 12), "a pinned size survives a texture swap"

# --- ItemSlot: ragged item art is not squeezed into a square ----------------

class TallSlot(itemSlot.ItemSlot):
    countOffset = (14, 14)
    countFontSize = 24
    countColor = (0, 0, 0, 255)

    def texturePath(self):
        return "player/player_idle"


asPackage(TallSlot, itemSlot.ItemSlot)


loose = TallSlot(core, (0, 0, "world"), "rock", 3, None, {ME}, {ME})
core.addObject(loose)
assert loose.image.size == tall, f"native art keeps its shape: {loose.image.size}"
assert loose.size == tall
assert loose.countText.axis == (14, 14), loose.countText.axis
assert loose.countText.color == (0, 0, 0, 255)
assert loose.countText.fontSize == 24
assert loose.countText.text == "3"
bigCount = loose.countText.size
plainCount = itemSlot.ItemSlot(core, (0, 0, "world"), "rock", 3, None, {ME}, {ME})
core.addObject(plainCount)
assert plainCount.countText.size[1] < bigCount[1], \
    f"a bigger point size draws bigger text: {plainCount.countText.size} vs {bigCount}"

boxed = itemSlot.ItemSlot(core, (0, 0, "world"), "rock", 1, (8, 8), {ME}, {ME})
core.addObject(boxed)
assert boxed.image.size == (8, 8) and boxed.size == (8, 8)
assert boxed.countText.text == "", "a single item shows no count"

# the icon and its count move together
loose.moveTo((60, 70, "world"))
assert loose.axis == (60, 70)
assert loose.countText.axis == (74, 84), loose.countText.axis

# and a longer number keeps the box around the pixels
loose.count = 12345
assert loose.countText.size == Image.measure(loose.countText.image.imageData), \
    "the text hitbox has to match the line it drew"

# Colour and face are the other half of what a line looks like, and a host
# streams them as plain attributes, so assigning one has to redraw the line
# rather than leave the look its own class defaults gave it.
line = loose.countText
wasBlack = pygame.image.tobytes(line.image.getRawImage(), "RGBA")
line.color = [255, 0, 0, 255]
assert line.color == (255, 0, 0, 255), "a colour off the wire arrives as a list"
assert pygame.image.tobytes(line.image.getRawImage(), "RGBA") != wasBlack, \
    "setting the colour has to redraw the line"
smallSize = line.size
line.fontSize = 8
assert line.size[1] < smallSize[1], f"a smaller point size draws smaller: {line.size}"
line.font = None
assert line.size == Image.measure(line.image.imageData), \
    "swapping the face keeps the box around the pixels"

# --- InventoryView: the panel a package draws is the panel it clicks --------

class BorderedView(inventory.InventoryView):
    """A view whose marker overhangs its cell, the way the original's did."""

    slotSize = 36
    iconSize = None
    iconPadding = (5, 5)
    border = 4

    def panelSize(self):
        grid = self.gridSize()
        return grid[0] + self.border, grid[1] + self.border

    def backgroundData(self):
        return ImageData("ui/slot", cutSize=self.panelSize(),
                         renderOrder=base.BACKGROUND)


asPackage(BorderedView, inventory.InventoryView)


view = BorderedView(core, (100, 40, "world"), 3, 2, (), {ME}, {ME})
core.addObject(view)
assert view.gridSize() == (108, 72)
assert view.panelSize() == (112, 76)
assert view.size == (112, 76), f"the hitbox is the panel, not the cells: {view.size}"
assert view.image.size == (112, 76), f"and so is the drawn art: {view.image.size}"
assert view.slotPos(0, 0) == (105, 45, "world"), view.slotPos(0, 0)
assert view.slotPos(1, 1) == (141, 81, "world"), view.slotPos(1, 1)
assert len(view.slots) == 6
assert view.slots[0].image.size == artSize("items/none"), \
    "a cell with no size draws the item at its own size"

# a click on the border belongs to no cell, but is still inside the panel
assert view.slotAt((100, 40)) == (0, 0)
assert view.slotAt((100 + 107, 40 + 71)) == (2, 1)
assert view.containsPoint((100 + 110, 40 + 74)), "the border is part of the panel"
assert view.slotAt((100 + 110, 40 + 74)) == None, "but it is not a cell"
assert view.slotAt((99, 40)) == None

# the panel and its cut survive a resize, through the override
view.setGrid(4, 4)
assert view.panelSize() == (148, 148)
assert view.size == (148, 148) and view.image.size == (148, 148)
assert len(view.slots) == 16

# the same over the network path a client takes
view.grid = [2, 2]
assert view.size == (76, 76) and view.image.size == (76, 76)

# a specialised cell class is reachable without rewriting the loop
class MarkedSlot(itemSlot.ItemSlot):
    pass


asPackage(MarkedSlot, itemSlot.ItemSlot)


class MarkedView(BorderedView):
    slotClass = MarkedSlot


asPackage(MarkedView, BorderedView)


marked = MarkedView(core, (0, 0, "world"), 2, 1, (), {ME}, {ME})
core.addObject(marked)
assert all(isinstance(slot, MarkedSlot) for slot in marked.slots), \
    "slotClass has to decide what a cell is"

# --- InventorySelector: art at its own size, overhanging the cell -----------

class NativeSelector(inventorySelector.InventorySelector):
    cursorSize = None


asPackage(NativeSelector, inventorySelector.InventorySelector)


scaledSelector = inventorySelector.InventorySelector(core, None, view, None, [view],
                                                     {ME}, {ME})
core.addObject(scaledSelector)
assert scaledSelector.image.size == (view.slotSize, view.slotSize), \
    f"the default scales both marks to the pitch: {scaledSelector.image.size}"

nativeSelector = NativeSelector(core, None, view, None, [view], {ME}, {ME})
core.addObject(nativeSelector)
cursorArt = artSize(NativeSelector.cursorTexture)
assert nativeSelector.image.size == cursorArt, \
    f"cursorSize None keeps the art's size: {nativeSelector.image.size}"
assert nativeSelector.size == cursorArt, "and the hitbox agrees"

nativeSelector.markCell((1, 0))
assert nativeSelector.mark.image.size == artSize(NativeSelector.markTexture)
assert nativeSelector.mark.axis == view.slotOrigin(1, 0), \
    "the mark sits on the cell origin, not inside the padding"

# --- Button: its own art, and its own hit box ------------------------------

class RedButton(button.Button):
    upTexture = "ui/slot"
    downTexture = "ui/selected"


asPackage(RedButton, button.Button)


pressed = []
custom = RedButton(core, (300, 200, "world"), {ME}, {ME}, size=(24, 24),
                   onPress=lambda widget, playerID: pressed.append(playerID))
core.addObject(custom)
assert custom.getAnimation("default").imageData.path == "ui/slot"
assert custom.getAnimation("pressed").imageData.path == "ui/selected"
assert custom.image.size == (24, 24) and custom.size == (24, 24)
step(events=[click((301, 201))], mouse=(301, 201))
assert pressed == [ME], pressed
assert custom.image.size == (24, 24), "the pressed frame is the same size"
step(events=[click((330, 201))], mouse=(330, 201))
assert pressed == [ME], "a click past the drawn edge is not a press"

iconed = RedButton(core, (300, 100, "world"), {ME}, {ME}, icon="items/rock",
                   size=(24, 24))
core.addObject(iconed)
assert iconed.iconLabel != None and iconed.iconLabel in iconed.uiParts
assert iconed.iconLabel.axis == (304, 104), iconed.iconLabel.axis
assert iconed.iconLabel.image.size == RedButton.iconSize((24, 24))
iconed.moveTo((500, 150, "world"))
assert iconed.iconLabel.axis == (504, 154), \
    f"the icon has to travel with the button: {iconed.iconLabel.axis}"

# --- children follow, hide with and die with their parent ------------------

parent = label.Label(core, (0, 0, "world"), "ui/slot", None, {ME}, {ME})
core.addObject(parent)
child = label.Label(core, (4, 4, "world"), "ui/selected", None, set(), set())
parent.addUiPart(child)
assert child in parent.uiParts
assert core.getObject(child.id) is child, "a part is a real sprite in the core"

parent.hide()
assert not child.visible, "a hidden parent hides its parts"
parent.show()
assert child.visible, "and shows them again"
parent.addVisiblePlayer(ME)
assert ME in child.visiblePlayers, "a new viewer reaches the parts"

parent.remove()
assert parent.uiParts == [], parent.uiParts
assert core.getObject(child.id) == None, "removing a widget removes its parts"

# a slot's count text is a part, so it goes with the slot
countID = loose.countText.id
loose.remove()
assert core.getObject(countID) == None, "a removed slot takes its count with it"

# and a view takes its cells
slotIDs = [slot.id for slot in view.slots]
selectorID = scaledSelector.id
view.clearSlots()
assert all(core.getObject(id) == None for id in slotIDs), "cleared cells are gone"

# --- a guest rebuilds a widget from nothing but its stream -----------------

# spawnFromEntry is the whole story on the receiving end: cls(core, pos) and
# then the streamed fields. Anything that decides what a widget looks like and
# came in as a constructor argument has to be in that stream, or the guest is
# left with whatever the class defaults gave it.

guest = data.core.Core()
guest.mode = guest.Mode.join


def streamed(widget, name):
    core.addObject(widget)
    copy = guest.spawnFromEntry(f"streamed-{widget.id}", widget.prefabPath,
                                widget.toData())
    assert copy != None, f"{name} did not rebuild on a guest at all"
    assert copy.renderOrder == widget.renderOrder, \
        f"{name} changed band on a guest: {widget.renderOrder} -> {copy.renderOrder}"
    assert copy.image.size == widget.image.size, \
        f"{name} changed size on a guest: {widget.image.size} -> {copy.image.size}"
    assert tuple(copy.rect.rect) == tuple(widget.rect.rect), \
        f"{name} changed hitbox on a guest: {tuple(copy.rect.rect)}"
    assert tuple(copy.artRect.rect) == tuple(widget.artRect.rect), \
        f"{name} draws somewhere else on a guest: {tuple(copy.artRect.rect)}"
    assert copy.visible == widget.visible, f"{name} lost its visibility"
    assert pygame.image.tobytes(copy.image.getRawImage(), "RGBA") == \
        pygame.image.tobytes(widget.image.getRawImage(), "RGBA"), \
        f"{name} draws different pixels on a guest"
    return copy


streamed(label.Label(core, (5, 5, "world"), "items/rock", None, {ME}, {ME}),
         "a label at its own size")
streamed(label.Label(core, (5, 5, "world"), "items/rock", (48, 9), {ME}, {ME},
                     base.CONTENT),
         "a scaled label out of its default band")
streamed(label.Label(core, (5, 5, "world"),
                     ImageData("ui/slot", cutSize=(72, 36), flipX=True,
                               color=(255, 0, 0, 255), renderOrder=base.BACKGROUND),
                     None, {ME}, {ME}),
         "a label built from whole image data")
streamed(text.Text(core, (5, 5, "world"), "42", None, 20, {ME}, {ME},
                   (10, 200, 30, 255), base.OVERLAY),
         "a coloured line out of its default band")
streamed(button.Button(core, (5, 5, "world"), {ME}, {ME}, None, (64, 32)),
         "a button bigger than the default")
streamed(button.Button(core, (5, 5, "world"), {ME}, {ME}, "items/rock", (40, 40),
                       None, 6, base.CONTENT),
         "a button raised out of its default band")
streamed(itemSlot.ItemSlot(core, (5, 5, "world"), "rock", 3, (24, 24), {ME}, {ME}),
         "a cell forcing every icon into one box")

wide = inventory.InventoryView(core, (200, 5, "world"), 3, 3, (), {ME}, {ME})
core.addObject(wide)
streamed(wide, "an inventory panel")
streamed(inventorySelector.InventorySelector(core, None, wide, None, [wide], {ME},
                                             {ME}),
         "a selector following the view's pitch")


class WidePitch(inventory.InventoryView):
    slotSize = 48
    iconSize = 32


asPackage(WidePitch, inventory.InventoryView)


pitched = WidePitch(core, (400, 5, "world"), 2, 2, (), {ME}, {ME})
core.addObject(pitched)
streamed(pitched.slots[0], "a cell from a package with a wider pitch")
guestCursor = streamed(
    inventorySelector.InventorySelector(core, None, pitched, None, [pitched], {ME},
                                        {ME}),
    "a cursor scaled to a wider pitch")
assert guestCursor.image.size == (WidePitch.slotSize, WidePitch.slotSize), \
    f"a guest cannot work the pitch out on its own: {guestCursor.image.size}"

# a guest cell that is handed a different item keeps the box it was given
guestCell = streamed(itemSlot.ItemSlot(core, (5, 5, "world"), "none", 0, (24, 24),
                                       {ME}, {ME}),
                     "an empty boxed cell")
guestCell.itemName = "rock"
assert guestCell.image.size == (24, 24), \
    f"a new item must not escape the cell's box: {guestCell.image.size}"

# a button's icon sits one band above its face, so a raised button stays whole
raised = button.Button(core, (5, 5, "world"), {ME}, {ME}, "items/rock", (40, 40),
                       None, 6, base.CONTENT)
core.addObject(raised)
assert raised.renderOrder == base.CONTENT, raised.renderOrder
assert raised.iconLabel.renderOrder == base.CONTENT + 1, raised.iconLabel.renderOrder
assert raised.getAnimation("pressed").imageData.renderOrder == base.CONTENT, \
    "the pressed frame belongs in the same band as the idle one"

# --- a view follows the inventory it was handed ----------------------------

# Inventory.toList() hands out one list object and refills it in place, so a
# view that copies it stops seeing the model the first time the grid reshapes.

live = player.inventory.toList()
tracking = inventory.InventoryView(core, (0, 200, "world"), player.inventory.getW(),
                                   player.inventory.getH(), live, {ME}, {ME})
core.addObject(tracking)
assert tracking.inventoryList is live, "the view has to hold the model's own list"

player.inventory.size = (player.inventory.getW() + 1, player.inventory.getH())
tracking.setGrid(player.inventory.getW(), player.inventory.getH())
tracking.refresh()
for h in range(tracking.h):
    for w in range(tracking.w):
        slot = tracking.slots[tracking.slotIndex(w, h)]
        item = player.inventory.getItem(w, h)
        assert (slot.itemName, slot.count) == (item.getItemName(), item.getCount()), \
            f"cell {(w, h)} shows {(slot.itemName, slot.count)}, model holds " \
            f"{(item.getItemName(), item.getCount())}"

# a view that was given a position owns it; only a centred one is re-derived
placed = inventory.InventoryView(core, (17, 23, "world"), 2, 2, (), {ME}, {ME})
core.addObject(placed)
placed.setGrid(3, 3)
assert placed.axis == (17, 23), f"a placed panel was moved by a resize: {placed.axis}"
assert placed.slots[0].axis == placed.slotPos(0, 0)[:2]

centred = inventory.InventoryView(core, None, 2, 2, (), {ME}, {ME})
core.addObject(centred)
wasCentred = centred.axis
centred.setGrid(4, 4)
assert centred.axis != wasCentred, "a centred panel still recentres when it grows"
assert centred.axis == centred.centeredPos(core)[:2], centred.axis

# --- the selector holds exactly one mark, and only a real one --------------

picker = inventorySelector.InventorySelector(core, None, tracking, player,
                                             [tracking], {ME}, {ME})
core.addObject(picker)
picker.markCell((0, 0))
firstMark = picker.mark.id
picker.markCell((1, 1))
assert core.getObject(firstMark) == None, \
    "marking a second cell has to take the first marker with it"
assert len(picker.uiParts) == 1, picker.uiParts
picker.clearMark()

# a mark taken before a resize names a cell that is no longer there; using it
# walks off the end of the inventory's rows
picker.markCell((tracking.w - 1, tracking.h - 1))
staleMark = picker.mark.id
player.inventory.size = (2, 2)
tracking.setGrid(2, 2)
tracking.refresh()
step()
assert picker.marked == None, f"a mark outside the grid survived: {picker.marked}"
assert core.getObject(staleMark) == None, "and its marker is still on the grid"

# a closed window answers no clicks, even with the cursor left visible
tracking.hide()
picker.show()
origin = tracking.slotOrigin(0, 0)
point = (origin[0] + 4, origin[1] + 4)
step(events=[click(point)], mouse=point)
assert picker.marked == None, "a hidden view must not be pickable"


# --- a frame with all of it on screen -------------------------------------

core.emittersManager.update(player, True)
surface = core.emittersManager.displayManager.displaySurface
placeholder = AssetsLoader.assets["textures"].defaultAsset[0][0]
for widget in (native, scaled, boxed, marked, nativeSelector, custom, plainCount):
    frame = widget.image.getRawImage()
    if frame.get_size() != placeholder.get_size():
        continue
    assert pygame.image.tobytes(frame, "RGBA") != pygame.image.tobytes(placeholder, "RGBA"), \
        f"{type(widget).__name__} is drawing the missing-texture marker"

shutil.rmtree(ROOT, ignore_errors=True)
print("widgets OK")
