import argparse
import os
import sys
from .core import load_and_process_image, get_cells, extract_features
from .assignment import compute_cost_matrix, solve_assignment
from .animate import generate_frames, save_video

def main():
    parser = argparse.ArgumentParser(description="py-surrafication: Turn any image into another.")
    
    parser.add_argument("--src", required=True, help="Path to source image")
    parser.add_argument("--tgt", help="Path to target image (default: target.jpg in current dir)")
    parser.add_argument("--out", type=str, default="outputs/out.mp4", help="Output file path")
    parser.add_argument("--duration", type=float, default=6.0, help="Animation duration in seconds")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--resolution", type=int, default=64, help="Grid resolution (cells per side)")
    parser.add_argument("--proximity-importance", type=float, default=0.3, help="0.0 = color only, 1.0 = position only")
    parser.add_argument("--algorithm", choices=["greedy", "approx", "optimal", "sort"], default="optimal", help="Assignment algorithm")
    parser.add_argument("--jitter", type=float, default=0.05, help="Amount of particle jitter")
    parser.add_argument("--particle-scale", type=float, default=0.6, help="Scale of particles (0.0-1.0)")
    parser.add_argument("--shape", choices=["square", "circle"], default="circle", help="Shape of particles")
    parser.add_argument("--color-mix", type=float, default=0.0, help="Amount to mix target color (0.0-1.0)")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--preset", choices=["custom", "sand", "blocks", "bubbles"], default="custom", help="Use a preset configuration")
    parser.add_argument("--preview", action="store_true", help="Show live preview window")
    parser.add_argument("--hold-start", type=float, default=1.0, help="Seconds to hold the start frame")
    parser.add_argument("--hold-end", type=float, default=2.0, help="Seconds to hold the end frame")
    
    args = parser.parse_args()
    
    # Ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)
    
    # Apply presets
    if args.preset == "sand":
        print("Applying 'sand' preset...")
        args.resolution = 128
        args.algorithm = "sort"
        args.shape = "circle"
        args.particle_scale = 0.5
        args.color_mix = 0.0  # Pure source colors
        args.jitter = 0.1
    elif args.preset == "blocks":
        print("Applying 'blocks' preset...")
        args.resolution = 32
        args.algorithm = "optimal"
        args.shape = "square"
        args.particle_scale = 1.0
        args.color_mix = 0.0
        args.jitter = 0.0
    elif args.preset == "bubbles":
        print("Applying 'bubbles' preset...")
        args.resolution = 64
        args.algorithm = "greedy"
        args.shape = "circle"
        args.particle_scale = 0.8
        args.color_mix = 0.2
        args.jitter = 0.05
        
    if args.seed is not None:
        import numpy as np
        import random
        np.random.seed(args.seed)
        random.seed(args.seed)
    
    # Validate paths
    if not os.path.exists(args.src):
        print(f"Error: Source image not found at {args.src}")
        sys.exit(1)
        
    tgt_path = args.tgt if args.tgt else "target.jpg"
    if not os.path.exists(tgt_path):
        if not args.tgt and os.path.exists("examples/sura.jpg"):
             tgt_path = "examples/sura.jpg"
             if args.verbose: print(f"Default target not found, using {tgt_path}")
        elif not os.path.exists(tgt_path):
            print(f"Error: Target image not found at {tgt_path}")
            sys.exit(1)

    if args.verbose:
        print(f"Source: {args.src}")
        print(f"Target: {tgt_path}")
        print(f"Resolution: {args.resolution}x{args.resolution}")
        print(f"Algorithm: {args.algorithm}")
        print(f"Preset: {args.preset}")
        print(f"Hold Start: {args.hold_start}s")
        print(f"Hold End: {args.hold_end}s")
    
    OUTPUT_SIZE = 512
    # Ensure divisible by resolution
    OUTPUT_SIZE = (OUTPUT_SIZE // args.resolution) * args.resolution
    if OUTPUT_SIZE == 0: OUTPUT_SIZE = args.resolution 
    
    if args.verbose: print(f"Output Size: {OUTPUT_SIZE}x{OUTPUT_SIZE}")
    
    src_img = load_and_process_image(args.src, OUTPUT_SIZE)
    tgt_img = load_and_process_image(tgt_path, OUTPUT_SIZE)
    
    # 2. Get cells and features
    if args.verbose: print("Extracting features...")
    src_cells, src_pos = get_cells(src_img, args.resolution)
    tgt_cells, tgt_pos = get_cells(tgt_img, args.resolution)
    
    src_features = extract_features(src_cells)
    tgt_features = extract_features(tgt_cells)
    
    # 3. Compute assignment
    if args.verbose: print("Computing assignment...")
    
    # Cap optimal
    if args.algorithm == "optimal" and args.resolution > 80:
        print(f"WARNING: 'optimal' algorithm with resolution {args.resolution} is too slow.")
        print("Switching to 'sort' algorithm automatically.")
        args.algorithm = "sort"
    
    # Pass features directly to solve_assignment
    assignment = solve_assignment(src_features, src_pos, tgt_features, tgt_pos, 
                                  args.algorithm, args.proximity_importance)
    
    # 4. Animate
    if args.verbose: print("Generating animation...")
    
    # Create generator
    frames_gen = generate_frames(src_cells, src_pos, tgt_pos, tgt_cells, assignment, 
                             args.duration, args.fps, OUTPUT_SIZE, args.jitter,
                             args.particle_scale, args.shape, args.color_mix,
                             args.hold_start, args.hold_end)
    
    # Handle Preview vs Save
    if args.preview:
        from .gui import show_preview
        show_preview(frames_gen, int(1000/args.fps))
             
    else:
        # 5. Save
        out_path = args.out
        
        # Ensure outputs directory
        if not out_path.startswith("outputs/") and not out_path.startswith("outputs\\"):
            out_path = os.path.join("outputs", os.path.basename(out_path))
        
        if not out_path.lower().endswith(('.mp4', '.gif')):
            out_path += ".mp4"
            
        save_video(frames_gen, out_path, args.fps)
        print("Done!")

if __name__ == "__main__":
    main()
