########## IMPORTS ####################################
import numpy as np
from PIL import Image, ImageTk
import copy
# import time
from vector import dot, magnitude, ssq, unit, vectorAngle
# import threading


##### PARAMETERS #######################################
default_behaviours = {
    "Sheep": {
        "size": 12,
        "herd-size": [1,30, 1, int, 20],
        "max-acceleration": [1, 100, 1, int, 30],
        "max-velocity": [1, 100, 1, int, 18],
        "cruising-speed": [1,10,1,int,6], #[0,max-velocity,_,_]
        "comfort-zone": [16, 100,1,int,14], #[size, inf,_,_]
        "danger-zone": [16,40,1,int,9], #[size, comfort,_,_]
        "obstacle-range": [16,100,1,int,40], #[size, inf,_,_]
        "flockmate-range": [40,200,1,int,40], #[comfort, inf]
        "view-angle": [1, 180,1,int,180],
        "drag-factor": [0, 55, 1, int, 4]
    },
    "Elephant": {
        "size": 20,
        "herd-size": [1,20, 1, int, 6],
        "max-acceleration": [1, 100, 1, int, 10],
        "max-velocity": [1, 100, 1, int, 20],
        "cruising-speed": [1,10,1,int,9], #[0,max-velocity,_,_]
        "comfort-zone": [16, 100,1,int,30], #[size, inf,_,_]
        "danger-zone": [16,40,1,int,20], #[size, comfort,_,_]
        "obstacle-range": [16,100,1,int,32], #[size, inf,_,_]
        "flockmate-range": [40,200,1,int,40], #[comfort, inf]
        "view-angle": [1, 180,1,int,180],
        "drag-factor": [0, 55, 1, int, 30],
    },
    "Fox": {
        "size": 10,
        "herd-size": [1,5, 1, int, 1],
        "max-acceleration": [1, 100, 1, int, 50],
        "max-velocity": [1, 100, 1, int, 35],
        "cruising-speed": [1,10,1,int,15], #[0,max-velocity,_,_]
        "comfort-zone": [16, 100,1,int,14], #[size, inf,_,_]
        "danger-zone": [16,40,1,int,9], #[size, comfort,_,_]
        "obstacle-range": [16,100,1,int,50], #[size, inf,_,_]
        "flockmate-range": [40,200,1,int,100], #[comfort, inf]
        "view-angle": [1, 180,1,int,130],
        "drag-factor": [0, 55, 1, int, 7]
    },
    "Penguin": {
        "size": 8,
        "herd-size": [1,100, 1, int, 100],
        "max-acceleration": [1, 100, 1, int, 40],
        "max-velocity": [1, 100, 1, int, 25],
        "cruising-speed": [1,4,1,int,3], #[0,max-velocity,_,_]
        "comfort-zone": [32, 100,1,int,14], #[size, inf,_,_]
        "danger-zone": [32,40,1,int,9], #[size, comfort,_,_]
        "obstacle-range": [32,100,1,int,32], #[size, inf,_,_]
        "flockmate-range": [40,100,1,int,40], #[comfort, inf]
        "view-angle": [1, 180,1,int,110],
        "drag-factor": [0, 55, 1, int, 20],
    },
    "Flamingo": {
        "size": 12,
        "herd-size": [1,30, 1, int, 20],
        "max-acceleration": [1, 100, 1, int, 30],
        "max-velocity": [1, 100, 1, int, 20],
        "cruising-speed": [1,10,1,int,15], #[0,max-velocity,_,_]
        "comfort-zone": [16, 100,1,int,14], #[size, inf,_,_]
        "danger-zone": [16,40,1,int,9], #[size, comfort,_,_]
        "obstacle-range": [16,100,1,int,32], #[size, inf,_,_]
        "flockmate-range": [40,200,1,int,40], #[comfort, inf]
        "view-angle": [1, 180,1,int,180],
        "drag-factor": [0, 55, 1, int, 30],
    },
    "Swallow": {
        "size": 12,
        "herd-size": [1,30, 1, int, 15],
        "max-acceleration": [1, 100, 1, int, 100],
        "max-velocity": [1, 100, 1, int, 30],
        "cruising-speed": [1,15,1,int,30], #[0,max-velocity,_,_]
        "comfort-zone": [16, 100,1,int,25], #[size, inf,_,_]
        "danger-zone": [16,40,1,int,9], #[size, comfort,_,_]
        "flockmate-range": [40,200,1,int,80], #[comfort, inf]
        "view-angle": [1, 180,1,int,120],
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
    "flockmate-range": "Flock Range",
}

lastModified = None

#tooltips for params
tooltips = {
    "max-acceleration": "Maximum acceleration species can achieve.",
    "max-velocity": "Maximum velocity species can achieve.",
    "herd-size": "Maximum number of animals allowed in a single flock.",
    "cruising-speed": "Preferred navigation speed of the species.",
    "comfort-zone": "Distance an animal maintains from others to feel comfortable.",
    "danger-zone": "Distance within which an animal is too close for comfort.",
    "obstacle-range": "Distance at which species starts to avoid obstacles.",
    "flockmate-range": "Distance within which other animals can join the flock.",
    "view-angle": "Field of view angle for perceiving other animals.",
    "drag-factor": "Factor determining resistance to movement across terrain contours.",
}

def updateParamBoundaries(species):
    if species == "Sheep":
        sheep = behaviours["Sheep"]
        sheep["max-velocity"][0] = sheep["cruising-speed"][4]
        sheep["cruising-speed"][1] = sheep["max-velocity"][4]
        sheep["comfort-zone"][0] = sheep["size"] + 1
        sheep["danger-zone"][0] = sheep["size"]
        sheep["danger-zone"][1] = sheep["comfort-zone"][4] -1
        sheep["flockmate-range"][0] = sheep["comfort-zone"][4]
        sheep["obstacle-range"][0] = sheep["size"]
    elif species == "Penguin":
        penguin = behaviours["Penguin"]
        penguin["max-velocity"][0] = penguin["cruising-speed"][4]
        penguin["cruising-speed"][1] = penguin["max-velocity"][4]
        penguin["comfort-zone"][0] = penguin["size"] + 1
        penguin["danger-zone"][0] = penguin["size"]
        penguin["danger-zone"][1] = penguin["comfort-zone"][4] -1
        penguin["flockmate-range"][0] = penguin["comfort-zone"][4]
        penguin["obstacle-range"][0] = penguin["size"]
    elif species == "Fox":
        fox = behaviours["Fox"]
        fox["max-velocity"][0] = fox["cruising-speed"][4]
        fox["cruising-speed"][1] = fox["max-velocity"][4]
        fox["comfort-zone"][0] = fox["size"] + 1
        fox["danger-zone"][0] = fox["size"]
        fox["danger-zone"][1] = fox["comfort-zone"][4] -1
        fox["flockmate-range"][0] = fox["comfort-zone"][4]
        fox["obstacle-range"][0] = fox["size"]
    elif species == "Flamingo":
        flamingo = behaviours["Flamingo"]
        flamingo["max-velocity"][0] = flamingo["cruising-speed"][4]
        flamingo["cruising-speed"][1] = flamingo["max-velocity"][4]
        flamingo["comfort-zone"][0] = flamingo["size"] + 1
        flamingo["danger-zone"][0] = flamingo["size"]
        flamingo["danger-zone"][1] = flamingo["comfort-zone"][4] -1
        flamingo["flockmate-range"][0] = flamingo["comfort-zone"][4]
        flamingo["obstacle-range"][0] = flamingo["size"]
    # elif species == "Fish":
    #     fish = behaviours["Fish"]
    #     fish["max-velocity"][0] = fish["cruising-speed"][4]
    #     fish["cruising-speed"][1] = fish["max-velocity"][4]
    #     fish["comfort-zone"][0] = fish["size"] + 1
    #     fish["danger-zone"][0] = fish["size"]
    #     fish["danger-zone"][1] = fish["comfort-zone"][4] -1
    #     fish["flockmate-range"][0] = fish["comfort-zone"][4]
    #     fish["obstacle-range"][0] = fish["size"]
    elif species == "Swallow":
        swallow = behaviours["Swallow"]
        swallow["max-velocity"][0] = swallow["cruising-speed"][4]
        swallow["cruising-speed"][1] = swallow["max-velocity"][4]
        swallow["comfort-zone"][0] = swallow["size"] + 1
        swallow["danger-zone"][0] = swallow["size"]
        swallow["danger-zone"][1] = swallow["comfort-zone"][4] -1
        swallow["flockmate-range"][0] = swallow["comfort-zone"][4]
        
    elif species == "Elephant":
        elephant = behaviours["Elephant"]
        elephant["max-velocity"][0] = elephant["cruising-speed"][4]
        elephant["cruising-speed"][1] = elephant["max-velocity"][4]
        elephant["comfort-zone"][0] = elephant["size"] + 1
        elephant["danger-zone"][0] = elephant["size"]
        elephant["danger-zone"][1] = elephant["comfort-zone"][4] -1
        elephant["flockmate-range"][0] = elephant["comfort-zone"][4]
        elephant["obstacle-range"][0] = elephant["size"]
      
    else:
        print(f"Species '{species}' not recognized. No parameter boundaries updated.")

### BOID ORIENTATION IMAGE STORING ##################################
# This is used to store the orientation of boids in a flock for a few angles from the positive x-axis.

# Fish Orientation TKImages
#default tkImages for fish orientations

#### HELPER FUNCTIONS ##################################################    
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
def factory(species, pos=None, state=None):
    """Factory function to create a boid of the specified species."""
    if species == "Sheep":
        animal = Sheep(pos)
        animal.loadState(state)
        return animal
    
    elif species == "Penguin":
        animal = Penguin(pos)
        animal.loadState(state)
        return animal
        
    elif species == "Fish":
        animal = Fish(pos)
        animal.loadState(state)
        return animal
        
    elif species == "Elephant":
        animal = Elephant(pos)
        animal.loadState(state)
        return animal
    
    elif species == "Swallow":
        animal = Swallow(pos)
        animal.loadState(state)
        return animal
    
    elif species == "Fox":
        animal = Fox(pos)
        animal.loadState(state)
        return animal
    
    elif species == "Flamingo":
        animal = Flamingo(pos)
        animal.loadState(state)
        return animal
        
    else:
        print("Species not in factory. Instantiating superclass.")
        animal = Boid(species, pos)
        animal.loadState(state)
        return animal

####### SUPER CLASS ##################################################
class Boid():
    def __init__(self, species, pos=None):
        self.species = species
        self.mass = 1
        self.size = behaviours[species]["size"]
        self.image = None
        self.tkImage = None
        self.imagePath = None
        self.canvasId = None
        
        self.isDead = False
        
        self.flock = Flock(species, members=[self])
        self.neighbours = []
        self.flockNeighbours = []
        
        self.goal = None
        
        #flags
        self.hasVisableNeighbours = False 

        self.position = np.array([pos[0], pos[1]], dtype=float) if pos is not None else np.array([0, 0], dtype=float)
        
        randomAngle = np.random.uniform(0, 2 * np.pi)
        self.velocity = (np.random.randint(0,101)/100)*behaviours[self.species]["max-velocity"][4]*np.array([np.cos(randomAngle), np.sin(randomAngle)], dtype=float)
        
        self.acceleration = np.array([0, 0], dtype=float)
        self.netForce = np.array([0, 0], dtype=float)
        
        self.hunger = 0
        
        #modifiers depending on terrain/state
        self.speedModifier = 1.0
        self.accelerationModifier = 1.0
        # self.perceptionModifier = 1.0  
        # self.obstacleModifier = 1.0
        
    def calculateDragForce(self, dragFactor):
        return -dragFactor * self.velocity
    
    def getState(self):
        return {
            "species": self.species,
            "position": self.position.copy(),
            "velocity": self.velocity.copy(),
            "acceleration": self.acceleration.copy(),
            "goal": self.goal.copy() if self.goal is not None else None,
        }
        
    def loadState(self, state):
        if state is None:
            return 
        
        self.species = state["species"]
        self.position = np.array(state["position"], dtype=float)
        self.velocity = np.array(state["velocity"], dtype=float)
        self.acceleration = np.array(state["acceleration"], dtype=float)
        self.goal = np.array(state["goal"], dtype=float) if state["goal"] is not None else None
        
    def setGoal(self, goal):
        self.goal = goal
    
    def loadImage(self, path):
        print("Loading image at", path)
        self.image = Image.open(path).resize((self.size, self.size))
        self.tkImage = ImageTk.PhotoImage(self.image)
        self.imagePath = path      
        
    def kill(self):
        self.isDead = True
        if self.flock is not None:
            self.flock.remove_member(self)
            self.flock = None 
        

    def update(self, boids, terrain, obstacles, dt):
        # if dead, do nothing
        if self.isDead:
            return
        
        self.neighbours = self.computeNeighbours(boids)
        for neighbour in self.neighbours:
            if self.mergeFlock(neighbour):      #break if flock is merged
                break
            
        self.flockNeighbours = self.computeNeighbours(self.flock.members)
        
        #if no flockNeighbours, leave flock
        if len(self.flockNeighbours) == 0:
            self.leaveFlock()
        
        #flocking behaviours
        self.updateBehaviours(obstacles, boids)    
        self.updateAcceleration()
        
        #terrain navigation behaviour
        self.resetModifiers()
        self.navigateTerrain(terrain)
        self.updateAcceleration()
        
        self.updateVelocity(dt)
        self.updatePosition(terrain, dt)
        self.updateHunger(dt)
        
    def updateHunger(self, dt):
        """Update the boid's hunger state."""
        self.hunger += dt  # Increase hunger over time
        
    def resetModifiers(self):
        self.speedModifier = 1.0
        self.accelerationModifier = 1.0
    
    def updateBehaviours(self, obstacles=None, boids=None):
        """Update the boid's behaviours based on its current state."""
        if self.isDead:
            return
        
        self.netForce = self.navigator(obstacles, boids)
        
    def navigator(self, obstacles, boids=None):
        acc = np.array([0, 0], dtype=float)
        mag = 0
        
        #Priority 1: Avoid obstacles
        mag = accumulate(acc, self.avoidObstacles(obstacles))
        
        # priority 2: Maintain distance from flockmates
        if mag < 1:
            mag = accumulate(acc, self.keepDistance())
        
        # Priority 3: Cohesion with flockmates
        if mag < 1:
            mag = accumulate(acc, self.matchHeading())   
        
        # Priority 4: Align with flockmates     
        if mag < 1:
            mag = accumulate(acc, self.steerToCenter())
            
        # Priority 5: Goal seeking
        if mag < 1 and self.goal is not None:
            mag = accumulate(acc, self.gotoGoal())
        
        # Priority 6: Maintain cruising speed    
        if mag < 1:
            mag = accumulate(acc, self.maintainSpeed())
             
        
        acc *= behaviours[self.species]["max-acceleration"][4]*self.mass  # Scale by max acceleration * mass
        return acc
    
    
    def updatePosition(self, terrain, dt):
        # Check bounds before accessing terrain data
        x, y = self.position[0], self.position[1]
        
        if (x < 0 or x >= terrain.width or y < 0 or y >= terrain.height):
            # If out of bounds, just update position without terrain influence
            self.position += self.velocity * dt
            return
        
        # Convert to integers for array indexing
        x_int, y_int = int(x), int(y)
        
        # Double-check integer indices are still in bounds
        if (x_int < 0 or x_int >= terrain.width or y_int < 0 or y_int >= terrain.height):
            self.position += self.velocity * dt
            return
        
        try:
            gradVelocityComponent = dot(unit(self.velocity), terrain.gradientField[y_int][x_int])
            slopeCorrectionFactor = 1/np.sqrt(gradVelocityComponent**2 + 1)
            self.position += slopeCorrectionFactor * self.velocity * dt
        except (IndexError, AssertionError):
            # Fallback to simple position update if terrain access fails
            self.position += self.velocity * dt
    
    def updateVelocity(self, dt):
        self.velocity += self.acceleration*dt
        
        if ssq(self.velocity) > behaviours[self.species]["max-velocity"][4]**2:
            # Limit the velocity to max-velocity
            self.velocity = unit(self.velocity) * self.speedModifier*behaviours[self.species]["max-velocity"][4]
            
    
    def updateAcceleration(self):
        self.acceleration = self.accelerationModifier*self.netForce/self.mass
    
    def resizeImage(self, newSize):
        if self.size == newSize: return
        self.size = newSize
        self.loadImage(self.imagePath)
    
    def handleBorder(self, borderType, w, h):
        if borderType == "Wrap":
            if self.position[0] > w  or self.position[0] < w:
                self.position[0] = self.position[0] % w
            if self.position[1] > h or self.position[1] < h:
                self.position[1] = self.position[1] % w
        elif borderType == "Bounce":
            #x coords
            hitLeft = self.position[0] - self.size/2 <= 0 and self.velocity[0] < 0
            hitRight = self.position[0] + self.size/2 >= w and self.velocity[0] > 0
            if (hitLeft or hitRight):
                self.position[0] = (self.size/2 if hitLeft else w-self.size/2)
                self.velocity[0] *= -1
            
            #y coords   
            hitBottom = self.position[1] + self.size/2 >= h and self.velocity[1] > 0
            hitTop = self.position[1] - self.size/2 <= 0 and self.velocity[1] < 0
            if (hitBottom or hitTop):
                self.position[1] = (self.size/2 if hitTop else h-self.size/2)
                self.velocity[1] *= -1
        elif borderType == "Void":
            if (self.position[0] < -self.size or self.position[0] > w+self.size or
                self.position[1] < -self.size or self.position[1] > h+self.size):
                self.kill()
        elif borderType == "Follow":
            # Left border
            if self.position[0] - self.size/2 <= 0:
                self.position[0] = self.size/2
                # Zero out x velocity, keep y
                self.velocity[0] = 0
                # Optionally nudge inward
                self.position[0] += 1
            # Right border
            elif self.position[0] + self.size/2 >= w:
                self.position[0] = w - self.size/2
                self.velocity[0] = 0
                self.position[0] -= 1
            # Top border
            if self.position[1] - self.size/2 <= 0:
                self.position[1] = self.size/2
                self.velocity[1] = 0
                self.position[1] += 1
            # Bottom border
            elif self.position[1] + self.size/2 >= h:
                self.position[1] = h - self.size/2
                self.velocity[1] = 0
                self.position[1] -= 1
            
    
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
        if self.isDead or other.isDead or self.flock is None or other.flock is None:
            return False      
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

    def leaveFlock(self):
        self.flock.remove_member(self)
        self.flock = Flock(species=self.species, members=[self])
    
    ### NAVIGATOR FUNCTIONS ##########################################    
    def maintainSpeed(self):
        current_speed = magnitude(self.velocity)
        target_speed = behaviours[self.species]["cruising-speed"][4]
        
        target_speed *= 0.4 if self.goal is None else 1.0
        
        if current_speed < target_speed * 0.8:  # If significantly below target
            if current_speed > 0.1:  # Avoid division by zero
                # Accelerate in current direction
                acceleration_needed = (target_speed - current_speed) / target_speed
                return unit(self.velocity) * acceleration_needed
            else:
                # If nearly stationary, pick a random direction
                random_angle = np.random.uniform(0, 2 * np.pi)
                return np.array([np.cos(random_angle), np.sin(random_angle)]) * 0.5
        
        return np.array([0, 0], dtype=float)     

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
   
    def gotoGoal(self):
        desiredVelocity = self.goal - self.position
       
        if ssq(desiredVelocity) > behaviours[self.species]["cruising-speed"][4]:
            desiredVelocity = unit(desiredVelocity)*behaviours[self.species]["cruising-speed"][4]

        change = (desiredVelocity- self.velocity)/(behaviours[self.species]["max-velocity"][4]/2)
        
        if ssq(change) > 1:
            return unit(change)
        
        return change
    
    def avoidObstacles(self, obstacles=None):
        if obstacles in [None, []]:
            return np.array([0,0], dtype=float)
        
        force = np.array([0,0], dtype=float)
        closestDistanceSqd = np.inf
        obstacleFound = False
        
        #obstacles = [(obstacle_type, xpos, ypos, radius), ..]
        for obstacle in obstacles:
            obstacle_type, xpos, ypos, hitboxRadius, hitboxOffset, _ = obstacle
            hitboxOffset = np.array(hitboxOffset, dtype=float)
            
            # radius not to hit the obstacle
            radius = hitboxRadius + behaviours[self.species]["size"]/2
            radius2 = radius**2
            
            # vector to center of obstacle
            d = (np.array([xpos,ypos], dtype=float) + hitboxOffset) - self.position
            
            # magnitude of distance squared to obstacle center
            d2mag = ssq(d)
            
            # if current obstacle is not closer than the closest found so far
            # then it is not a candidate for avoidance
            if obstacleFound and d2mag > closestDistanceSqd:
                continue    #with next obstacle
            
            # check emergency condition of being too close to the obstacle
            if d2mag <= radius2:
                
                #accerate directly away from the obstacle
                force = -d*(100*behaviours[self.species]["size"]**2/d2mag)
                
                obstacleFound = True
                closestDistanceSqd = d2mag
                continue  # no need to check further obstacles
        
            # otherwise, we are not colliding yet
            
            # check if the direction to the obstacle is behind the boid
            if dot(d,self.velocity) <= 0:
                # if the obstacle is behind, ignore it
                continue
            
            # otherwise, we are facing the obstacle
            
            #find the projection of the tree onto the line perpendicular to the displacement vector d
            projected_r = 0
            
            if d2mag < 4*radius2:
                # if the obstacle is close, use a stronger force
                projected_r = np.sqrt(radius2*d2mag/(d2mag - radius2))
            elif d2mag < behaviours[self.species]["obstacle-range"][4]**2:
                #use a bigger radius than actual to give some comfort space
                projected_r = radius * 1.3
            else:
                continue  # if the obstacle is too far, ignore it
            
            # Now we want to project the circle of the obstacle onto a line perpedicular to the velocity. 
            # If the obstacle projects entirely to the left pr to the right of the current position, then the boid will not collide with it.
            
            d_unit = unit(d)
            # rotate d_unit 90 degrees
            d_unit_rotated = np.array([d_unit[1], -d_unit[0]], dtype=float)
            
            # now we find 2 points on either side of the obstacle that we will project
            point1 = d_unit_rotated * projected_r + d
            point2 = -d_unit_rotated * projected_r + d
            
            # we want a vector perpendicular to the velocity
            right = np.array([self.velocity[1], -self.velocity[0]], dtype=float)
            
            # p1 and p2 are the projections of point1 and point 2
            p1 = dot(point1, right)
            p2 = dot(point2, right)
            
            # if one projection is positive abd the other is negative, then we're heading towards the obstacle
            # otherwise we are not
            if p1 * p2 < 0:
                #which edge of the obstacle is closer?
                if abs(p1) > abs(p2):
                    new_vel = point2
                else:
                    new_vel = point1
                    
                # set the new velocity magnitude to the current velocity magnitude
                new_vel = unit(new_vel) * magnitude(self.velocity)
                
                # apply force to change the velocity to new
                # use radius/distance to scale the force so nearer obstacles apply more force
                
                
                force = 10000 *(new_vel - self.velocity) * (radius / np.sqrt(d2mag))
                obstacleFound = True
                closestDistanceSqd = d2mag
                
        if ssq(force) > 1:
            return unit(force)   
        return force
                
            
    def handleTerrainType(self, terrainType, grad=None):
        return False
        

    def navigateTerrain(self, terrain):
        # More robust bounds checking - check both position components
        x, y = self.position[0], self.position[1]
        
        # Check bounds before any terrain access
        if (x < 0 or x >= terrain.width or y < 0 or y >= terrain.height):
            return
        
        # Convert to integers for array indexing
        x_int, y_int = int(x), int(y)
        
        # Double-check integer indices are still in bounds (handles edge cases)
        if (x_int < 0 or x_int >= terrain.width or y_int < 0 or y_int >= terrain.height):
            return
        
        try:
            grad = terrain.gradientField[y_int][x_int]
            terrainType = terrain.typeAt(x, y)  # This calls the method that has the assertion
        except (IndexError, AssertionError):
            # Position is out of bounds, skip terrain navigation
            return
        
        slope = magnitude(grad)
        
        F = np.array([0,0], dtype=float)
        
        # let species handle special terrain types first, e.g. swimming, sliding
        ignoreSlope = self.handleTerrainType(terrainType, grad)
        if ignoreSlope:
            return
        
        if slope > 0:
            # component of velocity parallel to the gradient
            vdotg = dot(self.velocity, grad)
            
            if vdotg > 0: #boid travelling uphill
                F = (-behaviours[self.species]["drag-factor"][4]*vdotg / slope)*grad
                
            elif vdotg < 0: # boid travelling downhill
                #if down hill and terrain type is water, apply positive drag factor
                F = (-(behaviours[self.species]["drag-factor"][4]/5)*vdotg / slope)*grad  #downhill dragfactor = dragfactor/5
            
            self.netForce += F
            
                    
#### SPECIES CLASSES ###############################
class Sheep(Boid):
    def __init__(self, pos):
        # print(f"Creating sheep at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Sheep", pos=pos)
        self.mass = 1.5
        
        self.predators = ["Fox"]
        
    def handleTerrainType(self, terrainType,grad):
        #bad swimmers so water pushes them strongly
        if terrainType == "Water":
            slope = magnitude(grad)
            
            if slope > 0.01:  # If there's noticeable slope (flowing water)
                # Push along gradient (stream/current)
                streamStrength = 30
                streamForce = streamStrength * unit(grad)
                self.netForce += streamForce
                return True
            else:  # Flat water (pond/lake)
                # Apply resistance - sheep struggle to swim in still water
                resistance_strength = 15
                resistance_force = -resistance_strength * self.velocity
                self.netForce += resistance_force
                self.accelerationModifier = 0.3
                return False
        
        if terrainType == "Ice":
            #limit max acceleration
            self.accelerationModifier = 0.1
            return True
            
        
        if terrainType == "Snow":
            self.accelerationModifier = 0.5
            # Apply drag force to slow down the boid
            self.netForce += self.calculateDragForce(8)
            return False
        
        if terrainType == "Sand":
            self.accelerationModifier = 0.5
            # Apply drag force to slow down the boid
            self.netForce += self.calculateDragForce(12)
            return False
            
        if terrainType == "Rock":
            # Apply drag force to slow down the boid
            self.accelerationModifier = 0.8
            self.netForce += self.calculateDragForce(2)
            return False
            
        if terrainType == "Grass":
            self.netForce += self.calculateDragForce(1.5)
            return False
            
        
        return False

    def flee(self, boids):
        """Improved flee from nearby predators"""
        if not boids:
            return np.array([0, 0], dtype=float)
        
        flee_vector = np.array([0, 0], dtype=float)
        closest_threat_dist = float('inf')
        
        for boid in boids:
            if boid.species not in self.predators or boid.isDead:
                continue
            
            # Vector from predator to self
            r = self.position - boid.position
            dist_sq = ssq(r)
            
            # Define detection ranges based on urgency
            panic_range_sq = 50**2      # Immediate danger
            alert_range_sq = 150**2     # General awareness
            
            # Check if predator is visible (within view angle)
            if dist_sq > 0.01:  # Avoid division by zero
                # Use velocity if moving, otherwise check all directions
                if ssq(self.velocity) > 0.1:
                    view_direction = unit(self.velocity)
                else:
                    # If stationary, can see in all directions
                    view_direction = unit(r)
                
                angle_cos = dot(view_direction, unit(r))
                view_angle_cos = np.cos(np.deg2rad(behaviours[self.species]["view-angle"][4]))
                
                # If behind us but close, still flee (peripheral awareness)
                if angle_cos < view_angle_cos and dist_sq > panic_range_sq:
                    continue  # Predator is behind and not too close
            
            # If within detection range, flee
            if dist_sq < alert_range_sq:
                # Scale urgency based on distance
                if dist_sq < panic_range_sq:
                    urgency = 1.0  # Maximum urgency
                else:
                    # Gradual urgency increase as predator gets closer
                    urgency = 1.0 - (dist_sq - panic_range_sq) / (alert_range_sq - panic_range_sq)
                    urgency = max(0.3, urgency)  # Minimum 30% urgency
                
                # Consider predator's heading
                predator_velocity_towards = -dot(unit(boid.velocity), unit(r))
                if predator_velocity_towards > 0.3:  # Predator moving towards us
                    urgency *= 1.5  # Increase urgency
                
                # Desired flee velocity
                if dist_sq < panic_range_sq:
                    # Panic - flee at max speed
                    desired_velocity = unit(r) * behaviours[self.species]["max-velocity"][4]
                else:
                    # Alert - flee at scaled speed
                    desired_velocity = unit(r) * behaviours[self.species]["cruising-speed"][4] * urgency
                
                # Calculate flee force
                flee_force = (desired_velocity - self.velocity) / (behaviours[self.species]["max-velocity"][4] / 2)
                flee_force *= urgency
                
                flee_vector += flee_force
                closest_threat_dist = min(closest_threat_dist, dist_sq)
        
        if ssq(flee_vector) > 1:
            return unit(flee_vector)
        return flee_vector
    
    def navigator(self, obstacles, boids=None):
        acc = np.array([0, 0], dtype=float)
        mag = 0
        
        # Priority 1: Avoid obstacles
        mag = accumulate(acc, self.avoidObstacles(obstacles))
        
        # Priority 2: FLEE from predators (high priority!)
        if mag < 1 and boids is not None:
            mag = accumulate(acc, self.flee(boids))
        
        # Priority 3: Maintain distance from flockmates
        if mag < 1:
            mag = accumulate(acc, self.keepDistance())
        
            
        # Priority 4: Cohesion with flockmates
        if mag < 1:
            mag = accumulate(acc, self.matchHeading())   
        
        # Priority 5: Align with flockmates     
        if mag < 1:
            mag = accumulate(acc, self.steerToCenter())
            
        # Priority 6: Goal seeking
        if mag < 1 and self.goal is not None:
            mag = accumulate(acc, self.gotoGoal())
        
        # Priority 7: Maintain cruising speed    
        if mag < 1:
            mag = accumulate(acc, self.maintainSpeed())
        
        acc *= behaviours[self.species]["max-acceleration"][4] * self.mass
        return acc

class Penguin(Boid):
    def __init__(self, pos):
        # print(f"Creating penguin at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Penguin", pos=pos)
        self.mass = 0.8
        
        self.predators = ["Fox"]
        
    def handleTerrainType(self, terrainType, grad=None): 
        if terrainType == "Water":
            # print(f"Applying swimming force.")
            self.accelerationModifier = 2
            self.speedModifier = 2
            swimming_strength = 3
            swimming_force = swimming_strength * unit(self.velocity)
            self.netForce += swimming_force
            return True
        
        elif terrainType == "Ice":
            print(f"Applying sliding force.")
            self.speedModifier = 1.5
            self.accelerationModifier = 0.4
            sliding_strength = 2
            sliding_force = sliding_strength * unit(self.velocity)
            self.netForce += sliding_force
            return True
        
        if terrainType == "Snow":
            # print(f"Applying wading force.")
            self.netForce += self.calculateDragForce(4)
            return False
        
        if terrainType == "Sand":
            self.accelerationModifier = 0.8
            self.netForce += self.calculateDragForce(12)
            return False
        
        if terrainType == "Rock":
            self.accelerationModifier = 0.5
            self.netForce += self.calculateDragForce(11)
            return False
            
        if terrainType == "Grass":
            self.netForce += self.calculateDragForce(1.5)
            return False
        
        return False

    def flee(self, boids):
        """Improved flee from nearby predators"""
        if not boids:
            return np.array([0, 0], dtype=float)
        
        flee_vector = np.array([0, 0], dtype=float)
        closest_threat_dist = float('inf')
        
        for boid in boids:
            if boid.species not in self.predators or boid.isDead:
                continue
            
            # Vector from predator to self
            r = self.position - boid.position
            dist_sq = ssq(r)
            
            # Define detection ranges based on urgency
            panic_range_sq = 50**2      # Immediate danger
            alert_range_sq = 150**2     # General awareness
            
            # Check if predator is visible (within view angle)
            if dist_sq > 0.01:  # Avoid division by zero
                # Use velocity if moving, otherwise check all directions
                if ssq(self.velocity) > 0.1:
                    view_direction = unit(self.velocity)
                else:
                    # If stationary, can see in all directions
                    view_direction = unit(r)
                
                angle_cos = dot(view_direction, unit(r))
                view_angle_cos = np.cos(np.deg2rad(behaviours[self.species]["view-angle"][4]))
                
                # If behind us but close, still flee (peripheral awareness)
                if angle_cos < view_angle_cos and dist_sq > panic_range_sq:
                    continue  # Predator is behind and not too close
            
            # If within detection range, flee
            if dist_sq < alert_range_sq:
                # Scale urgency based on distance
                if dist_sq < panic_range_sq:
                    urgency = 1.0  # Maximum urgency
                else:
                    # Gradual urgency increase as predator gets closer
                    urgency = 1.0 - (dist_sq - panic_range_sq) / (alert_range_sq - panic_range_sq)
                    urgency = max(0.3, urgency)  # Minimum 30% urgency
                
                # Consider predator's heading
                predator_velocity_towards = -dot(unit(boid.velocity), unit(r))
                if predator_velocity_towards > 0.3:  # Predator moving towards us
                    urgency *= 1.5  # Increase urgency
                
                # Desired flee velocity
                if dist_sq < panic_range_sq:
                    # Panic - flee at max speed
                    desired_velocity = unit(r) * behaviours[self.species]["max-velocity"][4]
                else:
                    # Alert - flee at scaled speed
                    desired_velocity = unit(r) * behaviours[self.species]["cruising-speed"][4] * urgency
                
                # Calculate flee force
                flee_force = (desired_velocity - self.velocity) / (behaviours[self.species]["max-velocity"][4] / 2)
                flee_force *= urgency
                
                flee_vector += flee_force
                closest_threat_dist = min(closest_threat_dist, dist_sq)
        
        if ssq(flee_vector) > 1:
            return unit(flee_vector)
        return flee_vector
        
    def navigator(self, obstacles, boids=None):
        acc = np.array([0, 0], dtype=float)
        mag = 0
        
        # Priority 1: Avoid obstacles
        mag = accumulate(acc, self.avoidObstacles(obstacles))
        
        # Priority 2: FLEE from predators (high priority!)
        if mag < 1 and boids is not None:
            mag = accumulate(acc, self.flee(boids))
        
        # Priority 3: Maintain distance from flockmates
        if mag < 1:
            mag = accumulate(acc, self.keepDistance())
        
            
        # Priority 4: Cohesion with flockmates
        if mag < 1:
            mag = accumulate(acc, self.matchHeading())   
        
        # Priority 5: Align with flockmates     
        if mag < 1:
            mag = accumulate(acc, self.steerToCenter())
            
        # Priority 6: Goal seeking
        if mag < 1 and self.goal is not None:
            mag = accumulate(acc, self.gotoGoal())
        
        # Priority 7: Maintain cruising speed    
        if mag < 1:
            mag = accumulate(acc, self.maintainSpeed())
        
        acc *= behaviours[self.species]["max-acceleration"][4] * self.mass
        return acc

class Fish(Boid):
    def __init__(self, pos):
        # print(f"Creating fish at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Fish", pos=pos)
        
    #ensure fish only stays in water

        
class Elephant(Boid):
    def __init__(self, pos):
        # print(f"Creating elephant at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Elephant", pos=pos)
        self.mass = 3.0
    
    def handleTerrainType(self, terrainType, grad=None):
        if terrainType == "Water":
            # print(f"Applying wading force.")
            self.netForce += self.calculateDragForce(1.5)
            return True
        
        if terrainType == "Snow":
            # print(f"Applying wading force.")
            self.accelerationModifier = 0.8
            self.netForce += self.calculateDragForce(2)
            return False
        
        if terrainType == "Ice":
            self.accelerationModifier = 0.1
            return True
        
        if terrainType == "Sand":
            self.accelerationModifier = 0.8
            self.netForce += self.calculateDragForce(1.5)
            return False
        
        if terrainType == "Grass":
            self.netForce += self.calculateDragForce(1.5)
            return False
        
        return False

        
class Swallow(Boid):
    def __init__(self, pos):
        # print(f"Creating bird at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Swallow", pos=pos)
        self.mass = 0.5
        
    # ensure bird can fly over all terrain types, obstacles and other boids ignored
    def navigateTerrain(self, terrain):
        return
    
    def avoidObstacles(self, obstacles=None):
        return np.array([0,0], dtype=float)
    
    def updatePosition(self, terrain, dt):
        self.position += self.velocity * dt
    
    
    def computeNeighbours(self, boids):
        #override to ignore other species
        neighbours = []
        self.hasVisableNeighbours = False
        for boid in boids:
            if boid is self or boid.species != "Swallow": continue
            r = boid.position - self.position
            rxr = ssq(r)
            if rxr <= behaviours[self.species]["flockmate-range"][4]**2:
                theta = np.arccos(dot(unit(self.velocity), unit(r)))
                if theta <= np.deg2rad(behaviours[self.species]["view-angle"][4]):
                    neighbours.append(boid)
                    self.hasVisableNeighbours = True
        return neighbours       

class Fox(Boid):
    def __init__(self, pos):
        # print(f"Creating fox at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Fox", pos=pos)
        self.mass = 1.2
        self.prey = ["Sheep", "Penguin"]
        self.targetPrey = None
        
    def handleTerrainType(self, terrainType, grad=None):
        if terrainType == "Water":
            slope = magnitude(grad)
            # Apply resistance
            resistance_strength = 8
            resistance_force = -resistance_strength * self.velocity
            self.netForce += resistance_force
            self.accelerationModifier = 0.3
            return False
            
        if terrainType == "Snow":
            # print(f"Applying wading force.")
            self.netForce += self.calculateDragForce(4)
            return False
        
        if terrainType == "Ice":
            self.accelerationModifier = 0.5
            return True
        
        if terrainType == "Sand":
            self.accelerationModifier = 0.8
            self.netForce += self.calculateDragForce(6)
            return False
            
        if terrainType == "Rock":
            self.accelerationModifier = 0.7
            self.netForce += self.calculateDragForce(5)
            return False
        
        if terrainType == "Grass":
            self.netForce += self.calculateDragForce(1.5)
            return False
        
        return False

    def hunt(self, boids):
        """Improved hunting behaviour with target persistence"""
        if self.hunger < 30:
            self.targetPrey = None
            return np.array([0, 0], dtype=float)
        
        # If we already have a target, check if it's still valid
        if self.targetPrey is not None:
            if self.targetPrey.isDead:
                self.targetPrey = None
            else:
                r = self.targetPrey.position - self.position
                dist_sq = ssq(r)
                # Keep target if within extended range (don't switch easily)
                
                if dist_sq > 200**2:  # Lost the target
                    self.targetPrey = None
        
        # Find a new target if we don't have one
        if self.targetPrey is None:
            closest_prey = None
            closest_dist_sq = float('inf')
            
            for boid in boids:
                if boid.species not in self.prey or boid.isDead or boid is self:
                    continue
                
                r = boid.position - self.position
                dist_sq = ssq(r)
                
                # Check if within detection range and visible
                if dist_sq <= 200**2:
                    # Check view angle
                    if dist_sq > 0.01:  # Avoid division by zero
                        angle_cos = dot(unit(self.velocity), unit(r))
                        if angle_cos < np.cos(np.deg2rad(behaviours[self.species]["view-angle"][4])):
                            continue  # Not visible
                    
                    # Pick the closest prey
                    if dist_sq < closest_dist_sq:
                        closest_prey = boid
                        closest_dist_sq = dist_sq
            
            self.targetPrey = closest_prey
        
        # If we have a target, pursue it
        if self.targetPrey is not None:
            r = self.targetPrey.position - self.position
            dist_sq = ssq(r)
            catch_radius_sq = (behaviours[self.species]["size"]/2 + behaviours[self.targetPrey.species]["size"]/2)**2
            
            # Check if we caught the prey
            if dist_sq < catch_radius_sq:
                self.targetPrey.kill()
                self.hunger = 0
                self.targetPrey = None
                return np.array([0, 0], dtype=float)
            
            # Calculate pursuit with distance-based prediction
            dt = 8
            target_pos = self.targetPrey.position + self.targetPrey.velocity * dt
            
            desiredVelocity = target_pos - self.position
            
            if ssq(desiredVelocity) > behaviours[self.species]["max-velocity"][4]**2:
                desiredVelocity = unit(desiredVelocity) * behaviours[self.species]["max-velocity"][4]
            
            change = (desiredVelocity - self.velocity) / (behaviours[self.species]["max-velocity"][4] / 2)
            
            if ssq(change) > 1:
                return unit(change)
            return change
        
        return np.array([0, 0], dtype=float)
        
    
    def navigator(self, obstacles, boids=None):
        acc = np.array([0, 0], dtype=float)
        mag = 0
        
        #Priority 1: Avoid obstacles
        mag = accumulate(acc, self.avoidObstacles(obstacles))
        
        # Priority 5: Hunting prey
        if mag < 1 and boids is not None:
            hunt_acc = self.hunt(boids)
            if hunt_acc is not None:
                mag = accumulate(acc, hunt_acc)
        
        # priority 2: Maintain distance from flockmates
        if mag < 1:
            mag = accumulate(acc, self.keepDistance())
        
        # Priority 3: Cohesion with flockmates
        if mag < 1:
            mag = accumulate(acc, self.matchHeading())   
        
        # Priority 4: Align with flockmates     
        if mag < 1:
            mag = accumulate(acc, self.steerToCenter())
            
        
        # Priority 6: Goal seeking
        if mag < 1 and self.goal is not None:
            mag = accumulate(acc, self.gotoGoal())
        
        # Priority 7: Maintain cruising speed    
        if mag < 1:
            mag = accumulate(acc, self.maintainSpeed())
             
        
        acc *= behaviours[self.species]["max-acceleration"][4]*self.mass  # Scale by max acceleration * mass
        return acc
        
class Flamingo(Boid):
    def __init__(self, pos):
        # print(f"Creating flamingo at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Flamingo", pos=pos)
        self.mass = 1
        
    def handleTerrainType(self, terrainType, grad=None):
        if terrainType == "Water":
            # print(f"Applying wading force.")
            self.netForce += self.calculateDragForce(12)
            return True
        if terrainType == "Snow":
            # print(f"Applying wading force.")
            self.netForce += self.calculateDragForce(15)
        if terrainType == "Ice":
            self.accelerationModifier = 0.1
            return True
        if terrainType == "Sand":
            self.accelerationModifier = 0.8
            self.netForce += self.calculateDragForce(4)
        if terrainType == "Rock":
            self.accelerationModifier = 0.7
            self.netForce += self.calculateDragForce(10)
        if terrainType == "Grass":
            self.netForce += self.calculateDragForce(1.5)
        
        return False




##### FLOCK CLASS #####################################
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
                
    def computeAverageVelocity(self):
        """Compute the average velocity of the flock."""
        if len(self.members) == 0:
            return np.array([0, 0], dtype=float)
        
        avg_velocity = np.array([0, 0], dtype=float)
        for member in self.members:
            avg_velocity += member.velocity
            
        return avg_velocity / len(self.members)