from tkinter import ttk
import tkinter as tk

from widgets.animalTab import SpeciesTab
from widgets.terrainEditorTab import TerrainTab
from widgets.behaviourTab import BehaviourTab

class Controller(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, background="#F5FBEF", highlightbackground="#4C6B32", highlightthickness=1.5)
        self.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=(20,10))

        self.selected_animal = None
        

        # Create the Notebook widget
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#F5FBEF", borderwidth=0)
        style.configure("TNotebook.Tab", background="#E2F0D9", foreground="#4C6B32", font=("Comic Sans MS", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#C1E1C1")])

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Create individual tabs
        tab1 = tk.Frame(notebook, bg="#F5FBEF")
        tab2 = tk.Frame(notebook, bg="#F5FBEF")
        tab3 = tk.Frame(notebook, bg="#F5FBEF")

        # Add tabs to notebook
        notebook.add(tab1, text="Species")
        notebook.add(tab2, text="Terrain Editor")
        notebook.add(tab3, text="Behaviour")
        
        #Tab 1
        self.speciesTab = SpeciesTab(tab1, self.unselect_terrains)
        
        #Tab 2
        self.terrainTab = TerrainTab(tab2, self.unselect_animals)
        
        #Tab 3
        self.behaviourTab = BehaviourTab(tab3)
        self.behaviourTab.pack(fill="both", expand=True)
        
    def get_selected_animal(self):
        return self.speciesTab.selected_animal
    
    def get_selected_terrain(self):
        return self.terrainTab.selected_terrain
    
    def unselect_animals(self):
        self.speciesTab.unselect_all()
        
    def unselect_terrains(self):
        self.terrainTab.unselect_all()