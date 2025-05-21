import tkinter as tk
from PIL import Image, ImageTk
from tktooltip import ToolTip


class TerrainTab(tk.Frame):
    def __init__(self, parent, f_unselect_animals):
        super().__init__(parent)
        
        self.selected_terrain = None
        self.terrain_btns = []
        
        self.f_unselect_animals = f_unselect_animals

        self.images = []
        
        tk.Label(parent, text="Modify the environment", bg="#F5FBEF", font=("Comic Sans MS", 9, "bold"), fg="#4C6B32").pack(pady=10)
        terrain_btn_frame = tk.Frame(parent, bg="#F5FBEF")
        terrain_btn_frame.pack()
        
        ## generate btn grid of icons
        btnIcons = [("icons/sand.png", "Sand", "From the desert"),
                    ("icons/tree.png", "Tree", "Great shelter"),
                    ("icons/tallGrass.png", "Tall Grass", "Perfect for hiding. Predators and prey use it strategically."),
                    ("icons/shallowWater.png", "Shallows" ,"Slows movement for non-aquatic animals. Semi-aquatic creatures thrive."),
                    ("icons/sea.png", "Sea" ,"Only strong swimmers venture here. Dangerous for land animals."),
                    ("icons/stone.png", "Stone", "Hard terrain. Difficult to cross"),
                    ("icons/ice.png", "Ice", "Careful, it's slippery"),
                    ("icons/fence.png", "Fence", "Keep things in... or out")]
        
        for i, icon in enumerate(btnIcons):
            image = Image.open(icon[0])
            image = image.resize((30, 30))
            photo = ImageTk.PhotoImage(image)
            self.images.append(photo)  # Store reference

            btn = tk.Button(
                terrain_btn_frame, image=photo, text=icon[1], compound="bottom",
                cursor="hand2", activebackground="#C1E1C1", background="#E2F0D9",
                foreground="#4C6B32", activeforeground="#4C6B32",
                relief="raised", width=60, height=60, bd=2, font=("Comic Sans MS", 8, "bold"),
                command=lambda terrain = icon[1]: self.clickTerrain(terrain)
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
            
            self.terrain_btns.append(btn)
            btn.tag = icon[1]
            
            ToolTip(btn, msg=icon[2], delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#E2F0D9", fg="#4C6B32")
            
    def selectTerrain(self, terrain):
        self.selected_terrain = terrain
            
    def clickTerrain(self,selected):
        print(f"Clicked {selected}")
                
        for btn in self.terrain_btns:
            if btn.tag == selected:
                if self.selected_terrain == selected:
                    self.selectTerrain(None)
                    btn.configure(bg="#E2F0D9", relief=tk.RAISED)
                else:
                    btn.configure(bg ="#A9C46C", relief=tk.SUNKEN)
                    self.selectTerrain(selected)
                    self.f_unselect_animals()
                    
                    
                    ## unselect everything else
                    for btnOther in [b for b in self.terrain_btns if b != btn]:
                        btnOther.configure(relief="raised", bg="#E2F0D9")                    
            
        
        print(f"Selected terrain: {self.selected_terrain}")
        
    def unselect_all(self):
        print("Unselecting all terrain btns")
        self.selectTerrain(None)
        for btn in self.terrain_btns:
            btn.configure(relief="raised", bg="#E2F0D9")