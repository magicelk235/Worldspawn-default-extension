from data.inventory.modifiers import Modifier, Mode
from packages.worldspawn.static.items.item import Item


class WoodenSword(Item):
    """Starter weapon.

    Modifiers are applied by Inventory.applyModifiers once per distinct item
    name in the inventory, so carrying two swords is worth no more than one.
    MaxSet is used instead of Set so a better weapon elsewhere in the
    inventory still wins, whatever order the slots are walked in.
    """

    def __init__(self):
        super().__init__("woodenSword", max=1, modifiers=(
            Modifier("damage", 3, Mode.MaxSet),
            Modifier("attackCountDown", 25, Mode.MinSet),
        ))


def getObject():
    return WoodenSword
