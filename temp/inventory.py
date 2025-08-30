from data.default import sprite,image,animation,hitbox,rect,displayType
from data.default.inventory import InventoryItem
from data.packages.worldspawn.dynamic.uis import base,item

class Inventory(base.UIObject):
    def __init__(self,core,w,h,inventoryList:list,visiblePlayers,interactivePlayers,offset=(0,0)):
        self.core = core
        self.slotSize = 36
        self.offset = offset
        self.w = w
        self.h = h
        self.inventoryList:list[InventoryItem] = inventoryList
        self.size = self.calculateSize()
        pos = self.calculatePos()
        objectData = sprite.SpriteData(hitbox.Hitbox(*self.size),{"default":animation.Animation(image.ImageData("ui/slot",cutSize="@size"),renderOrder=6,displayType=displayType.DisplayType.topLeft)})
        super().__init__(core,pos,objectData,visiblePlayers,interactivePlayers)
        self.updateItems()
        self.selector = None

    def setInventory(self,inventory):
        self.inventoryList = inventory
        self.updateItems()

    def calculatePos(self):
        halfSize = (self.size[0]//2,self.size[1]//2)
        screenHalfSize = (self.core.multiMedia.getScreenSize()[0]//2,self.core.multiMedia.getScreenSize()[1]//2)
        pos = rect.Rect.subPos(screenHalfSize,halfSize)
        pos = rect.Rect.addPos(pos,self.offset)
        return pos+("world",)
    

    def calculateSize(self):
        return self.w*self.slotSize,self.h*self.slotSize
    
    def setSize(self,w,h):
        self.w = w
        self.h = h
        size = self.calculateSize()
        self.changeSize(*size)

    def calculateItemPos(self,w,h):
        defaultOffset = rect.Rect.addPos((10,10),self.getAxis())
        offset = w*self.slotSize,h*self.slotSize
        return rect.Rect.addPos(offset,defaultOffset)+("world",)

    def getItemIndex(self,w,h):
        return w+h*self.w

    def getItem(self,w,h):
        return self.inventoryList[self.getItemIndex(w,h)]

    def updateItems(self):
        if self.uiParts == []:
            for h in range(self.h):
                for w in range(self.w):
                    try:
                        inventoryItem = self.getItem(w,h)
                        pos = self.calculateItemPos(w,h)+(self.getDimension(),)
                        self.addUiPart(item.Item(self.core,pos,inventoryItem.getItemName(),inventoryItem.getCount(),self.visiblePlayers,self.interactivePlayers))
                    except:
                        pass
        else:
            for h in range(self.h):
                for w in range(self.w):
                    try:
                        inventoryItem = self.getItem(w,h)
                        pos = self.calculateItemPos(w,h)+(self.getDimension(),)
                        index = self.getItemIndex(w,h)
                        self.uiParts[index].setItemName(inventoryItem.getItemName())
                        self.uiParts[index].setCount(inventoryItem.getCount())
                        self.uiParts[index].setPos(pos)
                    except:
                        pass

def getObject():
    return Inventory
