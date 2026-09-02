import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pickle as pkl
from PIL import Image, ImageTk
import os
import sys
import shutil
import webbrowser

from herdsim.core.terrain import Terrain

from herdsim.utils.path_utils import resource_path, user_data_path
from herdsim.utils import compat
from herdsim.ui.ui_utils import center_window

class TerrainLoader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Terrain Loader")
        self.win_width = 800
        self.win_height = 650
        self.geometry(f"{self.win_width}x{self.win_height}")
        self.resizable(0, 0)
        # self.config(background="#F5FBEF")
        self.config(background="#FFFFFF")
        self.center_window()
        self.protocol("WM_DELETE_WINDOW", sys.exit)

        # Biome selection variables
        self.biomeOptions = ["Grass", "Sand", "Ice", "Rock", "Water", "Snow"]
        self.selected_biome_idx = 0
        self.leftArrowImg = ImageTk.PhotoImage(Image.open(resource_path("icons/left-arrow.png")).resize((30, 30)))
        self.rightArrowImg = ImageTk.PhotoImage(Image.open(resource_path("icons/right-arrow.png")).resize((30, 30)))

        self.savedTerrains = []
        self.loadSaves()
        self.selectedTerrainIdx = 0

        self.setup_ui()
        self.update_terrain_display()
        self.mainloop()

    def setup_ui(self):
        # Main container with padding
        main_frame = tk.Frame(self, bg="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)


        # Section 2: Terrain Selection
        terrain_section = tk.Frame(main_frame, bg="#F5FBEF", highlightbackground="#4C6B32", highlightthickness=2, relief="solid")
        terrain_section.pack(fill="x", pady=(0, 20))
        
        terrain_inner = tk.Frame(terrain_section, bg="#F5FBEF")
        terrain_inner.pack(padx=15, pady=15, fill="both", expand=True)

        # Container for the entire section content
        content_container = tk.Frame(terrain_inner, bg="#F5FBEF")
        content_container.pack(fill="both", expand=True)
        
        # Download button frame with green background (positioned at top right)
        download_frame = tk.Frame(content_container, bg="#F5FBEF")
        download_frame.place(relx=1.0, rely=0.0, anchor="ne")
        
        # Download hyperlink label
        download_label = tk.Label(
            download_frame,
            text="Download more\nheightmaps online",
            bg="#F5FBEF",
            fg="#0000EE",
            font=("Comic Sans MS", 8, "underline"),
            justify="center",
            cursor="hand2",
            padx=10,
            pady=8
        )
        download_label.pack()
        download_label.bind("<Button-1>", lambda e: self.open_heightmap_website())
        
        # Heading (centered)
        heading2 = tk.Label(content_container, text="Saved Heightmaps", bg="#F5FBEF", fg="#4C6B32", font=("Comic Sans MS", 14, "bold"))
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
        self.prevPreviewLabel = tk.Label(biomeFrame, bg="#F5FBEF", relief="solid", borderwidth=2)
        self.prevPreviewLabel.grid(row=0, column=0, padx=(0, 10))

        # Left arrow button
        prevBtn = tk.Button(
            biomeFrame, image=self.leftArrowImg, command=self.prev_biome,
            bg="#F5FBEF", borderwidth=0, activebackground="#C1E1C1", relief="raised"
        )
        prevBtn.grid(row=0, column=1, padx=5)

        # Main biome preview (current biome)
        self.terrainPreview = tk.Label(biomeFrame, bg="#F5FBEF", relief="solid", borderwidth=3)
        self.terrainPreview.grid(row=0, column=2, padx=20)

        # Right arrow button
        nextBtn = tk.Button(
            biomeFrame, image=self.rightArrowImg, command=self.next_biome,
            bg="#F5FBEF", borderwidth=0, activebackground="#C1E1C1", relief="raised"
        )
        nextBtn.grid(row=0, column=3, padx=5)

        # Next preview image (next biome)
        self.nextPreviewLabel = tk.Label(biomeFrame, bg="#F5FBEF", relief="solid", borderwidth=2)
        self.nextPreviewLabel.grid(row=0, column=4, padx=(10, 0))

        # Biome name label (centered below main preview)
        self.biomeVar = tk.StringVar(value=self.selected_biome)
        self.biomeDisplay = tk.Label(
            biomeFrame, textvariable=self.biomeVar, bg="#F5FBEF",
            fg="#4C6B32", font=("Comic Sans MS", 12, "bold")
        )
        self.biomeDisplay.grid(row=1, column=2, pady=(15, 0))

        # Section 3: Start Simulation
        sim_section = tk.Frame(main_frame, bg="#F5FBEF")
        sim_section.pack(pady=(0, 0))

        self.startSimBtn = tk.Button(
            sim_section, text="Start Simulation", command=self.startSimulation,
            bg="#4C6B32", fg="white", font=("Comic Sans MS", 16, "bold"), 
            padx=30, pady=50, relief="raised", borderwidth=3
        )
        self.startSimBtn.pack()
        
        self.iconbitmap(resource_path("icons/sheep.ico"))

    @property
    def selected_biome(self):
        return self.biomeOptions[self.selected_biome_idx]

    @staticmethod
    def _savePath(name):
        return os.path.join(user_data_path("terrain"), f"{name}.terrain")

    @staticmethod
    def _displayName(name):
        return name[:18] + "..." if len(name) > 18 else name

    @staticmethod
    def _persistMigration(path, terrain):
        """Write back a terrain whose palette compat.load had to rebuild.

        Rebuilding costs ~0.18s per terrain and repeats on every launch until the
        migrated form reaches disk. path may be unwritable.
        """
        try:
            del terrain.paletteMigrated
        except AttributeError:
            pass

        tmp = path + ".tmp"
        try:
            with open(tmp, 'wb') as f:
                pkl.dump(terrain, f)
            os.replace(tmp, path)
        except Exception:
            try:
                os.remove(tmp)
            except OSError:
                pass

    @staticmethod
    def _makeFlatTerrain(path):
        flatTerrain = Terrain(512, 512, invert=False)
        flatTerrain.load(None, "Grass", levels=15)
        with open(path, 'wb') as f:
            pkl.dump(flatTerrain, f)
        return flatTerrain

    def get_preview_image(self, terrain_idx, biome, size=128):
        idx = terrain_idx % len(self.savedTerrains)
        img = self.savedTerrains[idx]["terrain"].getContourImage(biome)
        return img.resize((size, size))

    def loadSaves(self):
        terrainDir = user_data_path("terrain")
        if not os.path.exists(terrainDir):
            os.makedirs(terrainDir)
        
        # Check if this is first run (terrain folder is empty)
        is_first_run = len([f for f in os.listdir(terrainDir) if f.endswith('.terrain')]) == 0
        
        if is_first_run:
            print("First run detected - copying default terrains...")
            # Copy default terrains from bundled resources
            default_terrains_dir = resource_path("default_terrains")
            
            if os.path.exists(default_terrains_dir):
                for file in os.listdir(default_terrains_dir):
                    if file.endswith('.terrain'):
                        src = os.path.join(default_terrains_dir, file)
                        dst = os.path.join(terrainDir, file)
                        try:
                            shutil.copy2(src, dst)
                            print(f"  ✓ Copied {file}")
                        except Exception as e:
                            print(f"  ✗ Failed to copy {file}: {e}")
        
        #if flat.terrain does not exist, create it
        flatTerrainPath = os.path.join(terrainDir, "flat.terrain")
        if not os.path.exists(flatTerrainPath):
            self._makeFlatTerrain(flatTerrainPath)
        
        # Load all terrains from the terrain directory
        terrains = []
        
        for file in sorted(os.listdir(terrainDir)):
            if file.endswith(".terrain"):
                try:
                    with open(os.path.join(terrainDir, file), 'rb') as f:
                        terrain = compat.load(f)

                    if getattr(terrain, "paletteMigrated", False):
                        self._persistMigration(os.path.join(terrainDir, file), terrain)

                    display_name = file.replace(".terrain", "")

                    # Put flat terrain first if it exists
                    terrain_entry = {
                        "name": self._displayName(display_name),
                        "full_name": display_name,
                        "terrain": terrain
                    }

                    if file == "flat.terrain":
                        terrain_entry["name"] = "Flat Terrain"
                        terrains.insert(0, terrain_entry)
                    else:
                        terrains.append(terrain_entry)

                except Exception as e:
                    print(f"Failed to load {file}: {e}")
        
        # If no terrains loaded, create default flat
        if not terrains:
            flatTerrain = self._makeFlatTerrain(os.path.join(terrainDir, "flat.terrain"))
            terrains = [{
                "name": "Flat Terrain",
                "full_name": "flat",
                "terrain": flatTerrain
            }]
        
        self.savedTerrains = terrains
        
    def update_biome_previews(self):
        """Update all biome preview images"""
        previews = ((self.terrainPreview, 0, 200),
                    (self.prevPreviewLabel, -1, 100),
                    (self.nextPreviewLabel, 1, 100))

        for label, offset, size in previews:
            biome = self.biomeOptions[(self.selected_biome_idx + offset) % len(self.biomeOptions)]
            photo = ImageTk.PhotoImage(self.get_preview_image(self.selectedTerrainIdx, biome, size=size))
            label.config(image=photo)
            label.image = photo

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

    def _stepBiome(self, direction):
        self.selected_biome_idx = (self.selected_biome_idx + direction) % len(self.biomeOptions)
        self.biomeVar.set(self.selected_biome)
        self.update_biome_previews()

    def _stepTerrain(self, direction):
        if len(self.savedTerrains) > 1:
            self.selectedTerrainIdx = (self.selectedTerrainIdx + direction) % len(self.savedTerrains)
            self.update_terrain_display()

    def prev_biome(self):
        self._stepBiome(-1)

    def next_biome(self):
        self._stepBiome(1)

    def next_terrain(self):
        self._stepTerrain(1)

    def prev_terrain(self):
        self._stepTerrain(-1)

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
        
        # Prompt user for terrain name BEFORE any processing
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        terrain_name = simpledialog.askstring(
            "Name Your Terrain",
            "Enter a name for this terrain:",
            initialvalue=base_name,
            parent=self
        )
        
        if not terrain_name:
            return  # User cancelled or left empty
        
        # Clean the terrain name (remove invalid characters for filenames)
        terrain_name = terrain_name.strip()
        if not terrain_name:
            messagebox.showwarning(
                "Invalid Name",
                "Terrain name cannot be empty."
            )
            return
        
        # Check for name uniqueness
        existing_names = [t.get("full_name", t["name"]) for t in self.savedTerrains]
        if terrain_name in existing_names:
            messagebox.showerror(
                "Duplicate Name",
                f"A terrain with the name '{terrain_name}' already exists.\nPlease choose a different name."
            )
            return
        
        temp_path = None
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
            new_terrain.load(heightmap_path, "Grass", levels=25)
            
            # Save terrain to file
            save_path = self._savePath(terrain_name)
            with open(save_path, 'wb') as f:
                pkl.dump(new_terrain, f)
            
            self.savedTerrains.append({
                "name": self._displayName(terrain_name),
                "full_name": terrain_name,
                "terrain": new_terrain
            })
            
            # Select the newly added terrain
            self.selectedTerrainIdx = len(self.savedTerrains) - 1
            self.update_terrain_display()
            
            messagebox.showinfo(
                "Success",
                f"Heightmap '{terrain_name}' uploaded successfully!"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to load heightmap:\n{str(e)}"
            )
            
        #remove temp heightmap if it exists
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        

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
        
        terrain_name = self.savedTerrains[self.selectedTerrainIdx].get("full_name", self.savedTerrains[self.selectedTerrainIdx]["name"])
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{terrain_name}'?\nThis action cannot be undone."
        )
        
        if not result:
            return
        
        try:
            # Remove save file
            save_path = self._savePath(terrain_name)
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

    def open_heightmap_website(self):
        """Open website to download heightmaps"""
        url = "https://manticorp.github.io/unrealheightmap/index.html#latitude/35.362806018776496/longitude/138.7302017211914/zoom/13/outputzoom/14/width/512/height/512"
        webbrowser.open(url)

    def startSimulation(self):
        self.destroy()

    def center_window(self):
        center_window(self, self.win_width, self.win_height)

if __name__ == "__main__":
    t = TerrainLoader()