import tkinter as tk
import numpy as np
import os
from PIL import Image, ImageTk, ImageDraw
import math


color_map = {
    "Grass": {
        "bg_color": "#184D27",  # Darker green
        "shade_color": "#B9D8B2",
    },
    "Sand": {
        "bg_color": "#7B4019",
        "shade_color": "#FBDB93",
    },
    "Ice": {
        "bg_color": "#000000",
        "shade_color": "#84E3F0",
    },
    "Water": {
        "bg_color": "#0A223A",
        "shade_color": "#1461A0",
    },
    "Rock": {
        "bg_color": "#000000",
        "shade_color": "#A9A9A9",
    },
    "Snow": {
        # Slightly darker bg_color for more range, still snow-like
        "bg_color": "#7A8FA3",
        "shade_color": "#FFFFFF",  # Slightly off-white for a softer snow highlight
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
        
        self.heightmap = np.ones((int(h), int(w)), dtype=np.float32)*255
        self.gradientField = np.zeros(self.heightmap.shape, dtype=float)  # 2D gradient field (dx, dy)
        self.width = int(w)
        self.height = int(h)
        
        self.contourImg = None
        self.contourMask = None  # identify contours by unique colors
        self.terrainType = "Grass"  # Default terrain type
        
        self.typegrid = np.zeros(self.heightmap.shape, dtype=object)  # 2D array to store terrain types
        
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
        
        if self.invert and self.heightmapImg is not None:
            # Invert the heightmap for better visualization
            self.heightmap = 255 - self.heightmap
        
        self.gradientField = self.generateGradientField()
        
        #generate contour map images for each terrain type
        assert terrainType in color_map, f"Unknown terrain type: {terrainType}"
        
        self.terrainType = terrainType
        
        for terrain, colors in color_map.items():
            bg_color = colors["bg_color"]
            shade_color = colors["shade_color"]
            contour_img = self.generate_contour_map(bg_color, levels=levels, shade_color=shade_color, terrain_type=terrain)
            self.contourImgs[terrain] = contour_img
        self.contourImg = self.contourImgs[terrainType]
        
        #populate the contour mask, this codes each unique color in the contour image with a unique integer
        self.contourMask = np.zeros(self.heightmap.shape, dtype=np.int32)
        unique_colors = np.unique(np.array(self.contourImg))
        for idx, color in enumerate(unique_colors):
            mask = np.all(np.array(self.contourImg) == color, axis=-1)
            self.contourMask[mask] = idx
        
        # update the typegrid with the terrain type
        self.typegrid.fill(terrainType)
        
        print(f"Terrain loaded with heightmap shape: {self.heightmap.shape}")
        print(f"Terrain loaded with gradient field shape: {self.gradientField.shape}")
        print(f"Contour map generated for terrain type: {terrainType} with {levels} levels.\n")
        
        # STATS
        print(f"Heightmap statistics:")
        print(f"  Min: {self.heightmap.min()}")
        print(f"  Max: {self.heightmap.max()}")
        print(f"  Mean: {self.heightmap.mean()}")
        print(f"  Std: {self.heightmap.std()}")
        print(f"  Unique values: {len(np.unique(self.heightmap))}")
        
        
    
    def getHeightmap(self, greyscaleImagePath, w, h):
        """
        Returns a 2D numpy array of the heightmap
        """
        if not os.path.exists(greyscaleImagePath):
            raise FileNotFoundError(f"File not found: {greyscaleImagePath}")
        
        img = Image.open(greyscaleImagePath)
        
        
        #if image is 16 bit
        if img.mode == 'I;16' or img.mode == 'I':
            print(f"16 Bit heightmap detected: {img.mode}")
            imgArr = np.array(img, dtype=np.float32)
            
            # If there is variation, normalize to 0-255
            if imgArr.max() > imgArr.min():
                imgArr = (imgArr - imgArr.min()) / (imgArr.max() - imgArr.min()) * 255.0
            else:
                print("Warning: 16 Bit heightmap has no variation, setting to midgray (128).")
                imgArr = np.full_like(imgArr, 128, dtype=np.float32)
            
            # convert to pil image for resizing    
            img = Image.fromarray(imgArr.astype(np.uint8), mode='L')
        else:
            print(f"8 Bit Heightmap detected: {img.mode}")
            img = img.convert('L')
            
        img = img.resize((w, h), Image.LANCZOS)  # Resize to specified width and height
        heightmap = np.array(img, dtype=np.float32)
        return heightmap, img
    
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
    
    def heightAt(self, x, y):
        """
        Returns the height at the given coordinates (x, y).
        
        :param x: X coordinate.
        :param y: Y coordinate.
        :return: Height value at (x, y).
        """
        assert 0 <= x < self.width and 0 <= y < self.height, "Coordinates out of bounds."
        return self.heightmap[int(y), int(x)]
    
    def draw_gradient_arrows(self, image, arrow_color="#044BB6", arrow_spacing=30, arrow_scale=10):
        """
        Draws gradient direction arrows on the image for Water terrain.
        
        :param image: PIL Image to draw arrows on.
        :param arrow_color: Color of the arrows (blue by default).
        :param arrow_spacing: Spacing between arrows in pixels.
        :param arrow_scale: Scale factor for arrow size.
        """
        draw = ImageDraw.Draw(image)
        h, w = self.heightmap.shape
        
        # Draw arrows at regular intervals
        for y in range(0, h, arrow_spacing):
            for x in range(0, w, arrow_spacing):
                if y < h and x < w:
                    # Get gradient at this point
                    gradient = -1*self.gradientField[y, x]
                    dx, dy = gradient[0], gradient[1]
                    
                    # Skip if gradient is too small (flat areas)
                    magnitude = math.sqrt(dx*dx + dy*dy)
                    if magnitude < 0.1:  # Threshold for minimum gradient
                        continue
                    
                    # Normalize and scale the gradient vector
                    dx_norm = dx / magnitude * arrow_scale
                    dy_norm = dy / magnitude * arrow_scale
                    
                    # Calculate arrow endpoints
                    start_x = x
                    start_y = y
                    end_x = start_x + dx_norm
                    end_y = start_y + dy_norm
                    
                    # Draw arrow line
                    draw.line([(start_x, start_y), (end_x, end_y)], fill=arrow_color, width=2)
                    
                    # Draw arrowhead
                    arrow_length = 3
                    angle = math.atan2(dy_norm, dx_norm)
                    
                    # Calculate arrowhead points
                    head_angle1 = angle - math.pi * 0.75
                    head_angle2 = angle + math.pi * 0.75
                    
                    head_x1 = end_x + arrow_length * math.cos(head_angle1)
                    head_y1 = end_y + arrow_length * math.sin(head_angle1)
                    head_x2 = end_x + arrow_length * math.cos(head_angle2)
                    head_y2 = end_y + arrow_length * math.sin(head_angle2)
                    
                    # Draw arrowhead lines
                    draw.line([(end_x, end_y), (head_x1, head_y1)], fill=arrow_color, width=2)
                    draw.line([(end_x, end_y), (head_x2, head_y2)], fill=arrow_color, width=2)

    def generate_contour_map(self, bg_color, levels=10, shade_color="#000000", terrain_type="Grass"):

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
            mask = (gray_data >= lower) & (gray_data <= upper)
            t = i / max(levels-1, 1)
            #fill_color = self.interpolate_color(bg_rgb, shade_rgb, t * 0.7)  # 0.7 to avoid going full black
            fill_color = self.interpolate_color(bg_rgb, shade_rgb, t)
            color_data[mask] = fill_color

        print(f"Contour map generated with {levels} levels.")
        
        # Convert to PIL Image
        contour_image = Image.fromarray(color_data)
        
        # Add gradient arrows for Water terrain
        # if terrain_type == "Water":
        #     self.draw_gradient_arrows(contour_image)
        #     print("Added gradient arrows to Water terrain contour map.")
        
        return contour_image
        
    def typeAt(self, x, y):
        """
        Returns the terrain type at the given coordinates (x, y).
        
        :param x: X coordinate.
        :param y: Y coordinate.
        :return: Terrain type as a string.
        """
        assert 0 <= x < self.width and 0 <= y < self.height, "Coordinates out of bounds."
        return self.typegrid[int(y), int(x)]

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
        self.typegrid[mask_indices] = terrain_type
    
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
    
    def contourFill(self, x, y, target_terrain_type):
        """
        Fills a specific contour of the heightmap with the specified terrain type starting from (x, y).
        
        :param x: X coordinate to start filling.
        :param y: Y coordinate to start filling.
        :param terrain_type: Type of terrain to fill (e.g., "desert", "ice", "shallows").
        """
        assert 0 <= x < self.width and 0 <= y < self.height, "Coordinates out of bounds."
        
        # Create a mask for the region to fill
        mask = np.zeros(self.heightmap.shape, dtype=bool)
        
        # Use a simple flood fill algorithm
        stack = [(x, y)]
        
        #selected contour 
        targetContourIDX = self.contourMask[y, x]
        targetColor = self.contourImg.getpixel((x, y))
        
        #loop through all adjacent pixels with the same contour index and color. If the index is the same, and color matches, include it in the mask
        while stack:
            cx, cy = stack.pop()
            if mask[cy, cx]:
                continue
            
            # Check if the current pixel is part of the target contour
            if self.contourMask[cy, cx] == targetContourIDX and self.contourImg.getpixel((cx, cy)) == targetColor:
                mask[cy, cx] = True
                
                # Add adjacent pixels to the stack
                if cx > 0: stack.append((cx-1, cy))
                if cx < self.width - 1: stack.append((cx+1, cy))
                if cy > 0: stack.append((cx, cy-1))
                if cy < self.height - 1: stack.append((cx, cy+1))
        # Color the region with the specified terrain type
        self.color_region(mask, terrain_type=target_terrain_type)
        print(f"Filled contour at ({x}, {y}) with terrain type '{target_terrain_type}'")
        
        
    def getState(self):
        """
        Returns the current state of the terrain as a dictionary.
        
        :return: Dictionary containing heightmap, gradient field, contour image, and terrain type.
        """
        return {
            "heightmap": self.heightmap.copy(),
            "gradientField": self.gradientField.copy(),
            "contourImg": self.contourImg.copy(),
            "terrainType": self.terrainType,
            "typegrid": self.typegrid.copy()
        }
    
    def loadState(self, state):
        """
        Loads the terrain state from a dictionary.
        
        :param state: Dictionary containing heightmap, gradient field, contour image, and terrain type.
        """
        self.heightmap = state["heightmap"]
        self.gradientField = state["gradientField"]
        self.contourImg = state["contourImg"]
        self.terrainType = state["terrainType"]
        self.typegrid = state["typegrid"]
        
        # Recompute contour mask
        unique_colors = np.unique(np.array(self.contourImg))
        self.contourMask = np.zeros(self.heightmap.shape, dtype=np.int32)
        for idx, color in enumerate(unique_colors):
            mask = np.all(np.array(self.contourImg) == color, axis=-1)
            self.contourMask[mask] = idx
        
        print("Terrain state loaded successfully.")
        
            
        
        