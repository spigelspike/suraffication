# py-surrafication

A Python implementation of the "surrafication" concept: rearranging cells of a source image to match a target image, animated.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m py_surrafication \
    --src examples/demo_source.jpg \
    --tgt examples/sura.jpg \
    --out demo.mp4 \
    --resolution 64 \
    --algorithm optimal
```

### Arguments

- `--src`: Path to source image (required).
- `--tgt`: Path to target image (default: `target.jpg`).
- `--out`: Output video path (`.mp4` or `.gif`).
- `--duration`: Duration in seconds (default: 6.0).
- `--fps`: Frames per second (default: 30).
- `--resolution`: Grid resolution, e.g., 64 means 64x64 cells.
- `--proximity-importance`: 0.0 to 1.0. Lower means color matches are prioritized (more chaotic movement), higher means position is prioritized (subtle morph).
- `--algorithm`: `greedy` (fast, random), `approx` (fast, ordered), `optimal` (slow, best match).

## Algorithms

- **Greedy**: Fast but suboptimal. Good for high resolutions.
- **Approx**: A heuristic approach (currently ordered greedy).
- **Optimal**: Uses the Hungarian algorithm (`scipy.optimize.linear_sum_assignment`). Best quality but O(N^3). Avoid for resolutions > 80.

## 🌐 Web Application

A web interface is available! Run the Flask app:

```bash
python app.py
```

Visit `http://localhost:5000` to use the arcade-style web interface.

### Deploying to Render.com

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR-USERNAME/sura-nator.git
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Sign up at [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the settings from `Procfile`
   - Your app will be live at: `https://your-app-name.onrender.com`

### Features:
- 🎮 Retro arcade UI with CRT effects
- 📤 Drag & drop image upload
- 🎨 Multiple animation presets (Sand/Blocks/Bubbles)
- 📥 Download videos as MP4
