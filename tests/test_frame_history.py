"""Regression tests for painting, frame recording, rewind and replay.

These cover the paused-paint bug, where a terrain edit made while playback was
paused never reached terrainHistory and so could never be undone.
"""
import hashlib
import time

import numpy as np
import pytest
import tkinter as tk

from herdsim.core.terrain import Terrain
import herdsim.ui.sim_canvas as sc


class Ev:
    def __init__(self, x, y):
        self.x, self.y = x, y


class Ctl:
    def __init__(self, shape="Square"):
        self.shape = shape

    def get_brush_shape(self):
        return self.shape

    def get_selected_animal(self):
        return None

    def get_selected_terrain(self):
        return None

    def get_spawn_size(self):
        return 1

    def getBorderMode(self):
        return "Void"


class Media:
    def __init__(self):
        self.state, self.isPaused, self.dtMultiplier = "running", False, 1

    def pausePlay(self):
        self.isPaused = not self.isPaused

    def rewind(self):
        pass

    def fastRewind(self):
        pass

    def freezeRewind(self):
        pass

    def fastForward2x(self):
        pass

    def fastForward4x(self):
        pass


def sig(terrain):
    counts = tuple(int((terrain.typegrid == i).sum()) for i in range(6))
    digest = hashlib.md5(np.array(terrain.contourImg).tobytes()).hexdigest()[:10]
    return counts, digest


@pytest.fixture
def canvas(root):
    terrain = Terrain(128, 128, invert=False)
    terrain.load(None, "Grass", levels=8)
    media = Media()
    c = sc.SimCanvas(root, terrain, Ctl(), media)
    sc.paintWindowWidth = 20
    yield c, media
    c.destroy()


def record(c, frames=5, paint_every=2):
    truth = {}
    types = ["Sand", "Water", "Ice", "Rock", "Snow"]
    for f in range(frames):
        if f > 0 and f % paint_every == 0:
            c.fill_paint_window(Ev(10 + f * 11, 10 + f * 9), types[f % len(types)])
        c.nextFrame("running")
        truth[c.framePointer] = sig(c.terrain)
    return truth


def test_rewind_reaches_every_recorded_frame(canvas):
    c, media = canvas
    truth = record(c, frames=9)
    media.state = "rewind"
    while c.framePointer > 0:
        c.rewind("rewind")
        assert sig(c.terrain) == truth[c.framePointer]


def test_fast_rewind_reaches_recorded_frames(canvas):
    c, media = canvas
    truth = record(c, frames=9)
    media.state, media.dtMultiplier = "fast-rewind", 4
    while c.framePointer > 0:
        c.rewind("fast-rewind")
        assert sig(c.terrain) == truth[c.framePointer]


def test_forward_replay_reaches_recorded_frames(canvas):
    c, media = canvas
    truth = record(c, frames=9)
    present = max(truth)
    media.state = "rewind"
    while c.framePointer > 0:
        c.rewind("rewind")
    media.state, media.dtMultiplier = "forward", 2
    while c.framePointer < present:
        c.nextFrame("forward")
        assert sig(c.terrain) == truth[c.framePointer]


def test_paint_while_paused_can_still_be_rewound(canvas):
    c, media = canvas
    for _ in range(4):
        c.nextFrame("running")
    clean = sig(c.terrain)

    media.isPaused = True
    for i, biome in enumerate(["Sand", "Water", "Ice"]):
        c.fill_paint_window(Ev(30 + i * 25, 40), biome)
    assert sig(c.terrain) != clean
    assert len(c.currentFrameTerrainOps) == 3

    c.update(60, ti=time.time())
    assert c.currentFrameTerrainOps == []

    media.state = "rewind"
    while c.framePointer > 0:
        c.rewind("rewind")
    assert sig(c.terrain) == clean


def test_bucket_fill_undo_restores_brush_paint_underneath(canvas):
    c, media = canvas
    c.nextFrame("running")
    sc.paintWindowWidth = 20
    c.fill_paint_window(Ev(64, 64), "Sand")
    c.nextFrame("running")
    after_blob = sig(c.terrain)

    sc.paintWindowWidth = 0
    c.color_contour(Ev(64, 64), "Water")
    c.nextFrame("running")
    assert sig(c.terrain) != after_blob

    media.state = "rewind"
    c.rewind("rewind")
    assert sig(c.terrain) == after_blob


def test_background_uses_a_single_canvas_item(canvas):
    c, _ = canvas
    sc.paintWindowWidth = 16
    for i in range(25):
        c.fill_paint_window(Ev(20 + (i * 3) % 90, 20 + (i * 5) % 90), "Sand")
    images = [i for i in c.find_all() if c.type(i) == "image"]
    assert len(images) == 1
    assert c.find_all()[0] == c.bgPhotoID
    assert c.itemcget(c.bgPhotoID, "image") == str(c.bgPhoto)


def test_numFrames_always_matches_frames(canvas):
    c, _ = canvas
    for _ in range(6):
        c.nextFrame("running")
        assert c.numFrames == len(c.frames)
    c.framePointer = 3
    c.discardFuture()
    assert c.numFrames == len(c.frames) == 4
