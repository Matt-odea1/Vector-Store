"""
AudioRecorder Service (MVP)
Records audio from the default microphone and saves to file using sounddevice and scipy.io.wavfile.
Synchronizes start with threading events for AV sync.
"""
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import threading

class AudioRecorder:
    """
    Service to record audio from microphone and save to file.
    Supports synchronized start for AV sync.
    """
    def __init__(self, output_path: str = "output.wav", duration: int = 10, sample_rate: int = 44100, channels: int = 1, start_event: threading.Event = None, ready_event: threading.Event = None):
        """
        Args:
            output_path (str): Path to save the audio file.
            duration (int): Duration to record in seconds.
            sample_rate (int): Audio sample rate (Hz).
            channels (int): Number of audio channels (1=mono, 2=stereo).
        """
        self.output_path = output_path
        self.duration = duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.start_event = start_event
        self.ready_event = ready_event

    def record(self):
        """
        Start recording audio from the default microphone.
        Waits for start_event if provided, signals ready_event after initialization.
        """
        print(f"AudioRecorder initializing...")
        if self.ready_event:
            self.ready_event.set()
        if self.start_event:
            self.start_event.wait()
        print(f"Recording audio for {self.duration} seconds...")
        audio = sd.rec(int(self.duration * self.sample_rate), samplerate=self.sample_rate, channels=self.channels, dtype='int16')
        sd.wait()  # Wait until recording is finished
        write(self.output_path, self.sample_rate, audio)
        print(f"Audio saved to {self.output_path}")

    # Example usage/test
    # if __name__ == "__main__":
    #     recorder = AudioRecorder(output_path="test.wav", duration=5)
    #     recorder.record()
    #     print("Audio saved to test.wav")

# TODO: Handle edge cases (microphone not found, permission errors, etc.)
