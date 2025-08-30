from data.default import image,animation,sprite,hitbox,displayType
from data.packages.worldspawn.dynamic.uis.base import UIObject
class Button(UIObject):
    def __init__(self,core,pos,visiblePlayers,interactivePlayers,iconTexture,size=(20,20)):
        self.iconTexture = iconTexture

        objectData = sprite.SpriteData(hitbox.Hitbox(*size),{"default":animation.Animation(image.ImageData("ui/button/button_up",scaleSize=(size[0],size[1]+1)),displayType=displayType.DisplayType.bottomLeft),"pressed":animation.Animation(image.ImageData("ui/button/button_down",scaleSize=size),countDown=0.12,displayType=displayType.DisplayType.bottomLeft)})
        super().__init__(core,pos,objectData,visiblePlayers,interactivePlayers)
        self.state = False
        
    def update(self):
        super().update()
        for id in self.interactivePlayers:
            inp = self.core.getInputManager(id)
            if self.hitbox.collidePoint(*inp.mousePos,self.getDimension()) and inp.mouseClicked():
                self.setAnimation("pressed",False)
            



def getObject():
    return Button
    