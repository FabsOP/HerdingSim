#### IMPORTS ##################################################
import tkinter as tk
from herdsim.ui.controller import Controller
from herdsim.ui.media_controller import MediaController
from herdsim.ui.sim_canvas import SimCanvas

import os
import sys
from herdsim.utils.path_utils import resource_path
from herdsim.ui.ui_utils import center_window

#### SIMULATION CLASS ####################
windowSizeMap = {"small": (680, 490), "large": (810, 615)}

class Simulation(tk.Tk):
    ### a) Contructor
    def __init__(self, terrainSize,terrain):
        super().__init__()
        self.title("HerdSim")
        winWidth, winHeight = windowSizeMap[terrainSize]
        self.geometry(f"{winWidth}x{winHeight}")
        self.resizable(0,0)
        #self.config(background="#E4F1E0")  # Lighter greenish background
        self.config(background="#FFFFFF")

        #center window
        self.center_window(terrainSize)
        
        # Add widgets
        self.controller = Controller(self)
        self.media = MediaController(self)
        self.canvas = SimCanvas(self, terrain, self.controller, self.media)
        
        self.iconbitmap(resource_path("icons/sheep.ico"))
        
        # Only set focus for entry fields, not buttons
        self.bind_all("<Button-1>", lambda e: e.widget.focus_set()
                    if isinstance(e.widget, (tk.Entry, tk.Text)) else None)
        

    ### b) Function to center window on screen        
    def center_window(self, terrainSize):
        center_window(self, *windowSizeMap[terrainSize])
    
        