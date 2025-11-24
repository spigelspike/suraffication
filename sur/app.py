from flask import Flask, render_template, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
import uuid
from py_surrafication.core import load_and_process_image, get_cells, extract_features
from py_surrafication.assignment import solve_assignment
from py_surrafication.animate import generate_frames, save_video

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure folders exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('outputs', exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get uploaded source file
        if 'source' not in request.files:
            return jsonify({'error': 'Missing source image'}), 400
        
        source_file = request.files['source']
        
        if source_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(source_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save uploaded source file
        session_id = str(uuid.uuid4())
        source_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{session_id}_source.jpg')
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'{session_id}_output.mp4')
        
        # Use fixed ASCII target
        target_path = os.path.join('examples', 'ascii_target.png')
        print(f"DEBUG: Looking for target at: {os.path.abspath(target_path)}")
        print(f"DEBUG: Exists? {os.path.exists(target_path)}")
        
        if not os.path.exists(target_path):
            return jsonify({'error': f'Target image not found at {os.path.abspath(target_path)}'}), 500
        
        source_file.save(source_path)
        
        # Get parameters
        preset = request.form.get('preset', 'sand')
        resolution = int(request.form.get('resolution', 64))
        algorithm = request.form.get('algorithm', 'sort')
        
        # Apply preset defaults
        if preset == 'sand':
            resolution = 128
            algorithm = 'sort'
            particle_scale = 0.5
            color_mix = 0.0
            shape = 'circle'
            jitter = 0.1
        elif preset == 'blocks':
            resolution = 32
            algorithm = 'optimal'
            particle_scale = 1.0
            color_mix = 0.0
            shape = 'square'
            jitter = 0.0
        elif preset == 'bubbles':
            resolution = 64
            algorithm = 'greedy'
            particle_scale = 0.8
            color_mix = 0.2
            shape = 'circle'
            jitter = 0.05
        else:  # custom
            particle_scale = float(request.form.get('particle_scale', 0.6))
            color_mix = float(request.form.get('color_mix', 0.0))
            shape = request.form.get('shape', 'circle')
            jitter = float(request.form.get('jitter', 0.05))
        
        # Process images
        OUTPUT_SIZE = 512
        OUTPUT_SIZE = (OUTPUT_SIZE // resolution) * resolution
        if OUTPUT_SIZE == 0: OUTPUT_SIZE = resolution
        
        src_img = load_and_process_image(source_path, OUTPUT_SIZE)
        tgt_img = load_and_process_image(target_path, OUTPUT_SIZE)
        
        # Get cells and features
        src_cells, src_pos = get_cells(src_img, resolution)
        tgt_cells, tgt_pos = get_cells(tgt_img, resolution)
        
        src_features = extract_features(src_cells)
        tgt_features = extract_features(tgt_cells)
        
        # Cap optimal for large grids
        if algorithm == "optimal" and resolution > 80:
            algorithm = "sort"
        
        # Compute assignment
        assignment = solve_assignment(src_features, src_pos, tgt_features, tgt_pos, 
                                      algorithm, 0.3)
        
        # Generate frames
        frames_gen = generate_frames(src_cells, src_pos, tgt_pos, tgt_cells, assignment,
                                     6.0, 30, OUTPUT_SIZE, jitter,
                                     particle_scale, shape, color_mix,
                                     1.0, 2.0)
        
        # Save video
        save_video(frames_gen, output_path, 30)
        
        # Clean up uploaded source file
        os.remove(source_path)
        
        return jsonify({
            'success': True,
            'video_url': f'/download/{session_id}_output.mp4'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    return send_file(
        os.path.join(app.config['OUTPUT_FOLDER'], filename),
        as_attachment=True,
        download_name=filename
    )

@app.route('/examples/<filename>')
def serve_examples(filename):
    """Serve files from the examples folder"""
    return send_file(
        os.path.join('examples', filename),
        mimetype='image/jpeg' if filename.endswith('.jpg') else None
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
