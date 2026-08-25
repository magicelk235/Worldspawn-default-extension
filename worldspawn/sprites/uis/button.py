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
    """

    @staticmethod
    def buttonPressedEventTemplate(buttonID, playerID):
        return pygame.event.Event(events.EventRegister.getID("buttonPressed"), locals())

    buttonPressedEvent = events.EventRegister.register("buttonPressed",
                                                       buttonPressedEventTemplate)

    def __init__(self, core, pos=(0, 0, "world"), visiblePlayers=None,
                 interactivePlayers=None, icon=None, size=(20, 20), onPress=None,
                 pressedCycles=6):
        self.icon = icon
        self.onPress = onPress
        objectData = SpriteData(
            Hitbox(*size),
            {"default": Animation(ImageData("ui/button_up", scaleSize=size,
                                            renderOrder=base.BACKGROUND)),
             "pressed": Animation(ImageData("ui/button_down", scaleSize=size,
                                            renderOrder=base.BACKGROUND),
                                  countDown=pressedCycles)},
            clientData=self.clientKeys())
        super().__init__(core, pos, objectData, visiblePlayers, interactivePlayers)
        if self.icon != None:
            self.addUiPart(label.Label(core, self.iconPos(size), self.icon,
                                       self.iconSize(size), self.visiblePlayers,
                                       self.interactivePlayers, base.CONTENT))

    @staticmethod
    def iconSize(size):
        return max(size[0] - 8, 1), max(size[1] - 8, 1)

    def iconPos(self, size):
        icon = self.iconSize(size)
        return Rect.addPos(self.axis, ((size[0] - icon[0]) // 2,
                                       (size[1] - icon[1]) // 2)) + (self.dimension,)

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
