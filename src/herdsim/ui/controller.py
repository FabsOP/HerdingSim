from tkinter import ttk
import tkinter as tk

from herdsim.ui.animalTab import SpeciesTab
from herdsim.ui.terrainEditorTab import TerrainTab
from herdsim.ui.behaviourTab import BehaviourTab
from herdsim.core import boid
from herdsim.ui.borderHandler import BorderHandler

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

        style.layout("Tab",
        [('Notebook.tab', {'sticky': 'nswe', 'children':
            [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
                #[('Notebook.focus', {'side': 'top', 'sticky': 'nswe', 'children':
                    [('Notebook.label', {'side': 'top', 'sticky': ''})],
                #})],
            })],
        })]
        )

        notebook = ttk.Notebook(self, takefocus=False)
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
        #Section a : Parameter Tweaking
        self.behaviourTab = BehaviourTab(tab3)
        self.behaviourTab.pack(fill="both", expand=True)
        
        #Section b : Border Handling
        self.borderHandler = BorderHandler(tab3)
        self.borderHandler.pack(fill="x", padx=8, pady=(20, 20))
        
        self.after(100, lambda: self.focus_set())
        
    def get_selected_animal(self):
        return self.speciesTab.selected_animal
    
    def get_brush_shape(self):
        return self.terrainTab.brush_shape_var.get()
    
    def getBorderMode(self):
        return self.borderHandler.borderVar.get()
    
    def get_selected_terrain(self):
        return self.terrainTab.selected_terrain
    
    def unselect_animals(self):
        self.speciesTab.unselect_all()
        
    def unselect_terrains(self):
        self.terrainTab.unselect_all()
        
    def get_spawn_size(self):
        return self.speciesTab.spawnSizeSlider.get()