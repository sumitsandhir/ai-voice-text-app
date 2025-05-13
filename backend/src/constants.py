import os

# Application settings
APPLICATION_WIDTH = 80

# Audio settings
RECORD_SEC = 5  # Duration of each recording batch in seconds
SAMPLE_RATE = 44100  # Audio sample rate

# File paths
OUTPUT_FILE_NAME = os.path.join("output", "recorded_audio.wav")

# Interview settings
INTERVIEW_POSTION = "Full Stack Developer"  # Change this to the position you're interviewing for

# API keys - not needed for local models
OPENAI_API_KEY = ""  # Leave empty since we're not using OpenAI
