# Worldspawn default extension

Content for the [Worldspawn engine](https://github.com/magicelk235/Worldspawn-engine).

The engine handles sprites, animation, input, saved worlds and networking, and then stops. There is no character in it, no ground, no inventory, nothing to click. That is on purpose, but it does mean a fresh checkout gives you a black window. This package fills that gap: a character you can walk around, tiles to walk on, an inventory that actually moves items when you drag them, and the widgets to build the rest of your interface from.

Use it as the base for your own game, subclass the bits you want to change, or read it to see how a Worldspawn package fits together. Free to use and open source.

## Install

Copy or link the `worldspawn` folder into your engine's `packages`:

```bash
git clone https://github.com/magicelk235/Worldspawn-default-extension.git
ln -s "$PWD/Worldspawn-default-extension/worldspawn" /path/to/Worldspawn-engine/packages/worldspawn
cd /path/to/Worldspawn-engine && python main.py
```

Nothing to switch on. The package is `always-enabled`, and you get a character under `core.userID` the moment the core boots.

WASD walks. E opens the inventory. Click swings. Click one slot then another to move a stack.

## Players

`core.getPlayers("base")`

The character belongs to whoever owns its id, which is `main` on your own machine and the client id once someone joins your world. That is how it finds its own input manager without being told who is driving it, and it is what the camera follows.

Its two inventory windows get built on the first update rather than in the constructor. It needs an id before it can hand one to a widget that nobody else is allowed to see.

## Tiles

`core.getTiles("grass")`, `core.getTiles("stone")`

Squares of ground, drawn under everything else. Grass you can walk over, stone you cannot. A new one is four lines: subclass `Tile`, set `texture`, `tileSize` and `isSolid`.

```python
core.spawnTile("stone", (64, 0, "world"))
core.fillTiles("grass", (-160, -120), 20, 15)
```

## Widgets

`core.getUis(name)`

| name | what it is |
| --- | --- |
| `base` | `UI`, which everything else here extends |
| `text` | a line of text you can change after it is on screen |
| `label` | a plain image, useful as a child of another widget |
| `button` | clickable, takes an icon and an `onPress` callback |
| `itemSlot` | one cell: item icon and stack count |
| `inventory` | `InventoryView`, a grid of slots over an `Inventory` |
| `inventorySelector` | the cursor that picks up a slot and drops it on another |

Every widget carries the set of players allowed to see it and the set allowed to click it, so on a shared world a window can belong to exactly one person.

## Items

`core.getItems(name)`

Four of them: `item` (the base), `none`, `rock` and `woodenSword`. The engine's `Inventory` empties a slot by calling `core.getItems("none")()`, so without this package a world cannot hold an inventory at all.

Items are stateless and shared between every slot that holds them; the count lives on the slot. Modifiers are applied once per distinct item name in the inventory:

```python
class WoodenSword(Item):
    def __init__(self):
        super().__init__("woodenSword", max=1, modifiers=(
            Modifier("damage", 3, Mode.MaxSet),
        ))
```

## How it is laid out

```
worldspawn/
├── settings.yaml     always-enabled, no dependencies, two domains
├── domains.yaml      declares the sprites and static domains
├── core.py           the WorldSpawn core extension
├── assets/textures/  player, tiles, items, ui
├── sprites/          domain: things that live in the world and tick
│   ├── base.py
│   ├── players/
│   ├── tiles/
│   └── uis/
└── static/           domain: lookup only
    └── items/
```

A domain folder holds one folder per prefab, and every file in a prefab exposes `getObject()` returning its class. That is what turns `sprites/tiles/` into `core.getTiles(name)` for the classes and `core.tiles` for the live objects.

Anything in the `sprites` domain lands in `core.sprites`, which is the dict the main loop walks, so it updates every cycle. The `static` domain only creates getters. Items never enter the world.

## Online

Host or join and the package handles the rest:

```python
core.host(5599)
core.join("192.168.1.10", 5599, identity=myId)
```

The host spawns a character for each client that connects and removes it when they leave. Joining throws the local world away first, before the connection produces anything, because the host keeps track of what it has already sent and would never resend whatever you discarded after the fact. Lose the connection and you land back in a fresh local world with your own character.

`filterVisible` is replaced so a player's windows only go to that player. World sprites still go to everyone.

Windows are also marked `persistent = False`, which keeps them out of saved worlds. A save holds the world, and whoever owns a window builds it again after a load.

## Checks

Assert scripts, the same style the engine uses. They build a throwaway root out of the engine's `data/` and this package, so your engine checkout is never written to. Set `WORLDSPAWN_ENGINE` if it is somewhere other than the sibling `../Worldspawn-engine`.

```bash
python tests/test_package.py   # spawning, inventory, walking, collision, buttons, saves
python tests/test_online.py    # a host and a client, two processes
```

## Requirements

Whatever the engine needs: pygame-ce, gif-pygame, Pillow, sympy, pyyaml.
