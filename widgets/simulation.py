#### IMPORTS ##################################################
import tkinter as tk
from widgets.controller import Controller
from widgets.media_controller import MediaController
from widgets.sim_canvas import SimCanvas
from widgets.behaviourTab import behaviours
from terrain import Terrain


#### SIMULATION CLASS ####################
windowSizeMap = {"small": "680x490", "large": "810x600"}
canvasMultiplier = {"small": 1.5, "large": 2}

class Simulation(tk.Tk):
    ### a) Contructor
    def __init__(self, terrainSize,heightMapPath=None):
        super().__init__()
        self.title("HerdSim")
        self.geometry(f"{windowSizeMap[terrainSize]}")
        self.resizable(0,0)
        self.config(background="#E4F1E0")  # Lighter greenish background

        #center window
        self.center_window(terrainSize)
        
        #load terrain
        self.terrain = Terrain(256*canvasMultiplier[terrainSize], 256*canvasMultiplier[terrainSize])
        self.terrain.load(heightMapPath)
        if heightMapPath:
            self.terrain.generate_contour_map(bg_color="#B9D8B2", levels=15, shade_color="#000000")
        
        # Add widgets
        self.controller = Controller(self)
        self.media = MediaController(self)
        self.canvas = SimCanvas(self, self.terrain, self.controller, self.media)
        
        
        #Focus widget on click
        self.bind_all("<Button-1>", lambda event: (
            event.widget.focus_set()
            ))
        

    ### b) Function to center window on screen        
    def center_window(self, terrainSize):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        win_width = int(windowSizeMap[terrainSize].split("x")[0])
        win_height = int(windowSizeMap[terrainSize].split("x")[1])

        x = (screen_width // 2) - (win_width // 2)
        y = (screen_height // 2) - (win_height // 2)
        self.geometry(f"+{x}+{y}")
    
        