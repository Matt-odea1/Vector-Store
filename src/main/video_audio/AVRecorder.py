"""
AVRecorder Service (MVP)
Records video and audio simultaneously, then combines them into a single MP4 file using moviepy.
Synchronizes start by waiting for both recorders to be ready, then triggers recording.
"""
from VideoRecorder import VideoRecorder
from AudioRecorder import AudioRecorder
from moviepy import VideoFileClip, AudioFileClip
import os
import threading

class AVRecorder:
    """
    Service to record video and audio at the same time, then combine into one MP4 file.
    Synchronizes start for better AV sync.
    """
    def __init__(self, video_path="temp_video.mp4", audio_path="temp_audio.wav", output_path="output_av.mp4", duration=10):
        self.video_path = video_path
        self.audio_path = audio_path
        self.output_path = output_path
        self.duration = duration

    def record(self):
        """
        Record video and audio simultaneously, then combine into one MP4 file.
        Trims both to the shortest duration to improve sync.
        """
        start_event = threading.Event()
        ready_events = [threading.Event(), threading.Event()]
        # NOTE: VideoRecorder and AudioRecorder should be updated to accept start_event and ready_event, signal ready, then wait for start_event before recording.
        video_recorder = VideoRecorder(output_path=self.video_path, duration=self.duration, frame_size=None, start_event=start_event, ready_event=ready_events[0])
        audio_recorder = AudioRecorder(output_path=self.audio_path, duration=self.duration, start_event=start_event, ready_event=ready_events[1])
        video_thread = threading.Thread(target=video_recorder.record)
        audio_thread = threading.Thread(target=audio_recorder.record)
        video_thread.start()
        audio_thread.start()
        # Wait for both recorders to be ready
        ready_events[0].wait()
        ready_events[1].wait()
        # Trigger simultaneous start
        start_event.set()
        video_thread.join()
        audio_thread.join()
        # Combine using moviepy
        video_clip = VideoFileClip(self.video_path)
        audio_clip = AudioFileClip(self.audio_path)
        min_duration = min(video_clip.duration, audio_clip.duration)
        print(f"Video duration: {video_clip.duration:.2f}s, Audio duration: {audio_clip.duration:.2f}s, Using: {min_duration:.2f}s")
        video_clip = video_clip.subclip(0, min_duration)
        audio_clip = audio_clip.subclip(0, min_duration)
        final_clip = video_clip.with_audio(audio_clip)
        final_clip.write_videofile(self.output_path, codec="libx264", audio_codec="aac")
        # Clean up temp files
        try:
            os.remove(self.video_path)
            os.remove(self.audio_path)
        except Exception:
            pass
        print(f"Combined AV file saved to {self.output_path}")

    # Example usage/test
if __name__ == "__main__":
    av_recorder = AVRecorder(output_path="final_av.mp4", duration=5)
    av_recorder.record()
    print("AV recording complete.")