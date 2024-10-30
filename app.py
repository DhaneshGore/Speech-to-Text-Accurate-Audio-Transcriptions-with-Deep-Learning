from flask import Flask, request, render_template, jsonify
from wav2vec2_inference import transcribe_wav
from pydub import AudioSegment
import os

# Initialize the Flask app
app = Flask(__name__)

# Ensure the 'uploads' folder exists for saving uploaded files
os.makedirs("uploads", exist_ok=True)

# Limit maximum file size (e.g., 16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    # Render the HTML template for file upload
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Check if a file is in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    filename = file.filename

    # Validate file type (you can expand this list)
    if not (filename.endswith('.wav') or filename.endswith('.mp3') or filename.endswith('.ogg')):
        return jsonify({'error': 'Unsupported file type. Please upload a .wav, .mp3, or .ogg file.'}), 400

    # Define the path for saving the uploaded file
    input_path = os.path.join('uploads', filename)

    # Save the uploaded file
    file.save(input_path)

    # Convert file to .wav if it isn't already
    if not filename.endswith('.wav'):
        try:
            # Convert to .wav using pydub
            audio = AudioSegment.from_file(input_path)
            wav_path = os.path.join('uploads', os.path.splitext(filename)[0] + '.wav')
            audio.export(wav_path, format='wav')
            input_path = wav_path  # Update path to the converted file
        except Exception as e:
            return jsonify({'error': f'Failed to convert audio file to .wav format: {e}'}), 500

    # Use the transcribe function from wav2vec2_inference.py
    try:
        text = transcribe_wav(input_path)
        return jsonify({'transcription': text})
    except Exception as e:
        return jsonify({'error': f'An error occurred during transcription: {e}'}), 500
    finally:
        # Clean up: Delete the uploaded file to save space
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == '__main__':
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
