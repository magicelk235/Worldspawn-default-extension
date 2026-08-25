"""Assemble a throwaway engine root with this package installed.

The engine loads packages from ./packages relative to the working directory,
so the checks link the engine's data/ and this repo's worldspawn/ into a
temporary root instead of writing into the engine checkout.

Set WORLDSPAWN_ENGINE to point at an engine other than the sibling
../Worldspawn-engine.
"""

import os
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.abspath(os.environ.get(
    "WORLDSPAWN_ENGINE", os.path.join(os.path.dirname(REPO), "Worldspawn-engine")))


def buildRoot():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    if not os.path.isdir(os.path.join(ENGINE, "data")):
        sys.exit(f"no engine at {ENGINE}; set WORLDSPAWN_ENGINE")
    root = tempfile.mkdtemp(prefix="worldspawn-check-")
    os.symlink(os.path.join(ENGINE, "data"), os.path.join(root, "data"))
    os.makedirs(os.path.join(root, "packages"))
    os.symlink(os.path.join(REPO, "worldspawn"),
               os.path.join(root, "packages", "worldspawn"))
    sys.path.insert(0, root)
    os.chdir(root)
    return root
