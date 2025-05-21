import tkinter as tk
from PIL import Image, ImageTk
from widgets.behaviourTab import behaviours

import boid
import time

canvasMultiplier = {"small": 1.5, "large": 2}
paintWindowWidth = 55
paintWindowStep = 5

class SimCanvas(tk.Canvas):
    def __init__(self, parent, terrainSize, controller, mediaController):
        super().__init__(parent, width=256*canvasMultiplier[terrainSize],
                         height=256*canvasMultiplier[terrainSize],
                         background="#B9D8B2", highlightbackground="#4C6B32",
                         highlightthickness=1.5,
                         relief="sunken",
                         )

        self.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nsew")
        self.spawned_boids = [] 
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
    
    #update canvas
    def update(self, fps,ti):
        tf = time.time()
        if not self.mediaController.isPaused: 
            dt = tf-ti
            dt *= self.mediaController.dtMultiplier
            for animal in self.spawned_boids:
                params = behaviours[animal.species]
                animal.move(params, dt)
                self.coords(animal.getCanvasId(), animal.position[0], animal.position[1])
            
        self.after(int(1000/fps), lambda: self.update(fps, tf))

    # event handlers
    def handleClick(self, e):
        if self.controller.get_selected_animal() is not None:
            pos = (e.x,e.y)
            selectedSpecies = self.controller.get_selected_animal()
            print(f"Spawning {selectedSpecies} at: ({pos[0]}, {pos[1]})")
            
            animal = boid.factory(species=selectedSpecies, pos=pos)
            
            animal.loadImage(f"icons/{selectedSpecies.lower()}_land.png")
            image = animal.tkImage
            if image:
                #draw image
                animal.setCanvasId(self.create_image(e.x, e.y, image=image))
                self.spawned_boids.append(animal)
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
            