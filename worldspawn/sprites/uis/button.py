import pygame

from data.emitters.image import ImageData
from data.spatial.hitbox import Hitbox
from data.spatial.rect import Rect
from data.sprites.sprite import Animation, SpriteData
from data.system import events

from packages.worldspawn.sprites.uis import base, label


class Button(base.UI):
    """A clickable button with an optional icon.

    Reacts to any player listed in interactivePlayers, so the same button can
    be shared by a whole party or handed to exactly one client. Pressing it
    plays the pressed animation, calls onPress if one was given and posts a
    buttonPressed event for anything else that cares.

    A package with its own button art points upTexture and downTexture at it;
    both are scaled to the size the button was asked for, so a nine slice
    sheet is not going to look right, but a plain button will.

    renderOrder is the band the face is drawn in, with the icon one band
    above it, so a button that belongs to a raised panel can be lifted out of
    the default band together with it.
    """

    upTexture = "ui/button_up"
    downTexture = "ui/button_down"

    @staticmethod
    def buttonPressedEventTemplate(buttonID, playerID):
        return pygame.event.Event(events.EventRegister.getID("buttonPressed"), locals())

    buttonPressedEvent = events.EventRegister.register("buttonPressed",
                                                       buttonPressedEventTemplate)

    def __init__(self, core, pos=(0, 0, "world"), visiblePlayers=None,
                 interactivePlayers=None, icon=None, size=(20, 20), onPress=None,
                 pressedCycles=6, renderOrder=base.BACKGROUND):
        self.icon = icon
        self.onPress = onPress
        objectData = SpriteData(
            Hitbox(*size),
            {"default": Animation(ImageData(self.upTexture, scaleSize=size,
                                            renderOrder=renderOrder)),
             "pressed": Animation(ImageData(self.downTexture, scaleSize=size,
                                            renderOrder=renderOrder),
                                  countDown=pressedCycles)},
            clientData=self.clientKeys("renderOrder", "scale"))
        super().__init__(core, pos, objectData, visiblePlayers, interactivePlayers)
        self.iconLabel = None
        if self.icon != None:
            # one band above the face, so a button raised out of the default
            # band takes its icon along instead of being drawn over it
            self.iconLabel = label.Label(core, self.iconPos(size), self.icon,
                                         self.iconSize(size), self.visiblePlayers,
                                         self.interactivePlayers, renderOrder + 1)
            self.addUiPart(self.iconLabel)

    @staticmethod
    def iconSize(size):
        return max(size[0] - 8, 1), max(size[1] - 8, 1)

    def iconPos(self, size):
        icon = self.iconSize(size)
        return Rect.addPos(self.axis, ((size[0] - icon[0]) // 2,
                                       (size[1] - icon[1]) // 2)) + (self.dimension,)

    def moveTo(self, pos):
        self.axis = pos[:2]
        self.dimension = pos[2]
        if self.iconLabel != None:
            self.iconLabel.axis = self.iconPos(self.size)[:2]

    def press(self, playerID):
        self.setAnimation("pressed", False)
        self.addEvent(self.buttonPressedEventTemplate(self.id, playerID))
        if self.onPress != None:
            self.onPress(self, playerID)

    def update(self):
        super().update()
        if not self.visible:
            return False
        for playerID, inp in self.inputs():
            if inp.mouseClicked() and self.containsPoint(inp.getMousePos()):
                self.press(playerID)
        return False


def getObject():
    return Button
