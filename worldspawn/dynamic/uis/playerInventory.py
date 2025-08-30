from data.default import sprite,displayType,hitbox,animation,aliveObject
import data.default.inventory
from data.packages.worldspawn.dynamic.uis import inventory
class PlayerInventory(inventory.Inventory):
    def __init__(self, core, owner):
        self.owner = owner
        self.inventory:data.default.inventory.Inventory = self.getInventory()
        size = self.getInventorySize()
        super().__init__(core, *size, self.inventory.toList(), {self.owner.id}, {self.owner.id})

    def getInventorySize(self) -> tuple[int,int]:
        return self.inventory.getW,self.inventory.getH

    def getInventory(self) -> data.default.inventory.Inventory:
        return self.owner.inventory