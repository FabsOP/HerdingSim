# HerdSim Restructure and Camera Zoom Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move HerdSim to a conventional `src/` package layout, then add zoom to cursor on the simulation canvas with ctrl+wheel and space+drag panning.

**Architecture:** Part A converts a flat script directory into `src/herdsim/{core,ui,utils}`, with `resource_path` becoming the single place that knows where assets live so that all 36 call sites stay unchanged. Part B introduces a tkinter-free `Camera` unit that owns zoom level and viewport offset, and routes every mouse handler through one canvas-to-terrain conversion, which is what actually makes zoom possible.

**Tech Stack:** Python 3.9, tkinter, PIL/Pillow, numpy, pygame, mutagen, tkinter-tooltip

**Spec:** `docs/superpowers/specs/2026-09-02-zoom-and-restructure-design.md`

## Global Constraints

- Repository root is `HerdSim/Code/`. Everything in the parent folder is outside version control and must not be moved or deleted.
- No AI-style explanatory comments in source. Match the existing comment density and tone.
- No em dashes in any written deliverable.
- Zoom and pan are view state and must never enter `frames` or `terrainHistory`.
- Brush radius is measured in terrain pixels, not screen pixels.
- Discrete zoom levels only: 1.0, 1.5, 2.0, 3.0, 4.0.
- Work happens on branch `restructure-and-zoom`.

---

## Part A: Restructure

### Task A1: Create the package skeleton

**Files:**
- Create: `src/herdsim/__init__.py`, `src/herdsim/core/__init__.py`, `src/herdsim/ui/__init__.py`, `src/herdsim/utils/__init__.py`
- Create: `assets/`, `tests/`

- [ ] **Step 1: Make directories and empty package markers**

```bash
mkdir -p src/herdsim/core src/herdsim/ui src/herdsim/utils assets tests
touch src/herdsim/__init__.py src/herdsim/core/__init__.py \
      src/herdsim/ui/__init__.py src/herdsim/utils/__init__.py
```

- [ ] **Step 2: Verify**

Run: `find src -type f | sort`
Expected: four `__init__.py` files, nothing else.

---

### Task A2: Move assets and fix path resolution

**Files:**
- Move: `icons/` `audio/` `default_terrains/` into `assets/`
- Move: `assets/banner.svg` etc into `assets/readme/`
- Modify: `path_utils.py` (becomes `src/herdsim/utils/path_utils.py` in Task A3)

**Interfaces:**
- Produces: `resource_path(rel)` resolving to `<root>/assets/<rel>`; `user_data_path(rel)` resolving to `<root>/<rel>`; `project_root()` returning the repository root as a string.

- [ ] **Step 1: Move the asset trees with git mv so history is preserved**

```bash
mkdir -p assets/readme
git mv icons assets/icons
git mv audio assets/audio
git mv default_terrains assets/default_terrains
git mv assets/banner.svg assets/readme/banner.svg
git mv assets/palette.svg assets/readme/palette.svg
git mv assets/rules.svg assets/readme/rules.svg
```

- [ ] **Step 2: Rewrite path_utils.py**

```python
import sys
import os


def project_root():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    here = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(here, 'src')) and os.path.isdir(os.path.join(here, 'assets')):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return os.path.dirname(os.path.abspath(__file__))
        here = parent


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets', relative_path)
    return os.path.join(project_root(), 'assets', relative_path)


def user_data_path(relative_path):
    return os.path.join(project_root(), relative_path)
```

- [ ] **Step 3: Verify every asset path still resolves**

Run the check script from Task A6 Step 2. All 36 must resolve to files that exist.

---

### Task A3: Move python modules into the package

**Files:**
- Move: `boid.py` `flock.py` `terrain.py` `vector.py` into `src/herdsim/core/`
- Move: `path_utils.py` into `src/herdsim/utils/`
- Move: `widgets/*.py` into `src/herdsim/ui/`
- Move: `app.py` into `src/herdsim/app.py`

- [ ] **Step 1: Move with git mv**

```bash
git mv boid.py flock.py terrain.py vector.py src/herdsim/core/
git mv path_utils.py src/herdsim/utils/
for f in widgets/*.py; do git mv "$f" src/herdsim/ui/; done
git mv app.py src/herdsim/app.py
rmdir widgets
```

- [ ] **Step 2: Rewrite imports to package-relative form**

Every `from boid import behaviours` becomes `from herdsim.core.boid import behaviours`.
Every `from widgets.x import Y` becomes `from herdsim.ui.x import Y`.
Every `from path_utils import ...` becomes `from herdsim.utils.path_utils import ...`.
Every `from terrain import ...` becomes `from herdsim.core.terrain import ...`.
Every `from vector import ...` becomes `from herdsim.core.vector import ...`.

- [ ] **Step 3: Delete the seven sys.path.append blocks**

Remove from each of `animalTab.py`, `main_menu.py`, `media_controller.py`, `simulation.py`, `sim_canvas.py`, `terrainEditorTab.py`, `terrainLoader.py`:

```python
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

Keep `import os` where the module still uses `os` for other reasons.

- [ ] **Step 4: Verify imports**

Run: `venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'src'); import herdsim.app"`
Expected: no traceback.

---

### Task A4: Entry point and packaging metadata

**Files:**
- Create: `run.py`, `requirements.txt`
- Modify: `app.spec`

- [ ] **Step 1: Write run.py**

```python
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from herdsim.app import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Give app.py a main() function**

Wrap the current `if __name__ == "__main__":` body in `def main():` and keep a
`if __name__ == "__main__": main()` guard at the bottom.

- [ ] **Step 3: Write requirements.txt**

```
numpy
pillow
pygame
mutagen
tkinter-tooltip
```

- [ ] **Step 4: Update app.spec**

Change `['app.py']` to `['run.py']`, add `pathex=['src']`, and change datas to:

```python
    datas=[
        ('assets', 'assets'),
    ],
```

and `icon='assets/icons/sheep.ico'`.

- [ ] **Step 5: Verify**

Run: `venv/Scripts/python.exe -c "import ast; ast.parse(open('run.py').read())"`
Expected: no output.

---

### Task A5: Update README asset paths

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Repoint the images**

`assets/banner.svg` becomes `assets/readme/banner.svg`, same for `palette.svg` and
`rules.svg`. `icons/<species>_land.png` becomes `assets/icons/<species>_land.png`.

- [ ] **Step 2: Update the Project Layout section to the new tree.**

- [ ] **Step 3: Verify every referenced local file exists**

Run the README link check from Task A6 Step 3.

---

### Task A6: Land the tests and verify Part A end to end

**Files:**
- Create: `tests/conftest.py`, `tests/test_frame_history.py`, `tests/test_paths.py`

- [ ] **Step 1: Write tests/conftest.py so tests can import the package**

```python
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
```

- [ ] **Step 2: Write tests/test_paths.py**

```python
import os
from herdsim.utils.path_utils import resource_path, user_data_path, project_root


def test_project_root_contains_src_and_assets():
    root = project_root()
    assert os.path.isdir(os.path.join(root, "src"))
    assert os.path.isdir(os.path.join(root, "assets"))


def test_saves_resolves_inside_the_repository():
    assert os.path.dirname(user_data_path("saves")) == project_root()


def test_every_asset_reference_resolves():
    import re
    missing = []
    for folder, _, files in os.walk(os.path.join(project_root(), "src")):
        for name in files:
            if not name.endswith(".py"):
                continue
            text = open(os.path.join(folder, name), encoding="utf-8").read()
            for rel in re.findall(r'resource_path\(\s*[fr]?"([^"{}]+)"', text):
                if not os.path.exists(resource_path(rel)):
                    missing.append(rel)
    assert missing == [], f"unresolved asset paths: {missing}"
```

- [ ] **Step 3: Port the four debugging harnesses into tests/test_frame_history.py**

Port the paint/rewind differential, the rewind invariants, the paused-paint regression and
the render-layer check that were written during debugging, adapting imports to
`herdsim.ui.sim_canvas` and `herdsim.core.terrain`.

- [ ] **Step 4: Run everything**

Run: `venv/Scripts/python.exe -m pytest tests -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: move to src/herdsim package layout"
```

---

## Part B: Camera and zoom

### Task B1: The Camera unit

**Files:**
- Create: `src/herdsim/ui/camera.py`, `tests/test_camera.py`

**Interfaces:**
- Produces: `Camera(terrainWidth, terrainHeight, viewWidth, viewHeight)` with attributes `zoom`, `offsetX`, `offsetY`, and methods `toTerrain(x, y) -> (float, float)`, `toCanvas(tx, ty) -> (float, float)`, `zoomAt(x, y, direction) -> bool`, `pan(dx, dy)`, `visibleRegion() -> (left, top, right, bottom)`.

- [ ] **Step 1: Write the failing tests**

```python
import pytest
from herdsim.ui.camera import Camera, ZOOM_LEVELS


def make():
    return Camera(512, 512, 508, 508)


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
    cam = make()
    for (cx, cy) in [(0, 0), (100, 400), (507, 250), (254, 254)]:
        cam2 = make()
        before = cam2.toTerrain(cx, cy)
        cam2.zoomAt(cx, cy, +1)
        after = cam2.toTerrain(cx, cy)
        assert after[0] == pytest.approx(before[0], abs=0.75)
        assert after[1] == pytest.approx(before[1], abs=0.75)


def test_viewport_never_leaves_the_terrain():
    cam = make()
    cam.zoomAt(254, 254, +1)
    cam.zoomAt(254, 254, +1)
    for _ in range(50):
        cam.pan(-999, -999)
    l, t, r, b = cam.visibleRegion()
    assert l >= 0 and t >= 0
    assert r <= 512 and b <= 512
    for _ in range(50):
        cam.pan(999, 999)
    l, t, r, b = cam.visibleRegion()
    assert l >= 0 and t >= 0
    assert r <= 512 and b <= 512


def test_zoom_clamps_at_both_ends():
    cam = make()
    for _ in range(20):
        cam.zoomAt(254, 254, +1)
    assert cam.zoom == ZOOM_LEVELS[-1]
    for _ in range(20):
        cam.zoomAt(254, 254, -1)
    assert cam.zoom == ZOOM_LEVELS[0]


def test_at_zoom_one_terrain_and_canvas_coincide():
    cam = make()
    assert cam.zoom == 1.0
    assert cam.toTerrain(37, 91) == (37.0, 91.0)
```

- [ ] **Step 2: Run to verify they fail**

Run: `venv/Scripts/python.exe -m pytest tests/test_camera.py -q`
Expected: FAIL, no module named camera.

- [ ] **Step 3: Implement camera.py**

```python
ZOOM_LEVELS = (1.0, 1.5, 2.0, 3.0, 4.0)


class Camera:
    def __init__(self, terrainWidth, terrainHeight, viewWidth, viewHeight):
        self.terrainWidth = terrainWidth
        self.terrainHeight = terrainHeight
        self.viewWidth = viewWidth
        self.viewHeight = viewHeight
        self.zoomIdx = 0
        self.offsetX = 0.0
        self.offsetY = 0.0

    @property
    def zoom(self):
        return ZOOM_LEVELS[self.zoomIdx]

    def toTerrain(self, x, y):
        return (self.offsetX + x / self.zoom, self.offsetY + y / self.zoom)

    def toCanvas(self, tx, ty):
        return ((tx - self.offsetX) * self.zoom, (ty - self.offsetY) * self.zoom)

    def visibleRegion(self):
        return (self.offsetX, self.offsetY,
                self.offsetX + self.viewWidth / self.zoom,
                self.offsetY + self.viewHeight / self.zoom)

    def zoomAt(self, x, y, direction):
        newIdx = min(max(self.zoomIdx + (1 if direction > 0 else -1), 0), len(ZOOM_LEVELS) - 1)
        if newIdx == self.zoomIdx:
            return False
        anchorX, anchorY = self.toTerrain(x, y)
        self.zoomIdx = newIdx
        self.offsetX = anchorX - x / self.zoom
        self.offsetY = anchorY - y / self.zoom
        self._clamp()
        return True

    def pan(self, dx, dy):
        self.offsetX -= dx / self.zoom
        self.offsetY -= dy / self.zoom
        self._clamp()

    def _clamp(self):
        spanX = self.viewWidth / self.zoom
        spanY = self.viewHeight / self.zoom
        self.offsetX = min(max(self.offsetX, 0.0), max(0.0, self.terrainWidth - spanX))
        self.offsetY = min(max(self.offsetY, 0.0), max(0.0, self.terrainHeight - spanY))
```

- [ ] **Step 4: Run tests**

Run: `venv/Scripts/python.exe -m pytest tests/test_camera.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/herdsim/ui/camera.py tests/test_camera.py
git commit -m "feat: add Camera unit for zoom and viewport offset"
```

---

### Task B2: Route handlers through the camera at zoom 1

**Files:**
- Modify: `src/herdsim/ui/sim_canvas.py`

This task must produce no behaviour change at all. It introduces the boundary while the
camera stays at zoom 1, so the existing suite proves nothing broke.

- [ ] **Step 1: Construct the camera in `SimCanvas.__init__`**

```python
self.camera = Camera(terrain.width, terrain.height, self.width, self.height)
```

- [ ] **Step 2: Add the conversion helper**

```python
    def _terrainXY(self, e):
        tx, ty = self.camera.toTerrain(e.x, e.y)
        tx = min(max(tx, 0), self.terrain.width - 1)
        ty = min(max(ty, 0), self.terrain.height - 1)
        return int(tx), int(ty)
```

- [ ] **Step 3: Route every handler through it**

In `handleClick`, `handleHover`, `handleRightClick`, `fill_paint_window`, `color_contour`
and the obstacle placement branch, replace direct `e.x` / `e.y` reads used as terrain
coordinates with `self._terrainXY(e)`. Drawing positions for brush outlines stay in canvas
coordinates and keep using `e.x` / `e.y`.

- [ ] **Step 4: Run the full suite**

Run: `venv/Scripts/python.exe -m pytest tests -q`
Expected: all pass, identical results to before this task.

- [ ] **Step 5: Commit**

```bash
git commit -am "refactor: route canvas handlers through camera coordinates"
```

---

### Task B3: Render at zoom

**Files:**
- Modify: `src/herdsim/ui/sim_canvas.py`

- [ ] **Step 1: Add the scaled-sprite cache**

```python
    def _spriteFor(self, species):
        key = (species, self.camera.zoom)
        cached = self._spriteCache.get(key)
        if cached is None:
            size = max(1, int(behaviours[species]["size"] * self.camera.zoom))
            src = Image.open(resource_path(f"icons/{species.lower()}_land.png")).resize((size, size))
            cached = ImageTk.PhotoImage(src)
            self._spriteCache[key] = cached
        return cached
```

Initialise `self._spriteCache = {}` in `__init__`.

- [ ] **Step 2: Rebuild the background on zoom or pan change**

```python
    def refreshView(self):
        left, top, right, bottom = self.camera.visibleRegion()
        crop = self.terrain.contourImg.crop((int(left), int(top), int(right), int(bottom)))
        scaled = crop.resize((self.width, self.height), Image.NEAREST)
        self.setBgImage(scaled)
```

`setBgImage` already reuses one canvas item, so this stays at one background item.

- [ ] **Step 3: Draw animals, waypoints and obstacles through `camera.toCanvas`**

Replace `self.create_image(animal.position[0], animal.position[1], ...)` with the canvas
coordinates from `self.camera.toCanvas(animal.position[0], animal.position[1])` and use
`self._spriteFor(species)`. Do the same for waypoints and obstacles.

- [ ] **Step 4: Verify the suite still passes**

Run: `venv/Scripts/python.exe -m pytest tests -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git commit -am "feat: render terrain and sprites at the current zoom level"
```

---

### Task B4: Input bindings

**Files:**
- Modify: `src/herdsim/ui/sim_canvas.py`

- [ ] **Step 1: Split the wheel handler**

```python
    def handleScrollWheel(self, e):
        if e.state & 0x0004:
            direction = 1 if (getattr(e, "delta", 0) > 0 or e.num == 4) else -1
            if self.camera.zoomAt(e.x, e.y, direction):
                self.refreshView()
            return
        self.handleBrushResize(e)
```

Rename the existing body to `handleBrushResize`.

- [ ] **Step 2: Add space-drag panning**

```python
    def handleSpaceDown(self, _):
        if not self.isPanning:
            self.isPanning = True
            self.config(cursor="fleur")

    def handleSpaceUp(self, _):
        self.isPanning = False
        self.panAnchor = None
        self.config(cursor="arrow")

    def handlePanDrag(self, e):
        if self.panAnchor is not None:
            self.camera.pan(e.x - self.panAnchor[0], e.y - self.panAnchor[1])
            self.panAnchor = (e.x, e.y)
            self.refreshView()
```

Initialise `self.isPanning = False` and `self.panAnchor = None` in `__init__`, bind
`<KeyPress-space>` and `<KeyRelease-space>` on the root, and give the canvas focus so it
receives key events.

- [ ] **Step 3: Make panning suppress painting**

At the top of `handleClick`: if `self.isPanning`, set `self.panAnchor = (e.x, e.y)` and
return. At the top of `handleHover`: if `self.isPanning`, call `self.handlePanDrag(e)` and
return.

- [ ] **Step 4: Run the suite**

Run: `venv/Scripts/python.exe -m pytest tests -q`
Expected: all pass.

- [ ] **Step 5: Add a painting-at-zoom regression test**

```python
def test_painting_lands_at_the_same_terrain_pixel_at_any_zoom():
    # paint terrain coordinate (100, 100) at zoom 1 and at zoom 3,
    # assert the resulting typegrid is identical
    ...
```

Implement it concretely against `SimCanvas` with the stub controller and media objects
already used by `tests/test_frame_history.py`.

- [ ] **Step 6: Commit**

```bash
git commit -am "feat: ctrl+wheel zoom to cursor and space+drag panning"
```

---

## Self-review notes

- Spec coverage: Part A tasks A1 to A6 cover layout, path resolution, module moves, packaging, README and verification. Part B tasks B1 to B4 cover the Camera, the coordinate boundary, rendering and input. The deferred terrain palette fix is intentionally absent.
- Naming is consistent across tasks: `toTerrain`, `toCanvas`, `zoomAt`, `pan`, `visibleRegion`, `refreshView`, `_terrainXY`, `_spriteFor`, `_spriteCache`.
- Task B2 deliberately produces no behaviour change so that the existing suite is a regression guard for the riskiest edit.
