from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import librosa

# Load the Wav2Vec2 model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

def transcribe_wav(file_path):
    """
    Transcribe a .wav file to text using Facebook's Wav2Vec2 model.
    
    Args:
        file_path (str): Path to the .wav file
    
    Returns:
        str: Transcribed text
    """
    # Load the audio file
    speech, rate = librosa.load(file_path, sr=16000)
    
    # Process the audio with the Wav2Vec2 processor
    input_values = processor(speech, sampling_rate=rate, return_tensors="pt").input_values

    # Perform the transcription
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    
    # Decode the predicted IDs to text
    transcription = processor.decode(predicted_ids[0])
    
    return transcription
