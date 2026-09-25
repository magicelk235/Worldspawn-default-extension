class WorldSpawn:
    """Core extension for the default package.

    The engine mixes this class into Core, so everything here becomes a
    method on the core object itself. It owns the one rule the engine has no
    opinion about: every participant gets a Player whose id is their own id,
    because Core.main points the camera at whatever is stored under
    core.userID.

    Three core methods are replaced through createFunction. Adding a method
    to this class is not enough for those, since Core defines them itself and
    Core sits ahead of this class in the lookup order.
    """

    spawnPos = (0, 0, "world")

    def __init__(self):
        # The character that belongs to this process when it is not a guest
        # on somebody else's world.
        self.localPlayerID = self.userID

        coreJoin = self.join
        coreSetStartMode = self.setStartMode

        def join(self, ip, port, identity=None, password=None):
            """Leave the local world behind before the host starts talking.

            The host tracks what it has already sent per client, so anything
            thrown away after the first delta arrives never gets sent again.
            The only safe moment to drop the local world is here, before the
            connection produces anything.
            """
            if not coreJoin(ip, port, identity, password):
                return False
            self.clearWorld()
            return True

        def setStartMode(self):
            coreSetStartMode()
            self.clearWorld()
            if self.localPlayerID not in self.inputMangers:
                self.addInputManager(self.localPlayerID)
            self.userID = self.localPlayerID
            self.spawnPlayer(self.localPlayerID)

        self.createFunction("filterVisible", WorldSpawn.filterVisible)
        self.createFunction("join", join)
        self.createFunction("setStartMode", setStartMode)

    # world

    def spawnPlayer(self, playerID, pos=None):
        """Give playerID a character, or hand back the one they already have.

        Reconnecting fires clientConnected again for the same id, so this has
        to stay idempotent.
        """
        player = self.getObject(playerID)
        if player != None:
            return player
        player = self.getPlayers("base")(self, pos if pos != None else self.spawnPos)
        self.addObjectByID(player, playerID)
        return player

    def despawnPlayer(self, playerID):
        player = self.getObject(playerID)
        if player == None:
            return
        player.dispose()
        self.removeObjectByID(playerID)

    def clearWorld(self):
        """Empty the world, windows included."""
        for id in list(self.sprites.keys()):
            object = self.getObject(id)
            if object == None:
                continue
            dispose = getattr(object, "dispose", None)
            if dispose != None:
                dispose()
            if self.getObject(id) != None:
                self.removeObjectByID(id)

    def spawnTile(self, name, pos):
        return self.addObject(self.getTiles(name)(self, pos))

    def fillTiles(self, name, topLeft, w, h, dimension="world"):
        """Lay a rectangle of tiles, measured in tiles rather than pixels."""
        tile = self.getTiles(name)
        step = tile.tileSize
        ids = []
        for y in range(h):
            for x in range(w):
                pos = (topLeft[0] + x * step[0], topLeft[1] + y * step[1], dimension)
                ids.append(self.addObject(tile(self, pos)))
        return ids

    # persistence

    def saveState(self):
        # nothing of this package's own to keep, but the entry has to exist
        # for loadWorld to call loadState back
        return {}

    def loadState(self, state):
        """Make sure whoever loaded the world has a character in it.

        A save can come from another machine, or the one sprite that failed
        to restore can be the player. Core.main points the camera at
        core.userID and draws nothing at all when that id holds no sprite.
        """
        if self.mode == self.Mode.join:
            return
        if self.localPlayerID not in self.inputMangers:
            self.addInputManager(self.localPlayerID)
        self.userID = self.localPlayerID
        self.spawnPlayer(self.localPlayerID)

    # networking

    def filterVisible(self, clientID, sprites):
        """Keep one player's windows off everybody else's screen.

        World sprites have no audience and go to everyone. Widgets carry the
        set of players allowed to see them, and there is no reason to spend
        bandwidth on a menu the receiver will never draw.
        """
        visible = {}
        for id, sprite in sprites.items():
            audience = getattr(sprite, "visiblePlayers", None)
            if audience == None or clientID in audience:
                visible[id] = sprite
        return visible

    def clientUpdate(self):
        # A guest runs no simulation: the host owns every sprite and streams
        # the results, and the engine forwards this client's input for it.
        pass

    def serverUpdate(self):
        for event in self.getEventList("clientConnected"):
            self.spawnPlayer(event.clientID)
        for event in self.getEventList("clientDisconnected"):
            self.despawnPlayer(event.clientID)


def getObject():
    return WorldSpawn
