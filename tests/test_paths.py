import os
import re

from herdsim.utils.path_utils import project_root, resource_path, user_data_path


def test_project_root_contains_src_and_assets():
    root = project_root()
    assert os.path.isdir(os.path.join(root, "src"))
    assert os.path.isdir(os.path.join(root, "assets"))


def test_saves_resolves_inside_the_repository():
    assert os.path.dirname(user_data_path("saves")) == project_root()


def test_every_resource_path_reference_resolves():
    missing = []
    src = os.path.join(project_root(), "src")
    for folder, _, files in os.walk(src):
        for name in files:
            if not name.endswith(".py"):
                continue
            text = open(os.path.join(folder, name), encoding="utf-8").read()
            for rel in re.findall(r'resource_path\(\s*"([^"{}]+)"', text):
                if not os.path.exists(resource_path(rel)):
                    missing.append(rel)
    assert missing == [], f"unresolved asset paths: {missing}"


def test_obstacle_and_species_icon_conventions_hold():
    from herdsim.core.boid import behaviours
    from herdsim.core.terrain import color_map

    missing = []
    for species in behaviours:
        if not os.path.exists(resource_path(f"icons/{species.lower()}_land.png")):
            missing.append(f"icons/{species.lower()}_land.png")
    for folder in ("trees", "boulders", "bushes"):
        for biome in color_map:
            if not os.path.exists(resource_path(f"icons/{folder}/{biome}.png")):
                missing.append(f"icons/{folder}/{biome}.png")
    assert missing == [], f"missing icons: {missing}"
