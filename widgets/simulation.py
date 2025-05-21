#### IMPORTS ##################################################
import tkinter as tk
from widgets.controller import Controller
from widgets.media_controller import MediaController
from widgets.sim_canvas import SimCanvas
from widgets.behaviourTab import behaviours

#### SIMULATION CLASS ####################
windowSizeMap = {"small": "680x490", "large": "810x600"}
class Simulation(tk.Tk):
    ### a) Contructor
    def __init__(self, terrainSize):
        super().__init__()
        self.title("HerdSim")
        self.geometry(f"{windowSizeMap[terrainSize]}")
        self.resizable(0,0)
        self.config(background="#E4F1E0")  # Lighter greenish background

        #center window
        self.center_window(terrainSize)

        # Add widgets
        self.controller = Controller(self)
        self.media = MediaController(self)
        self.canvas = SimCanvas(self, terrainSize, self.controller, self.media)
        
        #Focus widget on click
        self.bind_all("<Button-1>", lambda event: event.widget.focus_set())
        

    ### b) Function to center window on screen        
    def center_window(self, terrainSize):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        win_width = int(windowSizeMap[terrainSize].split("x")[0])
        win_height = int(windowSizeMap[terrainSize].split("x")[1])

        x = (screen_width // 2) - (win_width // 2)
        y = (screen_height // 2) - (win_height // 2)
        self.geometry(f"+{x}+{y}")
    
        