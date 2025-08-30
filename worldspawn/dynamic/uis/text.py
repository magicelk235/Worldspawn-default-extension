from data.packages.worldspawn.dynamic.uis import base
from data.default import sprite,animation,image,hitbox
from data.media.fontLoader import getFont
class Text(base.UIObject):
    def __init__(self, core, pos,text,fontPath,fontSize, visiblePlayers, interactivePlayers,color=(255,255,255,255)):
        self.text = text
        self.color = color
        self.fontSize = fontSize
        self.fontPath = fontPath
        objectData = sprite.SpriteData(hitbox.Hitbox(1,1),{"default":animation.Animation(image.ImageData(text="@text",color="@color",path=self.fontPath,factoredSize=fontSize),renderOrder=6)},False)
        super().__init__(core, pos, objectData, visiblePlayers, interactivePlayers)
        

    def setColor(self, color):
        self.color = color
        self.addBlankEvent()
        
    def getSize(self):
        font = getFont(self.fontPath)
        w,h = font.size(self.text)
        return w*self.fontSize,h*self.fontSize
    

    
    def setText(self, text):
        self.text = str(text)
        self.changeSize(*self.getSize())
        self.addBlankEvent()

def getObject():
    return Text