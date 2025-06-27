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

BANKING_KEYWORDS = [
    "bank", "customer", "finance", "loan", "credit", "debit", "statement", "interest rate",
    "regulation", "risk", "compliance", "investment", "mortgage", "branch",
    "retail banking", "commercial banking", "fintech", "ATM", "deposit",
    "withdrawal", "transaction", "fraud", "AML", "KYC", "payment", "treasury"
]

def is_banking_question(transcript: str) -> bool:
    lower_transcript = transcript.lower()
    return any(keyword in lower_transcript for keyword in BANKING_KEYWORDS)

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

def generate_answer(transcript, short_answer=True, temperature=0.3):
    """
    Generates an answer based on the given transcript using Ollama.
    For banking-related questions, use STAR model; otherwise, give end-to-end technical answer.
    """
    try:
        # Detect type of question
        if is_banking_question(transcript):
            # STAR model for banking
            model_instruction = (
                "Answer using the STAR (Situation, Task, Action, Result) framework. "
                "Give examples based on UK law & Regulations. "
                "Strongly emphasize the Action and Result sections: "
                "describe in detail **what YOU did to resolve the issue**, and provide specific, concrete examples of your actions and the positive outcome. "
                "Use first-person language and focus on your personal contribution."
            )
        else:
            # Technical: comprehensive end-to-end explanation
            model_instruction = (
                "Provide a comprehensive, step-by-step technical answer suitable for an interview. "
                "Explain your reasoning and solution clearly."
                "Also give coding examples for an interviewer to understand the solution."
            )

        # Prompt style
        if short_answer:
            instruction = "Limit your answer to about 70 words."
            max_tokens = 500
        else:
            instruction = "Keep your answer under 150 words."
            max_tokens = 5000

        # System and final prompts
        system_prompt = f"You are interviewing for a {INTERVIEW_POSTION} position. Respond professionally."
        prompt = (
            f"{system_prompt}\n\n"
            f"Question (transcribed audio): {transcript}\n\n"
            f"{model_instruction}\n"
            f"{instruction}\n\n"
            "Your answer:\n"
        )

        payload = {
            "model": "llama2",  # Set this as needed
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