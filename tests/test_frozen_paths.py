"""When frozen, assets come out of the PyInstaller bundle and saves sit beside the exe."""
import os
import sys

import pytest

from herdsim.utils import path_utils


@pytest.fixture
def frozen(tmp_path, monkeypatch):
    bundle = tmp_path / "bundle"
    appdir = tmp_path / "app"
    (bundle / "assets" / "icons").mkdir(parents=True)
    (bundle / "assets" / "icons" / "sheep.ico").write_bytes(b"x")
    appdir.mkdir()

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle), raising=False)
    monkeypatch.setattr(sys, "executable", str(appdir / "HerdSim.exe"), raising=False)
    return bundle, appdir


def test_assets_resolve_into_the_bundle(frozen):
    bundle, _ = frozen
    resolved = path_utils.resource_path("icons/sheep.ico")
    assert resolved == os.path.join(str(bundle), "assets", "icons/sheep.ico")
    assert os.path.exists(resolved)


def test_saves_land_beside_the_executable_not_in_the_bundle(frozen):
    bundle, appdir = frozen
    saves = path_utils.user_data_path("saves")
    assert saves == os.path.join(str(appdir), "saves")
    assert str(bundle) not in saves


def test_project_root_is_the_executable_directory(frozen):
    _, appdir = frozen
    assert path_utils.project_root() == str(appdir)


def test_source_mode_is_unaffected():
    root = path_utils.project_root()
    assert os.path.isdir(os.path.join(root, "src"))
    assert os.path.isdir(os.path.join(root, "assets"))
