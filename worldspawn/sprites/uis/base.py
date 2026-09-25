from dataclasses import replace

from data.sprites import uiObject
from data.sprites.sprite import SpriteData
from data.spatial.hitbox import Hitbox

# Render bands used across the package. The display manager draws everything
# below 4 first, sorts the 4s by their y coordinate, then draws the rest in
# insertion order, so UI has to sit above 4 to stay on top of the world.
BACKGROUND = 5
CONTENT = 6
OVERLAY = 7


class UI(uiObject.UIObject):
    """Common base for this package's widgets.

    On top of the engine's UIObject it adds three things every widget needs:

    - constructor arguments that are all optional, and `pos` always second,
      because the engine rebuilds a sprite from a network delta with
      cls(core, pos) and nothing else
    - `viewers` / `controllers`, list-shaped mirrors of the visible and
      interactive player sets that survive a round trip through JSON
    - persistent = False, so windows and cursors stay out of saved worlds;
      whoever owns them builds them again after a load
    """

    persistent = False

    def __init__(self, core, pos=(0, 0, "world"), objectData=None,
                 visiblePlayers=None, interactivePlayers=None):
        super().__init__(core, pos, objectData,
                         set(visiblePlayers or ()), set(interactivePlayers or ()))

    def getDefaultData(self):
        self.objectData = SpriteData(Hitbox(1, 1), {"default": self.defaultAnimation()})

    def defaultAnimation(self):
        # a widget with no art of its own draws nothing, rather than the
        # engine's missing-texture marker: items/none is fully transparent
        from data.emitters.image import ImageData
        from data.sprites.sprite import Animation
        return Animation(ImageData(path="items/none", scaleSize=(1, 1),
                                   renderOrder=BACKGROUND))

    @staticmethod
    def clientKeys(*extra):
        """Fields a widget streams to clients, on top of rect and animation.

        `visible` has to travel: a client rebuilds the widget through
        Sprite.__init__, which starts everything shown, and a window the
        owner has closed would otherwise sit on the guest's screen forever.
        """
        return ["viewers", "controllers", "visible", *extra]

    @property
    def viewers(self):
        return sorted(self.visiblePlayers)

    @viewers.setter
    def viewers(self, viewers):
        self.visiblePlayers = set(viewers)

    @property
    def controllers(self):
        return sorted(self.interactivePlayers)

    @controllers.setter
    def controllers(self, controllers):
        self.interactivePlayers = set(controllers)

    @property
    def renderOrder(self):
        return self.image.renderOrder

    @renderOrder.setter
    def renderOrder(self, renderOrder):
        """Move every frame of this widget into a band.

        Which band a widget belongs in is decided by whoever builds it, so it
        arrives as a constructor argument rather than a class attribute, and
        that makes it one of the things a client cannot work out on its own.
        A widget that streams it applies it to all of its animations: the
        pressed frame of a button sits in the same band as the idle one.
        """
        for animation in self.objectData.animations.values():
            animation.imageData = replace(animation.imageData,
                                          renderOrder=renderOrder)
        self.image.setImageData(self.getCurrentAnimation().getImageData())

    @property
    def scale(self):
        """Box the art is squeezed into, or None when it is drawn as drawn."""
        scaleSize = self.getCurrentAnimation().getImageData().scaleSize
        return None if scaleSize == -1 else list(scaleSize)

    @scale.setter
    def scale(self, scale):
        """Re-apply the size the art was asked for, and follow it with the box.

        The scale is baked into the ImageData when the widget is built, so a
        client that rebuilt it with cls(core, pos) is left with whatever its
        own defaults gave it. The hitbox comes off the pixels afterwards for
        the same reason it does anywhere else: the box that gets clicked has
        to be the box that was drawn.
        """
        scaleSize = -1 if scale == None else tuple(scale)
        for animation in self.objectData.animations.values():
            animation.imageData = replace(animation.imageData,
                                          scaleSize=scaleSize)
        self.image.setImageData(self.getCurrentAnimation().getImageData())
        self.resize(*self.image.size)

    @property
    def authoritative(self):
        """True when this side owns the widget and may build its children.

        A joined client receives every part of a composite widget as its own
        sprite in the host's delta, so rebuilding them locally would draw
        each one twice.
        """
        return self.core.mode != self.core.Mode.join

    def inputs(self):
        """(playerID, InputManager) for every player allowed to interact.

        Skips players whose manager is gone: a client that disconnects has
        its manager dropped before anything gets a chance to forget its id.
        """
        for playerID in self.interactivePlayers:
            inp = self.core.inputMangers.get(playerID)
            if inp != None:
                yield playerID, inp

    def containsPoint(self, point):
        return self.rect.collidePoint(point[0], point[1], self.dimension)

    def resize(self, w, h):
        self.size = (w, h)


def getObject():
    return UI
