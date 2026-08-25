from packages.worldspawn.static.items.item import Item


class NoneItem(Item):
    """The empty slot.

    The engine's Inventory clears a slot with core.getItems("none")(), so this
    name has to exist in every world. Its texture is a fully transparent
    16x16, which is what makes an empty slot look empty.
    """

    def __init__(self):
        super().__init__("none", max=0)


def getObject():
    return NoneItem
