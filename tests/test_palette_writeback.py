"""A migrated palette is written back once, not rebuilt on every launch."""
import os
import pickle as pkl

import pytest

from herdsim.core.terrain import Terrain, PALETTE_VERSION
from herdsim.ui import terrainLoader as loader_module
from herdsim.ui.terrainLoader import TerrainLoader
from herdsim.utils import compat
from herdsim.utils.path_utils import resource_path


def smallTerrain():
    t = Terrain(32, 32, invert=False)
    t.load(None, "Grass", levels=4)
    return t


@pytest.fixture
def staleCheckout(tmp_path, monkeypatch):
    terrainDir = tmp_path / "terrain"
    defaults = tmp_path / "default_terrains"
    terrainDir.mkdir()
    defaults.mkdir()

    stale = smallTerrain()
    stale.paletteVersion = 0
    target = terrainDir / "Valley.terrain"
    with open(target, "wb") as fh:
        pkl.dump(stale, fh)

    # already current, so loadSaves neither rebuilds nor rewrites it
    with open(terrainDir / "flat.terrain", "wb") as fh:
        pkl.dump(smallTerrain(), fh)

    def smallFlat(path):
        t = smallTerrain()
        with open(path, "wb") as fh:
            pkl.dump(t, fh)
        return t

    monkeypatch.setattr(TerrainLoader, "_makeFlatTerrain", staticmethod(smallFlat))
    monkeypatch.setattr(loader_module, "user_data_path", lambda rel: str(tmp_path / rel))
    monkeypatch.setattr(loader_module, "resource_path",
                        lambda rel: str(defaults) if rel == "default_terrains" else resource_path(rel))
    return target


def runLoad():
    loader = TerrainLoader.__new__(TerrainLoader)
    loader.savedTerrains = []
    loader.loadSaves()
    return loader


def onDisk(path):
    with open(path, "rb") as fh:
        return pkl.load(fh)


def test_stale_terrain_is_written_back(staleCheckout):
    assert onDisk(staleCheckout).paletteVersion == 0
    runLoad()
    assert onDisk(staleCheckout).paletteVersion == PALETTE_VERSION


def test_write_back_does_not_persist_the_migration_flag(staleCheckout):
    runLoad()
    assert not hasattr(onDisk(staleCheckout), "paletteMigrated"), \
        "flag was pickled, so every launch would rewrite the file"


def test_second_launch_does_not_rewrite(staleCheckout):
    runLoad()
    first = staleCheckout.read_bytes()
    runLoad()
    assert staleCheckout.read_bytes() == first


def test_failed_write_leaves_the_original_intact(staleCheckout, monkeypatch):
    original = staleCheckout.read_bytes()

    def boom(*a, **k):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(loader_module.pkl, "dump", boom)
    loader = runLoad()

    assert staleCheckout.read_bytes() == original
    assert not os.path.exists(str(staleCheckout) + ".tmp")
    assert any(e["full_name"] == "Valley" for e in loader.savedTerrains)


def test_terrain_still_loads_correctly_after_write_back(staleCheckout):
    runLoad()
    t = compat.load(open(staleCheckout, "rb"))
    assert t.paletteVersion == PALETTE_VERSION
    assert t.getContourImage("Ice") is not None
