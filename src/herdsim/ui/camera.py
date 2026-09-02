ZOOM_LEVELS = (1.0, 1.5, 2.0, 3.0, 4.0)


class Camera:
    """Maps between canvas pixels and terrain pixels for a zoomable viewport."""

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
        return (self.offsetX,
                self.offsetY,
                self.offsetX + self.viewWidth / self.zoom,
                self.offsetY + self.viewHeight / self.zoom)

    def zoomAt(self, x, y, direction):
        step = 1 if direction > 0 else -1
        newIdx = min(max(self.zoomIdx + step, 0), len(ZOOM_LEVELS) - 1)
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

    def reset(self):
        self.zoomIdx = 0
        self.offsetX = 0.0
        self.offsetY = 0.0

    def _clamp(self):
        spanX = self.viewWidth / self.zoom
        spanY = self.viewHeight / self.zoom
        self.offsetX = min(max(self.offsetX, 0.0), max(0.0, self.terrainWidth - spanX))
        self.offsetY = min(max(self.offsetY, 0.0), max(0.0, self.terrainHeight - spanY))
