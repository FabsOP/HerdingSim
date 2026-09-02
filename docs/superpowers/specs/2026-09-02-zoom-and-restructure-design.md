# HerdSim: Repository Restructure and Camera Zoom

Date: 2026-09-02
Status: awaiting review

## Context

Two changes, done in order because the second is much easier once the first has landed.

1. Move the project from a single flat `Code/` directory to a conventional `src/` layout.
2. Add zoom to cursor on the simulation canvas, driven by ctrl+wheel, with space+drag panning.

They are specified together because the new `Camera` unit needs a home, and that home
depends on the layout.

## Findings from probing tkinter

These were measured, not assumed.

| Approach | Result |
|:--|:--|
| `canvas.scale()` | Repositions image items but does not resample their pixels. A 64px sprite stayed 64px after a 2x scale. |
| `tk.PhotoImage.zoom()` | Integer factors only. `zoom(1.5)` raises `TclError`. |
| PIL `resize` plus `ImageTk.PhotoImage` | Works at any factor. 2.1 ms at 1x, 8.7 ms at 2x, 31.9 ms at 4x for a 512x512 terrain. |

Conclusion: sprites do not need to be SVG, and cannot be, because tkinter has no SVG
support. Rescaling goes through PIL with `Image.NEAREST` to keep the pixel art crisp, and
results are cached per zoom level. The cost is paid only when the zoom level changes.

## Decisions taken

| Question | Decision |
|:--|:--|
| Panning | Space plus left drag, as in Photoshop |
| Zoom steps | Discrete: 1.0, 1.5, 2.0, 3.0, 4.0 |
| Layout | Full `src/` layout at the repository root |
| Terrain palette fix | Deferred, not part of this work |

## Part A: Repository restructure

### Target layout

The git repository is rooted at `HerdSim/Code/`, not at `HerdSim/`. The restructure
therefore happens inside the repository, and everything in the parent folder
(`HerdSim.exe`, `Heightmaps/`, `Demo Video/`, and the stray outer `saves/`) is outside
version control and is left untouched.

```
Code/                           the git repository root
├── README.md
├── requirements.txt
├── app.spec
├── run.py                      thin launcher
├── assets/
│   ├── icons/
│   ├── audio/music/
│   ├── default_terrains/
│   └── readme/                 banner.svg, palette.svg, rules.svg
├── src/herdsim/
│   ├── __init__.py
│   ├── app.py
│   ├── core/                   boid.py, flock.py, terrain.py, vector.py
│   ├── ui/                     simulation.py, sim_canvas.py, camera.py,
│   │                           controller.py, animalTab.py, behaviourTab.py,
│   │                           terrainEditorTab.py, borderHandler.py,
│   │                           media_controller.py, main_menu.py,
│   │                           terrainLoader.py, ui_utils.py
│   └── utils/                  path_utils.py
├── tests/
├── docs/
└── saves/                      user terrains, tracked, the single save location
```

Renaming the `Code/` directory itself is out of scope, since it is the repository root
and renaming it would not change anything inside the repository.

### Keeping the 36 asset call sites unchanged

`resource_path` and `user_data_path` are called 36 times across 9 files. Rewriting every
call to say `assets/icons/...` instead of `icons/...` would be 36 chances to introduce a
typo that only shows up at runtime.

Instead, `resource_path` becomes the single place that knows where assets live. It gains
the `assets/` prefix internally, so every existing call site keeps working untouched:

```python
resource_path("icons/sheep.ico")     # unchanged at all 36 sites
# resolves to <root>/assets/icons/sheep.ico
```

This is the same principle the earlier review flagged as an altitude problem: put the
knowledge in the abstraction, not in every caller.

### A real breakage this introduces

`user_data_path` currently resolves relative to the directory holding `path_utils.py`:

```python
base_path = os.path.dirname(os.path.abspath(__file__))
```

Today that file sits in `Code/`, so dev saves land in `Code/saves/`. After the move the
file lives in `src/herdsim/utils/`, and saves would silently land in
`src/herdsim/utils/saves/`.

`user_data_path` must therefore stop deriving the root from its own file location. It
resolves the root as follows, in this order:

1. If frozen, `os.path.dirname(sys.executable)`, which is the current behaviour and stays correct.
2. Otherwise, ascend from `__file__` until a directory containing both `src/` and `assets/` is found, and use that.

Ascending by a fixed number of `..` steps is rejected, because it breaks again the next
time a module moves depth.

### One contained saves directory

There are two saves directories today, because the frozen exe and the dev run resolve
`user_data_path` differently:

| Directory | Used by | Count | In version control |
|:--|:--|--:|:--|
| `HerdSim/saves/` | `HerdSim.exe` | 12 | no |
| `HerdSim/Code/saves/` | running from source | 15 | yes, 12 tracked |

This split was never designed. It falls out of `user_data_path` using the executable's
directory when frozen and the module's own directory otherwise, and the exe happens to
live one level above the source root.

Measured comparison: the outer directory contains nothing unique by name, 11 of its 12
files are byte identical to their counterparts in `Code/saves/`, and only
`Table Mountain.terrain` differs in content. `Code/saves/` is a strict superset by name
and additionally holds **Aconcagua**, **Crater 2** and **Crater 3**.

Decision: `Code/saves/` is the single save location and stays in version control. Nothing
is copied out of the outer directory, because it holds no unique terrain. The outer
directory is left in place rather than deleted, since it is outside the repository and is
the user's data to remove. Once `user_data_path` is fixed it is simply no longer written
to.

### Other required updates

- `app.spec` `datas` entries change from `('icons', 'icons')` to `('assets/icons', 'assets/icons')`, and likewise for audio and default_terrains. The `icon=` path changes too.
- The 7 `sys.path.append(os.path.join(os.path.dirname(__file__), '..'))` hacks are deleted. A real package with relative imports makes them unnecessary.
- README image paths change from `assets/banner.svg` and `icons/sheep_land.png` to their new locations.
- `requirements.txt` gets created: numpy, pillow, pygame, mutagen, tkinter-tooltip.

### Verification for Part A

1. Every module imports cleanly under the venv.
2. `compileall` passes.
3. The existing paint, rewind and replay test suite still passes unchanged.
4. Every one of the 36 asset paths resolves to a file that exists on disk. This is checked by a script, not by eye.
5. `saves/` still contains its 15 terrains and `user_data_path` resolves to it from both a source run and a simulated frozen run.
6. The app launches.

Rebuilding the exe with PyInstaller is out of scope for this change, but `app.spec` is
updated so that the next build is correct.

## Part B: Camera and zoom

### The actual problem

Zoom is not hard. The hard part is that six handlers currently treat canvas pixels as
terrain pixels and read `e.x` and `e.y` directly:

`handleClick`, `handleHover`, `fill_paint_window`, `color_contour`, `handleRightClick`,
and obstacle placement, plus `_inBrush` indirectly.

Zoom invalidates that assumption in all of them simultaneously. So the change is really
about introducing one coordinate boundary, and zoom then falls out of it. The same
boundary also absorbs the scattered 4px border inset that the earlier review flagged.

### The Camera unit

A small class holding zoom level and viewport offset, with no tkinter dependency so it can
be tested headlessly:

```
Camera
    zoom            current discrete level
    offset          terrain-space coordinate shown at canvas (0, 0)
    toTerrain(x, y)   canvas pixels  -> terrain pixels
    toCanvas(tx, ty)  terrain pixels -> canvas pixels
    zoomAt(x, y, direction)   change level, keeping the terrain point under (x, y) fixed
    pan(dx, dy)               move the viewport, clamped to terrain bounds
```

Zoom to cursor is then a single invariant: the terrain point under the cursor before the
zoom is the same terrain point under the cursor after it.

### Rules the implementation must follow

- Every handler takes terrain coordinates from `camera.toTerrain()`. No handler does coordinate arithmetic of its own.
- Zoom and pan are view state, never simulation state. They must not be written into `frames` or `terrainHistory`, otherwise rewinding would move the camera. Boid positions stay in terrain space at all times.
- Brush radius stays in terrain pixels, so a 20px brush paints 20 terrain pixels at any zoom level.
- Terrain image is resized once per zoom change and cropped to the viewport. Sprites are cached keyed by species and zoom level.
- `handleBorder` continues to use terrain dimensions and is unaffected.

### Input bindings

| Input | Action | Notes |
|:--|:--|:--|
| Wheel | Brush size | Unchanged |
| Ctrl plus wheel | Zoom about the cursor | Control bit read from `e.state`. Windows trackpad pinch already emits this. |
| Space held plus left drag | Pan | Cursor changes to a hand while space is held |

Space must not paint while held. The space-down handler sets a panning flag that the
existing click and motion handlers check first.

### Verification for Part B

The Camera is pure arithmetic, so most of this is testable without a window:

1. Round trip: `toCanvas(toTerrain(p)) == p` across a range of zoom levels and offsets.
2. Zoom to cursor invariant: for random cursor positions and zoom steps, the terrain point under the cursor is unchanged after zooming.
3. Clamping: the viewport never shows coordinates outside the terrain.
4. Painting at zoom: paint at 1x and at 3x through the same terrain coordinate, and confirm the resulting typegrid is identical.
5. The existing rewind and replay suite still passes, confirming the camera did not leak into frame history.
6. Manual check in the running app for feel, which the automated tests cannot cover.

## Order of work

Part A first. Doing zoom first would mean moving the new files immediately afterwards.

## Out of scope

- The terrain palette fix for pure black low bands. Measured and understood, deferred by request.
- Rebuilding `HerdSim.exe`.
- Any change to boid steering behaviour.

## Risks

| Risk | Mitigation |
|:--|:--|
| Asset paths break silently at runtime | Script that resolves all 36 paths and fails loudly on any miss |
| The three unique terrains in `Code/saves` are lost | Copy and verify counts before removing `Code/` |
| Camera state leaks into frame history | Existing rewind suite is the regression guard |
| Painting misaligns at zoom | Explicit test painting the same terrain coordinate at two zoom levels |
