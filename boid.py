import numpy as np
from PIL import Image, ImageTk

class Boid():
    def __init__(self, species, pos):
        print("Creating boid")
        self.species = species
        self.image = None
        self.tkImage = None
        self.canvasId = None
        self.maxVelocity = 0
        self.maxAcceleration = 0
        self.position = np.array([pos[0], pos[1]], dtype=float)
        self.origin = np.array([pos[0], pos[1]], dtype=float)
        self.velocity = np.array([0, 0], dtype=float)
        self.acceleration = np.array([0, 0], dtype=float)
        self.size = 32
        self.time_alive = 0  # track time since spawn

    def loadImage(self, path):
        print("Loading image at", path)
        self.image = Image.open(path).resize((self.size, self.size))
        self.tkImage = ImageTk.PhotoImage(self.image)

    def move(self, params, dt):
        self.time_alive += dt
        t = self.time_alive
        a = 2  # spiral scale factor (adjust for tightness)

        # Archimedean spiral formula
        r = a * t
        x = r * np.cos(t)
        y = r * np.sin(t)

        self.position = self.origin + np.array([x, y])

    def setCanvasId(self, id):
        self.canvasId = id

    def getCanvasId(self):
        return self.canvasId

#### BOID GENERATOR FUNCTION
def factory(species, pos):
    if species == "Sheep":
        return Sheep(pos)
    else:
        print("Species not in factory. Instantiating superclass.")
        return Boid(species=species, pos=pos)

#### SPECIES CLASSES ###############
class Sheep(Boid):
    def __init__(self, pos):
        print(f"Creating sheep at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Sheep", pos=pos)
    
    def move(self, params, dt):
        self.position += np.array([10,0],dtype=float) * dt