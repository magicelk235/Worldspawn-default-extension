from data.inventory.modifiers import Modifier


class Item:
    """Base for everything that can sit in an inventory slot.

    Items are stateless and shared: the engine looks a class up with
    core.getItems(name) and instantiates it whenever a slot needs one, so
    never keep per-slot state here. Slot count lives on the InventoryItem.
    """

    def __init__(self, name, max=32, modifiers=(), toolType=None, color=None):
        self.name = name
        self.max = max
        self.modifiers = tuple(modifiers)
        self.toolType = toolType
        self.color = color

    def getName(self):
        return self.name

    def getMax(self):
        return self.max

    def getModifiers(self):
        return self.modifiers

    def getColor(self):
        return self.color

    def applyModifiers(self, object, hand=False):
        Modifier.applyForList(self.modifiers, object, hand)

    def update(self):
        pass

    def __eq__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name == other.name and self.max == other.max
                and self.modifiers == other.modifiers
                and self.toolType == other.toolType and self.color == other.color)

    def __hash__(self):
        return hash((self.name, self.max, self.modifiers, self.toolType, self.color))

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"


def getObject():
    return Item
