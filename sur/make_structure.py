import cv2
import numpy as np
from PIL import Image
import os

def make_structure_image(path_in, path_out):
    if not os.path.exists(path_in):
        print(f"File not found: {path_in}")
        return

    # Load image
    img = cv2.imread(path_in, cv2.IMREAD_GRAYSCALE)
    
    # 1. Adaptive Thresholding (looks like a sketch/stencil)
    # This keeps facial features while removing flat shading
    structure = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 11, 2)
                                      
    # 2. Dilate slightly to make lines thicker for particles to grab onto
    kernel = np.ones((2,2), np.uint8)
    structure = cv2.dilate(structure, kernel, iterations=1)
    
    # Save
    cv2.imwrite(path_out, structure)
    print(f"Created structure image: {path_out}")

if __name__ == "__main__":
    make_structure_image("examples/sura.jpg", "examples/sura_structure.jpg")
