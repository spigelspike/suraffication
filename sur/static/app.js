// File upload handling
const sourceFile = document.getElementById('sourceFile');
const uploadArea = document.getElementById('uploadArea');
const uploadLabel = uploadArea.querySelector('.upload-label');
const previewContainer = document.getElementById('previewContainer');
const imagePreview = document.getElementById('imagePreview');
const removeBtn = document.getElementById('removeBtn');

// Handle file selection
sourceFile.addEventListener('change', handleFileSelect);

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadLabel.style.borderColor = 'var(--primary)';
    uploadLabel.style.background = 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(167, 139, 250, 0.15))';
});

uploadArea.addEventListener('dragleave', () => {
    uploadLabel.style.borderColor = '';
    uploadLabel.style.background = '';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadLabel.style.borderColor = '';
    uploadLabel.style.background = '';

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        sourceFile.files = files;
        handleFileSelect();
    }
});

function handleFileSelect() {
    const file = sourceFile.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            uploadLabel.style.display = 'none';
            previewContainer.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// Remove image
removeBtn.addEventListener('click', () => {
    sourceFile.value = '';
    uploadLabel.style.display = 'flex';
    previewContainer.style.display = 'none';
    imagePreview.src = '';
});

// Preset handling
const presetButtons = document.querySelectorAll('.preset-card');
const presetInput = document.getElementById('presetInput');

presetButtons.forEach(btn => {
    btn.addEventListener('click', function () {
        presetButtons.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        presetInput.value = this.dataset.preset;
    });
});

// Form submission
const uploadForm = document.getElementById('uploadForm');
const generateBtn = document.getElementById('generateBtn');
const btnText = document.getElementById('btnText');
const btnLoader = document.getElementById('btnLoader');
const progress = document.getElementById('progress');
const result = document.getElementById('result');
const error = document.getElementById('error');
const errorText = document.getElementById('errorText');

uploadForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    // Validate file
    if (!sourceFile.files.length) {
        showError('Please upload an image first!');
        return;
    }

    // Hide previous states
    result.style.display = 'none';
    error.style.display = 'none';

    // Show progress
    progress.style.display = 'block';
    generateBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';

    // Scroll to progress
    progress.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Create FormData
    const formData = new FormData(uploadForm);

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            let errorMessage = 'Unknown error occurred';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                // If response is not JSON (e.g. HTML error page), use status text
                errorMessage = `Server Error: ${response.status} ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();

        if (data.success) {
            // Show result
            progress.style.display = 'none';
            result.style.display = 'block';

            const resultVideo = document.getElementById('resultVideo');
            const downloadBtn = document.getElementById('downloadBtn');

            resultVideo.src = data.video_url;
            downloadBtn.href = data.video_url;

            // Scroll to result
            result.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            throw new Error(data.error || 'Unknown error occurred');
        }
    } catch (err) {
        progress.style.display = 'none';
        showError(err.message);
    } finally {
        // Re-enable button
        generateBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

function showError(message) {
    error.style.display = 'block';
    errorText.textContent = message;
    error.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Auto-hide after 5 seconds
    setTimeout(() => {
        error.style.display = 'none';
    }, 5000);
}
