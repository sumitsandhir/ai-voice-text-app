import os
import sys

# Silence Tk deprecation warning on macOS
os.environ['TK_SILENCE_DEPRECATION'] = '1'

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now import and run the actual script
from src.test_gui import VoiceApp

if __name__ == "__main__":
    app = VoiceApp()
    app.run()
