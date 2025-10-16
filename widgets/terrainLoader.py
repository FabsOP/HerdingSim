import tkinter as tk
from tkinter import filedialog, messagebox
import pickle as pkl
from PIL import Image, ImageTk
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from terrain import Terrain

class TerrainLoader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Terrain Loader")
        self.win_width = 800
        self.win_height = 650
        self.geometry(f"{self.win_width}x{self.win_height}")
        self.resizable(0, 0)
        self.config(background="#F5FBEF")
        self.center_window()
        self.protocol("WM_DELETE_WINDOW", sys.exit)

        # Biome selection variables
        self.biomeOptions = ["Grass", "Sand", "Ice", "Rock", "Water", "Snow"]
        self.selected_biome_idx = 0
        self.selected_biome = self.biomeOptions[self.selected_biome_idx]
        self.leftArrowImg = ImageTk.PhotoImage(Image.open("icons/left-arrow.png").resize((30, 30)))
        self.rightArrowImg = ImageTk.PhotoImage(Image.open("icons/right-arrow.png").resize((30, 30)))

        self.savedTerrains = []
        self.loadSaves()
        self.selectedTerrainIdx = 0

        self.setup_ui()
        self.update_terrain_display()
        self.mainloop()

    def setup_ui(self):
        # Main container with padding
        main_frame = tk.Frame(self, bg="#F5FBEF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Section 1: Biome Selection
        biome_section = tk.Frame(main_frame, bg="#F5FBEF", highlightbackground="#4C6B32", highlightthickness=2, relief="solid")
        biome_section.pack(fill="x", pady=(0, 20))
        
        biome_inner = tk.Frame(biome_section, bg="#F5FBEF")
        biome_inner.pack(padx=15, pady=15)

        heading1 = tk.Label(biome_inner, text="Select Biome Type", bg="#F5FBEF", fg="#4C6B32", font=("Comic Sans MS", 14, "bold"))
        heading1.pack(pady=(0, 15))

        biomeFrame = tk.Frame(biome_inner, bg="#F5FBEF")
        biomeFrame.pack(pady=5)

        # Previous preview image (previous biome)
        prev_biome_idx = (self.selected_biome_idx - 1) % len(self.biomeOptions)
        prev_biome = self.biomeOptions[prev_biome_idx]
        prev_preview_img = self.get_preview_image(self.selectedTerrainIdx, prev_biome, size=100)
        self.prevPreviewPhoto = ImageTk.PhotoImage(prev_preview_img)
        self.prevPreviewLabel = tk.Label(biomeFrame, image=self.prevPreviewPhoto, bg="#F5FBEF", relief="solid", borderwidth=2)
        self.prevPreviewLabel.grid(row=0, column=0, padx=(0, 10))

        # Left arrow button
        prevBtn = tk.Button(
            biomeFrame, image=self.leftArrowImg, command=self.prev_biome,
            bg="#F5FBEF", borderwidth=0, activebackground="#C1E1C1", relief="raised"
        )
        prevBtn.grid(row=0, column=1, padx=5)

        # Main biome preview (current biome)
        main_preview_img = self.get_preview_image(self.selectedTerrainIdx, self.selected_biome, size=200)
        self.previewPhoto = ImageTk.PhotoImage(main_preview_img)
        self.terrainPreview = tk.Label(biomeFrame, image=self.previewPhoto, bg="#F5FBEF", relief="solid", borderwidth=3)
        self.terrainPreview.grid(row=0, column=2, padx=20)
        self.terrainPreview.image = self.previewPhoto

        # Right arrow button
        nextBtn = tk.Button(
            biomeFrame, image=self.rightArrowImg, command=self.next_biome,
            bg="#F5FBEF", borderwidth=0, activebackground="#C1E1C1", relief="raised"
        )
        nextBtn.grid(row=0, column=3, padx=5)

        # Next preview image (next biome)
        next_biome_idx = (self.selected_biome_idx + 1) % len(self.biomeOptions)
        next_biome = self.biomeOptions[next_biome_idx]
        next_preview_img = self.get_preview_image(self.selectedTerrainIdx, next_biome, size=100)
        self.nextPreviewPhoto = ImageTk.PhotoImage(next_preview_img)
        self.nextPreviewLabel = tk.Label(biomeFrame, image=self.nextPreviewPhoto, bg="#F5FBEF", relief="solid", borderwidth=2)
        self.nextPreviewLabel.grid(row=0, column=4, padx=(10, 0))

        # Biome name label (centered below main preview)
        self.biomeVar = tk.StringVar(value=self.selected_biome)
        self.biomeDisplay = tk.Label(
            biomeFrame, textvariable=self.biomeVar, bg="#F5FBEF",
            fg="#4C6B32", font=("Comic Sans MS", 12, "bold")
        )
        self.biomeDisplay.grid(row=1, column=2, pady=(15, 0))

        # Section 2: Terrain Selection
        terrain_section = tk.Frame(main_frame, bg="#F5FBEF", highlightbackground="#4C6B32", highlightthickness=2, relief="solid")
        terrain_section.pack(fill="x", pady=(0, 20))
        
        terrain_inner = tk.Frame(terrain_section, bg="#F5FBEF")
        terrain_inner.pack(padx=15, pady=15)

        heading2 = tk.Label(terrain_inner, text="Saved Heightmaps", bg="#F5FBEF", fg="#4C6B32", font=("Comic Sans MS", 14, "bold"))
        heading2.pack(pady=(0, 15))

        # Terrain selector frame
        terrainsFrame = tk.Frame(terrain_inner, bg="#F5FBEF")
        terrainsFrame.pack(pady=(0, 15))
        
        self.leftTerrainArrow = tk.Button(
            terrainsFrame, image=self.leftArrowImg, command=self.prev_terrain,
            bg="#F5FBEF", borderwidth=0, activebackground="#C1E1C1", relief="raised"
        )
        self.leftTerrainArrow.grid(row=0, column=0, padx=(0, 15))
        
        self.terrainName = tk.Label(
            terrainsFrame, text=self.savedTerrains[self.selectedTerrainIdx]["name"],
            bg="#F5FBEF", fg="#4C6B32", font=("Comic Sans MS", 12, "bold"), width=25,
            relief="solid", borderwidth=2, pady=10
        )
        self.terrainName.grid(row=0, column=1, padx=10)

        self.rightTerrainArrow = tk.Button(
            terrainsFrame, image=self.rightArrowImg, command=self.next_terrain,
            bg="#F5FBEF", borderwidth=0, activebackground="#C1E1C1", relief="raised"
        )
        self.rightTerrainArrow.grid(row=0, column=2, padx=(15, 0))
        
        # Buttons frame
        buttons_frame = tk.Frame(terrain_inner, bg="#F5FBEF")
        buttons_frame.pack()

        self.uploadBtn = tk.Button(
            buttons_frame, text="Upload Heightmap", command=self.upload_heightmap,
            bg="#4C6B32", fg="white", font=("Comic Sans MS", 10, "bold"), 
            padx=15, pady=8, relief="raised", borderwidth=2
        )
        self.uploadBtn.pack(side="left", padx=(0, 10))

        self.deleteBtn = tk.Button(
            buttons_frame, text="Delete Heightmap", command=self.delete_heightmap,
            bg="#8B0000", fg="white", font=("Comic Sans MS", 10, "bold"), 
            padx=15, pady=8, relief="raised", borderwidth=2
        )
        self.deleteBtn.pack(side="left")

        # Section 3: Start Simulation
        sim_section = tk.Frame(main_frame, bg="#F5FBEF")
        sim_section.pack(pady=(0, 0))

        self.startSimBtn = tk.Button(
            sim_section, text="Start Simulation", command=self.startSimulation,
            bg="#4C6B32", fg="white", font=("Comic Sans MS", 16, "bold"), 
            padx=30, pady=50, relief="raised", borderwidth=3
        )
        self.startSimBtn.pack()

    def get_preview_image(self, terrain_idx, biome, size=128):
        idx = terrain_idx % len(self.savedTerrains)
        img = self.savedTerrains[idx]["terrain"].getContourImage(biome)
        return img.resize((size, size))

    def loadSaves(self):
        savesDir = "./saves"
        if not os.path.exists(savesDir):
            os.makedirs(savesDir)

        if "flat.terrain" not in os.listdir(savesDir):
            flatTerrain = Terrain(512, 512, invert=False)
            flatTerrain.load(None, "Grass", levels=15)
            with open(os.path.join(savesDir, "flat.terrain"), 'wb') as f:
                pkl.dump(flatTerrain, f)

        terrains = [{
            "name": "Flat Terrain",
            "terrain": pkl.load(open(os.path.join(savesDir, "flat.terrain"), 'rb'))
        }]

        for file in os.listdir(savesDir):
            if file.endswith(".terrain") and file != "flat.terrain":
                with open(os.path.join(savesDir, file), 'rb') as f:
                    terrain = pkl.load(f)
                    display_name = file.replace(".terrain", "")
                    if len(display_name) > 12:
                        display_name = display_name[:12] + "..."
                    terrains.append({
                        "name": display_name,
                        "full_name": file.replace(".terrain", ""),
                        "terrain": terrain
                    })
        self.savedTerrains = terrains

    def update_biome_previews(self):
        """Update all biome preview images"""
        # Update main preview (current biome)
        main_preview_img = self.get_preview_image(self.selectedTerrainIdx, self.selected_biome, size=200)
        self.previewPhoto = ImageTk.PhotoImage(main_preview_img)
        self.terrainPreview.config(image=self.previewPhoto)
        self.terrainPreview.image = self.previewPhoto

        # Update previous preview (previous biome)
        prev_biome_idx = (self.selected_biome_idx - 1) % len(self.biomeOptions)
        prev_biome = self.biomeOptions[prev_biome_idx]
        prev_preview_img = self.get_preview_image(self.selectedTerrainIdx, prev_biome, size=100)
        self.prevPreviewPhoto = ImageTk.PhotoImage(prev_preview_img)
        self.prevPreviewLabel.config(image=self.prevPreviewPhoto)
        self.prevPreviewLabel.image = self.prevPreviewPhoto

        # Update next preview (next biome)
        next_biome_idx = (self.selected_biome_idx + 1) % len(self.biomeOptions)
        next_biome = self.biomeOptions[next_biome_idx]
        next_preview_img = self.get_preview_image(self.selectedTerrainIdx, next_biome, size=100)
        self.nextPreviewPhoto = ImageTk.PhotoImage(next_preview_img)
        self.nextPreviewLabel.config(image=self.nextPreviewPhoto)
        self.nextPreviewLabel.image = self.nextPreviewPhoto
        
    def getSelectedTerrain(self):
        terrain = self.savedTerrains[self.selectedTerrainIdx]["terrain"]
        terrain.fillAll(self.selected_biome)
        return terrain

    def update_terrain_display(self):
        """Update terrain name and all preview images"""
        if self.savedTerrains:
            self.terrainName.config(text=self.savedTerrains[self.selectedTerrainIdx]["name"])
            self.update_biome_previews()
            
            # Update delete button state
            self.deleteBtn.config(state="disabled" if self.selectedTerrainIdx == 0 else "normal")

    def prev_biome(self):
        self.selected_biome_idx = (self.selected_biome_idx - 1) % len(self.biomeOptions)
        self.selected_biome = self.biomeOptions[self.selected_biome_idx]
        self.biomeVar.set(self.selected_biome)
        self.update_biome_previews()

    def next_biome(self):
        self.selected_biome_idx = (self.selected_biome_idx + 1) % len(self.biomeOptions)
        self.selected_biome = self.biomeOptions[self.selected_biome_idx]
        self.biomeVar.set(self.selected_biome)
        self.update_biome_previews()

    def next_terrain(self):
        if len(self.savedTerrains) > 1:
            self.selectedTerrainIdx = (self.selectedTerrainIdx + 1) % len(self.savedTerrains)
            self.update_terrain_display()

    def prev_terrain(self):
        if len(self.savedTerrains) > 1:
            self.selectedTerrainIdx = (self.selectedTerrainIdx - 1) % len(self.savedTerrains)
            self.update_terrain_display()

    def upload_heightmap(self):
        """Upload and add a new heightmap to the terrain list"""
        file_path = filedialog.askopenfilename(
            title="Select Heightmap Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.tif *.tiff"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("TIFF files", "*.tif *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return  # User cancelled
        
        # Check file extension
        valid_extensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff']
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in valid_extensions:
            messagebox.showerror(
                "Unsupported File Type",
                f"Unsupported file type: {file_ext}\nPlease select a PNG, JPG, JPEG, TIF, or TIFF file."
            )
            return
        
        try:
            # Check image dimensions
            # Define your standard terrain size (match flat terrain and simulation)
            STANDARD_SIZE = 512

            with Image.open(file_path) as img:
                width, height = img.size
                if width != height:
                    messagebox.showerror(
                        "Invalid Dimensions",
                        f"Image dimensions must be equal.\nCurrent dimensions: {width} x {height}\nPlease use a square image."
                    )
                    return
                # Resize to standard size if needed
                if width != STANDARD_SIZE:
                    img = img.resize((STANDARD_SIZE, STANDARD_SIZE), Image.LANCZOS)
                    # Save to a temporary file or use in-memory
                    temp_path = "temp_resized_heightmap.png"
                    img.save(temp_path)
                    heightmap_path = temp_path
                else:
                    heightmap_path = file_path

            new_terrain = Terrain(STANDARD_SIZE, STANDARD_SIZE, invert=False)
            new_terrain.load(heightmap_path, "Grass", levels=15)
            
            # Generate filename for save
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            save_name = base_name
            counter = 1
            
            # Ensure unique name
            existing_names = [t["name"] for t in self.savedTerrains]
            while save_name in existing_names:
                save_name = f"{base_name}_{counter}"
                counter += 1
            
            # Save terrain to file
            save_path = os.path.join("./saves", f"{save_name}.terrain")
            with open(save_path, 'wb') as f:
                pkl.dump(new_terrain, f)
            
            # Add to terrain list
            
            if len(save_name) > 18:
                display_name = save_name[:18] + "..."
            else:
                display_name = save_name
            
            self.savedTerrains.append({
                "name": display_name,
                "terrain": new_terrain
            })
            
            # Select the newly added terrain
            self.selectedTerrainIdx = len(self.savedTerrains) - 1
            self.update_terrain_display()
            
            messagebox.showinfo(
                "Success",
                f"Heightmap '{save_name}' uploaded successfully!"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to load heightmap:\n{str(e)}"
            )

    def delete_heightmap(self):
        """Delete the currently selected heightmap"""
        if self.selectedTerrainIdx == 0:
            messagebox.showwarning(
                "Cannot Delete",
                "The default flat terrain cannot be deleted."
            )
            return
        
        if len(self.savedTerrains) <= 1:
            messagebox.showwarning(
                "Cannot Delete",
                "Cannot delete the last remaining terrain."
            )
            return
        
        terrain_name = self.savedTerrains[self.selectedTerrainIdx]["full_name"]
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{terrain_name}'?\nThis action cannot be undone."
        )
        
        if not result:
            return
        
        try:
            # Remove save file
            save_path = os.path.join("./saves", f"{terrain_name}.terrain")
            if os.path.exists(save_path):
                os.remove(save_path)
            
            # Remove from list
            self.savedTerrains.pop(self.selectedTerrainIdx)
            
            # Adjust selected index
            if self.selectedTerrainIdx >= len(self.savedTerrains):
                self.selectedTerrainIdx = len(self.savedTerrains) - 1
            
            self.update_terrain_display()
            
            messagebox.showinfo(
                "Success",
                f"Heightmap '{terrain_name}' deleted successfully!"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to delete heightmap:\n{str(e)}"
            )

    def startSimulation(self):
        self.destroy()

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.win_width // 2)
        y = (screen_height // 2) - (self.win_height // 2) -30
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    t = TerrainLoader()