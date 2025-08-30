from data.default import hitbox,animation,sprite
from data.packages.worldspawn.dynamic.uis import base

class Lable(base.UIObject):
    def __init__(self, core, pos,imageData, visiblePlayers, interactivePlayers):
        objectData = sprite.SpriteData(hitbox.Hitbox(1,1),{"default":animation.Animation(imageData,renderOrder=7)},False)
        super().__init__(core, pos, objectData, visiblePlayers, interactivePlayers)

def getObject():
    return Lable