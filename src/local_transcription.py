import os
from loguru import logger
import requests
from src.constants import OUTPUT_FILE_NAME, INTERVIEW_POSTION
from src.local_whisper import transcribe_audio_locally  # Import Whisper-based function

def transcribe_local(path_to_file=OUTPUT_FILE_NAME):
    """
    Transcribes audio using the locally-installed Whisper model.
    """
    if not os.path.exists(path_to_file):
        raise Exception(f"Audio file not found at {path_to_file}. Please record audio first.")
    try:
        logger.info("Transcribing audio with Whisper...")
        text = transcribe_audio_locally(path_to_file)
        logger.info(f"Whisper transcription successful: {text[:50]}...")
        return text
    except Exception as e:
        logger.error(f"Error in transcription: {e}")
        return f"Transcription error: {e}"

def generate_answer_with_ollama(transcript, short_answer=True, temperature=0.7):
    """
    Generates an answer based on the given transcript using Ollama.
    """
    # Define system prompts
    if short_answer:
        instruction = (
            "Concisely respond, limiting your answer to 70 words. "
            "If the question asks for an example or can be demonstrated with code, provide a code example along with your concise explanation."
        )
        max_tokens = 500
    else:
        instruction = (
            "Before answering, take a deep breath and think one step at a time. "
            "Provide a complete answer in no more than 300 words. "
            "If possible, always write your answer with code and briefly explain the code."
            "If question is related to architecture make sure you always explain the proper architecture"
        )
        max_tokens = 10000

    system_prompt = f"You are interviewing for a {INTERVIEW_POSTION} position. Respond professionally."

    try:
        # Craft the prompt
        prompt = f"""
{system_prompt}

Question from interview (transcribed audio): {transcript}

{instruction}

Your answer:
"""

        # Prepare the request payload
        payload = {
            "model": "llama2",  # or any other model you have on Ollama
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        # Make the request to Ollama
        logger.debug(f"Sending request to Ollama...")
        response = requests.post("http://localhost:11434/api/generate", json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            answer = response.json().get("response", "")
            logger.debug(f"Received response from Ollama: {answer[:50]}...")
            return answer
        else:
            error = f"Error from Ollama API: {response.status_code} - {response.text}"
            logger.error(error)
            return f"Error generating answer: {error}"

    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return "Sorry, I couldn't generate an answer. Make sure Ollama is running correctly."