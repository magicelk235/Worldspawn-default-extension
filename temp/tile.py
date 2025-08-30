from data.default import npcObject,hitbox,animation,image

class TileData(npcObject.NpcObjectData):
    def __init__(self,
                  hitbox,animations,displayByDirectionX=True,displayByDirectionY=False
                  ,save=[],maxHealth=1,damage=1,shield=0,speed=1,react=0,visionRadius=200,
                  ride={"point":(0,0),"offset":(0,0),"max":1},lootableList=[],spawners=[],solid=False,dyeable=False):
        super().__init__(hitbox,animations,displayByDirectionX,displayByDirectionY,save,maxHealth,damage,shield,speed,react,visionRadius,ride,lootableList,spawners)
        self.solid = solid
        self.dyeable = dyeable


class Tile(npcObject.NpcObject):
    def __init__(self, core, pos: tuple[3],objectData,tag=None,dictData={}):
        super().__init__(core,pos,objectData,tag,dictData)
        self.color = (255,255,255,255)

def getObject():
    return Tile