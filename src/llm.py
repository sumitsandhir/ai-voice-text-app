import os
import requests
from loguru import logger

from src.constants import OUTPUT_FILE_NAME, INTERVIEW_POSTION

# Try to import SpeechRecognition and check availability
try:
    import speech_recognition as sr
    speech_recognition_available = True
except ImportError:
    speech_recognition_available = False
    logger.warning("SpeechRecognition not installed. Install with: pip install SpeechRecognition")

def transcribe_audio(path_to_file=OUTPUT_FILE_NAME):
    """
    Transcribe audio to text using SpeechRecognition.
    """
    if not os.path.exists(path_to_file):
        return f"Audio file not found at {path_to_file}. Please record audio first."

    if not speech_recognition_available:
        return "Speech recognition is not available. Please install with: pip install SpeechRecognition"

    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(path_to_file) as source:
            audio_data = recognizer.record(source)

        try:
            logger.info("Trying Google Speech Recognition...")
            text = recognizer.recognize_google(audio_data)
            logger.info(f"Transcription successful: {text[:50]}...")
            return text
        except sr.RequestError:
            logger.warning("Could not request results from Google Speech Recognition service")
            return "Could not connect to Google Speech Recognition service. Check your internet connection."
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return "Could not understand the audio. Please speak more clearly or check your microphone."
    except Exception as e:
        logger.error(f"Error in transcription: {e}")
        return f"Transcription error: {e}"

def generate_answer(transcript, short_answer=True, temperature=0.7):
    """
    Generates an answer based on the given transcript using Ollama.
    """
    try:
        # Choose prompt style
        if short_answer:
            instruction = "Concisely respond, limiting your answer to 70 words."
            max_tokens = 250
        else:
            instruction = "Before answering, take a deep breath and think one step at a time. Provide a complete answer in no more than 150 words."
            max_tokens = 500

        system_prompt = f"You are interviewing for a {INTERVIEW_POSTION} position. Respond professionally."
        prompt = f"""{system_prompt}\n\nQuestion from interview (transcribed audio): {transcript}\n\n{instruction}\n\nYour answer:\n"""

        payload = {
            "model": "llama2",  # or whichever model is configured
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        logger.debug("Sending request to Ollama...")
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)

        if response.status_code == 200:
            answer = response.json().get("response", "")
            logger.debug(f"Received response: {answer[:50]}...")
            return answer
        else:
            error_msg = f"Error from Ollama API: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return f"Error generating answer: {error_msg}"
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return "Sorry, I couldn't generate an answer. Make sure Ollama is running correctly."
