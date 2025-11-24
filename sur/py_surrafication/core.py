import numpy as np
from PIL import Image

def load_and_process_image(path: str, size: int) -> np.ndarray:
    """
    Loads an image, crops it to a square (center crop), and resizes it to size x size.
    Returns a numpy array of shape (size, size, 3) with values in [0, 1].
    """
    try:
        img = Image.open(path).convert("RGB")
    except Exception as e:
        raise ValueError(f"Could not open image at {path}: {e}")

    w, h = img.size
    min_dim = min(w, h)
    
    # Center crop
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    
    img = img.crop((left, top, right, bottom))
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Convert to numpy array [0, 1]
    return np.array(img, dtype=np.float32) / 255.0

def get_cells(image: np.ndarray, grid_res: int) -> np.ndarray:
    """
    Divides the image into a grid of grid_res x grid_res cells.
    image: (H, W, 3) array
    grid_res: number of cells along one dimension
    
    Returns:
        cells: (grid_res * grid_res, cell_h, cell_w, 3) array
        positions: (grid_res * grid_res, 2) array of (y, x) normalized centers [0, 1]
    """
    h, w, c = image.shape
    cell_h = h // grid_res
    cell_w = w // grid_res
    
    # We might lose a few pixels at the edge if not divisible, but we resized to 'size' 
    # which we assume is passed as 'resolution' * 'cell_pixel_size' or similar?
    # Actually, the prompt says "Resize both to the same size: N x N" and "Divide into grid of res x res".
    # Ideally N should be divisible by res. 
    # If we resize the image to exactly (res * something), it's easier.
    # But let's assume the input 'image' is already resized to be compatible or we handle the split.
    # For simplicity, let's enforce that the image size passed to load_and_process_image 
    # is a multiple of grid_res, OR we just use array splitting.
    
    # Let's re-verify the prompt: "Resize both to the same size: N x N" ... "Divide into grid of res x res".
    # If N is not divisible by res, we have partial pixels? No, pixels are discrete.
    # We should probably resize the image to exactly (grid_res * pixel_per_cell) if we want perfect blocks.
    # OR, we just treat 'resolution' as the target size and each cell is 1 pixel? 
    # The prompt says "Each cell is a block of pixels."
    # Let's assume we want decent quality. Let's say we fix the internal working resolution 
    # to be something like 512x512 or 1024x1024, and grid_res is e.g. 64.
    # 512 / 64 = 8 pixels per cell.
    
    # However, to keep it simple and robust:
    # We can just split using numpy.array_split or reshape if it divides evenly.
    
    # If we assume the caller ensures divisibility or we just truncate:
    
    # Reshape into (grid_res, cell_h, grid_res, cell_w, 3)
    # Then swap axes to (grid_res, grid_res, cell_h, cell_w, 3)
    # Then flatten to (grid_res*grid_res, cell_h, cell_w, 3)
    
    # Let's ensure we only take the divisible part
    valid_h = (h // grid_res) * grid_res
    valid_w = (w // grid_res) * grid_res
    
    image = image[:valid_h, :valid_w]
    cell_h = valid_h // grid_res
    cell_w = valid_w // grid_res
    
    grid = image.reshape(grid_res, cell_h, grid_res, cell_w, c)
    grid = grid.transpose(0, 2, 1, 3, 4)
    cells = grid.reshape(-1, cell_h, cell_w, c)
    
    # Calculate positions
    # Normalized coordinates of cell centers
    ys = np.linspace(0.5 / grid_res, 1.0 - 0.5 / grid_res, grid_res)
    xs = np.linspace(0.5 / grid_res, 1.0 - 0.5 / grid_res, grid_res)
    
    # Meshgrid
    grid_y, grid_x = np.meshgrid(ys, xs, indexing='ij')
    positions = np.stack([grid_y.ravel(), grid_x.ravel()], axis=1) # (N, 2)
    
    return cells, positions

def extract_features(cells: np.ndarray) -> np.ndarray:
    """
    Computes average color for each cell.
    cells: (N, h, w, 3)
    Returns: (N, 3) average colors
    """
    # Mean over height and width axes (1 and 2)
    return np.mean(cells, axis=(1, 2))
