import os
import whisper
from loguru import logger

from backend.src.constants import (OUTPUT_FILE_NAME)

# Load the model (only once)
# Options are: 'tiny', 'base', 'small', 'medium', 'large'
MODEL_SIZE = 'base'  # Use 'base' for a balance of speed and accuracy
model = None

def get_model():
    global model
    if model is None:
        logger.info(f"Loading Whisper {MODEL_SIZE} model...")
        model = whisper.load_model(MODEL_SIZE)
        logger.info("Model loaded successfully")
    return model

def transcribe_audio_locally(path_to_file=OUTPUT_FILE_NAME):
    """
    Transcribes audio using the locally-installed Whisper model.
    No OpenAI API key required.
    """
    if not os.path.exists(path_to_file):
        raise Exception(f"Audio file not found at {path_to_file}. Please record audio first.")

    try:
        # Get the model
        model = get_model()

        # Transcribe the audio
        logger.debug(f"Transcribing audio from {path_to_file}...")
        result = model.transcribe(path_to_file)

        return result["text"]
    except Exception as e:
        logger.error(f"Error transcribing audio locally: {e}")
        raise Exception(f"Failed to transcribe audio: {e}")