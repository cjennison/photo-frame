import cairosvg # type: ignore
import pygame
import os

from xml.etree import ElementTree as ET

def load_svg_as_surface(svg_path, size, color="white"):
  try:
    # Read and modify the SVG content
    with open(svg_path, "r") as svg_file:
      svg_content = svg_file.read()
    svg_tree = ET.ElementTree(ET.fromstring(svg_content))
    root = svg_tree.getroot()

    # Update `fill` attributes to the specified color
    for element in root.iter():
      if "fill" in element.attrib:
        element.attrib["fill"] = color

    # Convert the modified SVG back to a string
    modified_svg = ET.tostring(root, encoding="unicode")

    # Render the modified SVG to PNG bytes
    png_bytes = cairosvg.svg2png(bytestring=modified_svg, output_width=size[0], output_height=size[1])

    # Save the PNG bytes temporarily and load them with Pygame
    with open("temp_icon.png", "wb") as temp_file:
      temp_file.write(png_bytes)
    surface = pygame.image.load("temp_icon.png").convert_alpha()
    os.remove("temp_icon.png")  # Delete the temporary file
    return surface
  except Exception as e:
    print(f"Error loading SVG: {svg_path}, {e}")
    return None