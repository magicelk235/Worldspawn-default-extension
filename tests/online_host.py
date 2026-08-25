import sys
import threading

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import harness

harness.buildRoot()

import data.core

core = data.core.Core()
core.fillTiles("grass", (-64, -64), 4, 4)
core.spawnTile("stone", (64, 0, "world"))
core.host(5601, sendRate=1)

threading.Timer(60.0, lambda: setattr(core, "running", False)).start()
print("HOST READY", flush=True)
core.main()
