import tkinter as tk
from PIL import Image, ImageTk
from tktooltip import ToolTip

import os
import sys
from herdsim.utils.path_utils import resource_path


class TerrainTab(tk.Frame):
    def __init__(self, parent, f_unselect_animals):
        super().__init__(parent)
        parent.configure(takefocus=0)
        
        self.selected_terrain = None
        self.terrain_btns = []
        
        self.f_unselect_animals = f_unselect_animals

        self.images = []
        
        tk.Label(parent, text="Modify the environment", bg="#F5FBEF", font=("Comic Sans MS", 9, "bold"), fg="#4C6B32").pack(pady=10)
        terrain_btn_frame = tk.Frame(parent, bg="#F5FBEF",takefocus=0)
        terrain_btn_frame.pack()
        
        
        #create a frame of width spanning the buttons above from the left edge of the first button to the right edge of the last button
        # This frame will contain radio icons to choose the brush shape for terrain editing, either circle or square
        brush_shape_frame = tk.Frame(parent, bg="#F5FBEF")
        brush_shape_frame.pack(pady=5)
        
        #add radio buttons with icons to the right of the terrain buttons for brush shape selection
        self.brush_shape_var = tk.StringVar(value="Circle")
        circle_image = Image.open(resource_path("icons/circle.png"))
        circle_image = circle_image.resize((16, 16))

        square_image = Image.open(resource_path("icons/square.png"))
        square_image = square_image.resize((16, 16))
        circle_photo = ImageTk.PhotoImage(circle_image)
        square_photo = ImageTk.PhotoImage(square_image)
        
        self.images.append(circle_photo)
        self.images.append(square_photo)     
        
        ## generate btn grid of icons
        btnIcons = [
            (resource_path("icons/grass.png"), "Grass", "A lush green terrain, perfect for grazing animals."),
            (resource_path("icons/sand.png"), "Sand", "A dry, sandy terrain, suitable for desert animals."),
            (resource_path("icons/rock.png"), "Rock", "A rocky terrain, difficult to traverse"),
            (resource_path("icons/ice.png"), "Ice", "Careful, it's slippery"),
            (resource_path("icons/snow.png"), "Snow", "Snowy terrain, slows down movement"),
            (resource_path("icons/water.png"), "Water" ,"Slows movement for non-aquatic animals. Semi-aquatic creatures thrive."),
            (resource_path("icons/tree.png"), "Tree", "Provides shade and shelter."),
            (resource_path("icons/bush.png"), "Bush", "Dense foliage, ideal for hiding from predators."),
            (resource_path("icons/boulder.png"), "Boulder", "A large rock that can block paths or provide cover."),
            (resource_path("icons/eraser.png"), "Eraser", "Removes animals or obstacles from the environment."),]
        
        for i, icon in enumerate(btnIcons):
            image = Image.open(icon[0])
            image = image.resize((30, 30))
            photo = ImageTk.PhotoImage(image)
            self.images.append(photo)  # Store reference
            
            fg_color = "#ffffff" if icon[1] == "Eraser" else "#4C6B32"
            back_color = "#FF4D4D" if icon[1] == "Eraser" else "#E2F0D9"
            

            btn = tk.Button(
                terrain_btn_frame, image=photo, text=icon[1], compound="bottom",
                cursor="hand2", activebackground="#C1E1C1", background=back_color,
                foreground=fg_color, activeforeground="#4C6B32",
                relief="raised", width=60, height=60, bd=2, font=("Comic Sans MS", 8, "bold"),
                command=lambda terrain = icon[1]: self.clickTerrain(terrain),
                takefocus=0, highlightthickness=0
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
            
            self.terrain_btns.append(btn)
            btn.tag = icon[1]
            
            ToolTip(btn, msg=icon[2], delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#E2F0D9", fg="#4C6B32")
            
        ###### Brush selectors
        self.circle_btn = tk.Button(
                brush_shape_frame, image=circle_photo, compound="bottom",
                cursor="hand2", activebackground="#FFD4D4", background="#FFF0F0",
                foreground="#8B3A3A", activeforeground="#8B3A3A",
                relief="raised", width=28, height=28, bd=2, font=("Comic Sans MS", 7),
                takefocus=0, highlightthickness=0,
                command=lambda: self.selectBrush("Circle")
                )
        self.circle_btn.grid(row=0, column=0, padx=25, pady=10)
        # Make Circle brush active by default
        self.circle_btn.configure(relief="sunken", bg="#FFD4D4")
                
        ToolTip(self.circle_btn, msg="Circle Brush", delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#D4E8F5", fg="#2C5F7C")
                
        
        # square button
        self.square_btn = tk.Button(
                brush_shape_frame, image=square_photo, compound="bottom",
                cursor="hand2", activebackground="#FFD4D4", background="#FFF0F0",
                foreground="#8B3A3A", activeforeground="#8B3A3A",
                relief="raised", width=28, height=28, bd=2, font=("Comic Sans MS", 7),
                takefocus=0, highlightthickness=0,
                command=lambda: self.selectBrush("Square")
            )
        self.square_btn.grid(row=0, column=1, padx=25, pady=10)
        ToolTip(self.square_btn, msg="Square Brush", delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#D4E8F5", fg="#2C5F7C")
    
    def selectTerrain(self, terrain):
        self.selected_terrain = terrain
        
    def selectBrush(self, brush_shape):
        if brush_shape == self.brush_shape_var.get():
            return
        self.brush_shape_var.set(brush_shape)
        
        #modify button appearances
        if brush_shape == "Circle":
            self.circle_btn.configure(relief="sunken", bg="#FFD4D4")
            self.square_btn.configure(relief="raised", bg="#FFF0F0")
        else:
            self.square_btn.configure(relief="sunken", bg="#FFD4D4")
            self.circle_btn.configure(relief="raised", bg="#FFF0F0")
        
            
    def clickTerrain(self,selected):
        print(f"Clicked {selected}")
                
        for btn in self.terrain_btns:
            if btn.tag == selected:
                if self.selected_terrain == selected:
                    self.selectTerrain(None)
                    back_color = "#FF4D4D" if selected == "Eraser" else "#E2F0D9"
                    btn.configure(bg=back_color, relief=tk.RAISED)
                else:
                    back_color = "#CD1414" if selected == "Eraser" else "#A9C46C"
                    btn.configure(bg =back_color, relief=tk.SUNKEN)
                    self.selectTerrain(selected)
                    self.f_unselect_animals()
                    
                    
                    ## unselect everything else
                    for btnOther in [b for b in self.terrain_btns if b != btn]:
                        back_color = "#FF4D4D" if btnOther.tag == "Eraser" else "#E2F0D9"
                        btnOther.configure(relief="raised", bg=back_color)                    
            
        
        print(f"Selected terrain: {self.selected_terrain}")
        
    def unselect_all(self): 
        self.selectTerrain(None)
        for btn in self.terrain_btns:
            back_color = "#FF4D4D" if btn.tag == "Eraser" else "#E2F0D9"
            btn.configure(relief="raised", bg=back_color)