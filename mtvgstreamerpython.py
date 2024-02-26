import asyncio
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstRtspServer
import fastapi
from fastapi import FastAPI, WebSocket, BackgroundTasks
import threading

app = FastAPI()

# Global variable for GStreamer pipeline (ensuring singleton-like behavior)
pipeline = None

def create_pipeline(path):
    """
    Creates and returns a GStreamer pipeline for video playback.
    """
    global pipeline

    if pipeline is not None:
        # Reuse existing pipeline if already created
        return pipeline

    # Create pipeline elements
    pipeline = Gst.parse_launch(
        f"filesrc location={path} ! decodebin ! autovideosink"
    )

    # Handle pipeline EOS (End-of-Stream) event
    bus = pipeline.get_bus()
    bus.add_watch(lambda bus, message: handle_eos(bus, message))

    return pipeline

def handle_eos(bus, message):
    """
    Handles End-of-Stream (EOS) event and stops the pipeline.
    """
    global pipeline

    if message.get_structure().get_name() == "EOS":
        loop = asyncio.get_event_loop()
        loop.call_soon_threadsafe(lambda: stop_video())

def start_video(path):
    """
    Starts video playback on the GStreamer pipeline.
    """
    global pipeline

    pipeline = create_pipeline(path)

    # Start the pipeline
    pipeline.set_state(Gst.State.PLAYING)

def stop_video():
    """
    Stops video playback on the GStreamer pipeline.
    """
    global pipeline

    if pipeline is not None:
        pipeline.set_state(Gst.State.NULL)
        pipeline = None  # Reset pipeline for next request

def pause_video():
    """
    Pauses video playback on the GStreamer pipeline.
    """
    global pipeline

    if pipeline is not None:
        pipeline.set_state(Gst.State.PAUSED)

def play_video():
    """
    Resumes video playback on the GStreamer pipeline.
    """
    global pipeline

    if pipeline is not None:
        pipeline.set_state(Gst.State.PLAYING)

@app.get("/start/{path:path}")
async def start_video_handler(path: str, background_tasks: BackgroundTasks):
    """
    Starts video playback based on the provided path.
    """
    background_tasks.add_task(start_video, path)
    return {"message": "Video started successfully."}

@app.get("/stop")
async def stop_video_handler():
    """
    Stops video playback.
    """
    stop_video()
    return {"message": "Video stopped successfully."}

@app.get("/play")
async def play_video_handler():
    """
    Resumes video playback from a paused state.
    """
    play_video()
    return {"message": "Video playback resumed."}

@app.get("/pause")
async def pause_video_handler():
    """
    Pauses video playback.
    """
    pause_video()
    return {"message": "Video playback paused."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
