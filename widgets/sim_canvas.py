import itertools
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from boid import behaviours

import boid
import time

from vector import vectorAngle

import random

paintWindowWidth = 55
paintWindowStep = 5

borderMode = "Bounce"

testMode = True


obstacles = {
    "Tree": {
        "size": 32
        }
    , "Stone": {
        "size": 32
        }
    , "Tall Grass": {
        "size": 32
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
        self.obstacles = []
        self.controller = controller
        self.mediaController = mediaController
        self.windowRec = None
        
        self.bgPhoto = None
        self.bgPhotoID = None
        
        self.terrain = terrain
        self.waypoints = {species: None for species in behaviours.keys()}
        self.waypointImages = {"Sheep": ImageTk.PhotoImage(Image.open(f"icons/sheep_waypoint.png").resize((30, 30)))}
        
        if terrain.contourImg is not None:
            self.setBgImage(terrain.contourImg)
        

        ### EVENT BINDINGS
        self.bind("<Button-1>", self.handleClick)
        
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
    
    def clear_canvas(self,excl=None):
        if excl is None:
            self.delete("all")
            
        all_items = self.find_all()
        for item in all_items:
            if item not in excl:
                self.delete(item)
        
    
    #update canvas
    def update(self, fps,ti):
        self.delete("visual_param")
        
        tf = time.time()
        dt = tf-ti
        dt *= self.mediaController.dtMultiplier
        
        #draw animals
        for species in self.spawned_boids.keys():
            for animal in self.spawned_boids[species]:
                self.visualizeParams()               
                if not self.mediaController.isPaused:
                    allBoids = list(itertools.chain.from_iterable(self.spawned_boids.values()))  # Flatten the list of boids
                    animal.update(allBoids, self.terrain, dt)
                    animal.setGoal(self.waypoints[species])
                    animal.handleBorder(borderMode,w=self.width,h=self.height)
                self.coords(animal.canvasId, animal.position[0], animal.position[1])
        
        
        self.after(int(1000/fps), lambda: self.update(fps, tf))

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
                    
    # event handlers
    def handleClick(self, e):
        if self.controller.get_selected_animal() is not None:
            pos = (e.x,e.y)
            selectedSpecies = self.controller.get_selected_animal()
            print(f"Spawning {selectedSpecies} at: ({pos[0]}, {pos[1]})")
            
            for i in range(self.controller.get_spawn_size()):
                # spawn boid
                offsetPos = [random.choice([pos[0]-i*5, pos[0]+i*5]), random.choice([pos[1]-i*5, pos[1]+i*5])]
                animal = boid.factory(species=selectedSpecies, pos= offsetPos)
                animal.loadImage(f"icons/{selectedSpecies.lower()}_land.png")
                image = animal.tkImage
                if image:
                    # draw image
                    animal.canvasId = self.create_image(e.x, e.y, image=image)

                    # add to boid list
                    self.spawned_boids[selectedSpecies].append(animal)
                else: 
                    print("Failed to draw")
        elif self.controller.get_selected_terrain() is not None:
            terrain = self.controller.get_selected_terrain()
            print(f"Painting {terrain} at: ({e.x}, {e.y})")
            
            # #paint terrain
            #draw placeable terrain
            if terrain in ["Tree", "Stone"]:
                size = obstacles[terrain]["size"]         
                
                image = Image.open(f"./icons/{terrain.lower()}.png").resize((size, size))
                tkImage = ImageTk.PhotoImage(image)
                self.obstacles.append((terrain, e.x, e.y, tkImage))
                if image:
                    # draw image
                    self.create_image(e.x, e.y, image=tkImage)
            
            if terrain in ["Tall Grass"]:
                size = obstacles[terrain]["size"]         
                
                image = Image.open(f"./icons/tallGrass.png").resize((size, size)).convert("RGBA")
                # Set alpha to 80% (204 out of 255)
                alpha = image.split()[3].point(lambda p: int(p * 0.8))
                image.putalpha(alpha)
                tkImage = ImageTk.PhotoImage(image)
                self.obstacles.append((terrain, e.x, e.y, tkImage))
                if image:
                    # draw image at the top of the z-index
                    self.create_image(e.x, e.y, image=tkImage, tags="tall_grass")
                    self.tag_raise("tall_grass")
                    
            
   
    def handleHover(self, e):
        # print(f"Mouse coordinates ({e.x} {e.y})")
        
        if self.controller.get_selected_animal() != None:
            self.config(cursor="hand2")
        
        elif self.controller.get_selected_terrain() != None:
            self.config(cursor="none")
            #delete previous window
            self.delete(self.windowRec)
            
            #draw new window
            self.windowRec = self.create_rectangle(e.x - paintWindowWidth//2, e.y - paintWindowWidth//2, e.x + paintWindowWidth//2, e.y + paintWindowWidth//2, fill=None, outline="#C1E1C1", width=5)
            #self.windowRec = self.create_oval(e.x-paintWindowWidth//2, e.y-paintWindowWidth//2 , e.x+paintWindowWidth//2, e.y+paintWindowWidth//2, fill=None, outline="#C1E1C1", width=5 )
        else:
            self.config(cursor="arrow")
     
    def handleLeave(self,_):
        self.delete(self.windowRec)
            
    def handleScrollWheel(self, e):
        global paintWindowWidth
        
        if self.controller.get_selected_terrain() != None:
            if e.num == 4 or e.delta > 0:
                print(f"Increasing brush size: {paintWindowWidth}")
                paintWindowWidth = min(150, paintWindowWidth+ paintWindowStep)
            elif e.num == 5 or e.delta < 0:
                print("Scrolled down")
                print(f"decreasing brush size: {paintWindowWidth}")
                paintWindowWidth = max(0, paintWindowWidth - paintWindowStep)
            
            #delete previous window    
            self.delete(self.windowRec)
            
            #draw new window
            self.windowRec = self.create_rectangle(e.x - paintWindowWidth//2, e.y - paintWindowWidth//2, e.x + paintWindowWidth//2, e.y + paintWindowWidth//2, fill=None, outline="#C1E1C1", width=5)
            # self.windowRec = self.create_oval(e.x-paintWindowWidth//2, e.y-paintWindowWidth//2 , e.x+paintWindowWidth//2, e.y+paintWindowWidth//2, fill=None, outline="#C1E1C1", width=5 )
            
    def handleRightClick(self,e):
        #right click to place waypoint
        selectedSpecies = self.controller.get_selected_animal()
        
        if selectedSpecies:
            
            if self.waypoints[selectedSpecies] is not None:
                self.waypoints[selectedSpecies] = None
                self.delete("waypoint")
                return
            
            #set waypoint for selected animal
            pos = (e.x,e.y)
            print(f"Placing waypoint for {selectedSpecies} at: ({pos[0]}, {pos[1]})")
            self.waypoints[selectedSpecies] = np.array(pos, dtype=float)
            self.create_image(pos[0], pos[1], image=self.waypointImages[selectedSpecies], tags="waypoint")
