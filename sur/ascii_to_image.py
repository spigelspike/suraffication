from PIL import Image, ImageDraw, ImageFont
import os

def ascii_to_image(txt_path, img_path, font_size=10):
    """Convert ASCII art text file to a centered image."""
    
    # Read ASCII art
    with open(txt_path, 'r', encoding='utf-8') as f:
        ascii_art = f.read()
    
    # Use a monospace font
    try:
        font = ImageFont.truetype("consola.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Split into lines and find actual content bounds
    lines = ascii_art.split('\n')
    
    # Find the leftmost and rightmost non-space characters
    min_x = float('inf')
    max_x = 0
    non_empty_lines = []
    
    for line in lines:
        stripped = line.rstrip()
        if stripped:  # Non-empty line
            # Find first non-space char
            first = len(line) - len(line.lstrip('.'))
            if first == len(line):  # All dots
                first = len(line) - len(line.lstrip())
            
            min_x = min(min_x, first)
            max_x = max(max_x, len(stripped))
            non_empty_lines.append(line)
    
    # Crop lines to just the content area and center
    content_width = max_x - min_x if max_x > min_x else max_x
    
    # Calculate pixel dimensions for a square image
    char_width = font_size
    char_height = font_size + 2
    
    # Make it square based on the larger dimension
    max_dim = max(content_width, len(non_empty_lines))
    img_size = max_dim * char_width
    
    # Create square image
    img = Image.new('RGB', (img_size, img_size), color='black')
    draw = ImageDraw.Draw(img)
    
    # Calculate centering offsets
    x_offset = (max_dim - content_width) * char_width // 2
    y_offset = (max_dim - len(non_empty_lines)) * char_height // 2
    
    # Draw ASCII art centered
    y = y_offset
    for line in non_empty_lines:
        # Trim to content area
        content = line[min_x:max_x] if min_x < len(line) else line
        draw.text((x_offset, y), content, fill='white', font=font)
        y += char_height
    
    # Save
    img.save(img_path)
    print(f"Created centered ASCII image: {img_path}")
    print(f"Size: {img_size}x{img_size} (square)")

if __name__ == "__main__":
    # Use absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    txt_path = os.path.join(base_dir, "examples", "sura.txt")
    img_path = os.path.join(base_dir, "examples", "ascii_target.png")
    
    print(f"Reading from: {txt_path}")
    print(f"Writing to: {img_path}")
    
    if not os.path.exists(txt_path):
        print(f"ERROR: Source text file not found at {txt_path}")
    else:
        ascii_to_image(txt_path, img_path, font_size=8)
        
        if os.path.exists(img_path):
            print(f"SUCCESS: File created at {img_path}")
        else:
            print(f"ERROR: File was NOT created at {img_path}")
