from packages.worldspawn.static.items.item import Item


class Rock(Item):
    def __init__(self):
        super().__init__("rock", max=64)


def getObject():
    return Rock
