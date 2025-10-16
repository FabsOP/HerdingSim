from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
from tktooltip import ToolTip

class SpeciesTab(tk.Frame):
    def __init__(self, parent, f_unselect_terrains):
        super().__init__(parent)
        
        self.selected_animal = None
        self.animal_btns = []
        self.f_unselect_terrains = f_unselect_terrains

        self.images = []
        btnIcons = [("icons/sheep.png", "Sheep", "Great climbers"),
                    ("icons/penguin.png", "Penguin", "Great swimmers"),
                    ("icons/flamingo.png", "Flamingo", "Magestically pink"),
                    ("icons/elephant.png", "Elephant", "Large, friendly herbivores"),
                    ("icons/fox.png", "Fox", "Fave food: rabbits"),
                    ("icons/swallow.png", "Swallow", "Can fly anywhere"),]
        
        # a) Selection Section
        tk.Label(parent, text="Select a species", bg="#F5FBEF", font = ("Comic Sans MS", 9, "bold"), fg="#4C6B32").pack(pady=10)
        animal_btn_frame = tk.Frame(parent, bg="#F5FBEF")
        animal_btn_frame.pack()
        for i, icon in enumerate(btnIcons):
            image = Image.open(icon[0])
            image = image.resize((30, 30))
            photo = ImageTk.PhotoImage(image)
            self.images.append(photo)  # Store reference

            btn = tk.Button(
                animal_btn_frame, image=photo, text=icon[1], compound="bottom",
                cursor="hand2", activebackground="#C1E1C1", background="#E2F0D9",
                foreground="#4C6B32", activeforeground="#4C6B32",
                relief="raised", width=60, height=60, bd=2, font=("Comic Sans MS", 8, "bold"),
                command=lambda animal = icon[1]: self.clickAnimal(animal)
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
            
            self.animal_btns.append(btn)
            btn.tag = icon[1]
            
            ToolTip(btn, msg=icon[2], delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#E2F0D9", fg="#4C6B32")
            
        # b) Spawn Size section
        tk.Label(parent, text="Spawn Size", bg="#F5FBEF", font = ("Comic Sans MS", 9, "bold"), fg="#4C6B32").pack(pady=10)
        
        self.spawnSizeSlider = tk.Scale(
        parent,
        from_=1,
        to=10,
        orient=tk.HORIZONTAL,
        bg="#E2F0D9",         # Background of the scale widget
        fg="#4C6B32",         # Color of the text/labels
        troughcolor="#C1E1C1",# Background color of the trough (the bar)
        highlightbackground="#F5FBEF",  # Border color when unfocused
        highlightcolor="#A9C46C",       # Border color when focused
        activebackground="#A9C46C",     # Color when interacting with the slider
        font=("Comic Sans MS", 8, "bold"),
        sliderrelief=tk.FLAT,
        bd=1,
        length=160,
        command=self.handleSliderChange,
        )
        self.spawnSizeSlider.set(1)  # Set default spawn size to 1    
        
        self.spawnSizeSlider.pack(pady=5)
        
        # c) Border Handling section
        tk.Label(parent, text="Border Handling", bg="#F5FBEF", font = ("Comic Sans MS", 9, "bold"), fg="#4C6B32").pack(pady=10)
        borderSettingsFrame = tk.Frame(parent, bg="#F5FBEF")
        borderSettingsFrame.pack()
        
        # Radio buttons for border handling
        self.borderVar = tk.StringVar(value="Wrap")
        wrapRadio = tk.Radiobutton(borderSettingsFrame, width=6, text="Wrap", variable=self.borderVar, value="Wrap", bg="#E2F0D9", fg="#4C6B32", font=("Comic Sans MS", 8, "bold"), activebackground="#C1E1C1", activeforeground="#4C6B32", selectcolor="#A9C46C")
        stopRadio = tk.Radiobutton(borderSettingsFrame, width=6, text="Bounce", variable=self.borderVar, value="Bounce", bg="#E2F0D9", fg="#4C6B32", font=("Comic Sans MS", 8, "bold"), activebackground="#C1E1C1", activeforeground="#4C6B32", selectcolor="#A9C46C")
        followRadio = tk.Radiobutton(borderSettingsFrame, width=6, text="Follow", variable=self.borderVar, value="Follow", bg="#E2F0D9", fg="#4C6B32", font=("Comic Sans MS", 8, "bold"), activebackground="#C1E1C1", activeforeground="#4C6B32", selectcolor="#A9C46C") #wall following
        killRadio = tk.Radiobutton(borderSettingsFrame, width=6, text="Void", variable=self.borderVar, value="Void", bg="#E2F0D9", fg="#4C6B32", font=("Comic Sans MS", 8, "bold"), activebackground="#C1E1C1", activeforeground="#4C6B32", selectcolor="#A9C46C")
        
        wrapRadio.grid(row=0, column=0, padx=10, pady=7)
        stopRadio.grid(row=0, column=1, padx=10, pady=7)
        followRadio.grid(row=1, column=0, padx=10, pady=7)
        killRadio.grid(row=1, column=1, padx=10, pady=7)
        
        ToolTip(wrapRadio, msg="Animals reappear on the opposite side", delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#E2F0D9", fg="#4C6B32")
        ToolTip(stopRadio, msg="Animals cannot cross the terrain edge", delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#E2F0D9", fg="#4C6B32")
        ToolTip(killRadio, msg="Animals die if they reach the terrain edge", delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#E2F0D9", fg="#4C6B32")
        ToolTip(followRadio, msg="Animals follow the terrain edge", delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#E2F0D9", fg="#4C6B32")
        
        
        
        
        
        
    
    def handleSliderChange(self, value):
        print(f"Spawn size changed to: {value}")
        self.spawnSizeSlider.set(value)
        
            
    def selectAnimal(self, animal):
        self.selected_animal = animal
            
    def clickAnimal(self,selected):
        print(f"Clicked {selected}")
                
        for btn in self.animal_btns:
            if btn.tag == selected:
                if self.selected_animal == selected:
                    self.selectAnimal(None)
                    btn.configure(bg="#E2F0D9", relief=tk.RAISED)
                else:
                    btn.configure(bg ="#A9C46C", relief=tk.SUNKEN)
                    self.selectAnimal(selected)
                    self.f_unselect_terrains()
                    
                    
                    ## unselect everything else
                    for btnOther in [b for b in self.animal_btns if b != btn]:
                        btnOther.configure(relief="raised", bg="#E2F0D9")
                        
            
        
        print(f"Selected animal: {self.selected_animal}")
    
    def unselect_all(self):
        print("Unselecting all animal btns")
        self.selectAnimal(None)
        for btn in self.animal_btns:
            btn.configure(relief="raised", bg="#E2F0D9")