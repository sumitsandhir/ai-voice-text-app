"""Audio utilities."""
import numpy as np
import soundcard as sc  # Add this import at the top
from loguru import logger

from src.constants import RECORD_SEC, SAMPLE_RATE


# ... existing functions ...

def record_system_audio(record_sec: int = RECORD_SEC) -> np.ndarray:
    """
    Records system audio (speaker output) for a specified duration.
    """
    logger.debug(f"Recording system audio for {record_sec} second(s)...")

    try:
        # Get default speaker
        default_speaker = sc.default_speaker()
        logger.debug(f"Default output device: {default_speaker.name}")

        # Record audio
        with default_speaker.recorder(samplerate=SAMPLE_RATE) as recorder:
            audio_data = recorder.record(numframes=int(SAMPLE_RATE * record_sec))

            # Convert to mono if needed
            if audio_data.shape[1] > 1:
                audio_data = np.mean(audio_data, axis=1)

            # Reshape to match expected format
            audio_data = audio_data.reshape(-1, 1)

        logger.debug("System audio recording complete.")
        return audio_data

    except Exception as e:
        logger.error(f"Error recording system audio: {e}")
        raise Exception(f"Failed to record system audio: {e}")