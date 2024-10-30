from flask import Flask, request, render_template, jsonify
from wav2vec2_inference import transcribe_wav
from pydub import AudioSegment
import os
import threading

app = Flask(__name__)

os.makedirs("uploads", exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

def async_transcribe(input_path, filename):
    try:
        text = transcribe_wav(input_path)
        # Here you could save the transcription result somewhere (e.g., database, cloud storage)
        print(f'Transcription for {filename}: {text}')  # Or handle it accordingly
    except Exception as e:
        print(f'Error during transcription of {filename}: {e}')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    filename = file.filename

    if not (filename.endswith('.wav') or filename.endswith('.mp3') or filename.endswith('.ogg')):
        return jsonify({'error': 'Unsupported file type. Please upload a .wav, .mp3, or .ogg file.'}), 400

    input_path = os.path.join('uploads', filename)
    file.save(input_path)

    if not filename.endswith('.wav'):
        try:
            audio = AudioSegment.from_file(input_path)
            wav_path = os.path.join('uploads', os.path.splitext(filename)[0] + '.wav')
            audio.export(wav_path, format='wav')
            input_path = wav_path
        except Exception as e:
            return jsonify({'error': f'Failed to convert audio file to .wav format: {e}'}), 500

    # Run transcription in a separate thread
    threading.Thread(target=async_transcribe, args=(input_path, filename)).start()

    return jsonify({'message': 'Transcription is being processed in the background.'}), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
