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
        from data.sprites.sprite import Animation
        return Animation()

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

    def remove(self):
        for part in list(self.uiParts):
            part.remove()
            self.removeUiPart(part)

    def __del__(self):
        # The engine's UIObject unregisters its parts here. Teardown in this
        # package is explicit through remove(); doing it from the collector
        # means mutating the core's id tables at an arbitrary point, which
        # blows up when the parts were already removed with their parent.
        pass


def getObject():
    return UI
