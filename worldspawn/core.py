class WorldSpawn:
    def __init__(self):
        id = self.addObject(self.getPlayers("base")(self,(0,0,"world")))
        self.userID = id
        self.addObject(self.getUis("button")(self,(40,40,"world"),{id},{id},"",(30,30)))
    def newWorld(self):
        pass
    def generalUpdate(self):...
    def clientUpdate(self):...
    def serverUpdate(self):...

def getObject():
    return WorldSpawn