"""saves/ is not tracked, so a fresh clone must rebuild it from the bundled defaults."""
import pickle as pkl

import pytest

from herdsim.core.terrain import Terrain
from herdsim.ui import terrainLoader as loader_module
from herdsim.ui.terrainLoader import TerrainLoader
from herdsim.utils.path_utils import resource_path


@pytest.fixture
def fresh_checkout(tmp_path, monkeypatch):
    saves = tmp_path / "saves"
    defaults = tmp_path / "default_terrains"
    defaults.mkdir()

    # a tiny terrain, so the test does not copy 16MB around
    tiny = Terrain(32, 32, invert=False)
    tiny.load(None, "Grass", levels=4)
    with open(defaults / "Valley.terrain", "wb") as fh:
        pkl.dump(tiny, fh)

    def small_flat(path):
        terrain = Terrain(32, 32, invert=False)
        terrain.load(None, "Grass", levels=4)
        with open(path, "wb") as fh:
            pkl.dump(terrain, fh)
        return terrain

    monkeypatch.setattr(TerrainLoader, "_makeFlatTerrain", staticmethod(small_flat))
    monkeypatch.setattr(loader_module, "user_data_path", lambda rel: str(tmp_path / rel))
    monkeypatch.setattr(loader_module, "resource_path",
                        lambda rel: str(defaults) if rel == "default_terrains" else resource_path(rel))
    return saves, defaults


def loadInto(_):
    loader = TerrainLoader.__new__(TerrainLoader)
    loader.savedTerrains = []
    loader.loadSaves()
    return loader


def test_saves_is_created_when_missing(fresh_checkout):
    saves, _ = fresh_checkout
    assert not saves.exists()
    loadInto(None)
    assert saves.is_dir()


def test_bundled_defaults_are_copied_on_first_run(fresh_checkout):
    saves, _ = fresh_checkout
    loader = loadInto(None)
    names = {entry["full_name"] for entry in loader.savedTerrains}
    assert "Valley" in names, f"defaults were not copied, got {names}"
    assert (saves / "Valley.terrain").exists()


def test_flat_terrain_is_always_available(fresh_checkout):
    saves, _ = fresh_checkout
    loader = loadInto(None)
    assert (saves / "flat.terrain").exists()
    assert loader.savedTerrains[0]["name"] == "Flat Terrain"


def test_second_run_does_not_duplicate(fresh_checkout):
    loadInto(None)
    first = {e["full_name"] for e in loadInto(None).savedTerrains}
    second = {e["full_name"] for e in loadInto(None).savedTerrains}
    assert first == second


def test_terrains_copied_on_first_run_are_loadable(fresh_checkout):
    saves, _ = fresh_checkout
    loadInto(None)
    from herdsim.utils import compat
    with open(saves / "Valley.terrain", "rb") as fh:
        terrain = compat.load(fh)
    assert terrain.width > 0 and terrain.typegrid is not None
