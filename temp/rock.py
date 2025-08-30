from data.packages.worldspawn.static.items.item import Item
class Rock(Item):
    def __init__(self):
        super().__init__("rock")

def getObject():
    return Rock