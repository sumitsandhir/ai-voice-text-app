import os
import numpy as np
from loguru import logger
import customtkinter as ctk
import threading
from src import audio, llm, local_transcription
from src.constants import APPLICATION_WIDTH, OUTPUT_FILE_NAME


class InterviewApp:
    def __init__(self):
        self.is_recording = False
        self.audio_data = None
        self.recording_thread = None

        # Print debug info
        logger.debug(f"Audio output file will be: {OUTPUT_FILE_NAME}")
        logger.debug(f"File exists: {os.path.exists(OUTPUT_FILE_NAME)}")
        logger.debug(f"Current working directory: {os.getcwd()}")

        # Configure the window
        self.app = ctk.CTk()
        self.app.title("Voice Assistant")
        self.app.geometry("800x700")  # Made taller to accommodate new elements

        # Configure the grid
        self.app.grid_columnconfigure(0, weight=1)

        # Create widgets
        self.record_button = ctk.CTkButton(
            self.app,
            text="Start Recording",
            command=self.toggle_recording
        )
        self.record_button.grid(row=0, column=0, padx=20, pady=10)

        self.analyze_button = ctk.CTkButton(
            self.app,
            text="Analyze Recording",
            command=self.analyze_recording
        )
        self.analyze_button.grid(row=1, column=0, padx=20, pady=10)

        self.analyzed_text = ctk.CTkTextbox(
            self.app,
            height=100,
            width=700
        )
        self.analyzed_text.grid(row=2, column=0, padx=20, pady=10)

        self.quick_answer_label = ctk.CTkLabel(self.app, text="Short Answer:")
        self.quick_answer_label.grid(row=3, column=0, padx=20, pady=(10, 0))

        self.quick_answer = ctk.CTkTextbox(
            self.app,
            height=100,
            width=700
        )
        self.quick_answer.grid(row=4, column=0, padx=20, pady=10)

        self.full_answer_label = ctk.CTkLabel(self.app, text="Full Answer:")
        self.full_answer_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.full_answer = ctk.CTkTextbox(
            self.app,
            height=200,
            width=700
        )
        self.full_answer.grid(row=6, column=0, padx=20, pady=10)

        # Add audio source selection
        self.audio_source_frame = ctk.CTkFrame(self.app)
        self.audio_source_frame.grid(row=7, column=0, padx=20, pady=10, sticky="w")

        self.audio_source_label = ctk.CTkLabel(self.audio_source_frame, text="Audio Source:")
        self.audio_source_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.audio_source_var = ctk.StringVar(value="microphone")

        self.mic_radio = ctk.CTkRadioButton(
            self.audio_source_frame,
            text="Microphone",
            variable=self.audio_source_var,
            value="microphone"
        )
        self.mic_radio.grid(row=0, column=1, padx=10, pady=5)

        self.system_radio = ctk.CTkRadioButton(
            self.audio_source_frame,
            text="System Audio (Teams/Meet)",
            variable=self.audio_source_var,
            value="system"
        )
        self.system_radio.grid(row=0, column=2, padx=10, pady=5)

    def background_recording_loop(self):
        self.audio_data = None
        while self.is_recording:
            try:
                # Choose recording method based on selected audio source
                if self.audio_source_var.get() == "system":
                    audio_sample = audio.record_system_audio()
                else:  # Default to microphone
                    audio_sample = audio.record_batch()

                if self.audio_data is None:
                    self.audio_data = audio_sample
                else:
                    self.audio_data = np.vstack((self.audio_data, audio_sample))
            except Exception as e:
                logger.error(f"Recording error: {e}")
                self.is_recording = False
                self.app.after(0, lambda: ctk.CTkMessagebox.show_error(
                    "Recording Error",
                    f"An error occurred during recording: {e}"
                ))

        # After recording is complete
        if self.audio_data is not None:
            audio.save_audio_file(self.audio_data)

    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            source_type = "system audio" if self.audio_source_var.get() == "system" else "microphone"
            logger.debug(f"Starting recording from {source_type}...")
            self.record_button.configure(text=f"Stop Recording ({source_type})")
            self.recording_thread = threading.Thread(target=self.background_recording_loop)
            self.recording_thread.start()
        else:
            logger.debug("Stopping recording...")
            self.record_button.configure(text="Start Recording")
            if self.recording_thread:
                self.recording_thread.join()

    def analyze_recording(self):
        logger.debug("Analyzing audio...")
        self.analyzed_text.delete("0.0", "end")
        self.analyzed_text.insert("0.0", "Start analyzing...")

        # Transcribe audio
        try:
            audio_transcript = local_transcription.transcribe_local()
            self.analyzed_text.delete("0.0", "end")
            self.analyzed_text.insert("0.0", audio_transcript)

            # Generate quick answer
            self.quick_answer.delete("0.0", "end")
            self.quick_answer.insert("0.0", "Chatgpt is working...")
            quick_answer_text = llm.generate_answer(audio_transcript, short_answer=True, temperature=0)
            self.quick_answer.delete("0.0", "end")
            self.quick_answer.insert("0.0", quick_answer_text)

            # Generate full answer
            self.full_answer.delete("0.0", "end")
            self.full_answer.insert("0.0", "Chatgpt is working...")
            full_answer_text = llm.generate_answer(audio_transcript, short_answer=False, temperature=0.7)
            self.full_answer.delete("0.0", "end")
            self.full_answer.insert("0.0", full_answer_text)
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            self.analyzed_text.delete("0.0", "end")
            self.analyzed_text.insert("0.0", f"Error: {e}")

    def run(self):
        self.app.mainloop()


if __name__ == "__main__":
    app = InterviewApp()
    app.run()