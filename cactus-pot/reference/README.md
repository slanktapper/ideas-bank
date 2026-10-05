# reference

The source model this project started from, and anything else that is an
input rather than something built here.

This folder is **empty on purpose.** The pot is a third-party mesh Rob
supplied, and nothing here copies it: `build.py --pot <path>` takes it by path,
measures it, and renders the cactus seated in it, so the pot can live wherever
Rob keeps it without this project owning a copy of someone else's model.

    python3 build.py --pot '.../Good Place Cactus (Pot).stl'

That prints the socket, the floor and the rim, and says whether `params.py`
still agrees with them. The numbers it produced, which `params.py` now carries,
are written down in `../direction.md`.

If a copy of the pot ever does belong in the repository, that is a decision to
make deliberately rather than by a build script quietly reaching across
folders.
