from dataclasses import replace

from data.emitters.image import ImageData
from data.spatial.hitbox import Hitbox
from data.sprites.aliveObject import AliveObject, AliveObjectData
from data.sprites.sprite import Animation

from packages.worldspawn.sprites.uis import inventory, inventorySelector


class Player(AliveObject):
    """The character a person drives.

    One Player exists per participant and its id is that participant's id:
    "main" in single player, the client id once someone joins. That is what
    lets it pull its own InputManager out of the core without being told who
    it belongs to, and it is what the camera follows.

    Its inventory windows are built on the first update rather than in the
    constructor, because the object needs an id before it can hand one to
    the widgets that are only visible to it.
    """

    walkKeys = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
    stepTime = 0.02
    inventoryKey = "e"
    _facingLeft = False

    def __init__(self, core, pos=(0, 0, "world"), tag=None, dictData=None):
        super().__init__(core, pos, None, tag, dictData or {})
        self.inventoryView = None
        self.hotbar = None
        self.selector = None

    def getDefaultData(self):
        self.objectData = AliveObjectData(
            Hitbox(12, 20),
            {"default": Animation(ImageData("player/player_idle")),
             "walk": Animation(ImageData("player/player_walk"), countDown=6),
             "attack": Animation(ImageData("player/player_attack"), countDown=12, weight=2)},
            clientData=["facingLeft"],
            displayByDirectionX=False,
            health=10,
            damage=1,
            shield=0,
            speed=2,
            attackCountDown=25,
            visionRadius=200)

    # facing

    @property
    def facingLeft(self):
        return self._facingLeft

    @facingLeft.setter
    def facingLeft(self, facingLeft):
        if facingLeft == self._facingLeft:
            return
        self._facingLeft = facingLeft
        self.applyFacing()

    def applyFacing(self):
        """Mirror the current frame without touching the animation itself.

        Animation.load pushes its own ImageData into the Image on every
        switch, so the flip has to be re-applied after each load instead of
        being baked into the animation.
        """
        self.image.setImageData(replace(self.getCurrentAnimation().getImageData(),
                                        flipX=self._facingLeft))

    def loadCurrentAnimation(self):
        super().loadCurrentAnimation()
        self.applyFacing()

    # interface

    def buildUI(self):
        screenHeight = self.core.emittersManager.getScreenSize()[1]
        slot = inventory.InventoryView.slotSize
        items = self.inventory.toList()
        self.inventoryView = inventory.InventoryView(
            self.core, w=self.inventory.getW(), h=self.inventory.getH(),
            inventoryList=items, visiblePlayers={self.id}, interactivePlayers={self.id})
        self.hotbar = inventory.InventoryView(
            self.core, w=self.inventory.getW(), h=1, inventoryList=items,
            visiblePlayers={self.id}, interactivePlayers={self.id},
            offset=(0, screenHeight // 2 - slot))
        self.selector = inventorySelector.InventorySelector(
            self.core, view=self.inventoryView, owner=self,
            views=[self.inventoryView, self.hotbar])
        self.inventoryView.addUiPart(self.selector)
        self.core.addObject(self.inventoryView)
        self.core.addObject(self.hotbar)
        self.inventoryView.hide()

    def views(self):
        return [view for view in (self.inventoryView, self.hotbar) if view != None]

    def refreshViews(self):
        for view in self.views():
            view.refresh()

    def dispose(self):
        for view in self.views():
            view.remove()
            self.core.removeObject(view)
        self.inventoryView = None
        self.hotbar = None
        self.selector = None

    # input

    def moveInput(self, inp):
        for key, direction in self.walkKeys.items():
            if inp.isKeyHeld(key):
                self.addExcluciveVector(direction, self.stepTime)
        if inp.isKeyHeld("a") != inp.isKeyHeld("d"):
            self.facingLeft = inp.isKeyHeld("a")

    def inventoryInput(self, inp):
        if inp.isKeyPressed(self.inventoryKey):
            self.inventoryView.toggleVisibility()

    def attackInput(self, inp):
        if self.inventoryView.visible or not inp.mouseClicked():
            return
        if self.isTimer("attack") and not self.timerEnded("attack"):
            return
        self.addTimer("attack", self.attackCountDown)
        self.setAnimation("attack", False)

    # movement

    def solidTiles(self):
        return [tile for tile in self.core.tiles.values() if tile.solid]

    def blocked(self, tiles):
        return any(self.collideCheck(tile) for tile in tiles)

    def resolveCollisions(self, previous):
        """Undo whatever part of this step walked into something solid.

        Each axis is tried on its own first so that sliding along a wall
        still works instead of stopping dead against it. The solid set cannot
        change between those probes, so the world is scanned once.
        """
        if previous == self.axis:
            return
        tiles = self.solidTiles()
        if not self.blocked(tiles):
            return
        moved = self.axis
        self.axis = (previous[0], moved[1])
        if not self.blocked(tiles):
            return
        self.axis = (moved[0], previous[1])
        if not self.blocked(tiles):
            return
        self.axis = previous

    def update(self):
        if self.inventoryView == None:
            self.buildUI()
        inp = self.core.inputMangers.get(self.id)
        if inp != None:
            self.moveInput(inp)
            self.inventoryInput(inp)
            self.attackInput(inp)
        # a step lasts exactly one cycle, and Sprite.update spends it, so the
        # walk animation has to be chosen while the vector is still there
        if self.vectors and self.currentAnimation != "attack":
            self.setAnimation("walk")
        previous = self.axis
        dead = super().update()
        self.resolveCollisions(previous)
        return dead


def getObject():
    return Player
