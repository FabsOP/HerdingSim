"""Painting must land on the same terrain pixel whatever the zoom level."""
import pytest
import tkinter as tk

from herdsim.core.terrain import Terrain
from herdsim.ui.camera import ZOOM_LEVELS
import herdsim.ui.sim_canvas as sc

from test_frame_history import Ctl, Ev, Media, sig


@pytest.fixture
def makeCanvas(root):
    made = []

    def build():
        terrain = Terrain(128, 128, invert=False)
        terrain.load(None, "Grass", levels=8)
        c = sc.SimCanvas(root, terrain, Ctl(), Media())
        made.append(c)
        return c

    yield build
    for c in made:
        c.destroy()


@pytest.mark.parametrize("zoom_steps", [0, 1, 2, 3, 4])
def test_painting_hits_the_same_terrain_pixel_at_every_zoom(makeCanvas, zoom_steps):
    target = (50, 60)
    sc.paintWindowWidth = 16

    baseline = makeCanvas()
    baseline.fill_paint_window(baseline._terrainEvent(Ev(*target)), "Sand")
    expected = sig(baseline.terrain)

    zoomed = makeCanvas()
    for _ in range(zoom_steps):
        zoomed.camera.zoomAt(target[0], target[1], +1)
    assert zoomed.camera.zoom == ZOOM_LEVELS[zoom_steps]

    canvasX, canvasY = zoomed.camera.toCanvas(*target)
    converted = zoomed._terrainEvent(Ev(canvasX, canvasY))
    assert (converted.x, converted.y) == target

    zoomed.fill_paint_window(converted, "Sand")
    assert sig(zoomed.terrain) == expected


def test_brush_radius_is_measured_in_terrain_pixels(makeCanvas):
    sc.paintWindowWidth = 16

    at_one = makeCanvas()
    at_one.fill_paint_window(at_one._terrainEvent(Ev(64, 64)), "Sand")
    painted_at_one = int((at_one.terrain.typegrid == 1).sum())

    at_three = makeCanvas()
    at_three.camera.zoomAt(64, 64, +1)
    at_three.camera.zoomAt(64, 64, +1)
    at_three.camera.zoomAt(64, 64, +1)
    cx, cy = at_three.camera.toCanvas(64, 64)
    at_three.fill_paint_window(at_three._terrainEvent(Ev(cx, cy)), "Sand")
    painted_at_three = int((at_three.terrain.typegrid == 1).sum())

    assert painted_at_one == painted_at_three > 0


def test_zoom_does_not_enter_frame_history(makeCanvas):
    c = makeCanvas()
    for _ in range(3):
        c.nextFrame("running")
    c.camera.zoomAt(60, 60, +1)
    c.camera.pan(-20, -20)
    zoomBefore = c.camera.zoom
    offsetBefore = (c.camera.offsetX, c.camera.offsetY)

    c.mediaController.state = "rewind"
    while c.framePointer > 0:
        c.rewind("rewind")

    assert c.camera.zoom == zoomBefore
    assert (c.camera.offsetX, c.camera.offsetY) == offsetBefore
    for frame in c.frames:
        assert set(frame.keys()) == {"boids", "obstacles", "waypoints"}
