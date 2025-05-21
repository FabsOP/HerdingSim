from PIL import Image
import numpy as np
import os

def hex_to_rgb(hex_color):
    """Convert hex string like '#00FF00' to an RGB tuple (0–255)."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def interpolate_color(val, min_val, max_val, color_start, color_end):
    """Linearly interpolate between two RGB colors."""
    ratio = (val - min_val) / (max_val - min_val)
    return tuple(
        int(start + (end - start) * ratio)
        for start, end in zip(color_start, color_end)
    )

def convert_heightmap_to_colormap(input_path, output_path, hex_start, hex_end):
    """
    Converts a grayscale heightmap to a custom colormap between two hex color codes.

    Parameters:
        input_path (str): Path to the grayscale heightmap PNG.
        output_path (str): Output path for the new colored image.
        hex_start (str): Hex code for the lowest value (e.g., '#000000').
        hex_end (str): Hex code for the highest value (e.g., '#00FFFF').
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")
    
    # Load grayscale image
    gray_img = Image.open(input_path).convert("L")
    gray_data = np.array(gray_img)

    # Parse hex colors
    rgb_start = hex_to_rgb(hex_start)
    rgb_end = hex_to_rgb(hex_end)

    # Create new RGB image
    color_img = Image.new("RGB", gray_img.size)
    for y in range(gray_img.height):
        for x in range(gray_img.width):
            val = gray_data[y, x]
            color = interpolate_color(val, 0, 255, rgb_start, rgb_end)
            color_img.putpixel((x, y), color)

    # Save the output image
    color_img.save(output_path)
    print(f"Saved colored heightmap to: {output_path}")


convert_heightmap_to_colormap(
    input_path="terrain\large1(614)(614)(1.524)(423.0295522516001).png",
    output_path="heightmap_colored.png",
    hex_start="#1D3807",
    hex_end="#B9D8B2"
)
