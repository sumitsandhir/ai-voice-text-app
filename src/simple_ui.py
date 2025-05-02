import os
import threading

import PySimpleGUI as sg
import numpy as np
import sounddevice as sd
import soundfile as sf
from loguru import logger

from src import llm, local_transcription
from src.constants import APPLICATION_WIDTH, OUTPUT_FILE_NAME, RECORD_SEC, SAMPLE_RATE

def run_app():
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE_NAME), exist_ok=True)

    # Global variables for recording state
    recording_thread = None
    is_recording = False
    recording_saved = False

    # Set up the GUI
    sg.theme("DarkAmber")

    record_button = sg.Button("⚫ Start Recording", key="-RECORD_BUTTON-")
    status_text = sg.Text("Ready", size=(30, 1), key="-STATUS-")
    # SCROLLABLE, large multiline elements for all output areas:
    analyzed_text_label = sg.Multiline(
        "", size=(APPLICATION_WIDTH, 3), key="-ANALYZED-", autoscroll=True, disabled=True,
        font=("Consolas", 11)
    )
    quick_chat_gpt_answer = sg.Multiline(
        "", size=(APPLICATION_WIDTH, 8), key="-SHORT-", autoscroll=True, disabled=True,
        font=("Consolas", 11),
        sbar_background_color="#222"
    )
    full_chat_gpt_answer = sg.Multiline(
        "", size=(APPLICATION_WIDTH, 20), key="-FULL-", autoscroll=True, disabled=True,
        font=("Consolas", 11),
        sbar_background_color="#222"
    )

    # Audio source selection
    audio_source_layout = [
        [sg.Text("Audio Source:"),
         sg.Radio("Microphone", "AUDIO_SOURCE", default=True, key="-MIC_SOURCE-"),
         sg.Radio("System Audio (Teams/Meet)", "AUDIO_SOURCE", key="-SYSTEM_SOURCE-")]
    ]

    layout = [
        [sg.Text("Press R to start/stop recording", size=(int(APPLICATION_WIDTH * 0.8), 2)), record_button],
        [sg.Text("Press A to analyze the recording"), status_text],
        [sg.Frame("Audio Source", audio_source_layout)],
        [analyzed_text_label],
        [sg.Text("Short answer:")],
        [quick_chat_gpt_answer],
        [sg.Text("Full answer:")],
        [full_chat_gpt_answer],
        [sg.Button("Cancel")]
    ]

    window = sg.Window(
        "Interview Assistant", layout,
        return_keyboard_events=True,
        use_default_focus=False,
        finalize=True,
        resizable=True
    )

    # Function to record from microphone
    def record_microphone(seconds=RECORD_SEC, sample_rate=SAMPLE_RATE):
        """Record audio from the microphone."""
        logger.debug(f"Recording microphone audio for {seconds} second(s)...")
        try:
            # Record audio from microphone
            recording = sd.rec(
                int(seconds * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()  # Wait until recording is finished
            logger.debug("Microphone recording complete.")
            return recording
        except Exception as e:
            logger.error(f"Error recording from microphone: {e}")
            raise Exception(f"Failed to record from microphone: {e}")

    # Function to record system audio using sounddevice
    def record_system_audio_alt(seconds=RECORD_SEC, sample_rate=SAMPLE_RATE):
        """Alternative method to record system audio."""
        logger.debug(f"Recording system audio for {seconds} second(s) using alternative method...")
        try:
            # Try to get system audio devices - this is platform dependent
            devices = sd.query_devices()
            logger.debug(f"Available audio devices: {len(devices)}")

            # Try to find a loopback device
            loopback_device = None
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                if any(word in device_name for word in ['loopback', 'output', 'monitor', 'system']):
                    if device.get('max_input_channels', 0) > 0:
                        loopback_device = i
                        logger.debug(f"Found potential system audio device: {device['name']} (index {i})")
                        break

            if loopback_device is not None:
                logger.debug(f"Using device {loopback_device} for system audio")
                recording = sd.rec(
                    int(seconds * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype='float32',
                    device=loopback_device
                )
                sd.wait()
                logger.debug("System audio recording complete.")
                return recording
            else:
                # Fallback to default input device
                logger.warning("No loopback device found, falling back to default input")
                return record_microphone(seconds, sample_rate)

        except Exception as e:
            logger.error(f"Error recording system audio (alt method): {e}")
            # Fall back to microphone recording if system audio fails
            logger.warning("Falling back to microphone recording")
            return record_microphone(seconds, sample_rate)

    # Function to save audio data to file
    def save_audio_file(audio_data, output_file=OUTPUT_FILE_NAME):
        """Save audio data to file."""
        logger.debug(f"Saving audio to {output_file}")
        try:
            sf.write(output_file, audio_data, SAMPLE_RATE)
            logger.debug("Audio saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            return False

    # Recording function that runs in a separate thread
    def recording_worker():
        nonlocal is_recording, recording_saved
        audio_data = None

        logger.debug("Recording thread started")
        window["-STATUS-"].update("Recording...")
        recording_saved = False

        # Remove previous recording file to avoid analyzing old data
        if os.path.exists(OUTPUT_FILE_NAME):
            try:
                os.remove(OUTPUT_FILE_NAME)
                logger.debug(f"Removed previous recording: {OUTPUT_FILE_NAME}")
            except Exception as e:
                logger.error(f"Could not remove previous recording: {e}")

        while is_recording:
            try:
                # Choose recording method based on selected audio source
                use_system_audio = values["-SYSTEM_SOURCE-"]
                if use_system_audio:
                    try:
                        audio_sample = record_system_audio_alt()
                        logger.debug("Recorded system audio batch")
                    except Exception as e:
                        logger.error(f"System audio recording failed: {e}. Falling back to microphone.")
                        audio_sample = record_microphone()
                else:
                    # Use microphone recording
                    audio_sample = record_microphone()
                    logger.debug("Recorded microphone audio batch")

                if audio_data is None:
                    audio_data = audio_sample
                else:
                    audio_data = np.vstack((audio_data, audio_sample))

            except Exception as e:
                logger.error(f"Recording error: {e}")
                is_recording = False
                window["-STATUS-"].update(f"Error: {str(e)}")
                break

        logger.debug("Recording thread ending, saving audio")
        window["-STATUS-"].update("Saving recording...")

        # Save the audio when recording is stopped
        if audio_data is not None and len(audio_data) > 0:
            if save_audio_file(audio_data):
                recording_saved = True
                window["-STATUS-"].update("Recording saved")
            else:
                window["-STATUS-"].update("Failed to save recording")
        else:
            window["-STATUS-"].update("No audio recorded")

    # Main event loop
    while True:
        event, values = window.read(timeout=100)

        if event in (sg.WIN_CLOSED, "Cancel"):
            logger.debug("Closing application")
            # Stop recording if active
            is_recording = False
            if recording_thread and recording_thread.is_alive():
                recording_thread.join(timeout=1.0)
            break

        # Start/stop recording with either button or 'r' key
        if event in ("-RECORD_BUTTON-", "r", "R"):
            if not is_recording:
                # Start recording
                is_recording = True
                recording_saved = False
                source_type = "system audio" if values["-SYSTEM_SOURCE-"] else "microphone"
                logger.debug(f"Starting recording from {source_type}")
                window["-RECORD_BUTTON-"].update(f"🔴 Stop Recording ({source_type})")

                # Clear previous analysis results
                window["-ANALYZED-"].update("")
                window["-SHORT-"].update("")
                window["-FULL-"].update("")

                # Start a new recording thread
                recording_thread = threading.Thread(target=recording_worker, daemon=True)
                recording_thread.start()
            else:
                # Stop recording
                logger.debug("Stopping recording")
                is_recording = False
                window["-RECORD_BUTTON-"].update("⚫ Start Recording")
                window["-STATUS-"].update("Finishing recording...")

        # Analyze audio with 'a' key
        elif event in ("a", "A"):
            # Don't allow analysis while recording is in progress
            if is_recording:
                window["-STATUS-"].update("Please stop recording first")
                continue

            # Check if recording has been saved
            if not recording_saved and not os.path.exists(OUTPUT_FILE_NAME):
                window["-STATUS-"].update("No recording available to analyze")
                continue

            logger.debug("Analyzing audio...")
            window["-STATUS-"].update("Analyzing...")

            # Transcribe audio
            try:
                window["-STATUS-"].update("Transcribing audio...")
                window["-ANALYZED-"].update("Transcribing audio...")
                window.refresh()

                audio_transcript = local_transcription.transcribe_local()
                window["-ANALYZED-"].update(audio_transcript)
                window["-STATUS-"].update("Transcription complete")
                window.refresh()

                # Generate answers if transcription was successful
                if "error" not in audio_transcript.lower() and "could not" not in audio_transcript.lower():
                    # Short answer
                    window["-STATUS-"].update("Generating short answer...")
                    window["-SHORT-"].update("Generating short answer...")
                    window.refresh()

                    short_answer = llm.generate_answer(audio_transcript, short_answer=True, temperature=0)
                    window["-SHORT-"].update(short_answer)

                    # Full answer
                    window["-STATUS-"].update("Generating full answer...")
                    window["-FULL-"].update("Generating full answer...")
                    window.refresh()

                    full_answer = llm.generate_answer(audio_transcript, short_answer=False, temperature=0.7)
                    window["-FULL-"].update(full_answer)

                    window["-STATUS-"].update("Analysis complete")
                else:
                    window["-STATUS-"].update("Transcription failed")
            except Exception as e:
                logger.error(f"Error analyzing audio: {e}")
                window["-ANALYZED-"].update(f"Error: {e}")
                window["-STATUS-"].update(f"Analysis error: {str(e)}")

    window.close()


if __name__ == "__main__":
    run_app()