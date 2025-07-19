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
        "max-velocity": [1, 100, 1, int, 15],
        "cruising-speed": [1,10,1,int,15], #[0,max-velocity,_,_]
        "comfort-zone": [16, 100,1,int,14], #[size, inf,_,_]
        "danger-zone": [16,40,1,int,9], #[size, comfort,_,_]
        "obstacle-range": [16,100,1,int,40], #[size, inf,_,_]
        "flockmate-range": [40,200,1,int,40], #[comfort, inf]
        "view-angle": [1, 180,1,int,90],
        "drag-factor": [0, 55, 1, int, 4]
    },
    "Elephant": {
        "size": 20,
        "herd-size": [1,20, 1, int, 6],
        "max-acceleration": [1, 100, 1, int, 10],
        "max-velocity": [1, 100, 1, int, 3],
        "cruising-speed": [1,10,1,int,3], #[0,max-velocity,_,_]
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
        "obstacle-range": [16,100,1,int,32], #[size, inf,_,_]
        "flockmate-range": [40,200,1,int,40], #[comfort, inf]
        "view-angle": [1, 180,1,int,90],
        "drag-factor": [0, 55, 1, int, 7]
    },
    "Penguin": {
        "size": 8,
        "herd-size": [1,100, 1, int, 100],
        "max-acceleration": [1, 100, 1, int, 30],
        "max-velocity": [1, 100, 1, int, 25],
        "cruising-speed": [0,4,1,int,11], #[0,max-velocity,_,_]
        "comfort-zone": [32, 100,1,int,14], #[size, inf,_,_]
        "danger-zone": [32,40,1,int,9], #[size, comfort,_,_]
        "obstacle-range": [32,100,1,int,32], #[size, inf,_,_]
        "flockmate-range": [40,100,1,int,40], #[comfort, inf]
        "view-angle": [1, 180,1,int,90],
        "drag-factor": [0, 55, 1, int, 10],
    },
    "Bunny": {
        "size": 12,
        "herd-size": [1,30, 1, int, 20],
        "max-acceleration": [1, 100, 1, int, 30],
        "max-velocity": [1, 100, 1, int, 15],
        "cruising-speed": [1,10,1,int,0], #[0,max-velocity,_,_]
        "comfort-zone": [16, 100,1,int,14], #[size, inf,_,_]
        "danger-zone": [16,40,1,int,9], #[size, comfort,_,_]
        "obstacle-range": [16,100,1,int,32], #[size, inf,_,_]
        "flockmate-range": [40,200,1,int,40], #[comfort, inf]
        "view-angle": [1, 180,1,int,90],
        "drag-factor": [0, 55, 1, int, 30],
    },
    "Fish": {
        "size": 12,
        "herd-size": [1,30, 1, int, 20],
        "max-acceleration": [1, 100, 1, int, 30],
        "max-velocity": [1, 100, 1, int, 15],
        "cruising-speed": [1,10,1,int,0], #[0,max-velocity,_,_]
        "comfort-zone": [16, 100,1,int,14], #[size, inf,_,_]
        "danger-zone": [16,40,1,int,9], #[size, comfort,_,_]
        "obstacle-range": [16,100,1,int,32], #[size, inf,_,_]
        "flockmate-range": [40,200,1,int,40], #[comfort, inf]
        "view-angle": [1, 180,1,int,90],
        "drag-factor": [0, 55, 1, int, 30],
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
    elif species == "Bunny":
        bunny = behaviours["Bunny"]
        bunny["max-velocity"][0] = bunny["cruising-speed"][4]
        bunny["cruising-speed"][1] = bunny["max-velocity"][4]
        bunny["comfort-zone"][0] = bunny["size"] + 1
        bunny["danger-zone"][0] = bunny["size"]
        bunny["danger-zone"][1] = bunny["comfort-zone"][4] -1
        bunny["flockmate-range"][0] = bunny["comfort-zone"][4]
        bunny["obstacle-range"][0] = bunny["size"]
    elif species == "Fish":
        fish = behaviours["Fish"]
        fish["max-velocity"][0] = fish["cruising-speed"][4]
        fish["cruising-speed"][1] = fish["max-velocity"][4]
        fish["comfort-zone"][0] = fish["size"] + 1
        fish["danger-zone"][0] = fish["size"]
        fish["danger-zone"][1] = fish["comfort-zone"][4] -1
        fish["flockmate-range"][0] = fish["comfort-zone"][4]
        fish["obstacle-range"][0] = fish["size"]
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
        

    def update(self, boids, terrain, obstacles, dt):
        self.neighbours = self.computeNeighbours(boids)
        for neighbour in self.neighbours:
            if self.mergeFlock(neighbour):      #break if flock is merged
                break
            
        self.flockNeighbours = self.computeNeighbours(self.flock.members)
        
        #if no flockNeighbours, leave flock
        if len(self.flockNeighbours) == 0:
            self.leaveFlock()
        
        #flocking behaviours
        self.updateBehaviours(obstacles)    
        self.updateAcceleration()
        
        #terrain navigation behaviour
        self.navigateTerrain(terrain)
        self.updateAcceleration()
        
        self.updateVelocity(dt)
        self.updatePosition(terrain, dt)
    
    def updateBehaviours(self, obstacles=None):
        """Update the boid's behaviours based on its current state."""
        self.netForce = self.navigator(obstacles)
        
    def navigator(self, obstacles):
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
    
    def updatePosition(self,terrain, dt):
        gradVelocityComponent = dot(unit(self.velocity), terrain.gradientField[int(self.position[1])][int(self.position[0])])
        slopeCorrectionFactor = 1/np.sqrt(gradVelocityComponent**2 +1)
        self.position += slopeCorrectionFactor*self.velocity*dt
    
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

    def leaveFlock(self):
        self.flock.remove_member(self)
        self.flock = Flock(species=self.species, members=[self])
    
    ### NAVIGATOR FUNCTIONS ##########################################    
    def maintainSpeed(self):
        current_speed = magnitude(self.velocity)
        target_speed = behaviours[self.species]["cruising-speed"][4]
        
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
        grad = terrain.gradientField[int(self.position[1])][int(self.position[0])]
        # print(f"grad at ({self.position[0]}{self.position[1]}):", grad)
        slope = magnitude(grad)
        terrainType = terrain.typeAt(self.position[0], self.position[1])
        
        F = np.array([0,0], dtype=float)
        
        if self.handleTerrainType(terrainType, grad):
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
        
    def handleTerrainType(self, terrainType,grad):
        if terrainType == "Water":
            streamStrength = 30
            streamForce = streamStrength * unit(grad)
            self.netForce += streamForce
            return True
        
        return False
            

class Penguin(Boid):
    def __init__(self, pos):
        # print(f"Creating penguin at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Penguin", pos=pos)
        self.mass = 1
        
    def handleTerrainType(self, terrainType, grad=None):
        if terrainType == "Water":
            # print(f"Applying swimming force.")
            swimming_strength = 5
            swimming_force = swimming_strength * unit(self.velocity)
            self.netForce += swimming_force
            return True
        elif terrainType == "Ice":
            print(f"Applying sliding force.")
            sliding_strength = 1
            sliding_force = sliding_strength * unit(self.velocity)
            self.netForce += sliding_force
            return True
        
        return False

class Fish(Boid):
    def __init__(self, pos):
        # print(f"Creating fish at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Fish", pos=pos)
        
    #ensure fish only stays in water

        
class Elephant(Boid):
    def __init__(self, pos):
        # print(f"Creating elephant at position: ({pos[0]},{pos[1]})")
        super().__init__(species="Elephant", pos=pos)
        self.mass = 2.0





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