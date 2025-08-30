from data.default import sprite,hitbox,animation,image,rect
from data.packages.worldspawn.dynamic.uis import base,text
class Item(base.UIObject):
    def __init__(self, core, pos,itemName,count, visiblePlayers, interactivePlayers):
        self.setItemName(itemName)
        self.count = count
        objectData = sprite.SpriteData(hitbox.Hitbox(16,16),{"default":animation.Animation(image.ImageData("@path"),renderOrder=6)})
        super().__init__(core, pos, objectData, visiblePlayers, interactivePlayers)
        self.addUiPart(text.Text(core,rect.Rect.addPos(self.getAxis(),(10,10))+(pos[2],),"",None,1,visiblePlayers,interactivePlayers,(0,0,0,255)))
        self.setCount(count)

    def setPos(self,pos):
        super().setPos(pos)
        self.uiParts[0].setPos(rect.Rect.addPos(self.getAxis(),(10,10))+(pos[2],))

    def setCount(self,count):
        self.count = count
        if count != 0:
            self.uiParts[0].setText(self.count)
        else:
            self.uiParts[0].setText("")

    def setItemName(self, itemName):
        self.itemName = itemName
        self.path = f"items/{self.itemName}"

def getObject():
    return Item