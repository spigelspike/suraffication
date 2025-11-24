import numpy as np
import imageio
from tqdm import tqdm
import math

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def generate_frames(src_cells: np.ndarray, 
                    src_pos: np.ndarray, 
                    tgt_pos: np.ndarray, 
                    tgt_cells: np.ndarray, # Added tgt_cells
                    assignment: np.ndarray, 
                    duration: float, 
                    fps: int, 
                    output_size: int,
                    jitter_amount: float = 0.0,
                    particle_scale: float = 1.0,
                    shape: str = 'square',
                    color_mix: float = 0.0,
                    hold_start: float = 0.0,
                    hold_end: float = 0.0) -> list: # Added hold_start, hold_end
    """
    Generates frames for the animation.
    src_cells: (N, h, w, 3) pixel data
    src_pos: (N, 2) start positions [0, 1]
    tgt_pos: (N, 2) all target positions [0, 1]
    tgt_cells: (N, h, w, 3) target pixel data
    assignment: (N,) indices mapping src[i] -> tgt[assignment[i]]
    duration: seconds
    fps: frames per second
    output_size: size of the output video (square)
    jitter_amount: amount of random jitter
    particle_scale: scale factor for particle size (0.0 to 1.0+)
    shape: 'square' or 'circle'
    color_mix: 0.0 to 1.0, how much to blend towards target color at the end
    hold_start: seconds to hold the first frame
    hold_end: seconds to hold the last frame
    """
    num_frames = int(duration * fps)
    start_hold_frames = int(hold_start * fps)
    end_hold_frames = int(hold_end * fps)
    
    # Map source cells to their specific target positions
    end_pos = tgt_pos[assignment]
    
    # Get target cells corresponding to assignment
    assigned_tgt_cells = tgt_cells[assignment]
    
    # Pre-compute random jitter offsets
    N = src_cells.shape[0]
    jitter_offsets = (np.random.rand(N, 2) - 0.5) * 2 * jitter_amount
    
    # Cell size in pixels (approx)
    cell_h = src_cells.shape[1]
    cell_w = src_cells.shape[2]
    
    # Calculate rendered particle size
    part_h = int(cell_h * particle_scale)
    part_w = int(cell_w * particle_scale)
    part_h = max(1, part_h)
    part_w = max(1, part_w)
    
    from PIL import Image, ImageDraw
    
    # Pre-process particles
    print("Pre-processing particles...")
    src_particles = []
    tgt_particles = []
    
    # Helper to create particle from cell
    def create_particle(cell_data, w, h, shape_type):
        img = (cell_data * 255).astype(np.uint8)
        pil = Image.fromarray(img).resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")
        if shape_type == 'circle':
            mask = Image.new('L', (w, h), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, w, h), fill=255)
            pil.putalpha(mask)
        return pil

    for i in range(N):
        src_particles.append(create_particle(src_cells[i], part_w, part_h, shape))
        if color_mix > 0:
            tgt_particles.append(create_particle(assigned_tgt_cells[i], part_w, part_h, shape))
            
    print(f"Generating {num_frames} frames (plus {start_hold_frames} start, {end_hold_frames} end)...")
    
    # Helper to render a single frame at time t
    def render_frame(t):
        t_smooth = ease_in_out(t)
        
        # Interpolate positions
        current_pos_norm = (1 - t_smooth) * src_pos + t_smooth * end_pos
        
        # Add jitter
        jitter_amp = math.sin(math.pi * t)
        current_pos_norm += jitter_offsets * jitter_amp
        
        # Center coordinates in pixels
        cy = current_pos_norm[:, 0] * output_size
        cx = current_pos_norm[:, 1] * output_size
        
        # Top-left coordinates
        top = (cy - part_h / 2).astype(int)
        left = (cx - part_w / 2).astype(int)
        
        # Calculate current mix factor
        current_mix = t_smooth * color_mix
        
        frame_img = Image.new('RGB', (output_size, output_size), (0, 0, 0))
        
        for i in range(N):
            r, c = top[i], left[i]
            
            p = src_particles[i]
            
            if color_mix > 0 and current_mix > 0.01:
                p = Image.blend(src_particles[i], tgt_particles[i], current_mix)
            
            frame_img.paste(p, (c, r), p)
            
        return np.array(frame_img)

    # 1. Hold Start
    if start_hold_frames > 0:
        first_frame = render_frame(0.0)
        for _ in range(start_hold_frames):
            yield first_frame

    # 2. Animation
    for f in range(num_frames):
        t = f / (num_frames - 1) if num_frames > 1 else 1.0
        yield render_frame(t)
        
    # 3. Hold End
    if end_hold_frames > 0:
        last_frame = render_frame(1.0)
        for _ in range(end_hold_frames):
            yield last_frame

def save_video(frames_generator, path: str, fps: int):
    """
    Saves frames to a video file.
    frames_generator: iterator yielding numpy arrays
    """
    print(f"Saving video to {path}...")
    
    # We need to handle the generator. 
    # imageio.get_writer is best for this.
    
    if path.lower().endswith('.gif'):
        with imageio.get_writer(path, mode='I', fps=fps) as writer:
            for frame in frames_generator:
                writer.append_data(frame)
    else:
        with imageio.get_writer(path, fps=fps, codec='libx264') as writer:
            for frame in frames_generator:
                writer.append_data(frame)
