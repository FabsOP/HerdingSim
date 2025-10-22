import itertools
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from boid import behaviours
import copy

import boid
import time

from vector import vectorAngle
from types import SimpleNamespace
import random
import functools

paintWindowWidth = 0
paintWindowStep = 10

borderMode = "Void"  # Options: "Die", "Wrap", "Bounce"

testMode = True


obstacles = {
    "Tree": {
        "size": 32,
        "hitbox-radius": 8,
        "hitbox-offset": [0, 4],
        "image-terrain-map": {
            "Grass": "icons/trees/Grass.png",
            "Sand": "icons/trees/Sand.png",
            "Ice": "icons/trees/Ice.png",
            "Water": "icons/trees/Water.png",
            "Snow": "icons/trees/Snow.png",
            "Rock": "icons/trees/Rock.png",
            }
        }
    , "Boulder": {
        "size": 32,
        "hitbox-radius": 16,
        "hitbox-offset": [0, 0],
        "image-terrain-map": {
            "Grass": "icons/boulders/Grass.png",
            "Sand": "icons/boulders/Sand.png",
            "Ice": "icons/boulders/Ice.png",
            "Water": "icons/boulders/Water.png",
            "Snow": "icons/boulders/Snow.png",
            "Rock": "icons/boulders/Rock.png",
            }
        
        }
    , "Bush": {
        "size": 32,
        "hitbox-radius": 8,
        "hitbox-offset": [0, 0],
        "image-terrain-map": {
            "Grass": "icons/bushes/Grass.png",
            "Sand": "icons/bushes/Sand.png",
            "Ice": "icons/bushes/Ice.png",
            "Water": "icons/bushes/Water.png",
            "Snow": "icons/bushes/Snow.png",
            "Rock": "icons/bushes/Rock.png",
            } 
        }
    
}


#Helper functions


class SimCanvas(tk.Canvas):
    def __init__(self, parent, terrain, controller, mediaController):
        self.width = terrain.width - 4 # -4 for the border
        self.height = terrain.height - 4 # -4 for the border
        
        super().__init__(parent, width=self.width,
                         height=self.height,
                         background="#B9D8B2", highlightbackground="#4C6B32",
                         relief="sunken",
                         highlightthickness=1.5
                         )
        
        self.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nsew")
        self.spawned_boids = {species: [] for species in behaviours.keys()}
        
        ### BOID OBJECT POOLS - Store all created boids here ###
        self.boid_pools = {species: [] for species in behaviours.keys()}
        
        self.obstacles = []     # [(obstacle_type, e.x, e.y, tkImage), ..]
        self.controller = controller
        self.mediaController = mediaController
        self.windowRec = None
        
        self.bgPhoto = None
        self.bgPhotoID = None
        
        self.terrain = terrain
        self.isPainting = False
        self.mouseOnCanvas = False
        
        self.waypoints = {species: None for species in behaviours.keys()}
        self.waypointImages = {"Sheep": ImageTk.PhotoImage(Image.open(f"icons/sheep_waypoint.png").resize((30, 30))),
                               "Penguin": ImageTk.PhotoImage(Image.open(f"icons/penguin_waypoint.png").resize((30, 30))),
                               "Fox": ImageTk.PhotoImage(Image.open(f"icons/fox_wp.png").resize((30, 30))),
                               "Swallow": ImageTk.PhotoImage(Image.open(f"icons/swallow_waypoint.png").resize((30,30))),
                               "Elephant": ImageTk.PhotoImage(Image.open(f"icons/elephant_waypoint.png").resize((30, 30))),
                               "Flamingo": ImageTk.PhotoImage(Image.open(f"icons/flamingo_waypoint.png").resize((30, 30)))}
        
        self.boidImages = {"Sheep": ImageTk.PhotoImage(Image.open("icons/sheep_land.png").resize((behaviours["Sheep"]["size"], behaviours["Sheep"]["size"]))),
                           "Penguin": ImageTk.PhotoImage(Image.open("icons/penguin_land.png").resize((behaviours["Penguin"]["size"], behaviours["Penguin"]["size"]))),
                           "Elephant": ImageTk.PhotoImage(Image.open("icons/elephant_land.png").resize((behaviours["Elephant"]["size"], behaviours["Elephant"]["size"]))),
                           "Fox": ImageTk.PhotoImage(Image.open("icons/fox_land.png").resize((behaviours["Fox"]["size"], behaviours["Fox"]["size"]))),
                           "Swallow": ImageTk.PhotoImage(Image.open("icons/swallow_land.png").resize((behaviours["Swallow"]["size"], behaviours["Swallow"]["size"]))),
                           "Flamingo": ImageTk.PhotoImage(Image.open("icons/flamingo_land.png").resize((behaviours["Flamingo"]["size"], behaviours["Flamingo"]["size"])))}
        
        
        self.setBgImage(terrain.contourImg)
        self.paintBucketIcon = ImageTk.PhotoImage(Image.open("icons/paint-bucket.png").resize((15, 15)))
        
        
        ### SIMULATION FRAMES 
        self.frames = []
        self.framePointer = -1
        self.numFrames = 0
        
        ### OPERATION HISTORY - Changed to accumulate operations per frame
        self.terrainHistory = []
        self.currentFrameTerrainOps = []  # Accumulate operations for current frame
        
        self.pastBorder = None
        self.pastOverlay = None
        
        
        ### EVENT BINDINGS
        self.bind("<Button-1>", self.handleClick)
        
        #handle button 1 release
        self.bind("<ButtonRelease-1>", self.handleReleaseClick)
        
        self.bind('<Motion>', self.handleHover)     
        self.bind('<Enter>', self.handleHover)  # handle <Alt>+<Tab> switches between windows
        
        self.bind('<Leave>', self.handleLeave)
        
        self.bind_all("<MouseWheel>", self.handleScrollWheel)  # Windows & macOS
        self.bind_all("<Button-4>", self.handleScrollWheel)    # Linux scroll up
        self.bind_all("<Button-5>", self.handleScrollWheel)    # Linux scroll down  
        
        #right click to place waypoint
        self.bind("<Button-3>", self.handleRightClick)

    def setBgImage(self, bgImage):
        self.bgPhoto = ImageTk.PhotoImage(bgImage)
        self.bgPhotoID = self.create_image(0, 0, anchor=tk.NW, image=self.bgPhoto)
        self.lower(self.bgPhotoID)  # Ensure the background image is at the bottom layer        
    
    def _getOrCreateBoid(self, species, state=None, pos=None):
        """Get a boid from the pool or create a new one if pool is empty"""
        pool = self.boid_pools[species]
        
        # Try to reuse an existing boid from the pool
        if pool:
            boid_obj = pool.pop()
            # Load the state into the existing boid
            if state:
                boid_obj.loadState(state)
            elif pos:
                boid_obj.position = np.array(pos, dtype=float)
        else:
            # Create a new boid if pool is empty
            if state:
                boid_obj = boid.factory(species, state=state, pos=state["position"])
            else:
                boid_obj = boid.factory(species, pos=pos)
        
        return boid_obj
    
    def _returnBoidToPool(self, species, boid_obj):
        """Return a boid to the species pool for reuse"""
        self.boid_pools[species].append(boid_obj)
    
    def _restoreBoids(self, frame_boids):
        """Restore boids from frame data using object pooling"""
        # First, return all current active boids to their pools
        for species, active_boids in self.spawned_boids.items():
            for boid_obj in active_boids:
                self._returnBoidToPool(species, boid_obj)
        
        # Clear the active boids
        self.spawned_boids = {species: [] for species in behaviours.keys()}
        
        # Restore boids from frame data
        for species, boid_states in frame_boids.items():
            for state in boid_states:
                boid_obj = self._getOrCreateBoid(species, state=state)
                self.spawned_boids[species].append(boid_obj)
                
               
    #update canvas
    def update(self, fps, ti):
        # media state
        isPaused = self.mediaController.isPaused
        mediaState = self.mediaController.state
        
        self.delete("visual_param")
        self.delete("obstacle")
        self.delete("waypoint")
        self.delete("animal")
        self.delete("past_indicator")
        # self.delete("obstacle_hitbox") 
        
        tf = time.time()
        dt = tf - ti
        dt *= self.mediaController.dtMultiplier
        
        if mediaState in ["rewind", "fast-rewind"] and not isPaused:
            self.rewind(mediaState)
        
        
        
        # Draw animals
        for species in self.spawned_boids.keys():
            for animal in self.spawned_boids[species]:
                allBoids = list(itertools.chain.from_iterable(self.spawned_boids.values()))
                
                if animal.isDead:
                    #if an animal has been killed either by a predator or other reasons, remove
                    self.spawned_boids[species].remove(animal)
                    continue
                
                if not isPaused and mediaState not in ["rewind", "fast-rewind"] and self.framePointer == self.numFrames - 1: # Update animal state only if not paused and media is running and we've restored all frames
                    animal.update(allBoids, self.terrain, self.obstacles, dt)
                    animal.setGoal(self.waypoints[species])
                    animal.handleBorder(self.controller.getBorderMode(), w=self.width, h=self.height)
                    


                self.create_image(animal.position[0], animal.position[1], image=self.boidImages[species], tags=("animal", species))
        
        # Draw waypoints
        for species, waypoint in self.waypoints.items():
            if waypoint is not None:
                self.create_image(waypoint[0], waypoint[1], image=self.waypointImages[species], tags="waypoint")
        
        # Draw obstacles
        for obstacle in self.obstacles:
            _, x, y, _, _, tkImage = obstacle
            self.create_image(x, y, image=tkImage, tags="obstacle")
            
            # # Draw hitbox circle around the obstacle
            # self.create_oval(x - hitbox_radius + hitboxOffset[0], y - hitbox_radius + hitboxOffset[1],
            #                  x + hitbox_radius + hitboxOffset[0], y + hitbox_radius + hitboxOffset[1],
            #                  fill=None, outline="#0077FF", width=2, tags="obstacle_hitbox")
            
        # Update frames
        if not isPaused and mediaState not in ["rewind", "fast-rewind"]:
            self.nextFrame(mediaState)
            
        
            
        
            
        # Visualize parameters
        if boid.lastModified:
            if tf - boid.lastModified["time"] < 10:
                self.visualizeParams()
            else:
                boid.lastModified = None
            
        
        # Raise obstacles to the top layer
        self.tag_raise("obstacle")
        self.tag_raise("waypoint")
        self.tag_raise("Swallow")
        # self.tag_raise("obstacle_hitbox")
        self.after(int(1000 / fps), lambda: self.update(fps, tf))
        
        
        # Add visual feedback for past frames
        if self.framePointer < self.numFrames - 1:
            # Semi-transparent overlay - better alignment
            self.pastOverlay = self.create_rectangle(
                0, 0,  # Start just inside the border
                self.width+4, self.height+4,  # End just inside the border
                fill="gray", 
                stipple="gray25",  # Much lighter than gray50
                outline="",  # Remove any outline
                tags="past_indicator"
            )
            
            # Make sure the overlay is visible by raising it
            self.tag_raise("past_indicator")
        
            
        
        

    def nextFrame(self, mediaState):
        """Optimized nextFrame with accumulated terrain operations"""
        
        #### If we're still in the past, restore past frames
        if self.framePointer != self.numFrames - 1:
            self.framePointer = min(self.numFrames - 1, self.framePointer + self.mediaController.dtMultiplier)
            # print(f"Restoring... (Frame {self.framePointer +1}/{self.numFrames})")
            
            frame = self.frames[self.framePointer]
            boids = frame["boids"]
            obstacles = frame["obstacles"]
            waypoints = frame["waypoints"]
            
            # load terrain history: apply operations based on media state
            ops_to_apply = []
            if mediaState == "running":
                if self.framePointer < len(self.terrainHistory):
                    ops_to_apply = self.terrainHistory[self.framePointer]
                
            elif mediaState == "forward":
                # Apply operations from previous frame and current frame
                if self.framePointer - 1 >= 0 and self.framePointer - 1 < len(self.terrainHistory):
                    ops_to_apply.extend(self.terrainHistory[self.framePointer - 1])
                if self.framePointer < len(self.terrainHistory):
                    ops_to_apply.extend(self.terrainHistory[self.framePointer])
                
            elif mediaState == "fast-forward":
                # Apply operations from last 4 frames
                for i in range(max(0, self.framePointer - 3), self.framePointer + 1):
                    if i < len(self.terrainHistory):
                        ops_to_apply.extend(self.terrainHistory[i])
            
            # Apply all terrain operations (forward operations)
            for op_pair in ops_to_apply:
                if op_pair and len(op_pair) >= 2 and op_pair[1] is not None:
                    op_pair[1]()  # Apply forward operation
                    
            self.setBgImage(self.terrain.contourImg)
            
            # Use object pooling instead of creating new boids
            self._restoreBoids(boids)
            
            self.obstacles = obstacles
            
            self.waypoints = waypoints
            
            # Stop fast forwarding if we reach present
            if self.framePointer == self.numFrames - 1:
                if mediaState == "forward":
                    self.mediaController.fastForward2x()  
                elif mediaState == "fast-forward":
                    self.mediaController.fastForward4x()
            
            return
        
        ### Otherwise, we're in the present so save current state of simulation
        #print(f"Saving frame {self.framePointer}")
        
        frame = {"boids": None, "obstacles": None, "waypoints": None}
        
        # Save boids
        frame["boids"] = {species: [animal.getState() for animal in animals] for species, animals in self.spawned_boids.items()}
        
        # Save obstacles
        frame["obstacles"] = self.obstacles.copy()
        
        # Save waypoints
        frame["waypoints"] = self.waypoints.copy()
        
        # Save accumulated terrain operations for this frame
        self.terrainHistory.append(self.currentFrameTerrainOps.copy())
        self.currentFrameTerrainOps.clear()  # Clear for next frame
        
        # Append frame
        self.frames.append(frame)
        
        self.numFrames = len(self.frames)
        self.framePointer += 1
    
    def discardFuture(self):
        """
        Discards the future frames after the current framepointer
        """
    
        if self.mediaController.state in ["rewind", "fast-rewind"]:
            return
            
        
        print("Discarding future")
        self.frames = self.frames[:self.framePointer+1]
        self.numFrames = len(self.frames)
        
        self.terrainHistory = self.terrainHistory[:self.framePointer+1]
        
        print("Total frames:", self.numFrames)
        print("Frame pointer:", self.framePointer)
        
    def rewind(self, rewindType):
        """Optimized rewind with accumulated terrain operations"""
        
        if rewindType == "rewind":
            self.framePointer = max(0, self.framePointer-1)
            # Apply backward operations from the frame we're leaving
            if self.framePointer + 1 < len(self.terrainHistory):
                ops_to_apply = self.terrainHistory[self.framePointer + 1]
                for op_pair in reversed(ops_to_apply):  # Apply in reverse order
                    if op_pair and len(op_pair) >= 1 and op_pair[0] is not None:
                        op_pair[0]()  # Apply backward operation
        else:
            # Fast rewind: go back 4 frames
            old_frame_pointer = self.framePointer
            self.framePointer = max(0, self.framePointer-4)
            
            # Apply backward operations from all frames we're leaving
            for frame_idx in range(old_frame_pointer, self.framePointer, -1):
                if frame_idx < len(self.terrainHistory):
                    ops_to_apply = self.terrainHistory[frame_idx]
                    for op_pair in reversed(ops_to_apply):  # Apply in reverse order
                        if op_pair and len(op_pair) >= 1 and op_pair[0] is not None:
                            op_pair[0]()  # Apply backward operation

        frame = self.frames[self.framePointer]
        boids = frame["boids"]
        obstacles = frame.get("obstacles", [])
        waypoints = frame.get("waypoints", [])
        
        self.waypoints = waypoints.copy()
        self.obstacles = obstacles.copy()
        self._restoreBoids(boids)
                    
        self.setBgImage(self.terrain.contourImg)
        
        if self.framePointer == 0:
            mediaState = self.mediaController.state
            isPaused = self.mediaController.isPaused

            if mediaState in ["rewind", "fast-rewind"] and not isPaused:
                self.mediaController.pausePlay()
                if mediaState == "rewind":
                    self.mediaController.rewind()
                else:
                    self.mediaController.fastRewind()
                self.mediaController.freezeRewind()

    def visualizeParams(self):
        if not testMode: 
            print("Activate test mode to visualise params")
        else:
            
            # print(boid.lastModified)
            if not boid.lastModified: return
            
            
            #radial vizualizations
            if boid.lastModified["parameter"] in ["comfort-zone", "danger-zone"]:
                for animal in self.spawned_boids[boid.lastModified["species"]][:5]:
                    if animal.species != boid.lastModified["species"]: continue
                    radius = behaviours[boid.lastModified["species"]].get(boid.lastModified["parameter"],None)
                    if radius:
                        self.create_oval(animal.position[0]-radius[4]//1, animal.position[1]-radius[4]//1 ,animal.position[0]+radius[4]//1, animal.position[1]+radius[4]//1, fill=None, outline="#C1E1C1", width=2, tags="visual_param")
            
            #angle vizualizations
            if boid.lastModified["parameter"] in ["obstacle-range", "flockmate-range", "view-angle"]:
                for animal in self.spawned_boids[boid.lastModified["species"]][:5]:
                    if animal.species != boid.lastModified["species"]: continue
                    
                    arcRadius = behaviours[boid.lastModified["species"]].get(boid.lastModified["parameter"],None)
                    
                    if boid.lastModified["parameter"] == "view-angle":
                        arcRadius = behaviours[boid.lastModified["species"]].get("flockmate-range",None)
                    
                    viewAngle = behaviours[boid.lastModified["species"]].get("view-angle", None)
                    if arcRadius and viewAngle:
                        centerTheta = vectorAngle([animal.velocity[0], -animal.velocity[1]])
                        startTheta = (centerTheta - viewAngle[4]) % 360
                        
                        
                        #draw arc
                        if boid.lastModified["parameter"] == "obstacle-range":
                            arcColour = "#C1E1C1"
                        elif boid.lastModified["parameter"] == "flockmate-range":
                            arcColour = "red" if animal.hasVisableNeighbours else "#C1E1C1"
                        elif boid.lastModified["parameter"] == "view-angle":
                            arcColour = "#C1E1C1"
                            
                        self.create_arc(animal.position[0]-arcRadius[4], animal.position[1]-arcRadius[4],
                                        animal.position[0]+arcRadius[4], animal.position[1]+arcRadius[4],
                                        start=startTheta, extent= 2*viewAngle[4], fill=None, outline=arcColour, width=2, tags="visual_param")
   
    def fill_paint_window(self, e, terrain_type):
        # Get proper width and height
        width, height = self.terrain.contourImg.size
        
        if self.controller.get_brush_shape() == "Square":
            half_width = paintWindowWidth // 2
            
            # Calculate the intended brush area (can be negative or exceed bounds)
            brush_x_start = e.x - half_width
            brush_x_end = e.x + half_width
            brush_y_start = e.y - half_width
            brush_y_end = e.y + half_width
            
            # Clip to canvas boundaries
            x_start = max(0, brush_x_start)
            x_end = min(width, brush_x_end)
            y_start = max(0, brush_y_start)
            y_end = min(height, brush_y_end)
            
            # Create mask with correct dimensions
            mask = np.zeros((height, width), dtype=bool)
            
            # Only fill the valid region
            if x_end > x_start and y_end > y_start:
                mask[y_start:y_end, x_start:x_end] = True
                
        else:  # Circle brush - OPTIMIZED with NumPy vectorization
            radius = paintWindowWidth // 2
            
            # Calculate bounding box
            x_min = max(0, e.x - radius)
            x_max = min(width, e.x + radius)
            y_min = max(0, e.y - radius)
            y_max = min(height, e.y + radius)
            
            # Create coordinate grids for the bounding box
            y_coords, x_coords = np.ogrid[y_min:y_max, x_min:x_max]
            
            # Vectorized distance calculation
            distances_sq = (x_coords - e.x) ** 2 + (y_coords - e.y) ** 2
            circle_mask = distances_sq <= radius ** 2
            
            # Create full mask and insert the circle
            mask = np.zeros((height, width), dtype=bool)
            mask[y_min:y_max, x_min:x_max] = circle_mask
        
        mask_copy = np.copy(mask)
        typegrid = np.copy(self.terrain.typegrid)
        backward = functools.partial(self.terrain.overwriteRegion, mask_copy, typegrid)
        
        forward = functools.partial(self.terrain.color_region, mask, terrain_type)
        forward()
        self.setBgImage(self.terrain.contourImg)
                            
        self.currentFrameTerrainOps.append((backward, forward))
        
    def color_contour(self, e, terrain_type):
        # Reverse operation
        typeBefore = self.terrain.typeAt(e.x, e.y)
        
        if typeBefore == terrain_type:
            return  # No change needed
        
        backward = functools.partial(self.terrain.contourFill, e.x, e.y, typeBefore)
        
        forward = functools.partial(self.terrain.contourFill, e.x, e.y, terrain_type)
        forward()
        self.setBgImage(self.terrain.contourImg) # Update the background image to reflect the changes
        
        # Add operations to current frame accumulator instead of overwriting
        self.currentFrameTerrainOps.append((backward, forward))
        
                    
    # event handlers
    def handleClick(self, e):
        # we can't interact with the canvas during rewinding
        if self.mediaController.state in ["rewind", "fast-rewind"]:
            return
        
        ### ANIMAL SPAWNING 
        if self.controller.get_selected_animal() is not None:
            self.discardFuture()
            pos = (e.x,e.y)
            selectedSpecies = self.controller.get_selected_animal()
            print(f"Spawning {selectedSpecies} at: ({pos[0]}, {pos[1]})")
            
            for i in range(self.controller.get_spawn_size()):
                # spawn boid using object pooling
                offsetPos = [random.choice([pos[0]-i*5, pos[0]+i*5]), random.choice([pos[1]-i*5, pos[1]+i*5])]
                animal = self._getOrCreateBoid(species=selectedSpecies, pos=offsetPos)
                self.spawned_boids[selectedSpecies].append(animal)
            

                    
        ### TERRAIN AND OBSTACLE PAINTING            
        elif self.controller.get_selected_terrain() is not None:
            self.discardFuture()
            terrain = self.controller.get_selected_terrain()
            print(f"Painting {terrain} at: ({e.x}, {e.y})")
            self.isPainting = True
            print("isPainting:", self.isPainting)
            
            # a) IF AN OBSTACLE IS SELECTED
            if terrain in ["Tree", "Boulder", "Bush"]:
                size = obstacles[terrain]["size"]         
                terrainType = self.terrain.typeAt(e.x, e.y)
                imagePath = obstacles[terrain]["image-terrain-map"][terrainType]
                image = Image.open(imagePath).resize((size, size))
                
                tkImage = ImageTk.PhotoImage(image)
                hitboxRadius = obstacles[terrain]["hitbox-radius"]
                hitboxOffset = obstacles[terrain]["hitbox-offset"]
                self.obstacles.append((terrain, e.x, e.y, hitboxRadius,hitboxOffset, tkImage))
                
            elif terrain in ["Eraser"]:
                # remove obstacle or boid if clicked on one i.e window width is 0
                if paintWindowWidth == 0:
                    #find obstacle at click position
                    for obstacle in self.obstacles:
                        obstacle_type, x, y, _, _, _ = obstacle
                        size = obstacles[obstacle_type]["size"]
                        half_size = size // 2
                        if (e.x >= x - half_size and e.x <= x + half_size and
                            e.y >= y - half_size and e.y <= y + half_size):
                            self.obstacles.remove(obstacle)
                            break
                    
                    for boid in itertools.chain.from_iterable(self.spawned_boids.values()):
                        boid_size = behaviours[boid.species]["size"]
                        half_size = boid_size // 2
                        if (e.x >= boid.position[0] - half_size and e.x <= boid.position[0] + half_size and
                            e.y >= boid.position[1] - half_size and e.y <= boid.position[1] + half_size):
                            boid.kill()
                            break
                
                # else if window width is bigger remove all obstacles in the paint window
                else:
                    #loop through all obstacles and boids
                    obstacles_to_remove = []
                    boids_to_remove = []
                    
                    for obstacle in self.obstacles:
                        obstacle_type, x, y, _, _, _ = obstacle
                        size = obstacles[obstacle_type]["size"]
                        half_size = size // 2
                        
                        #check if obstacle is in paint window
                        if self.controller.get_brush_shape() == "Square":
                            half_width = paintWindowWidth // 2
                            if (x + half_size >= e.x - half_width and x - half_size <= e.x + half_width and
                                y + half_size >= e.y - half_width and y - half_size <= e.y + half_width):
                                obstacles_to_remove.append(obstacle)
                        else:  # Circle brush
                            radius = paintWindowWidth // 2
                            if (x - e.x) ** 2 + (y - e.y) ** 2 <= radius ** 2:
                                obstacles_to_remove.append(obstacle)
                                
                    for _, boids in self.spawned_boids.items():
                        for boid in boids:
                            if self.controller.get_brush_shape() == "Square":
                                half_width = paintWindowWidth // 2
                                if (boid.position[0] >= e.x - half_width and boid.position[0] <= e.x + half_width and
                                    boid.position[1] >= e.y - half_width and boid.position[1] <= e.y + half_width):
                                    boids_to_remove.append(boid)
                            else:  # Circle brush
                                radius = paintWindowWidth // 2
                                if (boid.position[0] - e.x) ** 2 + (boid.position[1] - e.y) ** 2 <= radius ** 2:
                                    boids_to_remove.append(boid)
                    
                    for obs in obstacles_to_remove:
                        self.obstacles.remove(obs)
                        
                    for boid in boids_to_remove:
                        boid.kill()

                
                    
                    
            # b) OTHERWISE IF A TERRAIN TYPE IS SELECTED        
            else:
                #paint contour
                if paintWindowWidth == 0:
                    self.color_contour(e, terrain)
                else:
                    #loop through all pixels in the paint window circle
                    self.fill_paint_window(e, terrain)
        
        
                    
    def handleHover(self, e):
        # print(f"Type at ({e.x} {e.y}): {self.terrain.typeAt(e.x, e.y)}")
        # print(f"Height at ({e.x} {e.y}): {self.terrain.heightAt(e.x, e.y)}")
        
        self.mouseOnCanvas = True
        
        if self.controller.get_selected_animal() != None or self.controller.get_selected_terrain() in ["Tree", "Boulder", "Bush"]:
            self.config(cursor="hand2")
        
        elif self.controller.get_selected_terrain() not in ["Tree", "Boulder", "Bush", "Eraser", None]:
            self.config(cursor="none")
            #delete previous window
            self.delete(self.windowRec)
            
            brush_shape = self.controller.get_brush_shape()
        
            if self.isPainting and paintWindowWidth > 0:
                self.fill_paint_window(e, self.controller.get_selected_terrain())
                if brush_shape == "Square":
                    self.windowRec = self.create_rectangle(e.x - paintWindowWidth//2, e.y - paintWindowWidth//2, e.x + paintWindowWidth//2, e.y + paintWindowWidth//2, fill=None, outline="#FF0000", width=5)
                else:
                    self.windowRec = self.create_oval(e.x-paintWindowWidth//2, e.y-paintWindowWidth//2 , e.x+paintWindowWidth//2, e.y+paintWindowWidth//2, fill=None, outline="#FF0000", width=5 )
            else:
                if paintWindowWidth == 0:
                    self.delete("paint_bucket")
                    self.create_image(e.x, e.y, image=self.paintBucketIcon, tags="paint_bucket")
                else:
                    self.delete("paint_bucket")
                    if brush_shape == "Square":
                        self.windowRec = self.create_rectangle(e.x - paintWindowWidth//2, e.y - paintWindowWidth//2, e.x + paintWindowWidth//2, e.y + paintWindowWidth//2, fill=None, outline="#C1E1C1", width=5)
                    else:
                        self.windowRec = self.create_oval(e.x-paintWindowWidth//2, e.y-paintWindowWidth//2 , e.x+paintWindowWidth//2, e.y+paintWindowWidth//2, fill=None, outline="#C1E1C1", width=5 )
        
        elif self.controller.get_selected_terrain() == "Eraser":
            self.config(cursor="none")
            #delete previous window
            self.delete(self.windowRec)
            
            #draw new window
            if paintWindowWidth == 0:
                self.delete("paint_bucket")
                self.configure(cursor="X_cursor")
            else:
                self.delete("paint_bucket")
                if self.controller.get_brush_shape() == "Square":
                    self.windowRec = self.create_rectangle(e.x - paintWindowWidth//2, e.y - paintWindowWidth//2, e.x + paintWindowWidth//2, e.y + paintWindowWidth//2, fill=None, outline="#C1E1C1", width=5)
                else:
                    self.windowRec = self.create_oval(e.x-paintWindowWidth//2, e.y-paintWindowWidth//2 , e.x+paintWindowWidth//2, e.y+paintWindowWidth//2, fill=None, outline="#C1E1C1", width=5 )
                if self.isPainting:
                    #loop through all obstacles and boids
                    obstacles_to_remove = []
                    boids_to_remove = []
                    for obstacle in self.obstacles:
                        obstacle_type, x, y, _, _, _ = obstacle
                        size = obstacles[obstacle_type]["size"]
                        half_size = size // 2
                        
                        #check if obstacle is in paint window
                        if self.controller.get_brush_shape() == "Square":
                            half_width = paintWindowWidth // 2
                            if (x + half_size >= e.x - half_width and x - half_size <= e.x + half_width and
                                y + half_size >= e.y - half_width and y - half_size <= e.y + half_width):
                                obstacles_to_remove.append(obstacle)
                        else:  # Circle brush
                            radius = paintWindowWidth // 2
                            if (x - e.x) ** 2 + (y - e.y) ** 2 <= radius ** 2:
                                obstacles_to_remove.append(obstacle)
                    
                    #check for boids in paint window
                    for _, boids in self.spawned_boids.items():
                        for boid in boids:
                            if self.controller.get_brush_shape() == "Square":
                                half_width = paintWindowWidth // 2
                                if (boid.position[0] >= e.x - half_width and boid.position[0] <= e.x + half_width and
                                    boid.position[1] >= e.y - half_width and boid.position[1] <= e.y + half_width):
                                    boids_to_remove.append(boid)
                            else:  # Circle brush
                                radius = paintWindowWidth // 2
                                if (boid.position[0] - e.x) ** 2 + (boid.position[1] - e.y) ** 2 <= radius ** 2:
                                    boids_to_remove.append(boid)
                    
                    for obs in obstacles_to_remove:
                        self.obstacles.remove(obs)
                        
                    for boid in boids_to_remove:
                        boid.kill()
                
        
        else:
            self.config(cursor="arrow")
     
    def handleLeave(self,_):
        self.mouseOnCanvas = False
        self.delete(self.windowRec)
        self.delete("paint_bucket")
            
    def handleScrollWheel(self, e):
        global paintWindowWidth
        
        if self.controller.get_selected_terrain() in ["Rock", "Sand", "Water", "Ice", "Snow", "Grass", "Eraser"]:
            if e.num == 4 or e.delta > 0:
                self.delete("paint_bucket")
                print(f"Increasing brush size: {paintWindowWidth}")
                paintWindowWidth = min(200, paintWindowWidth+ paintWindowStep)
            elif e.num == 5 or e.delta < 0:
                print("Scrolled down")
                print(f"decreasing brush size: {paintWindowWidth}")
                paintWindowWidth = max(0, paintWindowWidth - paintWindowStep)
            
            #delete previous window    
            self.delete(self.windowRec)
            
            #draw new window
            if self.mouseOnCanvas and paintWindowWidth > 0:
                self.config(cursor="none")
                if self.controller.get_brush_shape() == "Square":
                    self.windowRec = self.create_rectangle(e.x - paintWindowWidth//2, e.y - paintWindowWidth//2, e.x + paintWindowWidth//2, e.y + paintWindowWidth//2, fill=None, outline="#C1E1C1", width=5)
                else:
                    self.windowRec = self.create_oval(e.x-paintWindowWidth//2, e.y-paintWindowWidth//2 , e.x+paintWindowWidth//2, e.y+paintWindowWidth//2, fill=None, outline="#C1E1C1", width=5 )
            elif self.mouseOnCanvas and paintWindowWidth == 0:
                self.delete("paint_bucket")
                if self.controller.get_selected_terrain() != "Eraser":
                    self.create_image(e.x, e.y, image=self.paintBucketIcon, tags="paint_bucket")
                else:
                    self.config(cursor="X_cursor")
            
    def handleRightClick(self,e):
        # we can't interact with the canvas during rewinding
        if self.mediaController.state in ["rewind", "fast-rewind"]:
            return
        
        self.discardFuture()
        
        #right click to place waypoint
        selectedSpecies = self.controller.get_selected_animal()
        
        selectedTerrain = self.controller.get_selected_terrain()
        
        if selectedSpecies:
            
            if self.waypoints[selectedSpecies] is not None:
                self.waypoints[selectedSpecies] = None
                return
            
            #set waypoint for selected animal
            pos = (e.x,e.y)
            print(f"Placing waypoint for {selectedSpecies} at: ({pos[0]}, {pos[1]})")
            self.waypoints[selectedSpecies] = np.array(pos, dtype=float)

            
            
        if not selectedSpecies and not selectedTerrain: #if no animal or terrain is selected
            #remove all waypoints
            for species in self.waypoints.keys():
                self.waypoints[species] = None
            
        
            
    def handleReleaseClick(self, e):
        #print(f"Mouse released at ({e.x}, {e.y})")
        self.isPainting = False
        print("Mouse released")
        print("isPainting:", self.isPainting)