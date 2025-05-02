import os
import time
import numpy as np
import sounddevice as sd
import soundfile as sf

# Define constants
SAMPLE_RATE = 48000
RECORD_SEC = 5  # Record for 5 seconds to test

def test_sounddevice_recording():
    print("Testing sounddevice recording with AirPods/earbuds...")
    print("Please make sure your earbuds are connected and selected as the input device")

    try:
        # List available input devices
        print("\nAvailable audio devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"Device {i}: {device['name']} (inputs: {device['max_input_channels']}, outputs: {device['max_output_channels']})")

        # Show default device
        default_device = sd.query_devices(kind='input')
        print(f"\nDefault input device: {default_device['name']}")

        # Give user a chance to prepare
        print("\nRecording will start in 3 seconds... Please speak during recording.")
        time.sleep(3)

        print(f"Recording for {RECORD_SEC} seconds...")

        # Start recording
        audio_data = sd.rec(
            int(SAMPLE_RATE * RECORD_SEC),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='float32'
        )

        # Wait for recording to complete
        sd.wait()
        print("Recording complete!")

        # Save the audio file
        output_file = "test_sounddevice.wav"
        print(f"Saving to {output_file}...")

        # Normalize audio (optional)
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))

        sf.write(file=output_file, data=audio_data, samplerate=SAMPLE_RATE)

        # Check if file was created
        if os.path.exists(output_file):
            print(f"Success! Audio saved to {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
            return True
        else:
            print("Error: File was not created")
            return False

    except Exception as e:
        print(f"Error during recording: {e}")
        return False

if __name__ == "__main__":
    test_sounddevice_recording()