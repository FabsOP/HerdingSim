import tkinter as tk
from PIL import Image, ImageTk
from boid import behaviours, lastModified

import boid
import time

from vector import vectorAngle

import random

canvasMultiplier = {"small": 1.5, "large": 2}
paintWindowWidth = 55
paintWindowStep = 5

borderMode = "Wrap"

testMode = True

#Helper functions


class SimCanvas(tk.Canvas):
    def __init__(self, parent, terrainSize, controller, mediaController):
        self.width = 256*canvasMultiplier[terrainSize]
        self.height = 256*canvasMultiplier[terrainSize]
        
        super().__init__(parent, width=self.width,
                         height=self.height,
                         background="#B9D8B2", highlightbackground="#4C6B32",
                         highlightthickness=1.5,
                         relief="sunken",
                         )
        self.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nsew")
        self.spawned_boids = {species: [] for species in behaviours.keys()}
        self.controller = controller
        self.mediaController = mediaController
        self.windowRec = None
        
        self.bgPhoto = None
        self.heightMap = [[0 for _ in range(int(256*canvasMultiplier[terrainSize]))] for _ in range(int(256*canvasMultiplier[terrainSize]))]

        ### EVENT BINDINGS
        self.bind("<Button-1>", self.handleClick)
        
        self.bind('<Motion>', self.handleHover)     
        self.bind('<Enter>', self.handleHover)  # handle <Alt>+<Tab> switches between windows
        
        self.bind('<Leave>', self.handleLeave)
        
        self.bind_all("<MouseWheel>", self.handleScrollWheel)  # Windows & macOS
        self.bind_all("<Button-4>", self.handleScrollWheel)    # Linux scroll up
        self.bind_all("<Button-5>", self.handleScrollWheel)    # Linux scroll down          

    def setBgImage(self, path):
        bgImage = Image.open(path)
        bgImage= bgImage.resize((670, 470), Image.LANCZOS)
        self.bgPhoto = ImageTk.PhotoImage(bgImage)
        self.create_image(0, 0, anchor=tk.NW, image=self.bgPhoto)
    
    def clear_canvas(self,excl=None):
        if excl is None:
            self.delete("all")
            
        all_items = self.find_all()
        for item in all_items:
            if item not in excl:
                self.delete(item)
        
    
    #update canvas
    def update(self, fps,ti):
        self.clear_canvas(excl=[self.windowRec])
        
        tf = time.time()
        dt = tf-ti
        dt *= self.mediaController.dtMultiplier
        for species in self.spawned_boids.keys():
            for animal in self.spawned_boids[species]:
                self.visualizeParams()               
                if not self.mediaController.isPaused:
                    allBoids = [boid for s in self.spawned_boids.values() for boid in s]  # Flatten the list of boids
                    animal.update(allBoids,dt)       #todo: pass all boids regardless of species
                    animal.handleBorder(borderMode,w=self.width,h=self.height, pad = [10,10])
                self.create_image(animal.position[0], animal.position[1], image=animal.tkImage)
        
            
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
                        self.create_oval(animal.position[0]-radius[4]//1, animal.position[1]-radius[4]//1 ,animal.position[0]+radius[4]//1, animal.position[1]+radius[4]//1, fill=None, outline="#C1E1C1", width=2 )
            
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
                                        start=startTheta, extent= 2*viewAngle[4], fill=None, outline=arcColour, width=2 )
                    
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
                    self.create_image(e.x, e.y, image=image)

                    # add to boid list
                    self.spawned_boids[selectedSpecies].append(animal)
                else: 
                    print("Failed to draw")
            
   
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
            