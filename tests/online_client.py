import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness

harness.buildRoot()

import pygame

import data.core

core = data.core.Core()


def cycle():
    pygame.event.pump()
    if core.mode == core.Mode.join and core.network != None:
        core.clientNetworkUpdate()
    core.clearEvents()
    core.endCycle()
    time.sleep(0.02)


def waitFor(check, why, seconds=8, poke=None):
    deadline = time.time() + seconds
    while time.time() < deadline:
        if poke != None:
            poke()
        cycle()
        if check():
            return
    assert False, why


def widgets():
    return [sprite for sprite in core.sprites.values()
            if type(sprite).__name__ == "InventoryView"]


# before joining, the package runs a local world with its own character
assert core.getObject("main") != None, "single player should start with a character"
assert len(widgets()) == 0, "windows only exist once the player has updated"

assert core.join("127.0.0.1", 5601, identity="guest")
assert core.getObject("main") == None, "joining must drop the local world"
assert core.sprites == {}, f"local world left behind: {list(core.sprites)}"

waitFor(lambda: core.userID == "guest", "welcome should adopt the identity")
waitFor(lambda: core.getObject("guest") != None, "the host should spawn our character")

# the host's own character is world state and reaches every client
waitFor(lambda: core.getObject("main") != None, "the host's character should stream over")

# the host runs two players, each with two windows; filterVisible has to keep
# the host's pair off this connection
waitFor(lambda: len(widgets()) == 2, "our two windows should arrive")
time.sleep(0.5)
for _ in range(20):
    cycle()
assert len(widgets()) == 2, f"another player's windows leaked: {len(widgets())}"
for widget in widgets():
    assert core.userID in widget.visiblePlayers, widget.visiblePlayers

# the widgets have to arrive looking like the host's, not like whatever the
# default constructor produced
grid = next(widget for widget in widgets() if widget.grid == [5, 5])
hotbar = next(widget for widget in widgets() if widget.grid == [5, 1])
assert not grid.visible, "the full inventory arrives closed, the way the owner left it"
assert hotbar.visible, "the hotbar arrives open"
assert hotbar.image.getRawImage().get_size() == (180, 36), \
    f"hotbar background should match its grid, got {hotbar.image.getRawImage().get_size()}"
assert grid.image.getRawImage().get_size() == (180, 180)

# tiles reach the client too
tiles = [sprite for sprite in core.sprites.values() if hasattr(sprite, "solid")]
assert len(tiles) == 17, f"expected 16 grass and 1 stone, got {len(tiles)}"

# held keys travel to the host, which moves our character and streams it back
startX = core.getObject("guest").rect.x
localInput = core.getInputManager("guest")
waitFor(lambda: core.getObject("guest").rect.x > startX,
        "holding d should move our character on the host",
        poke=lambda: setattr(localInput, "keys", {"d"}))
localInput.keys = set()

# a keypress opens our window on the host and the new state streams back
waitFor(lambda: grid.visible, "e should open our inventory on the host",
        poke=lambda: localInput.addEvent(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e, mod=0, unicode="e")))

# clicking a slot makes the host mark it, and the highlight has to arrive with
# its texture rather than the engine's placeholder square
slot = (grid.rect.x + 18, grid.rect.y + 18)
localInput.mousePos = slot
for _ in range(5):
    cycle()
localInput.addEvent(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=slot))
waitFor(lambda: any(getattr(sprite, "texture", None) == "ui/selected"
                    for sprite in core.sprites.values()),
        "the marked slot's highlight should stream over with its texture")

# dropping the connection puts us back in our own world with a character
core.network.close()
waitFor(lambda: core.mode == core.Mode.start, "losing the host should fall back")
assert core.userID == "main", core.userID
assert core.getObject("main") != None, "the local character should come back"
assert core.getObject("guest") == None, "the host's world should be gone"

print("online OK", flush=True)
