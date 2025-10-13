"""
VideoRecorder Service (MVP)
Records video from the default webcam and saves to file using OpenCV.
Synchronizes start with threading events for AV sync.
"""
import cv2
import time
import threading

class VideoRecorder:
    """
    Service to record video from webcam and save to file.
    Automatically configures frame size from webcam, or defaults to 1280x720 (MacBook typical).
    Supports synchronized start for AV sync.
    """
    def __init__(self, output_path: str = "output.avi", duration: int = 10, fps: int = 20, frame_size: tuple = None, start_event: threading.Event = None, ready_event: threading.Event = None):
        """
        Args:
            output_path (str): Path to save the video file.
            duration (int): Duration to record in seconds.
            fps (int): Frames per second.
            frame_size (tuple|None): (width, height) of video frames. If None, auto-detect from webcam or default to 1280x720.
        """
        self.output_path = output_path
        self.duration = duration
        self.fps = fps
        self.frame_size = frame_size
        self.start_event = start_event
        self.ready_event = ready_event

    def _get_frame_size(self, cap):
        """
        Get frame size from webcam, or default to 1280x720 if unavailable.
        """
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # If OpenCV returns 0, use MacBook default
        if width <= 0 or height <= 0:
            width, height = 1280, 720
        return (width, height)

    def record(self):
        """
        Start recording video from the default webcam.
        Waits for start_event if provided, signals ready_event after initialization.
        """
        print(f"VideoRecorder initializing...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Could not open webcam.")
        # Auto-configure frame size if not set
        if self.frame_size is None:
            self.frame_size = self._get_frame_size(cap)
        # Use correct codec for file extension
        if self.output_path.endswith('.mp4'):
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(self.output_path, fourcc, self.fps, self.frame_size)
        if self.ready_event:
            self.ready_event.set()
        if self.start_event:
            self.start_event.wait()
        print(f"Recording video for {self.duration} seconds...")
        start_time = time.time()
        while int(time.time() - start_time) < self.duration:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, self.frame_size)
            out.write(frame)
        cap.release()
        out.release()

    # Example usage/test
if __name__ == "__main__":
    recorder = VideoRecorder(output_path="test.mp4", duration=10, frame_size=None)
    recorder.record()
    print("Video saved to test.mp4")

# TODO: Handle edge cases (webcam not found, permission errors, etc.)
