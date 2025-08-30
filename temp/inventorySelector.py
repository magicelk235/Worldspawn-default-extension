from data.default import sprite,image,animation,hitbox,rect,events
from data.packages.worldspawn.dynamic.uis import base,inventory,lable
import pygame

class InventorySelector(base.UIObject):
    @staticmethod
    def inventorySelectorInteractTemplate(labeldW,labeldH,currentW,currentH):
        return pygame.event.Event(events.EventRegister.getID("inventorySelectorInteract"),locals())
    events.EventRegister.register("inventorySelectorInteract",inventorySelectorInteractTemplate)

    def __init__(self,core,inventory:inventory.Inventory,usesLable=False):
        self.inventory = inventory
        self.maxH = self.inventory.h
        self.maxW = self.inventory.w
        self.currentH = self.inventory.h//2
        self.currentW = self.inventory.w//2
        self.usesLable = usesLable
        self.labledW = -1
        self.labledH = -1
        pos = self.calculatePos()
        objectData = sprite.SpriteData(hitbox.Hitbox(14,14),{"default":animation.Animation(image.ImageData("ui/selector"),renderOrder=7)},False)
        super().__init__(core,pos,objectData,inventory.visiblePlayers,inventory.interactivePlayers)


    def calculateCurrentSlot(self,inp):
        mousePos = inp.getMousePos()
        inventoryPos = self.inventory.getAxis()
        releventPos = rect.Rect.subPos(mousePos,inventoryPos)
        w = releventPos[0]//self.inventory.slotSize
        h = releventPos[1]//self.inventory.slotSize
        if 0<=w<self.maxW:
            self.currentW = w
            self.setPos(self.calculatePos())
        if 0<=h<self.maxH:
            self.currentH = h
            self.setPos(self.calculatePos())
    
    def isLableEmpty(self) -> bool:
        return self.labledW == -1

    def updateLable(self,inp):
        if self.usesLable and inp.mouseClicked():
            if self.isLableEmpty():
                self.labledH = self.currentH
                self.labledW = self.currentW
                imageData = image.ImageData("ui/selected")
                self.addUiPart(lable.Lable(self.core,self.calculatePos(),imageData,self.visiblePlayers,self.interactivePlayers))
            else:
                player = self.core.getObject(next(iter(self.interactivePlayers)))
                player.inventory.interact(self.labledW,self.labledH,self.currentW,self.currentH)
                for inventoryCompontent in player.inventoryCompontents:
                    inventoryCompontent.setInventory(player.inventory.toList())

                self.removeUiPart(self.uiParts[0])
                self.labledH = -1
                self.labledW = -1

    def displayImage(self, displaySurf, player, displayOffset):
        super().displayImage(displaySurf, player, displayOffset)


    def update(self):
        super().update()
        for id in self.interactivePlayers:
            inp = self.core.getInputManager(id)
            
            self.calculateCurrentSlot(inp)
            self.updateLable(inp)

    def calculatePos(self):
        x = self.currentW * self.inventory.slotSize + self.inventory.getX()
        y = self.currentH * self.inventory.slotSize + self.inventory.getY()
        return x,y,"world"


def getObject():
    return InventorySelector