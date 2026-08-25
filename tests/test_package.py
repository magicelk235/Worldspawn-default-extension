"""Headless check that the package still works against the engine.

    python tests/test_package.py

See harness.py for how the throwaway engine root is put together.
"""

import json
import shutil
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness

ROOT = harness.buildRoot()

import pygame

import data.core
from data.inventory.inventory import InventoryItem
from data.managers.timeManager import TimeManager

core = data.core.Core()
player = core.getObject(core.userID)
localInput = core.getInputManager(core.userID)


def keyDown(name):
    return pygame.event.Event(pygame.KEYDOWN, {"key": pygame.key.key_code(name),
                                               "mod": 0, "unicode": name})


def click(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})


def step(keys=(), events=(), mouse=(0, 0), times=1, render=False):
    """One engine cycle, with the timer event the loop normally waits for."""
    for _ in range(times):
        localInput.setInput(list(events), list(keys), mouse)
        core.addEvent(pygame.event.Event(TimeManager.timerEvent))
        core.clearEvents()
        core.update()
        if render:
            core.emittersManager.update(core.getObject(core.userID), True)
        core.endCycle()


# --- package loads and registers its content -------------------------------

assert "worldspawn" in core.packages, "package should be always-enabled"
assert player != None, "core extension must spawn a player under core.userID"
assert type(player).__name__ == "Player", type(player).__name__
assert player.prefabPath == "players.base", player.prefabPath
assert core.getTiles("grass") != None and core.getTiles("stone") != None
assert core.getUis("button") != None and core.getUis("inventory") != None

for name in ("none", "rock", "woodenSword"):
    item = core.getItems(name)()
    assert item.getName() == name, f"{name} -> {item.getName()}"

# --- inventory windows -----------------------------------------------------

step()
assert player.inventoryView != None and player.hotbar != None, "windows build on first update"
assert not player.inventoryView.visible, "the full grid starts closed"
assert player.hotbar.visible, "the hotbar stays open"
assert len(player.inventoryView.slots) == 25, len(player.inventoryView.slots)
assert player.selector in player.inventoryView.uiParts

for slot in player.inventoryView.slots:
    assert slot.itemName == "none" and slot.count == 0

player.inventory.addItemByCount(core.getItems("rock")(), 7)
player.refreshViews()
assert player.inventoryView.slots[0].itemName == "rock"
assert player.inventoryView.slots[0].count == 7
assert player.hotbar.slots[0].itemName == "rock", "hotbar shares the first row"
assert player.inventoryView.slots[0].countText.text == "7"

# --- opening and closing the grid ------------------------------------------

step(events=[keyDown("e")])
assert player.inventoryView.visible, "e should open the inventory"
assert player.selector.visible, "the selector follows its view"
step(events=[keyDown("e")])
assert not player.inventoryView.visible, "e should close it again"
assert not player.selector.visible

# --- picking an item up and putting it down --------------------------------

step(events=[keyDown("e")])
view = player.inventoryView
firstCell = view.slotOrigin(0, 0)
secondCell = view.slotOrigin(2, 1)
inside = (firstCell[0] + 4, firstCell[1] + 4)
target = (secondCell[0] + 4, secondCell[1] + 4)

step(events=[click(inside)], mouse=inside)
assert player.selector.marked == (0, 0), player.selector.marked
assert player.selector.mark != None, "a picked slot gets a highlight"

step(events=[click(target)], mouse=target)
assert player.selector.marked == None, "the second click resolves the move"
assert player.selector.mark == None
assert player.inventory.getItem(0, 0).getItemName() == "none", "source slot emptied"
assert player.inventory.getItem(2, 1).getItemName() == "rock", "rock moved"
assert player.inventory.getItem(2, 1).getCount() == 7
assert view.slots[view.slotIndex(2, 1)].itemName == "rock", "the view refreshed"
assert player.hotbar.slots[0].itemName == "none", "so did the hotbar"

# same item on both sides: the marked stack must land on the target, not the
# other way round
player.inventory.getItem(0, 0).copy(InventoryItem(core.getItems("rock")(), 4))
player.refreshViews()
assert player.inventory.getItem(0, 0).getCount() == 4
fromPoint = view.slotOrigin(0, 0)
step(events=[click((fromPoint[0] + 4, fromPoint[1] + 4))],
     mouse=(fromPoint[0] + 4, fromPoint[1] + 4))
step(events=[click(target)], mouse=target)
assert player.inventory.getItem(0, 0).getItemName() == "none", "the marked slot empties"
assert player.inventory.getItem(2, 1).getCount() == 11, \
    f"both stacks should end up on the target ({player.inventory.getItem(2, 1).getCount()})"

step(events=[keyDown("e")])

# --- walking ---------------------------------------------------------------

startX = player.x
step(keys=["d"], times=10)
assert player.x > startX, f"holding d should move right ({startX} -> {player.x})"
assert not player.facingLeft

step(keys=["a"], times=10)
assert player.facingLeft, "a should turn the character around"
assert player.image.imageData.flipX, "and mirror the frame it draws"

step(times=30)
assert player.currentAnimation == "default", "walking stops when the keys do"

# --- solid tiles block, open ground does not -------------------------------

player.axis = (0, 0)
step(times=2)
core.spawnTile("grass", (player.x + 24, player.y, "world"))
walkedX = player.x
step(keys=["d"], times=20)
assert player.x > walkedX, "grass is not solid"

blockX = player.x + 16
core.spawnTile("stone", (blockX, player.y, "world"))
step(keys=["d"], times=40)
assert player.rect.rect.right <= blockX + 1, f"stone should stop the player ({player.rect.rect.right} vs {blockX})"

step(keys=["s"], times=20)
assert player.y > 0, "the wall must not block the free axis"
assert player.currentAnimation == "walk", "moving should play the walk cycle"

step(times=30)
assert player.currentAnimation == "default", "and standing still should end it"

# --- buttons ---------------------------------------------------------------

pressed = []
button = core.getUis("button")(core, (300, 200, "world"), {core.userID}, {core.userID},
                               icon="items/rock", size=(24, 24),
                               onPress=lambda button, playerID: pressed.append(playerID))
core.addObject(button)
buttonPoint = (button.x + 4, button.y + 4)
step(events=[click(buttonPoint)], mouse=buttonPoint)
assert pressed == [core.userID], pressed
assert button.currentAnimation == "pressed"
assert core.eventHappened("buttonPressed") or core.eventWillHappen("buttonPressed")
step(times=10)
assert button.currentAnimation == "default", "the button pops back up"

step(events=[click((0, 0))], mouse=(0, 0))
assert pressed == [core.userID], "clicks outside the button are ignored"

# --- everything renders ----------------------------------------------------

step(times=3, render=True)

# --- saving and reloading a world ------------------------------------------

player.axis = (48, 64)
step(times=2)
core.saveWorld("check")
savedX, savedY = player.axis
tileCount = len(core.tiles)

with open(f"{ROOT}/save/check/sprites.json") as f:
    saved = json.load(f)
assert not any(entry["prefabPath"].startswith("uis.") for entry in saved.values()), \
    "windows must not end up in a saved world"

core.loadWorld("check")
reloaded = core.getObject(core.userID)
assert reloaded != None, "the player comes back"
assert (reloaded.x, reloaded.y) == (savedX, savedY), (reloaded.axis, (savedX, savedY))
assert len(core.tiles) == tileCount, (len(core.tiles), tileCount)

step()
assert reloaded.inventoryView != None, "the reloaded player rebuilds its windows"
assert len([s for s in core.sprites.values()
            if type(s).__name__ == "InventoryView"]) == 2, "and only one set of them"

step(times=2, render=True)

shutil.rmtree(ROOT, ignore_errors=True)
print("package OK")
