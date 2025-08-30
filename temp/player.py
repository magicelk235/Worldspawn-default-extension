from data.default import aliveObject,hitbox,animation,image,displayType,multiMedia
from data.packages.worldspawn.dynamic.uis.inventory import Inventory
class Player(aliveObject.AliveObject):
    
    def __init__(self, core, pos: tuple[3],tag=None, dict=None):
        super().__init__(core,pos,tag,dict)
        
        self.inventoryCompontents = []
        item = self.core.getItems("woodenSword")()
        for i in range(35):
            
            self.inventory.addItemByCount(item,1)
        item = self.core.getItems("rock")()
        for i in range(24):
            self.inventory.addItemByCount(item,1)
        

    def addInventoryCompontents(self, inventoryCompontents):
        self.inventoryCompontents.append(inventoryCompontents)
        self.core.addObject(inventoryCompontents)

    def setID(self,id):
        super().setID(id)
        self.core.addInputManager(self.id)
        self.inp = self.core.getInputManager(self.id)
        self.inventoryDisplay = Inventory(self.core,5,5,self.inventory.toList(),{self.id},{self.id},True)
        self.hotbar = Inventory(self.core,5,1,self.inventory.toList(),{self.id},{self.id},True,(0,self.core.multiMedia.getScreenSize()[1]//2-self.inventoryDisplay.slotSize//2))
        self.addInventoryCompontents(self.inventoryDisplay)
        self.addInventoryCompontents(self.hotbar)
        self.inventoryDisplay.toggleVisibility()


    def moveInput(self):
        if self.inp.isKeyHeld("w"):
            self.addExcluciveVector(90,0.02)
        if self.inp.isKeyHeld("s"):
            self.addExcluciveVector(270,0.02)
        if self.inp.isKeyHeld("d"):
            self.addExcluciveVector(0,0.02)
        if self.inp.isKeyHeld("a"):
            self.addExcluciveVector(180,0.02)
        
    def updateInventory(self):
        if self.inp.isKeyPressed("e"):
            self.inventoryDisplay.toggleVisibility()
            self.hotbar.toggleVisibility()

    def getAnimationByHand(self):
        pass

    def update(self):
        self.moveInput()
        self.updateInventory()
        if self.eventHappened(self.moveEvent):
            self.setAnimation("walk")
        super().update()



    def getDefaultData(self):
        self.objectData = aliveObject.AliveObjectData(hitbox.Hitbox(13,17),
                                             {"default":animation.Animation(image.ImageData(path="player/player_idle",flipX="@directionX.value"),displayType=displayType.DisplayType.bottomRight),
                                              "walk":animation.Animation(image.ImageData(path="player/player_walk",flipX="@directionX.value"),displayType=displayType.DisplayType.bottomRight,countDown=0.08),
                                              "sword":animation.Animation(image.ImageData(path="player/player_sword",flipX="@directionX.value",resetGif=True),displayType=displayType.DisplayType.bottomRight,countDown=0.5,weight=2,moveable=False),
                                              "damage":animation.Animation(imageData=image.ImageData(flipX="@directionX.value",color=(270,255,255,255)))},speed=10) 

def getObject():
    return Player