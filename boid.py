########## IMPORTS ####################################
import numpy as np
from PIL import Image, ImageTk
import copy
import time
from vector import dot, magnitude, ssq, unit, vectorAngle
# import threading


##### PARAMETERS #######################################
default_behaviours = {
    "Sheep": {
        "size": 8,
        "herd-size": [1,100, 1, int, 32],
        "max-acceleration": [1, 100, 1, int, 30],
        "max-velocity": [1, 100, 1, int, 10],
        "cruising-speed": [0,4,1,int,0], #[0,max-velocity,_,_]
        "comfort-zone": [32, 100,1,int,14], #[size, inf,_,_]
        "danger-zone": [32,40,1,int, 9 ], #[size, comfort,_,_]
        "obstacle-range": [32,100,1,int,32], #[size, inf,_,_]
        "flockmate-range": [40,100,1,int,40], #[comfort, inf]
        "view-angle": [1, 180,1,int,90],
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
    "max-acceleration": "Max Accel",
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
    sheep["danger-zone"][1] = sheep["comfort-zone"][4] -1
    sheep["flockmate-range"][0] = sheep["comfort-zone"][4]
    sheep["obstacle-range"][0] = sheep["size"]
    
def accumulate(accumulatorVector, vectorToAdd):
    temp = accumulatorVector + vectorToAdd
    if ssq(temp) <= 1:
        accumulatorVector[:] = temp
        return magnitude(temp)
    else:
        #print("Accumulation failed. Resulting vector exceeds unit length.")
        a = ssq(vectorToAdd)
        b = 2*dot(accumulatorVector, vectorToAdd)
        c = ssq(accumulatorVector) - 1
        t = (-b + np.sqrt(b**2 - 4*a*c)) / (2*a)
        accumulatorVector[:] += t * vectorToAdd
        return 1
        
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
        self.mass = 1
        self.size = behaviours[species]["size"]
        self.image = None
        self.tkImage = None
        self.imagePath = None
        
        self.flock = Flock(species, members=[self])
        self.neighbours = []
        self.flockNeighbours = []
        
        #flags
        self.hasVisableNeighbours = False 
        
        self.position = np.array([pos[0], pos[1]], dtype=float)
        self.origin = np.array([pos[0], pos[1]], dtype=float)

        randomAngle = np.random.uniform(0, 2 * np.pi)
        self.velocity = (np.random.randint(0,101)/100)*behaviours[self.species]["max-velocity"][4]*np.array([np.cos(randomAngle), np.sin(randomAngle)], dtype=float)
        
        self.acceleration = np.array([0, 0], dtype=float)
        self.netForce = np.array([0, 0], dtype=float)
        
        self.time_alive = 0  # track time since spawn
        
    
    def loadImage(self, path):
        print("Loading image at", path)
        self.image = Image.open(path).resize((self.size, self.size))
        self.tkImage = ImageTk.PhotoImage(self.image)
        self.imagePath = path       

    def update(self, boids, dt):
        self.time_alive += dt
        t = self.time_alive
        a = 2  # spiral scale factor (adjust for tightness)

        # Archimedean spiral formula
        r = a * t
        x = r * np.cos(t)
        y = r * np.sin(t)

        self.position = self.origin + np.array([x, y])
    
    def updatePosition(self, dt):
        self.position += self.velocity*dt #+ 1/2*self.acceleration*(dt)**2
    
    def updateVelocity(self, dt):
        self.velocity += self.acceleration*dt
        
        if ssq(self.velocity) > behaviours[self.species]["max-velocity"][4]**2:
            # Limit the velocity to max-velocity
            self.velocity = unit(self.velocity) * behaviours[self.species]["max-velocity"][4]
            
    
    def updateAcceleration(self):
        self.acceleration = self.netForce/self.mass
    
    def resizeImage(self, newSize):
        if self.size == newSize: return
        self.size = newSize
        self.loadImage(self.imagePath)
    
    def handleBorder(self, borderType, w, h, pad):
        if borderType == "Wrap":
            if self.position[0] > w + pad[0] or self.position[0] < w:
                self.position[0] = self.position[0] % w
            if self.position[1] > h + pad[1] or self.position[1] < h:
                self.position[1] = self.position[1] % w
    
    def computeNeighbours(self, boids):
        neighbours = []
        self.hasVisableNeighbours = False
        for boid in boids:
            if boid is self: continue
            
            r = boid.position - self.position
            rxr = ssq(r)
            if rxr <= behaviours[self.species]["flockmate-range"][4]**2:
                theta = np.arccos(dot(unit(self.velocity), unit(r)))
                if theta <= np.deg2rad(behaviours[self.species]["view-angle"][4]):
                    neighbours.append(boid)
                    self.hasVisableNeighbours = True
        return neighbours
    
    def mergeFlock(self, other):      
        if self.species == other.species:
            # Don't merge if they're already in the same flock
            if self.flock is other.flock:
                return False
                
            combined_size = self.flock.size + other.flock.size
            max_herd_size = behaviours[self.species]["herd-size"][4]
            
            #print(f"Debug: Attempting to merge flocks - self.flock.size={self.flock.size}, other.flock.size={other.flock.size}, max={max_herd_size}")
            
            if combined_size <= max_herd_size:
                # Get references to both flocks
                self_flock = self.flock
                other_flock = other.flock
                
                # Combine all members from both flocks
                all_members = self_flock.members + other_flock.members
                
                # Create new flock with all members
                newFlock = Flock(self.species, members=all_members)
                
                # Update all members to point to the new flock
                for member in all_members:
                    member.flock = newFlock
                
                #print(f"Merged flocks. New size: {newFlock.size}")
                return True
            else:
                #print(f"Failed to merge flocks. Combined size ({combined_size}) would exceed max ({max_herd_size})")
                return False
        else:
            #print("Failed to merge flocks. Not the same species")
            return False

    def keepDistance(self):
        if len(self.neighbours) == 0:
            return np.array([0,0], dtype=float)
        
        change = np.array([0,0], dtype=float)
        for neighbour in self.neighbours:
            #vector pointing to the other boid
            dist = neighbour.position - self.position
            mag2 = ssq(dist)
            comfortZone2 = behaviours[self.species]["comfort-zone"][4]**2
            dangerZone2 = behaviours[self.species]["danger-zone"][4]**2
            if mag2 < comfortZone2:
                # other boid is too close push away
                # decide how strongly to accelerate away
                pushStrength = (comfortZone2 - mag2) / (comfortZone2-dangerZone2)
                
                if pushStrength > 1:
                    pushStrength = 1
                    
                dist = unit(dist)*pushStrength
                change -= dist
                
        if ssq(change) > 1:
            return unit(change)
        return change
        
    def matchHeading(self):
        if len(self.flockNeighbours) == 0:
            return np.array([0,0], dtype=float)
        
        avgVelocity = np.array([0,0], dtype=float)    
        count = 0
        
        for neighbour in self.flockNeighbours:
            avgVelocity += neighbour.velocity
            count += 1
            
        if count == 0:
            return np.array([0,0], dtype=float)
        
        avgVelocity /= count
        
        change = (avgVelocity - self.velocity)/(behaviours[self.species]["max-velocity"][4]/2)
        if ssq(change) > 1:
            return unit(change) 
        return change
    
    def steerToCenter(self):
        if len(self.flockNeighbours) == 0:
            return np.array([0,0], dtype=float)
        
        avgPosition = np.array([0,0], dtype=float)
        count = 0
        
        for neighbour in self.flockNeighbours:
            avgPosition += neighbour.position
            count += 1
            
        if count == 0:
            return np.array([0,0], dtype=float)
        
        avgPosition /= count
        
        change = (avgPosition - self.position)/50
        if ssq(change) > 1:
            return unit(change)
        return change
        
#### SPECIES CLASSES ###############
class Sheep(Boid):
    def __init__(self, pos):
        print(f"Creating sheep at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Sheep", pos=pos)
    
    def update(self, boids, dt):
        self.neighbours = self.computeNeighbours(boids)
        for neighbour in self.neighbours:
            if self.mergeFlock(neighbour):
                break
            
        self.flockNeighbours = self.computeNeighbours(self.flock.members)
        
        self.updateBehaviours()    
        self.updateAcceleration()
        self.updateVelocity(dt)
        self.updatePosition(dt)
    
    def updateBehaviours(self):
        """Update the boid's behaviours based on its current state."""
        self.netForce = self.navigator()
        
    def navigator(self):
        acc = np.array([0, 0], dtype=float)
        mag = 0
        
        # mag = accumulate(acc, self.avoidObstacles())
        if mag < 1:
            mag = accumulate(acc, self.keepDistance())
        
        if mag < 1:
            mag = accumulate(acc, self.matchHeading())   
            
        if mag < 1:
            mag = accumulate(acc, self.steerToCenter())
        # if mag < 1:
        #     mag = accumulate(acc, self.gotoGoal())    
        
        acc *= behaviours[self.species]["max-acceleration"][4]*self.mass  # Scale by max acceleration * mass
        return acc

# FLOCK CLASS
class Flock:
    def __init__(self, species, members):
        self.members = list(members)  # Create a copy to avoid reference issues
        self.species = species
        self.size = len(self.members)
        
        # Set flock reference for all members
        for member in self.members:
            member.flock = self
        
    def add_member(self, boid):
        """Add a boid to the flock."""
        max_size = behaviours[self.species]["herd-size"][4]
        if self.size < max_size and boid not in self.members:
            self.members.append(boid)
            self.size = len(self.members)  # Update size based on actual list length
            boid.flock = self
            return True
        return False
    
    def remove_member(self, boid):
        """Remove a boid from the flock."""
        if boid in self.members:
            self.members.remove(boid)
            self.size = len(self.members)  # Update size based on actual list length
            # Create new single-member flock for the removed boid
            new_flock = Flock(species=self.species, members=[boid])
            return True
        return False
    
    def limitFlockSize(self):
        maxHerdSize = behaviours[self.species]["herd-size"][4]
        if self.size > maxHerdSize:
            # Keep first maxHerdSize members
            staying = self.members[:maxHerdSize]
            leaving = self.members[maxHerdSize:]
            
            # Update current flock to only have staying members
            self.members = staying
            self.size = len(staying)
            
            # Create individual flocks for leaving members
            for animal in leaving:
                new_flock = Flock(species=self.species, members=[animal])
                animal.flock = new_flock