########## IMPORTS ####################################
import numpy as np
from PIL import Image, ImageTk
import copy
import time
# import threading

##### PARAMETERS #######################################
default_behaviours = {
    "Sheep": {
        "size": 8,
        "herd-size": [1,100, 1, int, 32],
        "max-acceleration": [1, 10, 1, int, 1],
        "max-velocity": [1, 10, 1, int, 4],
        "cohesion": [0, 1, 0.1, float, 0.3],
        "adhesion": [0, 1, 0.1, float, 0.5],
        "separation": [0, 1, 0.1, float, 0.2],
        "cruising-speed": [0,4,1,int,0], #[0,max-velocity,_,_]
        "comfort-zone": [32, 100,1,int,40], #[size, inf,_,_]
        "danger-zone": [32,40,1,int, 32 ], #[size, comfort,_,_]
        "obstacle-range": [32,100,1,int,32], #[size, inf,_,_]
        "flockmate-range": [40,100,1,int,40], #[comfort, inf]
        "view-angle": [90, 180,1,int,90],
        "drag-factor": [0, 55, 1, int, 10]
    },
    "Lion": {
        "size": 32,
        "max-acceleration": [1, 10, 1, int, 8],
        "max-velocity": [1, 10, 1, int, 9],
        "cohesion": [0, 1, 0.1, float, 0.2],
        "adhesion": [0, 1, 0.1, float, 0.1],
        "separation": [0, 1, 0.1, float, 0.7],
        "perception-radius": [1, 20, 1, int, 15]
    },
    "Fox": {
        "size": 8,
        "max-acceleration": [1, 10, 1, int, 7],
        "max-velocity": [1, 10, 1, int, 8],
        "cohesion": [0, 1, 0.1, float, 0.2],
        "adhesion": [0, 1, 0.1, float, 0.1],
        "separation": [0, 1, 0.1, float, 0.6],
        "perception-radius": [1, 20, 1, int, 12]
    },
    "Penguin": {
        "size": 12,
        "max-acceleration": [1, 10, 1, int, 3],
        "max-velocity": [1, 10, 1, int, 5],
        "cohesion": [0, 1, 0.1, float, 0.8],
        "adhesion": [0, 1, 0.1, float, 0.7],
        "separation": [0, 1, 0.1, float, 0.4],
        "perception-radius": [1, 20, 1, int, 8]
    },
    "Bunny": {
        "size": 8,
        "max-acceleration": [1, 10, 1, int, 9],
        "max-velocity": [1, 10, 1, int, 7],
        "cohesion": [0, 1, 0.1, float, 0.1],
        "adhesion": [0, 1, 0.1, float, 0.1],
        "separation": [0, 1, 0.1, float, 0.8],
        "perception-radius": [1, 20, 1, int, 6]
    },
    "Fish": {
        "size": 8,
        "max-acceleration": [1, 10, 1, int, 4],
        "max-velocity": [1, 10, 1, int, 6],
        "cohesion": [0, 1, 0.1, float, 0.9],
        "adhesion": [0, 1, 0.1, float, 0.8],
        "separation": [0, 1, 0.1, float, 0.3],
        "perception-radius": [1, 20, 1, int, 10]
    }
}
behaviours = copy.deepcopy(default_behaviours)

# Short display names
param_short_names = {
    "max-acceleration": "Max Force",
    "max-velocity": "Max Velocity",
    "cohesion": "Cohesion",
    "adhesion": "Adhesion",
    "separation": "Separation",
    "perception-radius": "Perception",
    "drag-factor": "Drag Factor",
    "herd-size": "Herd Size",
    "comfort-zone": "Comfort Zone",
    "danger-zone": "Danger Zone",
    "view-angle": "View Angle",
    "cruising-speed": "Cruise Speed",
    "obstacle-range": "Avoidance",
    "flockmate-range": "Flock Range"
}

lastModified = None

def updateParamBoundaries():
    sheep = behaviours["Sheep"]
    sheep["max-velocity"][0] = sheep["cruising-speed"][4]
    sheep["cruising-speed"][1] = sheep["max-velocity"][4]
    sheep["comfort-zone"][0] = sheep["size"]
    sheep["danger-zone"][0] = sheep["size"]
    sheep["danger-zone"][1] = sheep["comfort-zone"][4]
    sheep["flockmate-range"][0] = sheep["comfort-zone"][4]
    sheep["obstacle-range"][0] = sheep["size"]
    

#### BOID FACTORY ####################################################
def factory(species, pos):
    if species == "Sheep":
        return Sheep(pos)
    else:
        print("Species not in factory. Instantiating superclass.")
        return Boid(species=species, pos=pos)

####### SUPER CLASS ##################################################
class Boid():
    def __init__(self, species, pos):
        print("Creating boid")
        self.species = species
        
        self.size = behaviours[species]["size"]
        self.image = None
        self.tkImage = None
        self.imagePath = None
        
        self.position = np.array([pos[0], pos[1]], dtype=float)
        self.origin = np.array([pos[0], pos[1]], dtype=float)
        self.velocity = np.array([0, 0], dtype=float)
        self.acceleration = np.array([0, 0], dtype=float)
        
        self.time_alive = 0  # track time since spawn
        
    
    def loadImage(self, path):
        print("Loading image at", path)
        self.image = Image.open(path).resize((self.size, self.size))
        self.tkImage = ImageTk.PhotoImage(self.image)
        self.imagePath = path

    def move(self, dt):
        self.time_alive += dt
        t = self.time_alive
        a = 2  # spiral scale factor (adjust for tightness)

        # Archimedean spiral formula
        r = a * t
        x = r * np.cos(t)
        y = r * np.sin(t)

        self.position = self.origin + np.array([x, y])
    
    def resizeImage(self, newSize):
        if self.size == newSize: return
        self.size = newSize
        self.loadImage(self.imagePath)
    
    def handleBorder(self, borderType, w, h, pad):
        if borderType == "Wrap":
            if self.position[0] > w+ pad[0] or self.position[0] < w:
                self.position[0] = self.position[0] % w
            if self.position[1] > h + pad[1] or self.position[1] < h:
                self.position[1] = self.position[1] % w

#### SPECIES CLASSES ###############
class Sheep(Boid):
    def __init__(self, pos):
        print(f"Creating sheep at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Sheep", pos=pos)
    
    def move(self, dt):
        self.position += np.array([10,0],dtype=float) * dt
        