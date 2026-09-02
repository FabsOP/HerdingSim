import pytest

from herdsim.ui.camera import Camera, ZOOM_LEVELS


def make():
    return Camera(512, 512, 508, 508)


def test_at_zoom_one_terrain_and_canvas_coincide():
    cam = make()
    assert cam.zoom == 1.0
    assert cam.toTerrain(37, 91) == (37.0, 91.0)
    assert cam.toCanvas(37, 91) == (37.0, 91.0)


def test_round_trip_identity_at_every_zoom():
    cam = make()
    for _ in range(len(ZOOM_LEVELS)):
        for (x, y) in [(0, 0), (13, 200), (507, 507), (250, 4)]:
            tx, ty = cam.toTerrain(x, y)
            bx, by = cam.toCanvas(tx, ty)
            assert bx == pytest.approx(x, abs=1e-6)
            assert by == pytest.approx(y, abs=1e-6)
        cam.zoomAt(254, 254, +1)


def test_zoom_keeps_the_point_under_the_cursor_fixed():
    for (cx, cy) in [(0, 0), (100, 400), (507, 250), (254, 254)]:
        cam = make()
        before = cam.toTerrain(cx, cy)
        cam.zoomAt(cx, cy, +1)
        after = cam.toTerrain(cx, cy)
        assert after[0] == pytest.approx(before[0], abs=1e-6)
        assert after[1] == pytest.approx(before[1], abs=1e-6)


def test_zoom_clamps_at_both_ends():
    cam = make()
    for _ in range(20):
        cam.zoomAt(254, 254, +1)
    assert cam.zoom == ZOOM_LEVELS[-1]
    assert cam.zoomAt(254, 254, +1) is False

    for _ in range(20):
        cam.zoomAt(254, 254, -1)
    assert cam.zoom == ZOOM_LEVELS[0]
    assert cam.zoomAt(254, 254, -1) is False


def test_viewport_never_leaves_the_terrain():
    cam = make()
    cam.zoomAt(254, 254, +1)
    cam.zoomAt(254, 254, +1)
    for (dx, dy) in [(-999, -999), (999, 999), (-999, 999), (999, -999)]:
        for _ in range(20):
            cam.pan(dx, dy)
        left, top, right, bottom = cam.visibleRegion()
        assert left >= -1e-9 and top >= -1e-9
        assert right <= 512 + 1e-9 and bottom <= 512 + 1e-9


def test_pan_range_at_zoom_one_is_just_the_border_inset():
    # the canvas is 508 wide but the terrain is 512, so 4px sits off screen
    cam = make()
    cam.pan(-100, -100)
    assert (cam.offsetX, cam.offsetY) == (4.0, 4.0)
    cam.pan(100, 100)
    assert (cam.offsetX, cam.offsetY) == (0.0, 0.0)


def test_reset_returns_to_the_default_view():
    cam = make()
    cam.zoomAt(100, 100, +1)
    cam.zoomAt(100, 100, +1)
    cam.pan(-50, -50)
    cam.reset()
    assert cam.zoom == 1.0
    assert (cam.offsetX, cam.offsetY) == (0.0, 0.0)


def test_visible_region_shrinks_as_zoom_increases():
    cam = make()
    widths = []
    for _ in range(len(ZOOM_LEVELS)):
        left, top, right, bottom = cam.visibleRegion()
        widths.append(right - left)
        cam.zoomAt(254, 254, +1)
    assert widths == sorted(widths, reverse=True)
    assert len(set(widths)) == len(widths)
