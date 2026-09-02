"""Saved terrains predate the package move, so their pickles name the old modules."""
import os

import pytest

from herdsim.utils import compat
from herdsim.utils.path_utils import resource_path, user_data_path
from herdsim.ui.terrainLoader import TerrainLoader


def terrain_files(directory):
    if not os.path.isdir(directory):
        return []
    return [os.path.join(directory, f) for f in sorted(os.listdir(directory))
            if f.endswith(".terrain")]


def all_terrain_files():
    return terrain_files(user_data_path("terrain")) + terrain_files(resource_path("default_terrains"))


def test_there_are_terrains_to_load():
    assert len(all_terrain_files()) > 0


@pytest.mark.parametrize("path", all_terrain_files(), ids=lambda p: os.path.basename(p))
def test_every_saved_terrain_still_loads(path):
    with open(path, "rb") as fh:
        terrain = compat.load(fh)
    assert terrain.width > 0 and terrain.height > 0
    assert terrain.typegrid.shape == (terrain.height, terrain.width)


def test_loadSaves_finds_every_terrain_on_disk():
    loader = TerrainLoader.__new__(TerrainLoader)
    loader.savedTerrains = []
    loader.loadSaves()

    onDisk = {os.path.basename(p)[: -len(".terrain")] for p in terrain_files(user_data_path("terrain"))}
    loaded = {entry["full_name"] for entry in loader.savedTerrains}
    assert onDisk - loaded == set(), f"terrains on disk that the loader missed: {onDisk - loaded}"
    assert len(loader.savedTerrains) == len(onDisk)


def test_flat_terrain_is_listed_first():
    loader = TerrainLoader.__new__(TerrainLoader)
    loader.savedTerrains = []
    loader.loadSaves()
    assert loader.savedTerrains[0]["name"] == "Flat Terrain"
