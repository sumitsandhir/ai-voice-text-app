from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from src.local_transcription import transcribe_local, generate_answer_with_ollama
from src.response_generator import ResponseGenerator
from src.constants import OUTPUT_FILE_NAME

# Set up FastAPI app
app = FastAPI(
    title="Voice Recognition AI REST API",
    description="Endpoints for uploading audio, transcription, and generating LLM or rule-based responses.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your front-end domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

response_generator = ResponseGenerator()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Voice Recognition AI backend is running."}

@app.post("/transcribe/")
async def transcribe_audio(audio: UploadFile = File(...)):
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE_NAME), exist_ok=True)
        with open(OUTPUT_FILE_NAME, "wb") as f:
            f.write(await audio.read())
        transcript = transcribe_local(OUTPUT_FILE_NAME)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")
    finally:
        if os.path.exists(OUTPUT_FILE_NAME):
            os.remove(OUTPUT_FILE_NAME)

@app.post("/generate-response/")
async def generate_response(transcript: str = Form(...), use_llm: bool = Form(True)):
    try:
        if use_llm:
            answer = generate_answer_with_ollama(transcript)
        else:
            answer = response_generator.generate_response(transcript)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response generation failed: {e}")

@app.post("/ask/")
async def ask_endpoint(audio: UploadFile = File(...), use_llm: bool = Form(True)):
    """
    One endpoint: Upload audio, transcribe, and get a response (LLM or rule-based).
    """
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE_NAME), exist_ok=True)
        with open(OUTPUT_FILE_NAME, "wb") as f:
            f.write(await audio.read())
        transcript = transcribe_local(OUTPUT_FILE_NAME)
        if use_llm:
            answer = generate_answer_with_ollama(transcript)
        else:
            answer = response_generator.generate_response(transcript)
        return {"transcript": transcript, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
    finally:
        if os.path.exists(OUTPUT_FILE_NAME):
            os.remove(OUTPUT_FILE_NAME)