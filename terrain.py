import tkinter as tk
import numpy as np
import os
from PIL import Image, ImageTk, ImageDraw


color_map = {
    "Grass": {
        "bg_color": "#B9D8B2",
        "shade_color": "#000000",
    },
    "Sand": {
        "bg_color": "#FBDB93",
        "shade_color": "#7B4019",
    },
    "Ice": {
        "bg_color": "#84E3F0",
        "shade_color": "#103436",
    },
    "Shallows": {
        "bg_color": "#1461A0",
        "shade_color": "#09263D",
    },
}

class Terrain:
    def __init__(self, w, h, invert=True):
        """
        Initializes the Terrain object with a heightmap from a greyscale image.
        
        :param greyscaleImagePath: Path to the greyscale image file.
        :param w: Width of the terrain.
        :param h: Height of the terrain.
        """
        
        assert w > 0 and h > 0, "Width and height must be positive integers."
        assert w == h, "Width and height must be equal."
        
        self.invert = invert  # Invert the greyscale and gradients for better visualization
        
        self.heightmap = np.zeros((int(h), int(w)), dtype=np.float32)
        self.gradientField = np.zeros(self.heightmap.shape, dtype=float)  # 2D gradient field (dx, dy)
        self.width = int(w)
        self.height = int(h)
        
        self.contourImg = None
        self.terrainType = "Grass"  # Default terrain type
        
        self.typegrid = np.zeros(self.heightmap.shape, dtype="S")  # RGB grid for terrain coloring
        
        self.contourImgs = {
            "Grass": None,
            "Sand": None,
            "Ice": None,
            "Shallows": None
        }
        
        self.heightmapImg = None
        
        self.contour_levels = 15  
        
    def load(self, greyscaleImagePath=None, terrainType="Grass", levels=15):
        """
        Loads the heightmap from a greyscale image file.
        
        :param greyscaleImagePath: Path to the greyscale image file.
        """
        print(f"Loading terrain from {greyscaleImagePath} with size ({self.width}, {self.height}) and terrain type '{terrainType}'")
        if greyscaleImagePath:
            self.heightmap, self.heightmapImg = self.getHeightmap(greyscaleImagePath, self.width, self.height)
        
        if self.invert:
            # Invert the heightmap for better visualization
            self.heightmap = 255 - self.heightmap
        
        self.gradientField = self.generateGradientField()
        
        #generate contour map images for each terrain type
        assert terrainType in color_map, f"Unknown terrain type: {terrainType}"
        
        self.terrainType = terrainType
        
        for terrain, colors in color_map.items():
            bg_color = colors["bg_color"]
            shade_color = colors["shade_color"]
            contour_img = self.generate_contour_map(bg_color, levels=levels, shade_color=shade_color)
            self.contourImgs[terrain] = contour_img
        self.contourImg = self.contourImgs[terrainType]
        
        # update the typegrid with the terrain type
        self.typegrid.fill(terrainType.encode('utf-8'))
        
        print(f"Terrain loaded with heightmap shape: {self.heightmap.shape}")
        print(f"Terrain loaded with gradient field shape: {self.gradientField.shape}")
        print(f"Contour map generated for terrain type: {terrainType} with {levels} levels.")
        
        
    
    def getHeightmap(self, greyscaleImagePath, w, h):
        """
        Returns a 2D numpy array of the heightmap
        """
        if not os.path.exists(greyscaleImagePath):
            raise FileNotFoundError(f"File not found: {greyscaleImagePath}")
        
        img = Image.open(greyscaleImagePath).convert("L")
        img = img.resize((w, h), Image.LANCZOS)  # Resize to specified width and height
        return np.array(img, dtype=float), img
    
    def hex_to_rgb(self, hex_color):
        """
        Converts a hex color string to an RGB tuple.
        
        :param hex_color: Color in hex format (e.g., "#RRGGBB").
        :return: Tuple of RGB values.
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def interpolate_color(self, color1, color2, t):
        """
        Interpolates between two RGB colors.
        
        :param color1: First color as an RGB tuple.
        :param color2: Second color as an RGB tuple.
        :param t: Interpolation factor (0.0 to 1.0).
        :return: Interpolated color as an RGB tuple.
        """
        return tuple(int(color1[i] + (color2[i] - color1[i]) * t) for i in range(3))
    
    def generate_contour_map(self, bg_color, levels=10, shade_color="#000000"):

        gray_data = self.heightmap
        
        self.contour_levels = levels

        bg_rgb = self.hex_to_rgb(bg_color)
        shade_rgb = self.hex_to_rgb(shade_color)

        # Compute contour levels
        thresholds = np.linspace(0, 255, levels+1)

        # Prepare output image
        color_data = np.zeros((*gray_data.shape, 3), dtype=np.uint8)

        for i in range(levels):
            lower = thresholds[i]
            upper = thresholds[i+1]
            mask = (gray_data >= lower) & (gray_data < upper)
            t = i / max(levels-1, 1)
            fill_color = self.interpolate_color(bg_rgb, shade_rgb, t * 0.7)  # 0.7 to avoid going full black
            color_data[mask] = fill_color

        print(f"Contour map generated with {levels} levels.")
        return Image.fromarray(color_data)
        

    def color_region(self, mask, terrain_type="desert"):
        """
        Colors a region of the heightmap based on a mask.
        
        :param mask: 2D numpy array of boolean values indicating the region to color.
        :param terrain_type: Type of terrain to color (e.g., "desert", "ice", "shallows").
        """
        assert mask.shape == self.heightmap.shape, "Mask shape must match heightmap shape."
        
        contourImage = np.array(self.contourImg)
        
        #replace the current contour image pixels with the saved contour image corresponding to the terrain type according to the mask
        # in one go with vectorized operations
        
        otherContourImage = np.array(self.contourImgs[terrain_type])
        mask_indices = np.where(mask)
        # Color the pixels in the contour image based on the mask
        contourImage[mask_indices] = otherContourImage[mask_indices]

        # Update the contour image with the new colored region
        self.contourImg = Image.fromarray(contourImage)
        
        #update the typegrid with the terrain type
        self.typegrid[mask_indices] = terrain_type.encode('utf-8')
    
    def compute_gradient(self, x, y):
        h, w = self.heightmap.shape
        
        # Handle boundary conditions by clamping indices
        x_left = max(0, x-1)
        x_right = min(w-1, x+1)
        y_bottom = max(0, y-1)  
        y_top = min(h-1, y+1)
        
        # Central difference approximation
        dh_dx = (self.heightmap[y, x_right] - self.heightmap[y, x_left]) / (x_right - x_left)
        dh_dy = (self.heightmap[y_top, x] - self.heightmap[y_bottom, x]) / (y_top - y_bottom)
        
        return np.array([dh_dx, dh_dy])

    def generateGradientField(self):
        """
        Generates a gradient field for the heightmap.
        
        :return: 2D numpy array of gradients (dx, dy).
        """
        h, w = self.heightmap.shape
        gradient_field = np.zeros((h, w, 2), dtype=float)

        for y in range(h):
            for x in range(w):
                gradient_field[y, x] = -1*self.compute_gradient(x, y)

        return gradient_field
    