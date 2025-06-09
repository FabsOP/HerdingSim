from PIL import ImageDraw

import tkinter as tk
import numpy as np
import os
from PIL import Image, ImageTk

class Terrain:
    def __init__(self, w, h):
        """
        Initializes the Terrain object with a heightmap from a greyscale image.
        
        :param greyscaleImagePath: Path to the greyscale image file.
        :param w: Width of the terrain.
        :param h: Height of the terrain.
        """
        
        assert w > 0 and h > 0, "Width and height must be positive integers."
        assert w == h, "Width and height must not be equal."
        
        self.heightmap = np.zeros((h, w), dtype=np.float32)
        self.gradientField = np.zeros((h, w,2), dtype=float)  # 2D gradient field (dx, dy)
        self.width = w
        self.height = h
        self.maxHeight = 0.0
        
        self.contourImg = None
        self.heightmapImg = None
        
    def load(self, greyscaleImagePath):
        """
        Loads the heightmap from a greyscale image file.
        
        :param greyscaleImagePath: Path to the greyscale image file.
        """
        if greyscaleImagePath:
            self.heightmap, self.heightmapImg = self.getHeightmap(greyscaleImagePath, self.width, self.height)
            
            #find the maximum height in the heightmap
            self.maxHeight = np.max(self.heightmap)
            print(f"Heightmap loaded from {greyscaleImagePath} with shape: {self.heightmap.shape}")
            print(f"Maximum height in the heightmap: {self.maxHeight}")
        
        self.gradientField = self.generateGradientField()
    
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
        assert self.heightmapImg is not None, "Heightmap image not loaded."

        gray_data = self.heightmap

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

        self.contourImg = Image.fromarray(color_data)
        print(f"Contour map generated with {levels} levels.")

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
    
    def scaleWithHeight(self, lowerBound, var, position):
        """
        Scales a variable based on the height at a given position in the heightmap.
        :param min: Minimum value to return if the height is at its minimum.
        :param var: Variable to scale based on the height.
        :param position: Tuple (x, y) representing the position in the heightmap.
        :return: Scaled variable based on the height at the given position.
        """
        factor = (255 - self.heightmap[int(position[1]), int(position[0])]) / 255
        return max(lowerBound, factor * var)
    
    
if __name__ == "__main__":
    terrain = Terrain(2*256, 2*256)
    terrain.load("terrain/small4(512)(512)(0.4572)(699.7683454453672).png")
    terrain.generate_contour_map(bg_color="#B9D8B2", levels=15, shade_color="#000000")
    print("Terrain.heightmap shape:", terrain.heightmap.shape)
    print("Terrain.heightmap:", terrain.heightmap)
    print()
    

    # Display the contour map
    root = tk.Tk()
    contour_img_tk = ImageTk.PhotoImage(terrain.contourImg)
    label = tk.Label(root, image=contour_img_tk)
    label.pack()
    #print height of mouse
    
    def on_mouse_move(event):
        x, y = event.x, event.y
        if 0 <= x < terrain.width and 0 <= y < terrain.height:
            height = terrain.heightmap[y, x]
            gradient = terrain.gradientField[y][x]
            print(f"Mouse at ({x}, {y}) - Height: {height}")
            print(f"Mouse at ({x}, {y}) - Gradient: {gradient}")

            # Draw the gradient vector as an arrow on a copy of the contour image
            img_with_arrow = terrain.contourImg.copy()
            draw = ImageDraw.Draw(img_with_arrow)

            # Scale the gradient for visualization
            scale = 20  # Adjust as needed
            dx, dy = gradient
            end_x = int(x + dx * scale)
            end_y = int(y + dy * scale)

            # Draw arrow (line + head)
            draw.line([(x, y), (end_x, end_y)], fill=(255, 0, 0), width=2)
            # Draw arrowhead
            arrow_size = 6
            angle = np.arctan2(dy, dx)
            left = (end_x - arrow_size * np.cos(angle - np.pi / 6),
                    end_y - arrow_size * np.sin(angle - np.pi / 6))
            right = (end_x - arrow_size * np.cos(angle + np.pi / 6),
                    end_y - arrow_size * np.sin(angle + np.pi / 6))
            draw.polygon([ (end_x, end_y), left, right ], fill=(255, 0, 0))

            # Update the Tkinter image
            img_tk = ImageTk.PhotoImage(img_with_arrow)
            label.config(image=img_tk)
            label.image = img_tk  # Prevent garbage collection

    root.bind("<Motion>", on_mouse_move)
    root.mainloop()
    
    

